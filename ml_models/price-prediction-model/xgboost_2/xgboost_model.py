import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ✅ Load Sold Property Data
sold_df = pd.read_csv(
    "data/price-prediction-model-data/Sold_Properties_Data.csv",
    parse_dates=["SETTLED_DATE"],
    engine="python"
)

# ✅ Select only necessary columns
sold_df = sold_df[[
    "LIST_OR_SALE_PRICE", "ORIG_PRICE", "LIST_PRICE", "SALE_PRICE",
    "SETTLED_DATE"
]].dropna()

# ✅ Time features
sold_df["date_sold"] = pd.to_datetime(sold_df["SETTLED_DATE"]).dt.normalize()
sold_df["year"] = sold_df["date_sold"].dt.year
sold_df["month"] = sold_df["date_sold"].dt.month

# ✅ Crime rate
crime_df = pd.read_csv("data/price-prediction-model-data/crime_rate/Crime_Rate_Data.csv")
sold_df["crime_rate"] = crime_df["CRIM"].mean()

# ✅ Market sentiment
market_df = pd.read_csv("data/price-prediction-model-data/market_trends/Market_News__Boston_.csv", parse_dates=["date"])
market_df["date"] = market_df["date"].dt.tz_localize(None).dt.normalize()
sold_df = pd.merge(sold_df, market_df[["date", "sentiment_score"]],
                   left_on="date_sold", right_on="date", how="left")
sold_df["sentiment_score"] = sold_df["sentiment_score"].fillna(0)

# ✅ Rename columns to match expected feature names
sold_df = sold_df.rename(columns={
    "LIST_OR_SALE_PRICE": "list_price",
    "ORIG_PRICE": "original_price",
    "LIST_PRICE": "list_price",
    "SALE_PRICE": "target_price"  # this is our actual sold price (target)
})

# ✅ Final feature list
feature_cols = [
    "list_price", "original_price", "year", "month",
    "crime_rate", "sentiment_score"
]

# ✅ Drop any rows with missing values
sold_df = sold_df.dropna(subset=feature_cols + ["target_price"])

# ✅ Split data
X = sold_df[feature_cols]
y = sold_df["target_price"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train XGBoost Model
model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=150, learning_rate=0.08, max_depth=6)
model.fit(X_train, y_train)

# ✅ Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n✅ XGBoost Model Evaluation:")
print(f"📊 MAE:  {mae:.2f}")
print(f"📊 RMSE: {rmse:.2f}")
print(f"📊 R²:   {r2:.2f}")

# ✅ Save the model
model.save_model("ml_models/price-prediction-model/xgboost_2/xgboost_dynamic_model.json")
print("\n✅ Model Saved: xgboost_dynamic_model.json")