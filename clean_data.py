import json
import re
from datetime import datetime

def clean_tweet_text(text):
    """Clean tweet text by removing URLs, extra whitespace"""
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_tweets(**context):
    """Clean tweets from previous task"""
    ti = context['ti']
    tweets = ti.xcom_pull(task_ids='generate_tweets')
    
    if isinstance(tweets, str):
        tweets = json.loads(tweets)
    
    cleaned_tweets = []
    for tweet in tweets:
        cleaned_data = {
            'airline': tweet.get('airline', ''),
            'text': tweet.get('text', ''),
            'cleaned_text': clean_tweet_text(tweet.get('text', '')),
            'airline_sentiment_confidence': tweet.get('airline_sentiment_confidence', 0),
            'negativereason': tweet.get('negativereason', ''),
            'tweet_created': tweet.get('tweet_created', '')
        }
        cleaned_tweets.append(cleaned_data)
    
    print(f"✅ Cleaned {len(cleaned_tweets)} tweets")
    return cleaned_tweets