import asyncio
import json
import random
import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tenacity import retry, retry_if_exception_type, wait_fixed
from aiohttp import ClientSession
from typing import Any, Generator


class RetryError(Exception):
    """custom error for excessive requests to Groq Cloud API"""

    def __init__(self, message="Maximum retries reached"):
        super().__init__(message)


system = "You are a helpful and obedient assistant."
human = """classify the industry/line of each job posting. ONLY USE ONE OF THE FOLLOWING CATEGORIES: 
            Engineering,
            IT,
            Administration/Management,
            Finance/Accounting,
            Sales/Marketing,
            Healthcare,
            Manufacturing/Production,
            Customer Service,
            Arts & Design,
            Other. write in this format: title:classification in a new line.DO NOT SKIP ANY JOB. The job posting titles are {batch}"""
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])


@retry(wait=wait_fixed(1), retry=retry_if_exception_type(RetryError))
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
    api_keys = ["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",
                "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",
                "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",
                "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",
                "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",
                "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",
                "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"]
    classifications = {}
    for batch in get_batch(df['Title'].unique()):
        await label_industry(batch, random.choice(api_keys), classifications)

    print(f'L: {len(classifications)} {classifications}')
    return classifications




async def send(zone: str, session: ClientSession, apikey: str,zones: dict):
    async with session.get(f'https://geocode.maps.co/search?q={zone}&api_key={apikey}') as resp:

        x = await resp.text()
        if (x != "[]"):

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