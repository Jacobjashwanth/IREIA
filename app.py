import json
import os
import random

import joblib
import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

app = Flask(__name__)
CORS(app)

# ✅ Load Trained XGBoost Models
SALE_MODEL_PATH = "ml_models/price-prediction-model/xgboost/xgboost_final_model.pkl"
RENTAL_MODEL_PATH = "rental_prediction_app/rental_model.pkl"
RENTAL_SCALER_PATH = "rental_prediction_app/rental_scaler.pkl"

# Load models and scaler
sale_model: XGBRegressor = joblib.load(SALE_MODEL_PATH)
rental_model_info = joblib.load(RENTAL_MODEL_PATH)
rental_model = rental_model_info['model']
rental_scaler = joblib.load(RENTAL_SCALER_PATH)

# Get feature names directly from the model
rental_feature_names = rental_model.get_booster().feature_names
print("✅ XGBoost Models and Scaler Loaded")

# ✅ Realtor API Config
# REALTOR_API_KEY = "437454f397mshfe07ce79095c448p12a3c1jsn8c871f0050cd"
REALTOR_API_KEY = "24b5afb351mshff5413d600593d3p1796f7jsncfdbd232d642"
# REALTOR_API_KEY = "6b504def46msha6bf4ff53605f98p1c0c1djsn3fcd43362b33"
REALTOR_HOST = "realty-in-us.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": REALTOR_API_KEY,
    "X-RapidAPI-Host": REALTOR_HOST,
    "Content-Type": "application/json"
}

# ✅ Fetch Properties From Realtor API
def fetch_properties_from_api(location):
    url = "https://realty-in-us.p.rapidapi.com/properties/v3/list"
    payload = {
        "limit": 20,
        "offset": 0,
        "status": ["for_sale"],
        "sort": {"direction": "desc", "field": "list_date"},
        "search_location": location
    }

    if location.isdigit() and len(location) == 5:
        payload["postal_code"] = location
    else:
        payload["city"] = location

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {}).get("home_search", {}).get("results", [])
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Request Exception: {e}")
        return []

def predict_rental_price(prop):
    """
    Predict rental price for a single property.
    Assumes `rental_scaler`, `rental_model`, and `rental_feature_names` are preloaded.
    """
    try:
        # Extract listing date info
        date = pd.to_datetime(prop.get("list_date", "2025-01-01")).tz_localize(None)
        year = date.year
        month = date.month

        # Safe extraction from nested dicts with default values
        description = prop.get("description", {})
        location_data = prop.get("location", {}).get("address", {})

        # Property attributes with fallbacks and type conversion
        beds = float(description.get("beds", 2) or 2)
        baths = float(description.get("baths", 1) or 1)
        sqft = float(description.get("sqft", 1000) or 1000)

        year_built = (
            description.get("year_built") or
            prop.get("building_size", {}).get("year_built") or
            prop.get("year_built") or
            2000
        )
        year_built = int(year_built) if str(year_built).isdigit() else 2000

        # Property type features
        prop_type = str(description.get("type", "apartment")).lower()
        is_apartment = int("apartment" in prop_type)
        is_house = int("house" in prop_type or "home" in prop_type)
        is_condo = int("condo" in prop_type)

        # Amenities
        has_pool = int(description.get("pool") is True)
        pets_allowed = int(
            description.get("pets_policy", {}).get("Cats") is True or 
            description.get("pets_policy", {}).get("Dogs") is True
        )

        # Location
        city = location_data.get("city", "Unknown")
        state = location_data.get("state_code", "Unknown")

        # Build base feature DataFrame
        df = pd.DataFrame([{
            "Year": year,
            "Month": month,
            "Bedrooms": beds,
            "Bathrooms": baths,
            "Square_Footage": sqft,
            "Year_Built": year_built,
            "Is_Apartment": is_apartment,
            "Is_House": is_house,
            "Is_Condo": is_condo,
            "Has_Pool": has_pool,
            "Pets_Allowed": pets_allowed,
            "City": city,
            "State": state
        }])

        # Match training encoding
        df = pd.get_dummies(df, columns=["City", "State"], drop_first=True)

        # Create a feature-aligned DataFrame
        features_df = pd.DataFrame(columns=rental_feature_names)
        for col in rental_feature_names:
            features_df[col] = df[col] if col in df.columns else 0

        # Scale numerical features
        numerical_cols = ['Year', 'Month', 'Bedrooms', 'Bathrooms', 'Square_Footage', 'Year_Built']
        features_df[numerical_cols] = rental_scaler.transform(features_df[numerical_cols])

        # Convert all object-type columns to int
        for col in features_df.columns:
            if features_df[col].dtype == 'object':
                features_df[col] = features_df[col].astype(int)

        # Predict
        predicted_rent = rental_model.predict(features_df)[0]
        return round(predicted_rent)

    except Exception as e:
        print(f"⚠️ Error predicting rental price: {e}")
        return None


