import json
import os
import numpy as np
import pandas as pd
import joblib
import requests
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# Configurations
MODEL_OUTPUT_PATH = "rental_model.pkl"
SCALER_OUTPUT_PATH = "rental_scaler.pkl"

# Configure Realtor API 
REALTOR_API_KEY = "ab95190718msh01306bce0ce10f9p12d666jsn866bf412bdeb"
REALTOR_HOST = "realty-in-us.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": REALTOR_API_KEY,
    "X-RapidAPI-Host": REALTOR_HOST,
    "Content-Type": "application/json"
}

def fetch_rental_data(cities, limit_per_city=100):
    """
    Fetch rental property data from the Realtor API for multiple cities
    """
    all_properties = []
    
    for city in cities:
        print(f"Fetching rental data for {city}...")
        url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"
        
        payload = {
            "limit": limit_per_city,
            "offset": 0,
            "status": ["for_rent"],
            "sort": {"direction": "desc", "field": "list_date"},
            "city": city,
            "state_code": get_state_code_for_city(city)
        }
        
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=15)
            if response.status_code == 200:
                results = response.json().get("data", {}).get("home_search", {}).get("results", [])
                all_properties.extend(results)
                print(f"  ✅ Successfully fetched {len(results)} properties for {city}")
            else:
                print(f"  ❌ API Error for {city}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Request Exception for {city}: {e}")
    
    return all_properties

def get_state_code_for_city(city):
    """Get most likely state code for a city - simple mapping for common cities"""
    city_to_state = {
        "New York": "NY",
        "Los Angeles": "CA",
        "Chicago": "IL",
        "Houston": "TX",
        "Phoenix": "AZ",
        "Philadelphia": "PA",
        "San Antonio": "TX",
        "San Diego": "CA",
        "Dallas": "TX",
        "San Jose": "CA",
        "Austin": "TX",
        "Jacksonville": "FL",
        "San Francisco": "CA",
        "Indianapolis": "IN",
        "Columbus": "OH",
        "Charlotte": "NC",
        "Seattle": "WA",
        "Denver": "CO",
        "Portland": "OR",
        "Boston": "MA",
        "Miami": "FL",
        "Atlanta": "GA",
        "Nashville": "TN"
    }
    return city_to_state.get(city, "CA")  # Default to CA if not found

def transform_rental_data(properties):
    """
    Transform raw property data into structured DataFrame for training
    """
    transformed_data = []
    
    for prop in properties:
        try:
            location_data = prop.get("location", {}).get("address", {})
            
            # Basic property info
            rent_price = prop.get("list_price")
            # Skip properties with missing or invalid rent price
            if rent_price is None or rent_price <= 0:
                continue
                
            date = pd.to_datetime(prop.get("list_date", "2025-01-01")).tz_localize(None)
            year = date.year
            month = date.month
            
            # Extract features with safe type conversion
            description = prop.get("description", {})
            
            # Handle beds - use default if None
            beds_value = description.get("beds")
            beds = float(beds_value) if beds_value is not None else 2.0
            
            # Handle baths - use default if None
            baths_value = description.get("baths")
            baths = float(baths_value) if baths_value is not None else 1.0
            
            # Handle sqft - use default if None
            sqft_value = description.get("sqft")
            sqft = float(sqft_value) if sqft_value is not None else 1000.0
            
            # Handle year_built with multiple fallbacks
            year_built_value = (
                description.get("year_built") or
                prop.get("building_size", {}).get("year_built") or
                prop.get("year_built")
            )
            year_built = int(year_built_value) if year_built_value is not None and str(year_built_value).isdigit() else 2000
            
            # Location features
            city = location_data.get("city", "Unknown")
            state = location_data.get("state_code", "Unknown")
            postal_code = location_data.get("postal_code", "00000")
            
            # Property type with safe handling
            prop_type = str(description.get("type", "apartment")).lower()
            is_apartment = 1 if "apartment" in prop_type else 0
            is_house = 1 if "house" in prop_type or "home" in prop_type else 0
            is_condo = 1 if "condo" in prop_type else 0
            
            # Other features 
            has_pool = 1 if description.get("pool") is True else 0
            pets_allowed = 1 if prop.get("pets_policy",{}).get("Cats") is True or prop.get("pets_policy",{}).get("Dogs") is True else 0
            
            # Create feature vector
            transformed_data.append({
                "Year": year,
                "Month": month,
                "Bedrooms": beds,
                "Bathrooms": baths,
                "Square_Footage": sqft,
                "Year_Built": year_built,
                "City": city,
                "State": state,
                "Postal_Code": postal_code,
                "Is_Apartment": is_apartment,
                "Is_House": is_house,
                "Is_Condo": is_condo,
                "Has_Pool": has_pool,
                "Pets_Allowed": pets_allowed,
                "Rent_Price": rent_price
            })
            
        except Exception as e:
            print(f"  ⚠️ Error processing property: {e}")
            continue
    
    # Verify we have enough data to proceed
    if len(transformed_data) < 100:
        print(f"⚠️ Warning: Only {len(transformed_data)} valid properties after filtering. Consider collecting more data.")
    
    print(f"✅ Successfully processed {len(transformed_data)} properties out of {len(properties)} fetched properties.")
    return pd.DataFrame(transformed_data)
    

