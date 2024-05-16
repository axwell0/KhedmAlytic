import asyncio
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
from folium.plugins import MarkerCluster
from nltk.corpus import stopwords
from utils.utils import auto_reconnect, get_coordinates
from streamlit_app.processing import pre_process
st.title='Tanitjobs analysis'
MONGO_URI = st.secrets['MONGODB_URI']
DB_NAME = st.secrets['DATABASE_NAME']
tanit_collection_name = st.secrets['Tanit_collection']
MAX_AUTO_RECONNECT_ATTEMPTS = 5

progress_bar = st.progress(0)
status_text = st.empty()


@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI)

@st.cache_data(ttl= 57600)
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
for i in range(3, 0, -1):
    status_text.success(f"Data successfully fetched. Proceeding in {i}...")
    time.sleep(1)

tab1, tab2,tab3 = st.tabs(["Introduction","Data Cleaning", "Visualization"])
with tab1:
    status_text.empty()
    progress_bar.empty()
    col1, col2 = st.columns([12, 1])
    with col1:
        st.markdown('# Introduction')
    with col2:
        if st.button('Fetch DB'):
            st.write("Data fetched and updated!")
    st.write(
        'Tanitjobs has been the leading job search website in Tunisia for many years. We scraped data from this website to gain insights into the job market, analyze trends, and understand the demands and opportunities available for job seekers in Tunisia')

    code_snippet0 = '''
            import asyncio
            import os
            import re
            import string
            import warnings
            import folium
            import numpy as np
            import pandas as pd
            import plotly.express as px
            import pymongo
            import spacy

            from dotenv import load_dotenv
            from folium import Marker
            from folium.plugins import MarkerCluster
            from nltk.corpus import stopwords

            from utils.utils import get_coordinates
            from utils.utils import get_job_industries
            from utils.utils import auto_reconnect

            nlp = spacy.load('fr_core_news_sm')
            stop = set(stopwords.words('french'))
            exclude = set(string.punctuation)
            warnings.filterwarnings("ignore")'''

    st.code(code_snippet0)
    st.write('Note: Data loading code has been omitted')
with tab2:

    st.markdown("# Data Cleaning and Processing")

    st.write("""
        - Rename columns to more readable names
        - Convert date strings to datetime objects
        - mapping French categorical values to English
        - splitting of comma-separated strings into lists
        """)
    code_snippet1 = '''
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
    code_snippet2 = '''job_openings = tanit_df['Openings'].map(lambda poste: re.search(r'\d', poste).group()).astype('int32')
        tanit_df['Openings'] = job_openings'''
    code_snippet3 = '''
        def clean(doc):
            if not(type(doc) in [np.nan,np.NAN,np.NaN,float,"",None]):
                stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
                punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
                only_alphabet = ''.join([c for c in punc_free if c.isalpha() or c == ' '])

                return only_alphabet
            return None

        tanit_df['Description'] = tanit_df['Description'].fillna('').map(lambda x: clean(x)).apply(lambda x: x.lower())
        tanit_df['Requirements'] = tanit_df['Requirements'].fillna('').map(lambda x: clean(x)).apply(lambda x: x.lower())
        tanit_df['Title'].map(lambda x: x.encode('ascii',"ignore").decode())'''
    code_snippet4 = '''
        tanit_df['Zone'] = tanit_df['Zone'].map(lambda x: x.encode('ascii',"ignore").decode())
        loop = asyncio.get_event_loop()
        task = loop.create_task(get_coordinates(tanit_df)) #by default get_coordinates will only retrieve coordinates for the top 50 most common locations
        coordinates = await task
        tanit_df = tanit_df.merge(coordinates, on='Zone', how='left')
        tanit_df['Latitude'] = tanit_df['Latitude'].astype(float)
        tanit_df['Longitude'] = tanit_df['Longitude'].astype(float) '''
    code_snipped5 = '''
        loop = asyncio.get_event_loop()
        task = loop.create_task(get_job_industries(tanit_df))
        task_result = await task
        tanit_df['Category'] = tanit_df['Title'].map(task_result)
        keep_categories = ['Administration/Management', 'Sales', 'Tradesperson', 'Software/IT',
               'Engineering', 'Arts & Design', 'Customer Service', 'Finance',
               'Marketing', 'Healthcare', 'Accounting', 'Manufacturing']

        total = tanit_df['Category'].value_counts().sum()
        categories = tanit_df['Category'].value_counts()
        tanit_df['Category'] = tanit_df['Category'].apply(lambda x: x if pd.notna(x) and ((x in keep_categories) or (categories[x] / total > 0.02)) else 'Other')'''
    st.code(code_snippet1)

    st.markdown('##### Extracting the number of available openings of a particular job')
    st.code(code_snippet2)
    st.markdown("##### Text data clean up (Punctuation, stop words, special characters removal)")
    st.code(code_snippet3)
    st.markdown(
        "##### Converting 'Zone' data into latitude and longitude using a geocoding API (implementation in utils)")
    st.code(code_snippet4)
    st.markdown("##### Extraction of broad job categories using Llama3 API (implementation in utils)")
    st.code(code_snipped5)
    tanit_df = pre_process(tanit_df)

    st.write(tanit_df.head(20))

with tab3:
    st.markdown("# **Visualization**")
    st.markdown('##### Distribution of job categories')

    filtered_df = tanit_df[tanit_df['Category'].notna()]
    category_counts = filtered_df.groupby('Category')['Openings'].sum()
    category_counts_df = category_counts.reset_index()
    category_counts_df.columns = ['Category', 'Count']

    # Create the pie chart with Plotly
    fig = px.pie(category_counts_df, values='Count', names='Category', hole=0.5)
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)
