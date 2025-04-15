# import pandas as pd
# import numpy as np
# import joblib
# import requests
# import time
# import os
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.impute import SimpleImputer
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import Lasso
# from sklearn.metrics import r2_score, mean_squared_error

# # Create the models directory if it doesn't exist
# os.makedirs('models', exist_ok=True)

# # Zillow API credentials
# api_key = "30c130cfe6mshb5b1c7bdb9d6832p10fad8jsnb59fe5804bc3"  # Replace with your actual API key
# api_host = "zillow-com1.p.rapidapi.com"

# def fetch_data_from_api():
#     """Fetch property data from Zillow API for model training"""
#     print("Fetching data from Zillow API...")
    
#     # List of locations to fetch (Massachusetts cities)
#     locations = [
#         "Boston, Massachusetts",
#         "Cambridge, Massachusetts",
#         "Worcester, Massachusetts",
#         "Springfield, Massachusetts",
#         "Lowell, Massachusetts",
#         "Somerville, Massachusetts"
#     ]
    
#     all_listings = []
    
#     # Fetch data for each location
#     for location in locations:
#         print(f"Fetching data for {location}...")
        
#         # Fetch both for sale and for rent listings
#         for status in ["forRent", "forSale"]:
#             print(f"  Fetching {status} listings...")
            
#             # Try multiple pages (up to 5 per location/status)
#             for page in range(1, 20):
#                 try:
#                     url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
#                     querystring = {
#                         "location": location,
#                         "status": status,
#                         "page": str(page)
#                     }
#                     headers = {
#                         "X-RapidAPI-Key": api_key,
#                         "X-RapidAPI-Host": api_host
#                     }
                    
#                     response = requests.get(url, headers=headers, params=querystring)
                    
#                     if response.status_code == 200:
#                         data = response.json()
                        
#                         if 'props' in data and data['props']:
#                             properties = data['props']
#                             all_listings.extend(properties)
#                             print(f"    Retrieved {len(properties)} listings from page {page}")
                            
#                             # Stop if fewer than expected listings (likely reached the end)
#                             if len(properties) < 10:
#                                 break
#                         else:
#                             print(f"    No properties found on page {page} for {location} {status}")
#                             break
#                     else:
#                         print(f"    Error: API returned status code {response.status_code}")
#                         print(f"    Response: {response.text}")
#                         break
                    
#                     # Sleep to avoid hitting API rate limits
#                     time.sleep(1.5)
                    
#                 except Exception as e:
#                     print(f"    Error fetching data: {e}")
#                     time.sleep(3)  # Wait longer on error
    
#     print(f"Fetched {len(all_listings)} total listings from Zillow API")
    
#     # Convert to DataFrame
#     df = pd.DataFrame(all_listings)
    
#     # Save raw data for reference
#     df.to_csv('zillow_api_data_raw.csv', index=False)
#     print("Raw data saved to zillow_api_data_raw.csv")
    
#     return df

# def generate_sample_data(n_samples=1000):
#     """Generate sample data if API fails or for testing"""
#     print("Generating sample data...")
    
#     np.random.seed(42)
    
#     property_types = ['SINGLE_FAMILY', 'CONDO', 'MULTI_FAMILY', 'TOWNHOUSE', 'MANUFACTURED']
#     type_weights = [0.6, 0.25, 0.08, 0.05, 0.02]
    
#     # Boston area coordinates
#     center_lat, center_lng = 42.3601, -71.0589
    
#     # Create sample data
#     data = []
#     for i in range(n_samples):
#         # Select property type
#         prop_type = np.random.choice(property_types, p=type_weights)
        
#         # Adjust bedrooms based on property type
#         if prop_type == 'CONDO':
#             bedrooms = np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
#         else:
#             bedrooms = np.random.choice([2, 3, 4, 5], p=[0.2, 0.4, 0.3, 0.1])
            
#         # Adjust bathrooms based on bedrooms
#         bathrooms = max(1, round(bedrooms * np.random.uniform(0.5, 1.2) * 2) / 2)  # Round to nearest 0.5
        
#         # Generate living area based on beds/baths
#         living_area = int((700 + bedrooms * 300 + bathrooms * 150) * np.random.uniform(0.8, 1.2))
        
#         # Generate random location in Boston area
#         latitude = center_lat + np.random.uniform(-0.1, 0.1)
#         longitude = center_lng + np.random.uniform(-0.1, 0.1)
        
