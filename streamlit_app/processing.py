import re

import nltk
import numpy as np
import string
import spacy
import pandas as pd
import streamlit as st
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
nlp = spacy.load('fr_core_news_sm')
stop = set(stopwords.words('french'))
exclude = set(string.punctuation)

@st.cache_data(ttl=30)
def pre_process(tanit_df):

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
        'Description de l\'emploi': 'Description',
        'Exigences de l\'emploi': 'Requirements',
        'Date d\'expiration': 'Expiration Date',
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
    tanit_df['Openings'] = job_openings

    def clean(doc):
        if not (type(doc) in [np.nan, np.NAN, np.NaN, float, "", None]):
            stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
            punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
            only_alphabet = ''.join([c for c in punc_free if c.isalpha() or c == ' '])

            return only_alphabet
        return None

    tanit_df['Description'] = tanit_df['Description'].fillna('').map(lambda x: clean(x)).apply(lambda x: x.lower())
    tanit_df['Requirements'] = tanit_df['Requirements'].fillna('').map(lambda x: clean(x)).apply(lambda x: x.lower())
    tanit_df['Title'].map(lambda x: x.encode('ascii', "ignore").decode())
    return tanit_df