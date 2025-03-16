import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load dataset
file_path = "data/final_dataset.csv"
df = pd.read_csv(file_path)

# Ensure required columns exist
if 'price_history' not in df.columns or 'location' not in df.columns:
    raise ValueError("The dataset does not contain required columns: 'price_history' and 'location'.")

# Function to extract dates and prices from price_history column
def extract_price_trends(history):
    if pd.isna(history):
        return []
    try:
        entries = history.split(", ")
        data_points = []
        for entry in entries:
            parts = entry.split(": ")
            if len(parts) == 2:
                date_str, price = parts
                date = pd.to_datetime(date_str.strip(), errors='coerce')
                price = float(price.replace(",", "")) if price.replace(",", "").isdigit() else None
                if pd.notna(date) and price is not None:
                    data_points.append((date, price))
        return data_points
    except:
        return []

# Expanding historical prices into a new DataFrame
expanded_data = []
for _, row in df.iterrows():
    history = extract_price_trends(row['price_history'])
    for date, price in history:
        if pd.notna(date):
            expanded_data.append({'date': date, 'price': price, 'location': row['location']})

df_expanded = pd.DataFrame(expanded_data)

# Debug: Print unique locations
print("🔹 Unique Locations in Dataset:")
print(df_expanded['location'].unique())

# Use contains() instead of isin() to allow flexible filtering
df_filtered = df_expanded[df_expanded['location'].str.contains("Boston|Dorchester|Merrimack|NH", case=False, na=False)]

# Debug: Check if NH data exists
if df_filtered.empty:
    print("⚠️ No NH data found! Possible location mismatch.")
    df_filtered_nh = df_expanded[df_expanded['location'].str.contains("Merrimack|NH", case=False, na=False)]
    print("🔹 NH Data After Fix:", df_filtered_nh)

# Sort for smoother plots
df_filtered = df_filtered.sort_values(by=['location', 'date'])

# Plot
plt.figure(figsize=(14, 7))
sns.lineplot(data=df_filtered, x="date", y="price", hue="location", marker='o', markersize=8, linewidth=2.5)

plt.xlabel("Date", fontsize=12)
plt.ylabel("Price (USD)", fontsize=12)
plt.title("Property Price Trends Over Time", fontsize=14)
plt.xticks(rotation=45)
plt.legend(title="Location", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()