#         # Calculate distance from city center
#         dist_from_center = np.sqrt((latitude - center_lat)**2 + (longitude - center_lng)**2)
        
#         # Generate rent estimate - higher near city center
#         location_factor = 1.5 if dist_from_center < 0.03 else (
#                          1.3 if dist_from_center < 0.06 else (
#                          1.1 if dist_from_center < 0.1 else 1.0))
        
#         base_rent = (1500 + bedrooms * 450 + bathrooms * 300 + living_area * 0.3) * location_factor
#         rent_estimate = int(base_rent * np.random.uniform(0.9, 1.1))
        
#         # Generate sale price (roughly 200x monthly rent)
#         price_factor = np.random.uniform(180, 220)
#         price = int(rent_estimate * price_factor)
        
#         # Create listing
#         listing = {
#             'zpid': 10000000 + i,
#             'address': f'Sample Address #{i}, Boston, MA',
#             'price': price,
#             'rentZestimate': rent_estimate,
#             'bedrooms': bedrooms,
#             'bathrooms': bathrooms,
#             'livingArea': living_area,
#             'latitude': latitude,
#             'longitude': longitude,
#             'propertyType': prop_type,
#             'lotAreaValue': np.random.uniform(0.1, 1.0),
#             'daysOnZillow': np.random.randint(1, 60)
#         }
        
#         data.append(listing)
    
#     df = pd.DataFrame(data)
    
#     # Save the sample data
#     df.to_csv('zillow_sample_data.csv', index=False)
#     print(f"Generated {n_samples} sample listings and saved to zillow_sample_data.csv")
    
#     return df

# # Main execution
# try:
#     # Try to fetch data from API
#     df = fetch_data_from_api()
    
#     # If we didn't get enough data, supplement with sample data
#     if len(df) < 100:
#         print("Insufficient data from API, supplementing with sample data...")
#         sample_df = generate_sample_data(500)
#         df = pd.concat([df, sample_df], ignore_index=True)
# except Exception as e:
#     print(f"Error fetching data from API: {e}")
#     print("Falling back to sample data generation...")
#     df = generate_sample_data(1000)

# # Data preparation
# print("\nPreparing data for model training...")

# # Define features and target
# features = ['bedrooms', 'bathrooms', 'livingArea', 'latitude', 'longitude', 
#             'propertyType', 'lotAreaValue', 'daysOnZillow']
# target = 'rentZestimate'

# # Create a working dataset with required columns
# model_df = df[features + [target]].copy()

# # Remove missing target values
# model_df = model_df.dropna(subset=[target])
# print(f"Working with {len(model_df)} properties after removing missing values")

# # Feature Engineering
# print("Adding engineered features...")
# model_df['bedrooms_squared'] = model_df['bedrooms'] ** 2
# model_df['bathrooms_squared'] = model_df['bathrooms'] ** 2
# model_df['living_area_sqrt'] = np.sqrt(model_df['livingArea'])
# model_df['bed_bath_ratio'] = model_df['bedrooms'] / model_df['bathrooms'].replace(0, 1)
# model_df['bed_area_ratio'] = model_df['bedrooms'] / (model_df['livingArea'] + 1)

# # Define feature types
# numeric_features = ['bedrooms', 'bathrooms', 'livingArea', 'latitude', 'longitude',
#                     'lotAreaValue', 'daysOnZillow', 'bedrooms_squared', 'bathrooms_squared',
#                     'living_area_sqrt', 'bed_bath_ratio', 'bed_area_ratio']
# categorical_features = ['propertyType']

# # Create train-test split
# X = model_df.drop(target, axis=1)
# y = model_df[target]

# # Log-transform the target for better distribution
# y_log = np.log1p(y)

# X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.2, random_state=42)
# print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

# # Create preprocessing pipeline
# print("Creating preprocessing pipeline...")
# numeric_transformer = Pipeline(steps=[
#     ('imputer', SimpleImputer(strategy='median')),
#     ('scaler', StandardScaler())
# ])

# categorical_transformer = Pipeline(steps=[
#     ('imputer', SimpleImputer(strategy='most_frequent')),
#     ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
# ])

# preprocessor = ColumnTransformer(
#     transformers=[
#         ('num', numeric_transformer, numeric_features),
#         ('cat', categorical_transformer, categorical_features)
#     ]
# )

# # Create the Lasso model pipeline
# model = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('regressor', Lasso(alpha=0.01))
# ])

# # Train the model
# print("Training the model...")
# model.fit(X_train, y_train)