def preprocess_data(df):
    """
    Preprocess data for training including one-hot encoding and scaling
    """
    # Drop rows with missing values
    df = df.dropna()
    
    # Remove extreme outliers in rent price (e.g. 99th percentile)
    rent_upper_limit = df['Rent_Price'].quantile(0.99)
    df = df[df['Rent_Price'] <= rent_upper_limit]
    
    # One-hot encode categorical columns
    df = pd.get_dummies(df, columns=['State'], drop_first=True)
    
    # For simplicity, we'll limit the number of cities by using only the top 20 most common
    # top_cities = df['City'].value_counts().nlargest(20).index
    # df['City'] = df['City'].apply(lambda x: x if x in top_cities else 'Other')
    df = pd.get_dummies(df, columns=['City'], drop_first=True)
    
    # Drop Postal_Code as it would create too many one-hot columns
    df = df.drop('Postal_Code', axis=1)
    
    # Define features and target
    X = df.drop('Rent_Price', axis=1)
    y = df['Rent_Price']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_cols = ['Year', 'Month', 'Bedrooms', 'Bathrooms', 'Square_Footage', 'Year_Built']
    X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
    X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])
    
    # Save scaler for future use
    joblib.dump(scaler, SCALER_OUTPUT_PATH)
    print(f"✅ Scaler saved to {SCALER_OUTPUT_PATH}")
    
    return X_train, X_test, y_train, y_test, scaler, list(X.columns)

def train_rental_model(X_train, y_train):
    """
    Train XGBoost regression model with hyperparameter tuning
    """
    print("⏳ Training rental price prediction model...")
    
    # Define hyperparameter grid
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    
    # Initialize XGBoost model
    base_model = XGBRegressor(objective='reg:squarederror', random_state=42)
    
    # Perform grid search with cross-validation
    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=3,
        n_jobs=-1,
        verbose=1,
        scoring='neg_mean_squared_error'
    )
    
    # Fit grid search
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_model = grid_search.best_estimator_
    print(f"✅ Best parameters: {grid_search.best_params_}")
    
    return best_model

def evaluate_model(model, X_test, y_test, feature_names):
    """
    Evaluate model performance and visualize feature importance
    """
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n📊 Model Evaluation Metrics:")
    print(f"  Root Mean Squared Error (RMSE): ${rmse:.2f}")
    print(f"  Mean Absolute Error (MAE): ${mae:.2f}")
    print(f"  R² Score: {r2:.4f}")
    
    # Calculate and plot feature importance
    feature_importance = model.feature_importances_
    sorted_idx = np.argsort(feature_importance)
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx], align='center')
    plt.yticks(range(len(sorted_idx)), [feature_names[i] for i in sorted_idx])
    plt.title('XGBoost Feature Importance')
    plt.tight_layout()
    plt.savefig('rental_feature_importance.png')
    print("✅ Feature importance plot saved to rental_feature_importance.png")
    
    # Plot predicted vs actual values
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Actual Rent Price')
    plt.ylabel('Predicted Rent Price')
    plt.title('Actual vs Predicted Rent Prices')
    plt.tight_layout()
    plt.savefig('rental_prediction_scatter.png')
    print("✅ Prediction scatter plot saved to rental_prediction_scatter.png")
    
    return rmse, mae, r2

def save_model(model, feature_names):
    """
    Save trained model to disk
    """
    model_info = {
        'model': model,
        'feature_names': feature_names,
        'metadata': {
            'model_type': 'XGBoost Regressor',
            'target': 'Monthly Rent Price',
            'features': feature_names,
            'date_trained': pd.Timestamp.now().strftime('%Y-%m-%d')
        }
    }
    
    joblib.dump(model_info, MODEL_OUTPUT_PATH)
    print(f"✅ Rental price prediction model saved to {MODEL_OUTPUT_PATH}")

def predict_rental_price(features):
    """
    Predict rental price using the trained model and scaler.
    """
    try:
        # Load model and scaler
        model_info = joblib.load(MODEL_OUTPUT_PATH)
        model = model_info['model']
        feature_names = model_info['feature_names']
        scaler = joblib.load(SCALER_OUTPUT_PATH)

        # Predict
        prediction = model.predict(features)
        return prediction[0]

    except Exception as e:
        print(f"Error making prediction: {e}")
        return None



def main():
    """
    Main function to execute the model training pipeline
    """
    print("🏠 Starting Rental Price Prediction Model Training")
    
    # Define target cities for data collection
    target_cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "San Francisco", "Seattle", "Miami", "Denver", "Boston",
        "Austin", "Dallas", "Atlanta", "Nashville"
    ]
    
    # Fetch rental data
    rental_properties = fetch_rental_data(target_cities, limit_per_city=200)
    print(f"📊 Total properties fetched: {len(rental_properties)}")
    
    if len(rental_properties) < 100:
        print("❌ Insufficient data for model training. Aborting.")
        return
    
    # Transform data
    df = transform_rental_data(rental_properties)
    print(f"📝 Transformed data shape: {df.shape}")

    # Save transformed data to CSV
    df.to_csv('rental_data.csv', index=False)
    print("✅ Transformed data saved to rental_data.csv")

    df = pd.read_csv('rental_data.csv')
    
    # Preprocess data
    X_train, X_test, y_train, y_test, scaler, feature_names = preprocess_data(df)
    print(f"🧮 Training data: {X_train.shape}, Test data: {X_test.shape}")
    
    # Train model
    model = train_rental_model(X_train, y_train)
    
    # Evaluate model
    evaluate_model(model, X_test, y_test, feature_names)
    
    # Save model
    save_model(model, feature_names)
    
    print("✅ Rental price prediction model training completed!")

    print(f"  Predicted Rent Price: ${predict_rental_price(X_test.iloc[:3]):.2f}")

if __name__ == "__main__":
    main()