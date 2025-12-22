from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import requests
import time

DATABASE_URL = "postgresql+psycopg2://postgres:hatim2001@localhost:5432/airline_sentiments"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

API_BASE_URL = "http://localhost:8001"
BATCH_ENDPOINT = f"{API_BASE_URL}/batch"

class TweetDB(Base):
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    airline_sentiment_confidence = Column(Float)
    airline = Column(String)
    negativereason = Column(String, nullable=True)
    tweet_created = Column(DateTime)
    text = Column(String)
    predicted_sentiment = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

def fetch_batch_from_api(batch_size=10):
    try:
        response = requests.get(BATCH_ENDPOINT, params={"batch_size": batch_size})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
        return []

def insert_batch_to_db(tweets_data):
    if not tweets_data:
        return 0
    
    db = SessionLocal()
    try:
        tweet_objects = []
        for tweet_data in tweets_data:
            tweet_created = datetime.fromisoformat(tweet_data['tweet_created'].replace('Z', '+00:00'))
            
            tweet = TweetDB(
                airline_sentiment_confidence=tweet_data['airline_sentiment_confidence'],
                airline=tweet_data['airline'],
                negativereason=tweet_data.get('negativereason'),
                tweet_created=tweet_created,
                text=tweet_data['text'],
                predicted_sentiment=tweet_data.get('predicted_sentiment')
            )
            tweet_objects.append(tweet)
        
        db.bulk_save_objects(tweet_objects)
        db.commit()
        return len(tweets_data)
    except Exception as e:
        db.rollback()
        print(f"Insert error: {e}")
        return 0
    finally:
        db.close()

def run_batch_insert(total_tweets=1000, batch_size=50, delay_seconds=1):
    inserted_count = 0
    batch_number = 0
    
    print(f"Inserting {total_tweets} tweets...")
    
    while inserted_count < total_tweets:
        batch_number += 1
        remaining = total_tweets - inserted_count
        current_batch_size = min(batch_size, remaining)
        
        tweets_data = fetch_batch_from_api(current_batch_size)
        
        if tweets_data:
            count = insert_batch_to_db(tweets_data)
            inserted_count += count
            print(f"Batch {batch_number}: {inserted_count}/{total_tweets}")
        
        if inserted_count < total_tweets:
            time.sleep(delay_seconds)
    
    print(f"Done! Inserted {inserted_count} tweets")

def view_tweets(limit=10):
    db = SessionLocal()
    try:
        tweets = db.query(TweetDB).limit(limit).all()
        print(f"\nFirst {limit} tweets:")
        for tweet in tweets:
            print(f"\n{tweet.airline} | {tweet.airline_sentiment_confidence}")
            print(f"{tweet.text}")
    finally:
        db.close()

if __name__ == "__main__":
    run_batch_insert(total_tweets=500, batch_size=50, delay_seconds=1)
    view_tweets(5)



    