# # Evaluate the model
# print("Evaluating model performance...")
# y_pred = model.predict(X_test)
# r2 = r2_score(y_test, y_pred)
# rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# print(f"Model performance on test set: R² = {r2:.4f}, RMSE = {rmse:.4f}")

# # Save the model
# model_path = 'models/rental_model.pkl'
# joblib.dump(model, model_path)
# print(f"Model saved to {model_path}")

# print("Done!")









import pandas as pd
import numpy as np
import joblib
import requests
import http.client
import json
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# Create the models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# API credentials
zillow_api_key = "30c130cfe6mshb5b1c7bdb9d6832p10fad8jsnb59fe5804bc3"
zillow_api_host = "zillow-com1.p.rapidapi.com"
realtor_api_key = "c8d5a538d6mshcd151c132e18e16p10b741jsnb7dd30daa2ab"
realtor_api_host = "realtor-search.p.rapidapi.com"

def fetch_zillow_data():
    """Fetch property data from Zillow API for model training"""
    print("Fetching data from Zillow API...")
    
    # List of locations to fetch (Massachusetts cities)
    locations = [
        "Boston, Massachusetts",
        "Cambridge, Massachusetts",
        "Worcester, Massachusetts",
        "Springfield, Massachusetts",
        "Lowell, Massachusetts",
        "Somerville, Massachusetts"
    ]
    
    all_listings = []
    
    # Fetch data for each location
    for location in locations:
        print(f"Fetching data for {location}...")
        
        # Fetch both for sale and for rent listings
        for status in ["forRent", "forSale"]:
            print(f"  Fetching {status} listings...")
            
            # Try multiple pages (up to 10 per location/status)
            for page in range(1, 11):
                try:
                    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
                    querystring = {
                        "location": location,
                        "status": status,
                        "page": str(page)
                    }
                    headers = {
                        "X-RapidAPI-Key": zillow_api_key,
                        "X-RapidAPI-Host": zillow_api_host
                    }
                    
                    response = requests.get(url, headers=headers, params=querystring)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'props' in data and data['props']:
                            properties = data['props']
                            all_listings.extend(properties)
                            print(f"    Retrieved {len(properties)} listings from page {page}")
                            
                            # Stop if fewer than expected listings (likely reached the end)
                            if len(properties) < 10:
                                break
                        else:
                            print(f"    No properties found on page {page} for {location} {status}")
                            break
                    else:
                        print(f"    Error: API returned status code {response.status_code}")
                        print(f"    Response: {response.text}")
                        break
                    
                    # Sleep to avoid hitting API rate limits
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"    Error fetching data: {e}")
                    time.sleep(3)  # Wait longer on error
    
    print(f"Fetched {len(all_listings)} total listings from Zillow API")
    
    # Convert to DataFrame
    df_zillow = pd.DataFrame(all_listings)
    
    # Add a source column
    if len(df_zillow) > 0:
        df_zillow['source'] = 'zillow'
        
        # Save raw data for reference
        df_zillow.to_csv('zillow_api_data_raw.csv', index=False)
        print("Raw Zillow data saved to zillow_api_data_raw.csv")
    
    return df_zillow

