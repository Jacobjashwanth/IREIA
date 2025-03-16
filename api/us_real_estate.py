import json

import requests

# API Key and Headers
US_REAL_ESTATE_API_KEY = "437454f397mshfe07ce79095c448p12a3c1jsn8c871f0050cd"
HEADERS = {
    "X-RapidAPI-Key": US_REAL_ESTATE_API_KEY,
    "X-RapidAPI-Host": "us-real-estate.p.rapidapi.com"
}

# Property ID for fetching details
PROPERTY_ID = "4951372754"

# API Endpoint for Property Details
URL = f"https://us-real-estate.p.rapidapi.com/v3/property-detail?property_id={PROPERTY_ID}"

# Making the API Request
response = requests.get(URL, headers=HEADERS)

# Handling API Response
if response.status_code == 200:
    data = response.json()
    
    # Extracting useful property details
    if "data" in data and data["data"]:
        property_info = {
            "address": data["data"].get("location", {}).get("address", {}).get("line", "N/A"),
            "city": data["data"].get("location", {}).get("address", {}).get("city", "N/A"),
            "state": data["data"].get("location", {}).get("address", {}).get("state_code", "N/A"),
            "postal_code": data["data"].get("location", {}).get("address", {}).get("postal_code", "N/A"),
            "price": data["data"].get("list_price", "N/A"),
            "sqft": data["data"].get("description", {}).get("sqft", "N/A"),
            "year_built": data["data"].get("description", {}).get("year_built", "N/A"),
            "bedrooms": data["data"].get("description", {}).get("beds", "N/A"),
            "bathrooms": data["data"].get("description", {}).get("baths", "N/A"),
            "crime_rate": data["data"].get("local", {}).get("crime", {}).get("crime_index", "N/A"),
            "school_rating": data["data"].get("nearby_schools", {}).get("rating", "N/A"),
            "last_sold_price": data["data"].get("last_sold_price", "N/A"),
            "property_history": data["data"].get("property_history", [])
        }

        print("\n✅ **Property Details Fetched Successfully!**\n")
        print(json.dumps(property_info, indent=4))
    
    else:
        print("\n❌ **No Data Found in API Response**")
else:
    print(f"\n❌ **API Error: {response.status_code} - {response.text}**")