import json
import os
import time

import pymongo
from dotenv import load_dotenv
import asyncio
from config.bayt_config import bayt_cfg
from config.Tanit_config import Tanit_cfg

from database.database import Mongo
from scrapers.BaytScraper import BaytScraper
from scrapers.TanitScraper import TanitScraper

load_dotenv('database/.env')
bayt_collection_name = os.environ['Bayt_collection']
tanit_collection_name = os.environ['Tanit_collection']
start_time = time.time()


async def main() -> None:
    """main entry point"""

    async with (Mongo() as mongo):
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
            for key,value in jobs.items():
                for job in value:
                    tg.create_task(mongo.insert_job(job,key))




asyncio.run(main())

print(f'{time.time() - start_time} Elapsed')
