import time

import streamlit as st
st.set_page_config(layout="wide")
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
from utils.utils import auto_reconnect
from streamlit_app.processing import pre_process

MONGO_URI = st.secrets['MONGODB_URI']
DB_NAME = st.secrets['DATABASE_NAME']
tanit_collection_name = st.secrets['Tanit_collection']
MAX_AUTO_RECONNECT_ATTEMPTS = 5

progress_bar = st.progress(0)
status_text = st.empty()


@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI)


@st.cache_data(ttl=57600)  # Keep cache for 16 hours
@auto_reconnect(MAX_AUTO_RECONNECT_ATTEMPTS)
def load_data():
    df = pd.DataFrame(iter(tanit_col.find({})))
    return df


status_text.info("Connecting to MongoDB...")
progress_bar.progress(10)
client = init_connection()
db = client.get_database(DB_NAME)
tanit_col = db.get_collection(tanit_collection_name)
status_text.info("Connected to MongoDB.")
progress_bar.progress(30)
status_text.info("Fetching data from the collection...")
progress_bar.progress(50)
tanit_df = load_data()
progress_bar.progress(100)
# for i in range(3, -1, -1):
#     status_text.success(f"Data successfully fetched. Proceeding in {i}...")
#     time.sleep(1)
status_text.empty()
progress_bar.empty()

st.markdown("# **Data Cleaning and Processing**")

st.write("""
- Rename columns to more readable names
- Convert date strings to datetime objects
- mapping French categorical values to English
- splitting of comma-separated strings into lists
""")

code_snippet1='''
experience_map = {'Débutant': 'No experience', '0 à 1 an': '0-1 year', '1 à 3 ans': '1-3 years',
                '3 à 5 ans': '3-5 years', '5 à 10 ans': '5-10 years', 'plus 10 ans': '10+ years'}
experience_order = ['No experience', '0-1 year', '1-3 years', '3-5 years', '5-10 years', '10+ years']
salary_map = {'Inférieur à 500 DT': "0-500 DT",
              "Entre 500 DT et 1000 DT": "500-1000 DT",
              "Entre 1000 DT et 1500 DT": "1000-1500 DT",
              "Entre 1500 DT et 2000 DT": "1500-2000 DT",
              "Entre 2000 DT et 3000 DT": "2000-3000 DT",
              "Plus 3000 DT": "3000+ DT"}
salary_order = ["0-500 DT", "500-1000 DT", "1000-1500 DT", "1500-2000 DT", "2000-3000 DT", "3000+ DT"]
del tanit_df['_id']

tanit_df.rename(columns=
{
    "Description de l'emploi": 'Description',
    "Exigences de l'emploi": 'Requirements',
    "Date d'expiration": 'Expiration Date',
    'Rémunération proposée': 'Salary Range',
    'Postes vacants': 'Openings',
    "Niveau d'étude": "education levels",
    'Langue': 'Language',
    "Type d'emploi désiré": "Employment Type"
}, inplace=True)

tanit_df['posting_date'] = pd.to_datetime(tanit_df['posting_date'], format='%d/%m/%Y')
tanit_df['Expiration Date'] = pd.to_datetime(tanit_df['Expiration Date'], format='%d/%m/%Y')

tanit_df['Experience'] = tanit_df['Experience'].map(experience_map)
tanit_df['Experience'] = pd.Categorical(tanit_df['Experience'], categories=experience_order, ordered=True)

tanit_df['Salary Range'] = tanit_df['Salary Range'].map(salary_map)
tanit_df['Salary Range'] = pd.Categorical(tanit_df['Salary Range'], categories=salary_order, ordered=True)
tanit_df['Language_list'] = tanit_df['Language'].str.split(', ')
tanit_df['contract_types'] = tanit_df["Employment Type"].str.split(', ')
tanit_df['education_levels'] = tanit_df["education levels"].str.split(', ')
job_openings = tanit_df['Openings'].map(lambda poste: re.search(r'\d', poste).group()).astype('int32')
tanit_df['Openings'] = job_openings'''
code_snippet2= '''job_openings = tanit_df['Openings'].map(lambda poste: re.search(r'\d', poste).group()).astype('int32')
tanit_df['Openings'] = job_openings'''
st.code(code_snippet1)

tanit_df = pre_process(tanit_df)
st.write(tanit_df.head(5))
st.write('- **Extracting the number of available openings of a particular job**')
st.code(code_snippet2)



