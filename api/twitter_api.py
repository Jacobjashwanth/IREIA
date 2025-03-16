import json
import os
import time

import pandas as pd
import requests
from textblob import TextBlob

# ✅ Twitter API Key (Replace with valid token)
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAE0NzwEAAAAAKmA596iMyKOJd%2B%2BVMtj8hsurUlo%3DizAUb89eu0XjrpXjM64HPFEaFsQjFsIoXeQ9WQJvb1GCZTtBZO"

# ✅ Ensure directory exists
MARKET_TRENDS_FOLDER = "data/market_trends"
os.makedirs(MARKET_TRENDS_FOLDER, exist_ok=True)

# ✅ Cities to fetch data for
CITIES = [
    "Boston", "New York", "Los Angeles", "Chicago", "San Francisco",
    "Houston", "Miami", "Seattle", "Denver", "Phoenix", "Austin",
    "Washington DC", "Philadelphia", "Las Vegas", "Atlanta"
]

# ✅ Function to Fetch Twitter Data with Timeout Handling
def fetch_twitter_real_estate_tweets(city):
    print(f"🐦 Fetching real estate tweets for {city}...")

    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    
    params = {
        "query": f"{city} real estate market -is:retweet",
        "max_results": 50,  # Twitter API allows max 100
        "tweet.fields": "created_at,author_id,text",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)  # Increased timeout

        if response.status_code == 429:
            print(f"⚠️ Rate limit exceeded for {city}. Waiting 60s...")
            time.sleep(60)  # Wait before retrying
            return fetch_twitter_real_estate_tweets(city)

        if response.status_code == 200:
            data = response.json().get("data", [])
            if not data:
                print(f"⚠️ No tweets found for {city}.")
                return []

            # ✅ Sentiment Analysis
            structured_data = []
            for tweet in data:
                text = tweet.get("text", "N/A")
                created_at = tweet.get("created_at", "N/A")
                tweet_id = tweet.get("id", "N/A")
                author_id = tweet.get("author_id", "N/A")

                # Sentiment Analysis (-1 = Negative, 0 = Neutral, 1 = Positive)
                sentiment_score = round(TextBlob(text).sentiment.polarity, 3)

                structured_data.append({
                    "city": city,
                    "tweet_id": tweet_id,
                    "author_id": author_id,
                    "created_at": created_at,
                    "text": text,
                    "sentiment_score": sentiment_score
                })

            return structured_data

        else:
            print(f"❌ Twitter API Error {response.status_code} for {city}:\n{response.text}")
            return []

    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout occurred for {city}. Retrying in 30s...")
        time.sleep(30)
        return fetch_twitter_real_estate_tweets(city)

    except requests.exceptions.ConnectionError:
        print(f"🚨 Connection Error. Check internet & API access.")
        return []

# ✅ Fetch Tweets for All Cities
all_tweets = []
for city in CITIES:
    city_tweets = fetch_twitter_real_estate_tweets(city)
    if city_tweets:
        all_tweets.extend(city_tweets)
    
    # ✅ Avoid hitting Twitter's rate limit
    time.sleep(30)  # Wait between requests

# ✅ Save structured data
json_path = os.path.join(MARKET_TRENDS_FOLDER, "twitter_real_estate.json")
with open(json_path, "w") as f:
    json.dump(all_tweets, f, indent=4)

csv_path = os.path.join(MARKET_TRENDS_FOLDER, "twitter_real_estate.csv")
df = pd.DataFrame(all_tweets)
df.to_csv(csv_path, index=False)

# ✅ Debugging Step: Verify file saves
if os.path.exists(json_path) and os.path.exists(csv_path):
    print(f"✅ Twitter real estate data saved in:\n   📂 {json_path}\n   📂 {csv_path}")
else:
    print("❌ Files were not saved properly. Check write permissions.")