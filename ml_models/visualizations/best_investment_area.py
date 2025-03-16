import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load JSON file
file_path = "data/realty_us/realty_us_properties_02125.json"  # Adjust path if needed
with open(file_path, "r") as file:
    data = json.load(file)

# Print structure of first property
print(json.dumps(data[:2], indent=4)) 
# Extract relevant details
investment_data = []
for property in data:
    try:
        # Extract Location
        address = property.get("location", {}).get("address", {})
        city = address.get("city", "Unknown")
        state = address.get("state_code", "Unknown")
        location = f"{city}, {state}"

        # Extract Latest Price
        property_history = property.get("property_history", [])
        latest_price = property_history[0]["price"] if property_history else None

        # Extract Days on Market (if available)
        neighborhoods = property.get("location", {}).get("neighborhoods", [])
        days_on_market = None
        for neighborhood in neighborhoods:
            if "geo_statistics" in neighborhood:
                days_on_market = neighborhood["geo_statistics"]["housing_market"].get("median_days_on_market", None)
                break  # Take the first valid entry

        # Append extracted data
        if latest_price and days_on_market:
            investment_data.append({"Location": location, "Price": latest_price, "Days on Market": days_on_market})

    except Exception as e:
        print(f"Error processing property: {e}")

# Convert to DataFrame
df = pd.DataFrame(investment_data)

# Check if data was extracted successfully
if df.empty:
    print("⚠️ No valid data found for investment analysis.")
else:
    print("✅ Successfully extracted investment data!")

    # Visualization: Best Investment Areas (Lower days on market = High Demand)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df.sort_values(by="Days on Market"), x="Location", y="Days on Market", palette="coolwarm")
    plt.xlabel("Location", fontsize=12)
    plt.ylabel("Days on Market", fontsize=12)
    plt.title("Best Investment Areas: Properties with Low Days on Market", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.grid(True)
    plt.show()