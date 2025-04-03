import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# 🚀 Load your full dataset
df = pd.read_csv("data/price-prediction-model-data/Sold_Properties_Data.csv", parse_dates=["SETTLED_DATE"], low_memory=False)

# 🧹 Clean and rename required columns
df = df.rename(columns={
    "SETTLED_DATE": "date_sold",
    "LIST_PRICE": "list_price",
    "ORIG_PRICE": "original_price",
    "SALE_PRICE": "sale_price",
    "SQUARE_FEET": "sqft",
    "NO_BEDROOMS": "bedrooms",
    "NO_FULL_BATHS": "bathrooms",
    "YEAR_BUILT": "year_built",
    "ADDRESS": "address",
    "ZIP_CODE": "zip_code",
    "STATE": "state",
    "TOWN": "city",
    "COUNTY": "county"
})

# ⏳ Extract time-based features
df["year"] = pd.to_datetime(df["date_sold"]).dt.year
df["month"] = pd.to_datetime(df["date_sold"]).dt.month

# 🧠 Add dummy crime rate and sentiment score for now
df["crime_rate"] = 3.2  # Can be updated from Crime_Rate_Data.csv
df["sentiment_score"] = 0.5  # Can be pulled dynamically from news API later

# 🎯 Feature columns for training
features = [
    "list_price", "original_price", "bedrooms", "bathrooms", "sqft",
    "year_built", "year", "month", "crime_rate", "sentiment_score"
]

# Drop missing values
df = df.dropna(subset=features + ["sale_price"])

# 🎓 Training
X = df[features]
y = df["sale_price"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBRegressor(
    objective="reg:squarederror",
    n_estimators=200,
    learning_rate=0.07,
    max_depth=5,
    random_state=42
)
model.fit(X_train, y_train)

# 🧾 Evaluation
y_pred = model.predict(X_test)
print("\n✅ XGBoost Model Evaluation:")
print(f"📊 MAE:  {mean_absolute_error(y_test, y_pred):.2f}")
print(f"📊 RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"📊 R²:   {r2_score(y_test, y_pred):.2f}")

# 💾 Save model
model.save_model("ml_models/price-prediction-model/xgboost_final_model.json")
print("✅ Model Saved")

# 🔮 Predict full dataset
df["predicted_price"] = model.predict(df[features])

# 💡 Optional: Compute future price (simple growth assumption for demo)
df["future_price"] = df["predicted_price"] * 1.05  # assuming 5% appreciation

# 📁 Output final predictions
prediction_output = df[[
    "address", "zip_code", "city", "state", "county",
    "list_price", "original_price", "sale_price", "predicted_price", "future_price",
    "crime_rate", "sentiment_score", "year", "month"
]]

prediction_output.to_csv("predicted_property_prices.csv", index=False)
print("\n✅ Predictions saved to predicted_property_prices.csv")