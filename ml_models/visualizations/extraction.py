import json

import pandas as pd

# Load the JSON file
json_file_path = "data/realty_us/realty_us_properties_02125.json"

with open(json_file_path, "r") as file:
    data = json.load(file)

# Flattening JSON structure
properties_list = []

for prop in data:
    try:
        address = prop.get("location", {}).get("address", {})
        history = prop.get("property_history", [])
        if history:
            price = history[0].get("price")
        else:
            price = None
        
        neighborhood_data = prop.get("location", {}).get("neighborhoods", [])
        if neighborhood_data:
            neighborhood = neighborhood_data[0].get("name")
            median_days_on_market = neighborhood_data[0].get("geo_statistics", {}).get("housing_market", {}).get("median_days_on_market")
        else:
            neighborhood = None
            median_days_on_market = None

        # Extract property details
        property_entry = {
            "Street": address.get("line"),
            "City": address.get("city"),
            "State": address.get("state_code"),
            "Postal Code": address.get("postal_code"),
            "Price": price,
            "Neighborhood": neighborhood,
            "Days on Market": median_days_on_market
        }
        properties_list.append(property_entry)
    
    except Exception as e:
        print(f"Error processing property: {e}")

# Convert to DataFrame
df_properties = pd.DataFrame(properties_list)

# Save as CSV
csv_file_path = "data/realty_us_properties.csv"
df_properties.to_csv(csv_file_path, index=False)

# Display the dataframe to user
print("Converted Realty Properties Data:")
print(df_properties)

# Provide the download link
csv_file_path