from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random
from faker import Faker


DATABASE_URL = "postgresql+psycopg2://postgres:hatim2001@localhost:5432/airline_sentiments"  
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TweetDB(Base):
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    airline_sentiment_confidence = Column(Float)
    airline = Column(String)
    negativereason = Column(String, nullable=True)
    tweet_created = Column(DateTime)
    text = Column(String)

Base.metadata.create_all(bind=engine)
