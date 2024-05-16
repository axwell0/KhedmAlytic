import asyncio
import functools
import json
import logging
import random
import time
import streamlit as st
import pandas as pd
import pymongo

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt
from aiohttp import ClientSession
from typing import Any, Generator


class RetryError(Exception):
    """custom error for excessive requests to Groq Cloud API"""

    def __init__(self, message="Maximum retries reached"):
        super().__init__(message)


system = "You are a helpful and obedient assistant."
human = """classify the industry/line of each job posting. ONLY USE ONE OF THE FOLLOWING CATEGORIES. DO NOT COME UP WITH ANOTHER CATEGORY: 
            Tradesperson,
            Engineering (THIS ONLY INCLUDES ALL COLLEGE-LEVEL Engineering disciplines except software),
            Software/IT,
            Administration/Management,
            Finance,
            Accounting
            Sales,
            Marketing
            Healthcare,
            Manufacturing,
            Customer Service,
            Arts & Design. write in this format: title:classification in a new line.DO NOT SKIP ANY JOB. The job posting titles are {batch}"""
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])


@retry(wait=wait_fixed(1),stop=stop_after_attempt(5) ,retry=retry_if_exception_type(RetryError))
async def label_industry(batch: list, api_key: str, classifications: dict):
    """
    runs the batch through the groq cloud API (LLM) to infer industry

    :param batch: list of job titles
    :param api_key: groq cloud api key
    :param classifications: final classifications dictionary
    :return:
    """
    try:

        chat = ChatGroq(temperature=0,
                        groq_api_key=api_key,
                        model_name="llama3-8b-8192")
        chain = prompt | chat
        chat_completion = await chain.ainvoke({"batch": ','.join(batch)})
        response = chat_completion.content

        response_pre = response[response.find('\n\n') + 2:].replace('\n\n', '\n')
        jobs = response_pre.split('\n')

        for item in jobs:
            if item.find(':'):
                key = item[:item.find(':')]
                value = item[item.find(':') + 1:].strip()
                classifications[key] = value
        print(f'Progress: length({len(classifications)})')

    except:
        raise RetryError('API Timeout')


def get_batch(series: pd.Series, batch_size: int = 100) -> Generator[list, Any, None]:
    """Generates batches from a pandas Series object"""

    total_titles = len(series)

    for start in range(0, total_titles, batch_size):
        end = start + batch_size
        batch_titles = series[start:end]
        yield list(batch_titles)


async def get_job_industries(df: pd.DataFrame) -> dict:
    """Uses the 'Title' column of a dataframe and runs it through a Llama3 API to infer its industry/line of work
    :param df: dataframe containing a 'Title' column"""
    api_keys = [
        "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",
        "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",
        "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",
    ]

    classifications = {}
    unique_titles = df['Title'].unique()

    batches = list(get_batch(unique_titles))

    for i, batch in enumerate(batches):
        api_key = api_keys[i % len(api_keys)]
        await label_industry(batch, api_key, classifications)

    print(f'L: {len(classifications)} {classifications}')
    return classifications

async def send(zone: str, session: ClientSession, apikey: str,zones: dict):
    async with session.get(f'https://geocode.maps.co/search?q={zone}&api_key={apikey}') as resp:

        x = await resp.text()
        if x != "[]":

            try:

                json_response = json.loads(x)[0]
                lon = json_response['lon']
                lat = json_response['lat']
                print((zone,lon,lat))
                zones[zone] = {'Longitude': lon,
                               "Latitude": lat}
            except:
                print('Error with Json')


async def get_coordinates(df: pd.DataFrame,n_zones: int = 50) -> pd.DataFrame:
    geocoding_apikeys = ["6640181610756399606617buna43faa",
                         "6640b722d851d739895184xch5acb84",
                         "6640b7a0782db510080964dztb878fd"]
    zones = {}
    async with ClientSession() as session:
        for item in df['Zone'].value_counts().head(n_zones).index:
            await send(item, session, random.choice(geocoding_apikeys),zones)
            await asyncio.sleep(1)
    data = [{'Zone': zone, 'Longitude': coords['Longitude'], 'Latitude': coords['Latitude']} for zone, coords in
            zones.items()]

    return pd.DataFrame(data)
def auto_reconnect(max_auto_reconnect_attempts):
    """Auto reconnect handler"""
    def decorator(mongo_op_func):
        @functools.wraps(mongo_op_func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_auto_reconnect_attempts):
                try:
                    return mongo_op_func(*args, **kwargs)
                except pymongo.errors.AutoReconnect as e:
                    wait_t = 0.5 * pow(2, attempt)
                    logging.warning("PyMongo auto-reconnecting... %s. Waiting %.1f seconds.", str(e), wait_t)
                    time.sleep(wait_t)
            raise pymongo.errors.AutoReconnect(f"Failed to reconnect after {max_auto_reconnect_attempts} attempts.")
        return wrapper
    return decorator



class block:
    """Block for rendering elements on streamlit"""
    def __init__(self, subtitle: str = "", code_snippet: str = ""):
        self.sub = subtitle
        self.code = code_snippet

    def render(self):
        if (self.sub):
            st.markdown(f'#### {self.sub}')
        if (self.code):
            st.code(self.code)