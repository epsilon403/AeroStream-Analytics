from typing import Union
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import joblib

app = FastAPI()
app.title = "Airline Sentiment Analysis API"

embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', local_files_only=True)


classifier = joblib.load('../models/best_airline_sentiment_model.pkl')

@app.post("/predict/")
def predict_sentiment(text: str) -> Union[str, None]:
    try:

        embeddings = embedding_model.encode([text])
        prediction = classifier.predict(embeddings)
        labels = ["negative", "neutral", "positive"]

        return labels[prediction[0]]


    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Airline Sentiment Analysis API!"}
