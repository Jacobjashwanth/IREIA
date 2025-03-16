import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load dataset
file_path = "data/final_dataset.csv"  # Adjust path if needed
df = pd.read_csv(file_path)

# Ensure required columns exist
if 'rental_estimate' not in df.columns or 'school_score' not in df.columns:
    raise ValueError("Dataset must contain 'rental_estimate' and 'school_score' columns.")

# Convert rental price to numeric (if needed)
df['rental_estimate'] = pd.to_numeric(df['rental_estimate'], errors='coerce')
df['school_score'] = pd.to_numeric(df['school_score'], errors='coerce')

# Drop rows with missing values
df_cleaned = df.dropna(subset=['rental_estimate', 'school_score'])

# Scatter Plot: Rental Price vs. School Score
plt.figure(figsize=(12, 6))
sns.scatterplot(data=df_cleaned, x='school_score', y='rental_estimate', alpha=0.6)
plt.xlabel("Neighborhood School Score")
plt.ylabel("Estimated Rental Price (USD)")
plt.title("Rental Price vs. Neighborhood School Score")
plt.grid(True)
plt.show()

# Heatmap: Correlation Matrix
plt.figure(figsize=(10, 6))
corr_matrix = df[['rental_estimate', 'school_score', 'walk_score', 'transit_score', 'bike_score']].corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
plt.title("Correlation Between Rental Price & Neighborhood Scores")
plt.show()
