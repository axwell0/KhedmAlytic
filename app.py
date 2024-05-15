import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import spacy
import pymongo
import string
import os
from dotenv import load_dotenv
from folium.plugins import MarkerCluster
from nltk.corpus import stopwords

# Load environment variables
load_dotenv('database/.env')
MONGO_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DATABASE_NAME')
tanit_collection_name = os.getenv('Tanit_collection')

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database(DB_NAME)
tanit = db[tanit_collection_name]

# Load Spacy model and stopwords
nlp = spacy.load('fr_core_news_sm')
stop = set(stopwords.words('french'))
exclude = set(string.punctuation)

# Streamlit App
st.title("Data Analysis and Visualization")


# Display the data
st.write("Data from MongoDB collection:", tanit_collection_name)

# Fetch and display some data
sample_data = list(tanit.find().limit(5))
st.write(sample_data)