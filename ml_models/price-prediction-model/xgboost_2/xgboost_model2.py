import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ✅ Load sold property data
sold_df = pd.read_csv(
    "data/price-prediction-model-data/Sold_Properties_Data.csv",
    parse_dates=["SETTLED_DATE"],
    engine="python"
)

# ✅ Basic required columns
required_cols = [
    "LIST_NO", "ADDRESS", "LIST_OR_SALE_PRICE", "LIST_PRICE", "ORIG_PRICE",
    "SALE_PRICE", "SETTLED_DATE", "ZIP_CODE", "STATE"
]
sold_df = sold_df[required_cols].dropna()

# ✅ Add property_id for uniqueness
sold_df["property_id"] = sold_df["LIST_NO"].astype(str)

# ✅ Add time-based features
sold_df["date_sold"] = pd.to_datetime(sold_df["SETTLED_DATE"]).dt.normalize()
sold_df["year"] = sold_df["date_sold"].dt.year
sold_df["month"] = sold_df["date_sold"].dt.month

# ✅ Crime rate (static placeholder for now)
crime_df = pd.read_csv("data/price-prediction-model-data/crime_rate/Crime_Rate_Data.csv")
sold_df["crime_rate"] = crime_df["CRIM"].mean()

# ✅ Market sentiment merge
market_df = pd.read_csv("data/price-prediction-model-data/market_trends/Market_News__Boston_.csv", parse_dates=["date"])
market_df["date"] = market_df["date"].dt.tz_localize(None).dt.normalize()
sold_df = pd.merge(sold_df, market_df[["date", "sentiment_score"]],
                   left_on="date_sold", right_on="date", how="left")
sold_df["sentiment_score"] = sold_df["sentiment_score"].fillna(0)

# ✅ Rename for model input
sold_df = sold_df.rename(columns={
    "LIST_OR_SALE_PRICE": "fallback_price",
    "LIST_PRICE": "list_price",
    "ORIG_PRICE": "original_price",
    "SALE_PRICE": "target_price"
})

# ✅ Final features for model
feature_cols = ["list_price", "original_price", "year", "month", "crime_rate", "sentiment_score"]

# ✅ Convert numeric & drop missing
for col in feature_cols + ["target_price"]:
    sold_df[col] = pd.to_numeric(sold_df[col], errors="coerce")
sold_df = sold_df.dropna(subset=feature_cols + ["target_price"])

# ✅ Define X, y
X = sold_df[feature_cols]
y = sold_df["target_price"]

# ✅ Split & train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=150, learning_rate=0.08, max_depth=6)
model.fit(X_train, y_train)

# ✅ Evaluate model
y_pred = model.predict(X_test)
print("\n✅ XGBoost Model Evaluation:")
print(f"📊 MAE:  {mean_absolute_error(y_test, y_pred):,.2f}")
print(f"📊 RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"📊 R²:   {r2_score(y_test, y_pred):.2f}")

# ✅ Save model
model.save_model("ml_models/price-prediction-model/xgboost_2/xgboost_dynamic_model.json")
print("✅ Model Saved!")

# ✅ Forecast future prices for next 5 years per property
latest_year = sold_df["year"].max()
future_rows = []

for year in range(latest_year + 1, latest_year + 6):
    for _, row in sold_df.iterrows():
        future_rows.append({
            "property_id": row["property_id"],
            "list_price": row["list_price"],
            "original_price": row["original_price"],
            "year": year,
            "month": row["month"],
            "crime_rate": row["crime_rate"],
            "sentiment_score": row["sentiment_score"],
            "address": row["ADDRESS"],
            "state": row["STATE"],
            "zip_code": row["ZIP_CODE"]
        })

future_df = pd.DataFrame(future_rows)
future_df[feature_cols] = future_df[feature_cols].apply(pd.to_numeric, errors="coerce")
future_df = future_df.dropna(subset=feature_cols)

# ✅ Predict and save
future_df["future_price"] = model.predict(future_df[feature_cols])
future_df.to_csv("data/predicted_property_prices_5years.csv", index=False)
print("✅ Future prices saved to data/predicted_property_prices_5years.csv")

# Sort for better visualization over time
sorted_index = y_test.sort_index()

plt.figure(figsize=(10, 5))
plt.plot(sorted_index.values, label="Actual Price", marker="o")
plt.plot(y_pred, label="Predicted Price", marker="x")
plt.title("Actual vs Predicted Sold Property Prices")
plt.xlabel("Property Index")
plt.ylabel("Price ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

xgb.plot_importance(model)
plt.title("Feature Importance - XGBoost")
plt.tight_layout()
plt.show()