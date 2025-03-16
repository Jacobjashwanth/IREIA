import json
import os
import time

import pandas as pd
import requests
from textblob import TextBlob

# ✅ API Setup
NEWS_API_KEY = "e352e45355934931950960bf831673df"  # Replace with your valid API key

# ✅ Ensure directory exists
MARKET_TRENDS_FOLDER = "data/market_trends"
os.makedirs(MARKET_TRENDS_FOLDER, exist_ok=True)

# ✅ U.S. States and Major Cities
US_STATES_CITIES = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Texas": ["Houston", "Austin", "Dallas", "San Antonio"],
    "New York": ["New York City", "Buffalo", "Albany", "Rochester"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Illinois": ["Chicago", "Springfield", "Peoria"],
    "Massachusetts": ["Boston", "Cambridge", "Worcester", "Springfield"],
    "Washington": ["Seattle", "Spokane", "Tacoma"],
    "Arizona": ["Phoenix", "Tucson", "Mesa"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "Georgia": ["Atlanta", "Savannah", "Augusta"],
    # Add more states & cities as needed
}

# ✅ Fetch Real Estate News for Each State & City (Store in One File)
def fetch_real_estate_news():
    print("📰 Fetching real estate news for all states & cities...")

    all_news_data = []  # Store all news articles in a single list

    for state, cities in US_STATES_CITIES.items():
        for city in cities:
            print(f"🔍 Fetching news for {city}, {state}...")
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{city} real estate market",
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": NEWS_API_KEY
            }

            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json().get("articles", [])
                    if not data:
                        print(f"⚠️ No articles found for {city}, {state}.")
                        continue

                    # ✅ Sentiment Analysis
                    for article in data:
                        title = article.get("title", "N/A")
                        description = article.get("description", "") or ""  # Ensure it's a string
                        source = article.get("source", {}).get("name", "N/A")
                        url = article.get("url", "N/A")
                        published_at = article.get("publishedAt", "N/A")

                        # Combine title + description for sentiment analysis
                        text = f"{title}. {description}".strip()
                        sentiment_score = round(TextBlob(text).sentiment.polarity, 3)  # -1 (Negative) to 1 (Positive)

                        article_data = {
                            "state": state,
                            "city": city,
                            "title": title,
                            "source": source,
                            "date": published_at,
                            "sentiment_score": sentiment_score,
                            "url": url
                        }
                        all_news_data.append(article_data)

                except json.JSONDecodeError:
                    print(f"❌ Error parsing JSON response for {city}, {state}.")
            else:
                print(f"❌ News API Error for {city}, {state}: {response.status_code}")

            # ✅ Prevent hitting API rate limits (pause for 2 seconds)
            time.sleep(2)

    # ✅ Save all collected data into a single JSON file
    final_json_path = os.path.join(MARKET_TRENDS_FOLDER, "us_real_estate_news.json")
    with open(final_json_path, "w") as f:
        json.dump(all_news_data, f, indent=4)

    # ✅ Save all collected data into a single CSV file
    if all_news_data:
        df = pd.DataFrame(all_news_data)
        final_csv_path = os.path.join(MARKET_TRENDS_FOLDER, "us_real_estate_news.csv")
        df.to_csv(final_csv_path, index=False)
        print(f"✅ US Real Estate News saved in:\n   📂 {final_json_path}\n   📂 {final_csv_path}")
    else:
        print("⚠️ No news data collected.")

# ✅ Run the function
fetch_real_estate_news()