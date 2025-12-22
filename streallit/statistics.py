import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, DateTime, func, distinct, select
)
from sqlalchemy.orm import sessionmaker, declarative_base

# database connection settings
DATABASE_URL = "postgresql+psycopg2://postgres:hatim2001@localhost:5432/airline_sentiments"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# database table model
class TweetDB(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    airline_sentiment_confidence = Column(Float)
    airline = Column(String)
    negativereason = Column(String)
    tweet_created = Column(DateTime)
    text = Column(String)
    predicted_sentiment = Column(String)

# setup streamlit page
st.set_page_config(page_title="Airline Sentiment Dashboard", layout="wide")
st.title("✈️ Twitter US Airline Sentiment Dashboard")

# start database session
session = SessionLocal()

# get basic counts for the top metrics
tweet_count = session.execute(
    select(func.count(TweetDB.id))
).scalar()

total_airline = session.execute(
    select(func.count(distinct(TweetDB.airline)))
).scalar()

# get count of tweets for each sentiment type
sentiment_rows = session.execute(
    select(TweetDB.predicted_sentiment, func.count(TweetDB.id))
    .group_by(TweetDB.predicted_sentiment)
).all()

sentiment_results = dict(sentiment_rows)

# find the most common reason for negative tweets
negative_reason_row = session.execute(
    select(TweetDB.negativereason, func.count(TweetDB.id))
    .filter(TweetDB.predicted_sentiment == "negative")
    .group_by(TweetDB.negativereason)
    .order_by(func.count(TweetDB.id).desc())
).first()

top_reason_text = negative_reason_row[0] if negative_reason_row else "None"

# display the top metrics on the dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("COUNT OF TWEET", tweet_count)
col2.metric("COUNT OF AIRLINE", total_airline)
col3.metric("NEGATIVE TWEETS", sentiment_results.get("negative", 0))
col4.metric("TOP NEGATIVE REASON", top_reason_text)

st.divider()

# get data for airline vs sentiment bar chart
airline_sentiment = session.execute(
    select(
        TweetDB.airline,
        TweetDB.predicted_sentiment,
        func.count(TweetDB.id).label("count")
    )
    .group_by(TweetDB.airline, TweetDB.predicted_sentiment)
).all()

df_airline_sentiment = pd.DataFrame(
    airline_sentiment,
    columns=["airline", "sentiment", "count"]
)

st.subheader("Airline vs Sentiment")
st.bar_chart(
    df_airline_sentiment.pivot(
        index="airline",
        columns="sentiment",
        values="count"
    )
)

# get data for negative reasons bar chart
negative_reasons = session.execute(
    select(
        TweetDB.negativereason,
        func.count(TweetDB.id).label("count")
    )
    .filter(TweetDB.predicted_sentiment == "negative")
    .group_by(TweetDB.negativereason)
    .order_by(func.count(TweetDB.id).desc())
).all()

df_negative = pd.DataFrame(
    negative_reasons,
    columns=["reason", "count"]
)

st.subheader("Negative Reason Count")
st.bar_chart(df_negative.set_index("reason"))

# draw a pie chart for sentiment distribution
df_sentiment = pd.DataFrame(
    sentiment_results.items(),
    columns=["sentiment", "count"]
)

st.subheader("Sentiment Distribution")

fig, ax = plt.subplots()
ax.pie(
    df_sentiment["count"],
    labels=df_sentiment["sentiment"],
    autopct="%1.1f%%",
    startangle=90
)
ax.axis("equal")
st.pyplot(fig)

# get data for date vs negative sentiment line chart
date_sentiment = session.execute(
    select(
        func.date(TweetDB.tweet_created).label("date"),
        func.count(TweetDB.id).label("count")
    )
    .filter(TweetDB.predicted_sentiment == "negative")
    .group_by(func.date(TweetDB.tweet_created))
    .order_by(func.date(TweetDB.tweet_created))
).all()

df_date = pd.DataFrame(date_sentiment, columns=["date", "count"])

st.subheader("Date vs Negative Sentiment")
st.line_chart(df_date.set_index("date"))

# close the database session
session.close()