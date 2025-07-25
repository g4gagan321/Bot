import os
import requests
import openai
import time

# API Keys
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_KEY

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Replace with the usernames of big accounts you want to track
TARGET_USERS = ["elonmusk", "kunalb11"]

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=HEADERS)
    return r.json()["data"]["id"]

def get_latest_tweet(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at"
    r = requests.get(url, headers=HEADERS)
    tweets = r.json()["data"]
    return tweets[0]["id"], tweets[0]["text"]

def generate_reply(tweet_text):
    prompt = f"Write a witty, short reply (max 200 characters) to this tweet:\n\n{tweet_text}\n\nTone: Smart, funny, Indian professional style."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

def post_reply(tweet_id, text):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text, "reply": {"in_reply_to_tweet_id": tweet_id}}
    r = requests.post(url, headers=HEADERS, json=payload)
    print("Reply posted:", r.status_code, r.text)

if __name__ == "__main__":
    user_ids = {u: get_user_id(u) for u in TARGET_USERS}
    print("Tracking users:", user_ids)

    last_seen = {}

    while True:
        for username, uid in user_ids.items():
            try:
                tweet_id, tweet_text = get_latest_tweet(uid)
                if last_seen.get(username) != tweet_id:
                    reply = generate_reply(tweet_text)
                    post_reply(tweet_id, reply)
                    last_seen[username] = tweet_id
            except Exception as e:
                print("Error:", e)
        time.sleep(60)  # check every 1 minute
