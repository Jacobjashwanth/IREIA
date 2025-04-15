import http.client
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.cluster import KMeans
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import joblib
import folium
import time
import warnings
warnings.filterwarnings("ignore")

# Function to fetch properties using Realtor API
def fetch_properties(lat, lon, offset=0, limit=25):
    conn = http.client.HTTPSConnection("realtor-search.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "c8d5a538d6mshcd151c132e18e16p10b741jsnb7dd30daa2ab",  # Replace with your own key
        'x-rapidapi-host': "realtor-search.p.rapidapi.com"
    }
    url = f"/properties/nearby-home-values?lat={lat}&lon={lon}&offset={offset}&limit={limit}"
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return json.loads(data)

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
    "Haverhill": (42.7762, -71.0773),
    "Plymouth": (41.9584, -70.6673),
    "Peabody": (42.5279, -70.9287),
    "Medford": (42.4184, -71.1062),
    "Malden": (42.4251, -71.0662),
    "Waltham": (42.3765, -71.2356),
    "Fitchburg": (42.5834, -71.8023)
}

# Step 1: Fetch Data from API
all_results = []
unique_ids = set()

print("\nFetching property data from Realtor API...")
for city, (lat, lon) in cities.items():
    print(f"\nFetching properties for {city}...")
    for offset in range(0, 200, 25):
        try:
            response = fetch_properties(lat, lon, offset=offset, limit=25)
            results = response.get("data", {}).get("home_search", {}).get("results", [])
            print(f" -> Retrieved {len(results)} properties at offset {offset}")
            for r in results:
                pid = r.get("property_id")
                if pid and pid not in unique_ids:
                    unique_ids.add(pid)
                    all_results.append(r)
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching data for {city} at offset {offset}: {e}")

print(f"\n✅ Total unique properties retrieved: {len(all_results)}")

# Step 2: Extract and Process Data
records = []
for prop in all_results:
    try:
        address = prop.get("location", {}).get("address", {})
        record = {
            "property_id": prop.get("property_id"),
            "price": prop.get("list_price"),
            "bedrooms": prop.get("description", {}).get("beds"),
            "bathrooms": prop.get("description", {}).get("baths_full"),
            "sqft": prop.get("description", {}).get("sqft"),
            "latitude": address.get("lat"),
            "longitude": address.get("lon"),
            "city": address.get("city"),
            "property_type": prop.get("prop_type", "Unknown"),
            "date": prop.get("last_update_date", None)
        }
        records.append(record)
    except Exception as e:
        print(f"Error processing record: {e}")

df = pd.DataFrame(records)

# Fill missing lat/lon using city
df['latitude'] = df.apply(
    lambda row: row['latitude'] if pd.notnull(row['latitude']) else cities.get(row['city'], (None, None))[0],
    axis=1
)
df['longitude'] = df.apply(
    lambda row: row['longitude'] if pd.notnull(row['longitude']) else cities.get(row['city'], (None, None))[1],
    axis=1
)

# Clean and preprocess
df.columns = df.columns.str.strip()
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df.dropna(subset=['price'], inplace=True)

# Identify numeric columns and remove empty ones
numeric_cols = ['price', 'bedrooms', 'bathrooms', 'sqft', 'latitude', 'longitude']
non_empty_cols = [col for col in numeric_cols if df[col].notna().sum() > 0]
df_numeric = df[non_empty_cols]

# Impute missing values
imputer = SimpleImputer(strategy="mean")
df_imputed_numeric = pd.DataFrame(imputer.fit_transform(df_numeric), columns=non_empty_cols)

# Add back categorical data
df_imputed = df_imputed_numeric.copy()
df_imputed['property_type'] = df['property_type'].fillna('Unknown').values
df_imputed['date'] = df['date'].values

# Rental Zone Categorization
df_imputed['rental_zone'] = pd.qcut(df_imputed['price'], q=3, labels=['Low', 'Mid', 'High'])