def fetch_realtor_data():
    """Fetch property data from Realtor API"""
    print("\nFetching data from Realtor API...")
    
    # Expanded Massachusetts city coordinates
    cities = {
        "Boston": (42.3601, -71.0589),
        "Cambridge": (42.3736, -71.1097),
        "Worcester": (42.2626, -71.8023),
        "Springfield": (42.1015, -72.5898),
        "Lowell": (42.6334, -71.3162),
        "Brockton": (42.0834, -71.0184),
        "Quincy": (42.2529, -71.0023),
        "Lynn": (42.4668, -70.9495),
        "Newton": (42.3370, -71.2092),
        "Fall River": (41.7015, -71.1550),
        "Lawrence": (42.7070, -71.1631),
        "Somerville": (42.3876, -71.0995),
        "Framingham": (42.2793, -71.4162),
        "Haverhill": (42.7762, -71.0773)
    }
    
    all_results = []
    unique_ids = set()
    
    for city, (lat, lon) in cities.items():
        print(f"Fetching properties for {city}...")
        for offset in range(0, 100, 25):  # Limiting to 4 pages per city to avoid excessive API calls
            try:
                conn = http.client.HTTPSConnection(realtor_api_host)
                headers = {
                    'x-rapidapi-key': realtor_api_key,
                    'x-rapidapi-host': realtor_api_host
                }
                url = f"/properties/nearby-home-values?lat={lat}&lon={lon}&offset={offset}&limit=25"
                conn.request("GET", url, headers=headers)
                res = conn.getresponse()
                data = res.read()
                conn.close()
                
                response = json.loads(data)
                results = response.get("data", {}).get("home_search", {}).get("results", [])
                print(f" -> Retrieved {len(results)} properties at offset {offset}")
                
                for r in results:
                    pid = r.get("property_id")
                    if pid and pid not in unique_ids:
                        unique_ids.add(pid)
                        all_results.append(r)
                
                time.sleep(1.5)  # Sleep to avoid API rate limits
                
            except Exception as e:
                print(f"Error fetching data for {city} at offset {offset}: {e}")
                time.sleep(3)
    
    print(f"Fetched {len(all_results)} total listings from Realtor API")
    
    # Process Realtor data
    records = []
    for prop in all_results:
        try:
            address = prop.get("location", {}).get("address", {})
            zipcode = address.get("postal_code", None)
            
            # Extract property details
            record = {
                "property_id": prop.get("property_id"),
                "price": prop.get("list_price"),
                "bedrooms": prop.get("description", {}).get("beds"),
                "bathrooms": prop.get("description", {}).get("baths_full"),
                "livingArea": prop.get("description", {}).get("sqft"),
                "latitude": address.get("lat"),
                "longitude": address.get("lon"),
                "city": address.get("city"),
                "zipcode": zipcode,
                "propertyType": prop.get("prop_type", "Unknown"),
                "source": "realtor"
            }
            
            # Calculate estimated rent (roughly 0.5% of property value monthly)
            if record["price"] is not None and record["price"] > 0:
                rent_factor = np.random.uniform(0.004, 0.008)  # 0.4% to 0.8% of property value
                record["rentZestimate"] = int(record["price"] * rent_factor)
            
            records.append(record)
        except Exception as e:
            print(f"Error processing Realtor record: {e}")
    
    df_realtor = pd.DataFrame(records)
    
    # Save raw data for reference
    if len(df_realtor) > 0:
        df_realtor.to_csv('realtor_api_data_raw.csv', index=False)
        print("Raw Realtor data saved to realtor_api_data_raw.csv")
    
    return df_realtor

def generate_sample_data(n_samples=1000):
    """Generate sample data if APIs fail or for testing"""
    print("Generating sample data...")
    
    np.random.seed(42)
    
    property_types = ['SINGLE_FAMILY', 'CONDO', 'MULTI_FAMILY', 'TOWNHOUSE', 'MANUFACTURED']
    type_weights = [0.6, 0.25, 0.08, 0.05, 0.02]
    
    # Massachusetts area coordinates
    cities = {
        "Boston": (42.3601, -71.0589),
        "Cambridge": (42.3736, -71.1097),
        "Worcester": (42.2626, -71.8023),
        "Springfield": (42.1015, -72.5898),
        "Lowell": (42.6334, -71.3162),
        "Somerville": (42.3876, -71.0995)
    }
    
    # Boston area zipcodes
    zipcodes = {
        "Boston": ["02108", "02109", "02110", "02111", "02113", "02114", "02115", "02116", 
                   "02118", "02119", "02120", "02121", "02122", "02124", "02125", "02126", 
                   "02127", "02128", "02129", "02130", "02131", "02132", "02134", "02135"],
        "Cambridge": ["02138", "02139", "02140", "02141", "02142"],
        "Worcester": ["01601", "01602", "01603", "01604", "01605", "01606", "01607", "01608", "01609", "01610"],
        "Springfield": ["01101", "01103", "01104", "01105", "01107", "01108", "01109", "01118", "01119", "01128", "01129"],
        "Lowell": ["01850", "01851", "01852", "01853", "01854"],
        "Somerville": ["02143", "02144", "02145"]
    }
    
    # Create sample data
    data = []
    for i in range(n_samples):
        # Select random city and get its coordinates
        city = np.random.choice(list(cities.keys()))
        center_lat, center_lng = cities[city]
        
        # Select random zipcode from that city
        zipcode = np.random.choice(zipcodes[city])
        
        # Select property type
        prop_type = np.random.choice(property_types, p=type_weights)
        
        # Adjust bedrooms based on property type
        if prop_type == 'CONDO':
            bedrooms = np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
        else:
            bedrooms = np.random.choice([2, 3, 4, 5], p=[0.2, 0.4, 0.3, 0.1])
            
        # Adjust bathrooms based on bedrooms
        bathrooms = max(1, round(bedrooms * np.random.uniform(0.5, 1.2) * 2) / 2)  # Round to nearest 0.5
        
        # Generate living area based on beds/baths
        living_area = int((700 + bedrooms * 300 + bathrooms * 150) * np.random.uniform(0.8, 1.2))
        
        # Generate random location near city center
        latitude = center_lat + np.random.uniform(-0.05, 0.05)
        longitude = center_lng + np.random.uniform(-0.05, 0.05)
        
        # Calculate distance from city center
        dist_from_center = np.sqrt((latitude - center_lat)**2 + (longitude - center_lng)**2)
        
        # Generate rent estimate - higher near city center
        location_factor = 1.5 if dist_from_center < 0.03 else (
                         1.3 if dist_from_center < 0.06 else (
                         1.1 if dist_from_center < 0.1 else 1.0))
        
        base_rent = (1500 + bedrooms * 450 + bathrooms * 300 + living_area * 0.3) * location_factor
        rent_estimate = int(base_rent * np.random.uniform(0.9, 1.1))
        
        # Generate sale price (roughly 200x monthly rent)
        price_factor = np.random.uniform(180, 220)
        price = int(rent_estimate * price_factor)
        
        # Create listing
        listing = {
            'zpid': 10000000 + i,
            'address': f'Sample Address #{i}, {city}, MA {zipcode}',
            'price': price,
            'rentZestimate': rent_estimate,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'livingArea': living_area,
            'latitude': latitude,
            'longitude': longitude,
            'propertyType': prop_type,
            'lotAreaValue': np.random.uniform(0.1, 1.0),
            'daysOnZillow': np.random.randint(1, 60),
            'zipcode': zipcode,
            'city': city,
            'source': 'sample'
        }
        
        data.append(listing)
    
    df = pd.DataFrame(data)
    
    # Save the sample data
    df.to_csv('zillow_sample_data.csv', index=False)
    print(f"Generated {n_samples} sample listings and saved to zillow_sample_data.csv")
    
    return df

