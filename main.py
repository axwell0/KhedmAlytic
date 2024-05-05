import json
import os
import time

import pymongo
from dotenv import load_dotenv
import asyncio
from config.bayt_config import bayt_cfg
from config.Tanit_config import Tanit_cfg

from db.database import Mongo
from scrapers.BaytScraper import BaytScraper
from scrapers.TanitScraper import TanitScraper

load_dotenv('db/.env')
bayt_collection = os.environ['Bayt_collection']
Tanit_collection = os.environ['Tanit_collection']
start_time = time.time()


async def main() -> None:
    """main entry point"""
    tanit_scraper = TanitScraper(Tanit_cfg)
    bayt_scraper = BaytScraper(bayt_cfg)
    results = await asyncio.gather(bayt_scraper.run(), tanit_scraper.run())

    async with Mongo() as mongo:
        await asyncio.gather(*(mongo.insert_job(job, bayt_collection) for job in results[0]),*(mongo.insert_job(job, Tanit_collection) for job in results[1]))




asyncio.run(main())

print(f'{time.time() - start_time} Elapsed')


