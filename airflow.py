from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
import requests
import json

API_URL = "http://127.0.0.1:8000"

def generate_tweets(**context):
    """Task 1: Generate fake tweets from /batch endpoint"""
    response = requests.get(f"{API_URL}/batch", params={"batch_size": 10})
    tweets = response.json()
    print(f"✅ Generated {len(tweets)} tweets")
    return tweets

def clean_tweets(**context):
    """Task 2: Clean the generated tweets"""
    from clean_data import clean_tweets as clean_func
    return clean_func(**context)

def predict_sentiment(**context):
    """Task 3: Predict sentiment for cleaned tweets"""
    ti = context['ti']
    cleaned_tweets = ti.xcom_pull(task_ids='clean_tweets')
    
    predictions = []
    for tweet in cleaned_tweets:
        response = requests.post(
            f"{API_URL}/predict/",
            params={"text": tweet['cleaned_text']}
        )
        if response.status_code == 200:
            tweet['predicted_sentiment'] = response.json()
            predictions.append(tweet)
    
    print(f"✅ Predicted sentiment for {len(predictions)} tweets")
    return predictions

def insert_to_db(**context):
    """Task 4: Insert predictions to database"""
    from insert import insert_batch_to_db
    ti = context['ti']
    predictions = ti.xcom_pull(task_ids='predict_sentiment')
    
    count = insert_batch_to_db(predictions)
    print(f"✅ Inserted {count} tweets to database")
    return count

with DAG(
    'twitter_sentiment_pipeline',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    description='Generate tweets → Clean → Predict → Insert to DB'
) as dag:
    
    task_1 = PythonOperator(
        task_id='generate_tweets',
        python_callable=generate_tweets,
        provide_context=True
    )
    
    task_2 = PythonOperator(
        task_id='clean_tweets',
        python_callable=clean_tweets,
        provide_context=True
    )
    
    task_3 = PythonOperator(
        task_id='predict_sentiment',
        python_callable=predict_sentiment,
        provide_context=True
    )
    
    task_4 = PythonOperator(
        task_id='insert_to_db',
        python_callable=insert_to_db,
        provide_context=True
    )
    
    task_1 >> task_2 >> task_3 >> task_4
