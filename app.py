import streamlit as st
import requests

st.title("Airline Sentiment Analyzer")

url = "http://127.0.0.1:8001/predict/"

user_input = st.text_input("Enter the text you want to predict")

if st.button("Predict"):
    if user_input:
        response = requests.post(url=url, params={"text": user_input})


        if response.status_code == 200:
            prediction = response.json() 
            
            st.success(f"Predicted Sentiment: {prediction}")
        else:
            st.error("Error: Could not get prediction")
    else:
        st.warning("Please enter some text first.")