def clean_and_prepare_data(df):
    """Clean and prepare the combined dataset for modeling"""
    print("\nCleaning and preparing data...")
    
    # Make a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Standardize column names
    df_clean.columns = df_clean.columns.str.strip()
    
    # Handle missing values in key columns
    for col in ['bedrooms', 'bathrooms', 'livingArea', 'latitude', 'longitude']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Extract zipcode from address if missing
    if 'zipcode' not in df_clean.columns or df_clean['zipcode'].isna().all():
        df_clean['zipcode'] = df_clean['address'].str.extract(r'(\d{5})(?:[-\s]\d{4})?$')
    
    # Ensure rentZestimate exists - for sale listings might not have this
    if 'rentZestimate' not in df_clean.columns or df_clean['rentZestimate'].isna().sum() > len(df_clean) / 2:
        print("  Calculating rental estimates for listings without rentZestimate...")
        
        # For properties with price but no rentZestimate, estimate rent as 0.5% of price
        if 'price' in df_clean.columns:
            mask = (df_clean['rentZestimate'].isna() | ~('rentZestimate' in df_clean.columns)) & df_clean['price'].notna()
            rent_factor = np.random.uniform(0.004, 0.008, size=len(df_clean[mask]))  # 0.4% to 0.8% of property value
            df_clean.loc[mask, 'rentZestimate'] = df_clean.loc[mask, 'price'] * rent_factor
    
    # Basic data cleaning
    # Remove extreme outliers in price and rentZestimate
    for col in ['price', 'rentZestimate']:
        if col in df_clean.columns:
            q1 = df_clean[col].quantile(0.01)
            q3 = df_clean[col].quantile(0.99)
            iqr = q3 - q1
            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
    
    # Ensure propertyType is standardized
    if 'propertyType' in df_clean.columns:
        # Convert to uppercase and replace spaces with underscores
        df_clean['propertyType'] = df_clean['propertyType'].astype(str).str.upper().str.replace(' ', '_')
        
        # Map similar values to standard categories
        type_mapping = {
            'HOUSE': 'SINGLE_FAMILY',
            'APARTMENT': 'MULTI_FAMILY',
            'COOP': 'CONDO',
            'DUPLEX': 'MULTI_FAMILY',
            'TRIPLEX': 'MULTI_FAMILY',
            'UNKNOWN': 'SINGLE_FAMILY',
            'NAN': 'SINGLE_FAMILY'
        }
        
        df_clean['propertyType'] = df_clean['propertyType'].replace(type_mapping)
        
        # Fill missing with most common
        df_clean['propertyType'] = df_clean['propertyType'].fillna('SINGLE_FAMILY')
    
    return df_clean

