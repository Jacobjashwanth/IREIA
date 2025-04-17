import json
import os

import joblib
import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from xgboost import XGBRegressor

app = Flask(__name__)
CORS(app)

# ✅ Load Trained XGBoost Model
MODEL_PATH = "ml_models/price-prediction-model/xgboost/xgboost_final_model.pkl"
model: XGBRegressor = joblib.load(MODEL_PATH)
print("✅ XGBoost Model Loaded")

# ✅ Realtor API Config
# REALTOR_API_KEY = "437454f397mshfe07ce79095c448p12a3c1jsn8c871f0050cd"
# REALTOR_API_KEY = "879275a2b6mshf4b3de1300b03aep10b3edjsn456c19e64bda"
REALTOR_API_KEY = "6b504def46msha6bf4ff53605f98p1c0c1djsn3fcd43362b33"
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
        "limit": 15,
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
            beds = prop.get("description", {}).get("beds", "N/A")  # Add default "N/A" in case of missing data
            baths = prop.get("description", {}).get("baths", "N/A")  # Add default "N/A" in case of missing data
            sqft = prop.get("description", {}).get("sqft", 1500)
            year_built = prop.get("description", {}).get("year_built", 2005)
            list_price = price

            # ✅ Final Feature Vector
            features = pd.DataFrame([{
                "Year": year,
                "Month": month,
                "Crime Rate": 0.05,
                "sentiment_score": 0.0,
                "Bedrooms": beds,
                "Bathrooms": baths,
                "Square Footage": sqft,
                "Year Built": year_built,
                "Price": list_price
            }])

            prediction = model.predict(features)[0]

            # ✅ High-Quality Image Fallback
            image_url = (
                prop.get("photos", [{}])[0].get("href") or
                prop.get("primary_photo", {}).get("href") or
                prop.get("advertisers", [{}])[0].get("photo", {}).get("href") or
                "https://via.placeholder.com/400x300?text=No+Image"
            )

            # ✅ Location
            coords = prop.get("location", {}).get("coordinate", {}) or prop.get("location", {}).get("address", {}).get("coordinate", {})
            latitude = coords.get("lat")
            longitude = coords.get("lon")

            output.append({
                "address": address,
                "city": location_data.get("city", "N/A"),              # ✅ Add city
                "state": location_data.get("state_code", "N/A"),       # ✅ Add state
                "sqft": sqft, 
                "current_price": price,
                "predicted_price": round(prediction),
                "recommendation": "✅ Worth Investing" if prediction > price else "❌ Overpriced",
                "image_url": image_url,
                "latitude": latitude,
                "longitude": longitude,
                "historical_prices": [{"date": str(date.date()), "price": price}],
                "future_forecast": {
                    str(year + i): round(prediction * (1.02 ** i)) for i in range(1, 4)
                },
                "beds": beds,  # Adding beds data
                "baths": baths,  # Adding baths data
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