print("\nRental Zone Distribution:")
print(df_imputed['rental_zone'].value_counts())

# Feature selection
X = df_imputed.drop(columns=['price', 'rental_zone', 'date', 'property_type'])
y = df_imputed['price']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train models
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

xgb_model = XGBRegressor(objective="reg:squarederror", n_estimators=100, random_state=42)
xgb_model.fit(X_train, y_train)

# Save models
joblib.dump(xgb_model, 'rental_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print(f"\nLinear Regression Score: {lr_model.score(X_test, y_test):.4f}")
print(f"XGBoost Score: {xgb_model.score(X_test, y_test):.4f}")

# Clustering
optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_imputed['Cluster'] = kmeans.fit_predict(X_scaled)

# Plot clusters
plt.figure(figsize=(12, 8))
plt.scatter(df_imputed['bedrooms'], df_imputed['price'], c=df_imputed['Cluster'], cmap='viridis', alpha=0.6, edgecolors='black')
plt.colorbar(label='Cluster')
plt.xlabel("No. of Bedrooms")
plt.ylabel("Price")
plt.title("Clustering of Listings Based on Bedrooms & Price")
plt.grid(True)
plt.show()

# Relabel clusters as rental zones
cluster_means = df_imputed.groupby('Cluster')['price'].mean().sort_values()
cluster_labels = {cluster: label for cluster, label in zip(cluster_means.index, ['Low', 'Mid', 'High'])}
df_imputed['rental_zone'] = df_imputed['Cluster'].map(cluster_labels)

print("\nRental Zone Distribution After Clustering:")
print(df_imputed['rental_zone'].value_counts())

# Forecasting
if 'date' in df and 'price' in df:
    df_forecast = df[['date', 'price']].dropna().groupby('date').mean().reset_index()

    if len(df_forecast) > 20:
        print("\nTraining ARIMA model...")
        arima_model = ARIMA(df_forecast['price'], order=(2, 1, 2))
        arima_result = arima_model.fit()
        df_forecast['arima_forecast'] = arima_result.forecast(steps=12)

        print("Training Prophet model...")
        prophet_df = df_forecast.rename(columns={'date': 'ds', 'price': 'y'})
        prophet_model = Prophet()
        prophet_model.fit(prophet_df)
        future = prophet_model.make_future_dataframe(periods=12, freq='M')
        forecast = prophet_model.predict(future)

        # Plot ARIMA
        plt.figure(figsize=(12, 6))
        plt.plot(df_forecast['date'], df_forecast['price'], label="Actual Prices", marker='o')
        plt.plot(df_forecast['date'].iloc[-1] + pd.to_timedelta(np.arange(1, 13), unit='M'),
                 df_forecast['arima_forecast'], label="ARIMA Forecast", linestyle="dashed", color="red")
        plt.xlabel("Date")
        plt.ylabel("Average Rental Price")
        plt.title("Rental Price Forecasting using ARIMA")
        plt.legend()
        plt.grid()
        plt.show()

        # Plot Prophet
        print("Plotting Prophet forecast...")
        prophet_model.plot(forecast)
        plt.title("Rental Price Forecasting with Prophet")
        plt.show()
    else:
        print("Not enough data for forecasting.")
else:
    print("Date column missing in dataset.")

# Map visualization
m = folium.Map(location=[df_imputed['latitude'].mean(), df_imputed['longitude'].mean()], zoom_start=12)
zone_colors = {'Low': 'green', 'Mid': 'orange', 'High': 'red'}

for _, row in df_imputed.iterrows():
    folium.CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=5,
        color=zone_colors.get(row['rental_zone'], 'gray'),
        fill=True,
        fill_color=zone_colors.get(row['rental_zone'], 'gray'),
        fill_opacity=0.7
    ).add_to(m)

m.save("rental_zones_map.html")
print("\n🗺️ Map saved as rental_zones_map.html (Open in a browser)")