def add_zipcode_features(df):
    """Add features based on zipcode analysis"""
    print("Adding zipcode-based features...")
    
    # Create copy to avoid modifying original
    df_features = df.copy()
    
    # Only process if zipcode column exists and has values
    if 'zipcode' in df_features.columns and df_features['zipcode'].notna().sum() > 0:
        # Calculate median rent by zipcode
        zipcode_stats = df_features.groupby('zipcode')['rentZestimate'].agg(['mean', 'median', 'count']).reset_index()
        zipcode_stats = zipcode_stats[zipcode_stats['count'] >= 3]  # Only use zipcodes with enough data
        
        # Create zipcode price tier (High, Medium, Low)
        if len(zipcode_stats) > 0:
            zipcode_stats['price_tier'] = pd.qcut(zipcode_stats['median'], q=3, labels=['Low', 'Medium', 'High'])
            
            # Map these back to the dataframe
            zipcode_price_map = dict(zip(zipcode_stats['zipcode'], zipcode_stats['median']))
            zipcode_tier_map = dict(zip(zipcode_stats['zipcode'], zipcode_stats['price_tier']))
            
            df_features['zipcode_median_rent'] = df_features['zipcode'].map(zipcode_price_map)
            df_features['zipcode_price_tier'] = df_features['zipcode'].map(zipcode_tier_map)
            
            # Fill missing with median values
            df_features['zipcode_median_rent'].fillna(df_features['zipcode_median_rent'].median(), inplace=True)
            
            # One-hot encode the price tier
            tier_dummies = pd.get_dummies(df_features['zipcode_price_tier'], prefix='zipcode_tier')
            df_features = pd.concat([df_features, tier_dummies], axis=1)
    
    return df_features

def add_engineered_features(df):
    """Add engineered features to the dataframe"""
    print("Adding engineered features...")
    
    # Create a copy to avoid modifying the original
    df_features = df.copy()
    
    # Add squared terms for non-linear relationships
    if 'bedrooms' in df_features.columns:
        df_features['bedrooms_squared'] = df_features['bedrooms'] ** 2
    
    if 'bathrooms' in df_features.columns:
        df_features['bathrooms_squared'] = df_features['bathrooms'] ** 2
    
    # Add square root for living area (diminishing returns)
    if 'livingArea' in df_features.columns:
        df_features['living_area_sqrt'] = np.sqrt(df_features['livingArea'])
    
    # Add ratios between features
    if 'bedrooms' in df_features.columns and 'bathrooms' in df_features.columns:
        # Avoid division by zero
        df_features['bed_bath_ratio'] = df_features['bedrooms'] / df_features['bathrooms'].replace(0, 1)
    
    if 'bedrooms' in df_features.columns and 'livingArea' in df_features.columns:
        # Add 1 to avoid division by zero
        df_features['bed_area_ratio'] = df_features['bedrooms'] / (df_features['livingArea'] + 1)
    
    # Add location-based features if latitude and longitude are available
    if 'latitude' in df_features.columns and 'longitude' in df_features.columns:
        # Distance from Boston city center
        boston_lat, boston_lng = 42.3601, -71.0589
        df_features['boston_distance'] = np.sqrt(
            (df_features['latitude'] - boston_lat) ** 2 + 
            (df_features['longitude'] - boston_lng) ** 2
        )
        
        # Distance from Cambridge
        cambridge_lat, cambridge_lng = 42.3736, -71.1097
        df_features['cambridge_distance'] = np.sqrt(
            (df_features['latitude'] - cambridge_lat) ** 2 + 
            (df_features['longitude'] - cambridge_lng) ** 2
        )
    
    return df_features

# Main execution
print("Starting rental price prediction model training process...")

