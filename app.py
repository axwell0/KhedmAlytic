import nltk
import streamlit as st
from streamlit_folium import folium_static

from streamlit_app.cleaning import *
from streamlit_app.visualization import *
st.set_page_config(layout="wide")
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

import time
import pandas as pd
import pymongo
import spacy

from streamlit_app.processing import pre_process
from streamlit_app.introduction import render_introduction

nlp = spacy.load('fr_core_news_sm')
st.title = 'Tanitjobs analysis'

MONGO_URI = st.secrets['MONGODB_URI']
DB_NAME = st.secrets['DATABASE_NAME']
tanit_collection_name = st.secrets['Tanit_collection']
MAX_AUTO_RECONNECT_ATTEMPTS = 5

progress_bar = st.progress(0)
status_text = st.empty()


@st.cache_data(ttl=82800 * 3)
def load_data(uri, db_name, collection_name):
    client = init_connection(uri)
    db = client[db_name]
    collection = db[collection_name]
    df = pd.DataFrame(iter(collection.find({})))
    return df


@st.cache_resource(ttl=82800 * 3)
def init_connection(uri):
    return pymongo.MongoClient(uri)


status_text.text("Connected to MongoDB.")
progress_bar.progress(30)
status_text.text("Fetching data from the collection...")
progress_bar.progress(50)

tanit_df = load_data(MONGO_URI, DB_NAME, tanit_collection_name)
progress_bar.progress(100)

for i in range(3, 0, -1):
    status_text.text(f"Data successfully fetched. Proceeding in {i}...")
    time.sleep(1)

status_text.empty()
progress_bar.empty()

tab1, tab2, tab3 = st.tabs(["Introduction", "Data Cleaning", "Visualization"])
with tab1:
    render_introduction()
with tab2:
    st.markdown("# Data Cleaning and Processing")
    st.write("""
        - Rename columns to more readable names
        - Convert date strings to datetime objects
        - mapping French categorical values to English
        - splitting of comma-separated strings into lists
        """)
    render_cleaning_tab()
    tanit_df = pre_process(tanit_df)
    st.write(tanit_df.head(20))

with tab3:
    st.markdown("# **Visualization**")
    st.markdown('#### Distribution of job categories')
    pie_chart = execute_block1(tanit_df)
    st.plotly_chart(pie_chart,use_container_width=True)

    map = execute_block2(tanit_df)

    folium_static(map,width=1280)
    st.write(
        'Unsurprisingly, Most jobs posted online are located on major coastal cities (Sousse, Monastir, Nabeul) and the capital Tunis.')
    salary_chart = execute_block3(tanit_df)
    st.plotly_chart(salary_chart,use_container_width=True)
    st.write(
        'The graph shows the distribution of salary ranges across various job categories, highlighting that Sales and Administration/Management have the most job postings, predominantly offering lower salaries (500-1500 DT). Customer Service follows a similar trend. Tradesperson and Software/IT categories display a more balanced distribution across mid to higher salary ranges (1500-3000+ DT), with fewer postings overall. Specialized fields like Engineering, Healthcare, and Finance, though with fewer postings, offer higher salaries. This indicates that more specialized jobs tend to offer higher compensation compared to more common roles. However, many job postings do not include salary ranges, therefore this chart may not fully reflect the actual salary distribution across')

    language_chart = execute_block4(tanit_df)
    st.plotly_chart(language_chart,use_container_width=True)
    st.write(
            '- As one would expect, french is still very much a requirement in certain fields (Management, Sales, Finance & Accounting, Customer Service, Trades etc..).')
    st.write('- Engineering and IT-related jobs show a notable demand for english proficiency.')

    past_experience = execute_block5(tanit_df)
    st.plotly_chart(past_experience,use_container_width=True)
    st.write(
        'The plot reveals that most job categories require 1-3 years of experience, indicating a strong demand for candidates with early to mid-level experience. Certain fields such as IT, Engineering, and Finance roles are not very entry-level friendly, as they show fewer job postings for candidates with no experience or 0-1 years of experience.')

    internships = execute_block6(tanit_df)
    st.plotly_chart(internships,use_container_width=True)
    st.write('Internships/Part time jobs postings are more frequent in the middle of April and the start of May.')

    experience_internship = execute_block7(tanit_df)
    st.plotly_chart(experience_internship, use_container_width=True)
    st.write(
        'Most job postings in categories like IT, Engineering, and Marketing require some level of experience (0-1 year and 1-3 years). In contrast, categories like finance offer more balanced opportunities across different experience levels, including those with no prior experience. In essence, There are relatively fewer opportunities for candidates with no experience, though these are still present in all categories.')

    degree_requirements = execute_block8(tanit_df)
    st.plotly_chart(degree_requirements,use_container_width=True)
    st.write(
        "- Most postings in Accounting, Finance, Marketing require a Bachelor's, with few needing a Master’s degree.")
    st.write(
        "- Classical Engineering disciplines are accessible with a Bachelors. However, Engineering Diplomas are heavily favored. There does not seem to be much benefit from acquiring a Master's in a classical engineering field.")
    st.write(
        "- Software/IT: Although there are good prospects for both Bachelor and Master's degrees holders, more emphasis and preference is placed on engineering degree holders.")

    salaries_by_degree = execute_block9(tanit_df)
    st.plotly_chart(salaries_by_degree,use_container_width=True)
    st.write(
        "- Finance and Marketing: Master's degrees seem to be a requirement for higher pay. Schools don't have much influence on salary.")
    st.write(
        "- Engineering: Engineering diploma looks to be the main requirement for higher pay. Preference for elite institutions doesn't seem to factor in that in the mid to high pay brackets.")
    st.write(
        "- Software/IT: Master's degrees and engineering diplomas seem to yield similar returns. Preference for elite institutions is significant for high-paying jobs.")
    software_requirements = execute_block10(tanit_df)
    st.plotly_chart(software_requirements,use_container_width=True)
    st.write(
        "high demand for web development skills like SQL, PHP, HTML, JavaScript, and Python. React and Angular indicate a need for modern web applications. Docker, AWS, azure indicate demand for cloud and devops engineers. Mobile app development is also in demand (java, android, flutter). The market for AI and Machine Learning has not flourished yet.")

