import pandas as pd

df = pd.read_csv("data/price-prediction-model-data/Sold_Properties_Data.csv", low_memory=False)

# Print all column names that include relevant keywords
relevant_keywords = ["property", "id", "city", "zip", "address", "price", "settled"]
for col in df.columns:
    for keyword in relevant_keywords:
        if keyword.lower() in col.lower():
            print(col)