# Try to fetch data from both APIs
try:
    # Fetch Zillow data
    df_zillow = fetch_zillow_data()
    zillow_count = len(df_zillow)
    
    # Fetch Realtor data
    df_realtor = fetch_realtor_data()
    realtor_count = len(df_realtor)
    
    # Combine datasets if both have data
    if zillow_count > 0 and realtor_count > 0:
        print(f"\nCombining {zillow_count} Zillow and {realtor_count} Realtor listings...")
        df_combined = pd.concat([df_zillow, df_realtor], ignore_index=True)
    elif zillow_count > 0:
        print("\nOnly using Zillow data...")
        df_combined = df_zillow
    elif realtor_count > 0:
        print("\nOnly using Realtor data...")
        df_combined = df_realtor
    else:
        raise Exception("No data retrieved from APIs")
    
    # If we didn't get enough data, supplement with sample data
    if len(df_combined) < 100:
        print("Insufficient data from APIs, supplementing with sample data...")
        sample_df = generate_sample_data(500)
        df_combined = pd.concat([df_combined, sample_df], ignore_index=True)
except Exception as e:
    print(f"Error fetching data from APIs: {e}")
    print("Falling back to sample data generation...")
    df_combined = generate_sample_data(1000)

# Clean and prepare data
df = clean_and_prepare_data(df_combined)

# Add zipcode-based features
df = add_zipcode_features(df)

# Add engineered features
df = add_engineered_features(df)

# Data preparation for modeling
print("\nPreparing data for model training...")

# Define features and target
features = [
    # Mandatory fields that must be provided
    'bedrooms', 'bathrooms', 'zipcode',
    
    # Optional fields that improve prediction but aren't required
    'livingArea', 'latitude', 'longitude', 'propertyType', 
    'lotAreaValue', 'daysOnZillow',
    
    # Engineered features
    'bedrooms_squared', 'bathrooms_squared', 'living_area_sqrt', 
    'bed_bath_ratio', 'bed_area_ratio',
    
    # Location-based features
    'boston_distance', 'cambridge_distance'
]

# Ensure all features exist in the dataframe
available_features = [f for f in features if f in df.columns]
print(f"Using {len(available_features)} features: {', '.join(available_features)}")

# Define target
target = 'rentZestimate'

# Create a working dataset with required columns
model_df = df[available_features + [target]].copy()

# Remove missing target values
model_df = model_df.dropna(subset=[target])
print(f"Working with {len(model_df)} properties after removing missing values")

# Fix categorical zipcode
if 'zipcode' in model_df.columns:
    model_df['zipcode'] = model_df['zipcode'].astype(str)

# Separate features by type
numeric_features = [f for f in available_features if f not in ['zipcode', 'propertyType'] 
                   and model_df[f].dtype in ['int64', 'float64']]
categorical_features = [f for f in available_features if f in ['zipcode', 'propertyType']]

# Create train-test split
X = model_df[available_features]
y = model_df[target]

# Log-transform the target for better distribution
y_log = np.log1p(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.2, random_state=42)
print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

# Create preprocessing pipeline
print("Creating preprocessing pipeline...")
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Train multiple models and compare
models = {
    'Lasso': Lasso(alpha=0.01),
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
}

best_score = -float('inf')
best_model_name = None
model_performances = {}

for name, model_instance in models.items():
    print(f"\nTraining {name}...")
    
    # Create the model pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model_instance)
    ])
    
    # Train the model
    pipeline.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"{name} performance: R² = {r2:.4f}, RMSE = {rmse:.4f}, MAE = {mae:.4f}")
    
    model_performances[name] = {
        'r2': r2,
        'rmse': rmse,
        'mae': mae,
        'pipeline': pipeline
    }
    
    # Track the best model
    if r2 > best_score:
        best_score = r2
        best_model_name = name

# Save the best model
best_pipeline = model_performances[best_model_name]['pipeline']
model_path = 'models/rental_model.pkl'
joblib.dump(best_pipeline, model_path)
print(f"\nBest model: {best_model_name} with R² = {best_score:.4f}")
print(f"Best model saved to {model_path}")

# Also save feature columns for reference
feature_info = {
    'numeric_features': numeric_features,
    'categorical_features': categorical_features,
    'all_features': available_features
}
joblib.dump(feature_info, 'models/feature_info.pkl')
print("Feature information saved to models/feature_info.pkl")