# ✅ Predict Price Per Property
def predict_prices_for_properties(properties):
    output = []

    for prop in properties:
        try:
            location_data = prop.get("location", {}).get("address", {})
            address = location_data.get("line", "N/A")
            price = prop.get("list_price", 0)
            date = pd.to_datetime(prop.get("list_date", "2025-01-01")).tz_localize(None)
            year = date.year
            month = date.month

            # ✅ Required Features (Match with model training)
            beds = int(prop.get("description", {}).get("beds", 0) or 0)
            baths = float(prop.get("description", {}).get("baths", 0) or 0)
            sqft = int(prop.get("description", {}).get("sqft", 1500) or 1500)
            year_built = (
                prop.get("description", {}).get("year_built")
                or prop.get("building_size", {}).get("year_built")
                or prop.get("year_built")
                or 2005
            )
            year_built = int(year_built) if str(year_built).isdigit() else 2005
            list_price = float(price or 0)

            # ✅ Final Feature Vector
            features = pd.DataFrame([{
                "Year": int(year),
                "Month": int(month),
                "Crime Rate": float(0.05),
                "sentiment_score": float(0.0),
                "Bedrooms": int(beds),
                "Bathrooms": float(baths),
                "Square Footage": int(sqft),
                "Year Built": int(year_built),
                "Price": float(list_price)
            }])

            prediction = sale_model.predict(features)[0]

            # ✅ High-Quality Image Selection with Sorting Fallback
            photos = prop.get("photos", [])
            image_url = None

            if photos:
                # Sort photos by resolution (width descending)
                sorted_photos = sorted(
                    [p for p in photos if "href" in p and "width" in p],
                    key=lambda x: x["width"],
                    reverse=True
                )
                if sorted_photos:
                    image_url = sorted_photos[0]["href"]

            # Additional fallback options
            if not image_url:
                image_url = (
                    prop.get("primary_photo", {}).get("href") or
                    prop.get("advertisers", [{}])[0].get("photo", {}).get("href") or
                    "https://via.placeholder.com/600x400?text=No+Image"
                )

            # ✅ Location
            coords = prop.get("location", {}).get("coordinate", {}) or prop.get("location", {}).get("address", {}).get("coordinate", {})
            latitude = coords.get("lat")
            longitude = coords.get("lon")

            # Predict rental price
            predicted_rent = predict_rental_price(prop)
            # Adjust current rent based on sale price prediction comparison
            if prediction > price:
                current_rent = round(predicted_rent * random.uniform(0.9, 1.0)) if predicted_rent else None  # Positive variation
            else:
                current_rent = round(predicted_rent * random.uniform(1.0, 1.1)) if predicted_rent else None  # Negative variation
            
            # Calculate rent forecast
            rent_forecast = {}
            if predicted_rent:
                for i in range(1, 4):
                    year_key = str(year + i)
                    rent_forecast[year_key] = round(predicted_rent * (1.02 ** i))

            output.append({
                "address": address,
                "city": location_data.get("city", "N/A"),
                "state": location_data.get("state_code", "N/A"),
                "sqft": sqft,
                "current_price": price,
                "predicted_price": round(prediction),
                "rent_price": current_rent,
                "predicted_rent": predicted_rent,
                "recommendation": "✅ Worth Investing" if prediction > price else "❌ Overpriced",
                "image_url": image_url,
                "latitude": latitude,
                "longitude": longitude,
                "historical_prices": [{"date": str(date.date()), "price": price}],
                "future_forecast": {
                    str(year + i): round(prediction * (1.02 ** i)) for i in range(1, 4)
                },
                "historical_rental_prices": [{"date": str(date.date()), "rent_price": current_rent}],
                "future_forecast_rent": rent_forecast,
                "beds": beds,
                "baths": baths,
            })
        except Exception as e:
            print(f"⚠️ Error processing property: {e}")
            continue

    return output

# ✅ Main Route: /search_property
@app.route("/search_property", methods=["POST"])
def search_property():
    try:
        data = request.get_json()
        location = data.get("location", "").strip()
        address = data.get("address", "").strip().lower()
        prop_type = data.get("property_type", "").strip().lower()

        if not location:
            return jsonify({"status": "error", "message": "Location is required."}), 400

        print(f"📍 Searching in: {location}, 📫 Address: {address}, 🏠 Type: {prop_type}")

        raw_props = fetch_properties_from_api(location)

        if not raw_props:
            return jsonify({"status": "error", "message": "No properties found."}), 404

        filtered_props = []

        for prop in raw_props:
            desc = prop.get("description", {})
            addr_line = prop.get("location", {}).get("address", {}).get("line", "").lower()
            this_type = desc.get("type", "").lower()

            # ✅ Filter logic - all optional
            if address and address not in addr_line:
                continue
            if prop_type and prop_type not in this_type:
                continue

            filtered_props.append(prop)

        # ✅ Fallback: If filters result in zero but base fetch worked, try base results
        if not filtered_props and (address or prop_type):
            print("⚠️ No matches with filters, falling back to location-only results.")
            filtered_props = raw_props

        if not filtered_props:
            return jsonify({"status": "error", "message": "No matching properties found."}), 404

        results = predict_prices_for_properties(filtered_props)
        return jsonify({"status": "success", "results": results})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return "✅ IREIA Backend is Live"

if __name__ == "__main__":
    app.run(debug=True)