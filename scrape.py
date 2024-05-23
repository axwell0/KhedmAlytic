import asyncio
import os
import time
# TODO: Add cron job scheduling for the scrapers
# TODO: Add Keejob to the scrapers

from dotenv import load_dotenv

from config.Tanit_config import Tanit_cfg
from config.bayt_config import bayt_cfg
from database.database import Mongo
from scrapers.BaytScraper import BaytScraper
from scrapers.TanitScraper import TanitScraper

load_dotenv('database/.env')
MONGODB_URI = os.environ['MONGODB_URI']
DB = os.environ['DB']
bayt_collection_name = os.environ['bayt_collection_name']
tanit_collection_name = os.environ['tanit_collection_name']
start_time = time.time()


async def scrape() -> None:
    """main entry point"""

    async with (Mongo(MONGODB_URI, DB) as mongo):
        collections = \
            {
                "Bayt": mongo[bayt_collection_name],
                "Tanit": mongo[tanit_collection_name]
            }
        bayt = BaytScraper(bayt_cfg)
        tanit_scraper = TanitScraper(Tanit_cfg)

        async with asyncio.TaskGroup() as tg:
            bayt_task = tg.create_task(bayt.run(collections['Bayt']))
            tanit_task = tg.create_task(tanit_scraper.run(collections['Tanit']))
        jobs = \
            {
                bayt_collection_name: bayt_task.result(),
                tanit_collection_name: tanit_task.result()
            }

        async with asyncio.TaskGroup() as tg:
            for key, value in jobs.items():
                for job in value:
                    tg.create_task(mongo.insert_job(job, key))


asyncio.run(scrape())

print(f'{time.time() - start_time} Elapsed')