# Create a simple prediction function that works with mandatory fields
def predict_rent(model, bedrooms, bathrooms, zipcode, **kwargs):
    """
    Predict rental price using the trained model.
    
    Required parameters:
    - bedrooms: Number of bedrooms
    - bathrooms: Number of bathrooms
    - zipcode: Property zipcode
    
    Optional parameters:
    - livingArea: Square footage
    - latitude: Property latitude
    - longitude: Property longitude
    - propertyType: Type of property (SINGLE_FAMILY, CONDO, etc.)
    - lotAreaValue: Lot size
    - daysOnZillow: Days the property has been listed
    """
    # Create a dictionary with the mandatory fields
    data = {
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'zipcode': str(zipcode)
    }
    
    # Add any optional fields that were provided
    for key, value in kwargs.items():
        if key in available_features:
            data[key] = value
    
    # Create a DataFrame with one row
    input_df = pd.DataFrame([data])
    
    # Add default values for missing fields
    if 'livingArea' not in input_df.columns:
        input_df['livingArea'] = 1000  # Default square footage
    
    if 'latitude' not in input_df.columns and 'longitude' not in input_df.columns:
        # Use Boston coordinates as default
        input_df['latitude'] = 42.3601
        input_df['longitude'] = -71.0589
    elif 'latitude' not in input_df.columns:
        input_df['latitude'] = 42.3601
    elif 'longitude' not in input_df.columns:
        input_df['longitude'] = -71.0589
    
    if 'propertyType' not in input_df.columns:
        input_df['propertyType'] = 'SINGLE_FAMILY'
    
    if 'lotAreaValue' not in input_df.columns:
        input_df['lotAreaValue'] = 0.25  # Default lot size in acres
    
    if 'daysOnZillow' not in input_df.columns:
        input_df['daysOnZillow'] = 0
    
    # Add derived/engineered features
    input_df['bedrooms_squared'] = input_df['bedrooms'] ** 2
    input_df['bathrooms_squared'] = input_df['bathrooms'] ** 2
    input_df['living_area_sqrt'] = np.sqrt(input_df['livingArea'])
    input_df['bed_bath_ratio'] = input_df['bedrooms'] / input_df['bathrooms'].replace(0, 1)
    input_df['bed_area_ratio'] = input_df['bedrooms'] / (input_df['livingArea'] + 1)
    
    # Calculate distance from Boston and Cambridge
    boston_lat, boston_lng = 42.3601, -71.0589
    input_df['boston_distance'] = np.sqrt(
        (input_df['latitude'] - boston_lat) ** 2 + 
        (input_df['longitude'] - boston_lng) ** 2
    )
    
    cambridge_lat, cambridge_lng = 42.3736, -71.1097
    input_df['cambridge_distance'] = np.sqrt(
        (input_df['latitude'] - cambridge_lat) ** 2 + 
        (input_df['longitude'] - cambridge_lng) ** 2
    )
    
    # Make prediction
    log_prediction = model.predict(input_df)[0]
    
    # Convert from log space
    prediction = np.expm1(log_prediction)
    
    return prediction

# Example usage of the prediction function
print("\nExample predictions with the model:")

example_properties = [
    {'bedrooms': 1, 'bathrooms': 1, 'zipcode': '02116', 'livingArea': 700, 'propertyType': 'CONDO'},
    {'bedrooms': 2, 'bathrooms': 1, 'zipcode': '02138', 'livingArea': 900, 'propertyType': 'CONDO'},
    {'bedrooms': 3, 'bathrooms': 2, 'zipcode': '02145', 'livingArea': 1500, 'propertyType': 'SINGLE_FAMILY'},
    {'bedrooms': 4, 'bathrooms': 2.5, 'zipcode': '01610', 'livingArea': 2200, 'propertyType': 'SINGLE_FAMILY'}
]

for props in example_properties:
    bedrooms = props['bedrooms']
    bathrooms = props['bathrooms']
    zipcode = props['zipcode']
    
    # Extract optional parameters
    optional_params = {k: v for k, v in props.items() if k not in ['bedrooms', 'bathrooms', 'zipcode']}
    
    # Make prediction
    pred_rent = predict_rent(best_pipeline, bedrooms, bathrooms, zipcode, **optional_params)
    
    print(f"\nProperty: {bedrooms} bed, {bathrooms} bath in zipcode {zipcode}")
    if 'propertyType' in props:
        print(f"Type: {props['propertyType']}", end="")
    if 'livingArea' in props:
        print(f", {props['livingArea']} sq ft", end="")
    print(f"\nPredicted Rent: ${pred_rent:.2f} per month")

# Visualize model performance
if len(model_performances) > 1:
    plt.figure(figsize=(10, 6))
    models_names = list(model_performances.keys())
    r2_scores = [model_performances[name]['r2'] for name in models_names]
    
    plt.bar(models_names, r2_scores)
    plt.title('Model Performance Comparison (R² Score)')
    plt.xlabel('Model')
    plt.ylabel('R² Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('model_performance.png')
    print("\nModel performance comparison saved to model_performance.png")

print("\nTraining completed successfully!")