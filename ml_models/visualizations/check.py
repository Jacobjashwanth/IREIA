import pandas as pd

# Load our final real estate dataset
df_real_estate = pd.read_csv("data/final_dataset.csv")

# Print available columns
print(df_real_estate.columns)

df_boston = pd.read_csv("data/boston_housing.csv")  # Adjust path if needed
print(df_boston.columns)