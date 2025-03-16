import json
import os

import pandas as pd
import requests

# ✅ API Setup
ZILLOW_API_KEY = "879275a2b6mshf4b3de1300b03aep10b3edjsn456c19e64bda"
ZILLOW_HOST = "zillow-com1.p.rapidapi.com"

# ✅ Ensure directory
ZILLOW_FOLDER = "data/zillow"
os.makedirs(ZILLOW_FOLDER, exist_ok=True)

HEADERS = {
    "X-RapidAPI-Key": ZILLOW_API_KEY,
    "X-RapidAPI-Host": ZILLOW_HOST
}

# ✅ Fetch Property Listings
def fetch_property_listings(location, status="ForSale", home_type="Houses", limit=50):
    print(f"🔍 Fetching {status} properties for {location}...")
    url = f"https://{ZILLOW_HOST}/propertyExtendedSearch"
    params = {
        "location": location,
        "status_type": status,
        "home_type": home_type,
        "limit": limit
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json().get("props", [])
    else:
        print(f"❌ Zillow API Error: {response.status_code} - {response.text}")
        return []

# ✅ Fetch Property Details
def fetch_property_details(zpid):
    url = f"https://{ZILLOW_HOST}/zestimate"
    params = {"zpid": zpid}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ API Error (Property Details): {response.status_code} - {response.text}")
        return None

# ✅ Fetch Zestimate History
def fetch_zestimate_history(zpid):
    url = f"https://{ZILLOW_HOST}/zestimateHistory"
    params = {"zpid": zpid}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ API Error (Zestimate History): {response.status_code} - {response.text}")
        return None

# ✅ Fetch Walk & Transit Score
def fetch_walk_transit_score(zpid):
    url = f"https://{ZILLOW_HOST}/walkAndTransitScore"
    params = {"zpid": zpid}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ API Error (Walk & Transit Score): {response.status_code} - {response.text}")
        return None

# ✅ Fetch Local Market Trends
def fetch_local_home_values():
    url = f"https://{ZILLOW_HOST}/valueHistory/localHomeValues"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ API Error (Local Home Values): {response.status_code} - {response.text}")
        return None

# ✅ Main Function
def fetch_and_store_zillow_data(location):
    properties = fetch_property_listings(location)
    full_data = []
    
    for prop in properties:
        zpid = prop.get("zpid")
        details = fetch_property_details(zpid) if zpid else {}
        zestimate_history = fetch_zestimate_history(zpid) if zpid else {}
        walk_transit_score = fetch_walk_transit_score(zpid) if zpid else {}
        
        prop.update({
            "property_details": details,
            "zestimate_history": zestimate_history,
            "walk_transit_score": walk_transit_score
        })
        full_data.append(prop)
    
    # ✅ Fetch Extra Data
    market_trends = fetch_local_home_values()
    
    # ✅ Save Data
    with open(f"{ZILLOW_FOLDER}/zillow_data.json", "w") as f:
        json.dump(full_data, f, indent=4)
    
    df = pd.DataFrame(full_data)
    df.to_csv(f"{ZILLOW_FOLDER}/zillow_data.csv", index=False)
    print(f"✅ Data saved successfully in {ZILLOW_FOLDER}/")

# ✅ Run
fetch_and_store_zillow_data("Boston, MA")