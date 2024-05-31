import asyncio
import os
import time
import pandas as pd

from dotenv import load_dotenv
from APIs.geo_api import get_coordinates
from APIs.industry_classification import get_job_industries
from config.Tanit_config import Tanit_cfg
from config.bayt_config import bayt_cfg
from database.database import Mongo
from scrapers.BaytScraper import BaytScraper
from scrapers.TanitScraper import TanitScraper

load_dotenv('.env')
MONGODB_URI = os.environ['MONGODB_URI']
DB = os.environ['DB']
bayt_collection_name = os.environ['bayt_collection_name']
tanit_collection_name = os.environ['tanit_collection_name']
GEO_KEY1 = os.environ['GEO_KEY1']
GEO_KEY2 = os.environ['GEO_KEY2']
GEO_KEY3 = os.environ['GEO_KEY3']
GROQ_API_KEY = os.environ['GROQ_API_KEY']
start_time = time.time()


async def scrape() -> None:
    """main entry point"""

    async with (Mongo(MONGODB_URI, DB) as mongo_client):
        collections = \
            {
                "Bayt": mongo_client[bayt_collection_name],
                "Tanit": mongo_client[tanit_collection_name]
            }

        bayt_scraper = BaytScraper(bayt_cfg)
        tanit_scraper = TanitScraper(Tanit_cfg)

        async with asyncio.TaskGroup() as tg:
            bayt_task = tg.create_task(bayt_scraper.run(collections['Bayt']))
            tanit_task = tg.create_task(tanit_scraper.run(collections['Tanit']))
        bayt_jobs = bayt_task.result()
        tanit_jobs = tanit_task.result()
        if tanit_jobs:
            print('Preprocessing Tanitjobs....')
            df = pd.DataFrame(tanit_task.result())
            coordinates = await get_coordinates(df,GEO_KEY1,GEO_KEY2,GEO_KEY3)
            print('Coordinates obtained')
            classes = await get_job_industries(df,GROQ_API_KEY)
            df['Category'] = df['Title'].map(classes)

            df = df.merge(coordinates, on='Zone', how='left')
            df['Latitude'] = df['Latitude'].astype(float)
            df['Longitude'] = df['Longitude'].astype(float)
            tanit_jobs = df.to_dict('records')

        jobs = \
            {
                bayt_collection_name: bayt_jobs,
                tanit_collection_name: tanit_jobs
            }

        async with asyncio.TaskGroup() as tg:
            for key, value in jobs.items():
                for job in value:
                    tg.create_task(mongo_client.insert_job(job, key))


asyncio.run(scrape())

print(f'{time.time() - start_time} Elapsed')
