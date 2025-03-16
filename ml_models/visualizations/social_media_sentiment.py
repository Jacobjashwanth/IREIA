import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 📌 Load the dataset
file_path = "data/market_trends/us_real_estate_news.csv"  # Adjust the path if needed
df = pd.read_csv(file_path)

# ✅ Ensure required columns exist
required_columns = ['state', 'city', 'date', 'sentiment_score']
if not all(col in df.columns for col in required_columns):
    raise ValueError("Dataset must contain 'state', 'city', 'date', and 'sentiment_score' columns.")

# 🧹 Data Cleaning: Convert date column and drop missing values
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date', 'sentiment_score'])

# 🏙️ Aggregate sentiment scores by location (City & State)
df['location'] = df['city'] + ", " + df['state']
location_sentiment = df.groupby('location')['sentiment_score'].mean().reset_index()

# 📉 Sentiment Trends Over Time
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x="date", y="sentiment_score", marker='o', linewidth=2)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Sentiment Score", fontsize=12)
plt.title("📈 Real Estate Market Sentiment Trends Over Time", fontsize=14)
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# 📍 Sentiment Scores by Location (Top 10 locations)
top_locations = location_sentiment.sort_values(by='sentiment_score', ascending=False).head(10)
plt.figure(figsize=(12, 6))
sns.barplot(data=top_locations, x="sentiment_score", y="location", palette="coolwarm")
plt.xlabel("Average Sentiment Score", fontsize=12)
plt.ylabel("Location", fontsize=12)
plt.title("🌍 Top 10 Locations with Highest Sentiment Scores", fontsize=14)
plt.grid(axis="x")
plt.tight_layout()
plt.show()