import os
import pickle
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# STEP 1: Load Datasets
historical_data_1 = pd.read_csv("data/price-prediction-model-data/historical_data/realty_us_historical_complete_data_02122.csv", parse_dates=["Price Date"])
historical_data_2 = pd.read_csv("data/price-prediction-model-data/historical_data/realty_us_historical_complete_data_02125.csv", parse_dates=["Price Date"])
crime_data = pd.read_csv("data/price-prediction-model-data/crime_rate/Crime_Rate_Data.csv")
market_trends = pd.read_csv("data/price-prediction-model-data/market_trends/Market_News__Boston_.csv", parse_dates=["date"])

# STEP 2: Merge & Clean Historical Data
historical_data = pd.concat([historical_data_1, historical_data_2], ignore_index=True)
historical_data = historical_data.sort_values(by=["Property ID", "Price Date"])
historical_data["Property ID"] = historical_data["Property ID"].astype(str)
historical_data = historical_data[historical_data["Status"] == "for_sale"]
historical_data.rename(columns={"Price Date": "ds", "Price Amount": "y"}, inplace=True)
historical_data["ds"] = pd.to_datetime(historical_data["ds"]).dt.tz_localize(None)
market_trends.rename(columns={"date": "ds"}, inplace=True)
market_trends["ds"] = pd.to_datetime(market_trends["ds"]).dt.tz_localize(None)

# Merge Trends & Crime Rate
historical_data = historical_data.merge(market_trends, on="ds", how="left")
historical_data["Crime Rate"] = crime_data["CRIM"].mean() if "CRIM" in crime_data.columns else 0.05

# Clean Nulls
historical_data["Crime Rate"] = historical_data["Crime Rate"].fillna(historical_data["Crime Rate"].median())
historical_data["sentiment_score"] = historical_data["sentiment_score"].fillna(0)
historical_data = historical_data.dropna(subset=["y"])
historical_data = historical_data[np.isfinite(historical_data["y"])]

# Add Time Features
historical_data["Year"] = historical_data["ds"].dt.year
historical_data["Month"] = historical_data["ds"].dt.month

# Final feature list
features = [
    "Year", "Month", "Crime Rate", "sentiment_score",
    "Bedrooms", "Bathrooms", "Square Footage", "Year Built", "Price"
]
target = "y"

# Remove rows with missing features
historical_data = historical_data.dropna(subset=features)

# STEP 9: Save Models
model_dir = "ml_models/price-prediction-model/xgboost/saved_models/xgboost_models"
forecast_dir = "ml_models/price-prediction-model/xgboost/saved_models/xgboost_forecasts"
os.makedirs(model_dir, exist_ok=True)
os.makedirs(forecast_dir, exist_ok=True)

property_ids = historical_data["Property ID"].unique()
all_forecasts = []

for property_id in property_ids:
    subset = historical_data[historical_data["Property ID"] == property_id]
    if len(subset) < 2:
        print(f"⚠️ Skipping Property {property_id}: Not enough data.")
        continue

    X = subset[features]
    y = subset[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=500, learning_rate=0.05, max_depth=6)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"\n📊 Property {property_id} Performance:")
    print(f"✅ MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"✅ R² Score: {r2_score(y_test, y_pred):.2f}")

    with open(os.path.join(model_dir, f"xgboost_property_{property_id}.pkl"), "wb") as f:
        pickle.dump(model, f)

    future_dates = [datetime(2025, 1, 1) + timedelta(days=365 * i) for i in range(5)]
    future_df = pd.DataFrame({
        "Year": [d.year for d in future_dates],
        "Month": [d.month for d in future_dates],
        "Crime Rate": historical_data["Crime Rate"].mean(),
        "sentiment_score": historical_data["sentiment_score"].mean(),
        "Bedrooms": subset["Bedrooms"].median(),
        "Bathrooms": subset["Bathrooms"].median(),
        "Square Footage": subset["Square Footage"].median(),
        "Year Built": subset["Year Built"].mode()[0] if not subset["Year Built"].mode().empty else 2000,
        "Price": subset["Price"].median()
    })

    future_df["Predicted Price"] = model.predict(future_df)
    future_df["Property ID"] = property_id
    all_forecasts.append(future_df)
    future_df.to_csv(os.path.join(forecast_dir, f"xgboost_forecast_{property_id}.csv"), index=False)

# Save All Forecasts
pd.concat(all_forecasts).to_csv(os.path.join(forecast_dir, "xgboost_all_properties_forecast.csv"), index=False)
print("📌 ✅ All Property Forecasts Saved")

# FINAL GLOBAL MODEL
X_global = historical_data[features]
y_global = historical_data[target]

final_model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=300, max_depth=6)
final_model.fit(X_global, y_global)
joblib.dump(final_model, "ml_models/price-prediction-model/xgboost/xgboost_final_model.pkl")
print("✅ Final model saved correctly as xgboost_final_model.pkl")
print("🎯 Training complete.")