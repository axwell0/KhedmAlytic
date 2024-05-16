import streamlit as st

code_snippet = '''
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



def render_introduction():
    """Renders the introduction tab of the web app"""

    col1, col2 = st.columns([12, 1])
    with col1:
        st.markdown('# Introduction')
    with col2:
        if st.button('Fetch DB'):
            st.write("Data fetched and updated!")
    st.write(
        'Tanitjobs has been the leading job search website in Tunisia for many years. We scraped data from this website to gain insights into the job market, analyze trends, and understand the demands and opportunities available for job seekers in Tunisia')

    st.code(code_snippet)
    st.write('Note: Data loading code has been omitted')
