from fastapi import FastAPI

app = FastAPI(title="Airline Sentiment Analysis - Complete API", version="1.0")

from api import predict_sentiment, read_root as api_root, embedding_model, classifier
from fastapi_tweet import get_microbatch

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Airline Sentiment Analysis API!",
        "endpoints": {
            "predict": "POST /predict/ - Predict sentiment for a single text",
            "batch_generator": "GET /batch - Generate fake tweets for testing",
            "health": "GET /health - Check API health"
        }
    }

app.post("/predict/")(predict_sentiment)
app.get("/batch")(get_microbatch)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": classifier is not None,
        "embedding_model_loaded": embedding_model is not None
    }
