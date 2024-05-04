import asyncio
import math
import os
import time
from dotenv import load_dotenv
import aiohttp
import asyncio

from config.bayt_config import bayt_cfg
from config.Tanit_config import Tanit_cfg

from db.database import Mongo
from scrapers.BaytScraper import BaytScraper
from scrapers.TanitScraper import TanitScraper


load_dotenv('db/.env')
bayt_collection = os.environ['Bayt_collection']
start_time = time.time()

# async def upload_json_files(folder_path,mongo : Mongo):
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".json"):
#             file_path = os.path.join(folder_path, filename)
#             with open(file_path, "rb") as file:
#                 data = json.load(file)
#                 await mongo.update_collection(data,'Bayt_jobs')

#


# async def main():
#     async with aiohttp.ClientSession() as session:
#         async with session.get('https://www.tanitjobs.com/jobs/',headers=headers) as resp:
#             print(await resp.text())
#             print(resp.status)

# @request( run_async=True, output=None)
# def scrape_job_links(request: AntiDetectRequests, data):
#
#     next_page = True
#     soup = request.bs4(data)
#     items = soup.select('article.listing-item')
#     print(data)
#     print()
#     return [item.find('a',class_="link").text.strip() for item in items]
#
# async def main():
#     for i in range(1, 227):
#         scrape_job_links(data=f"https://www.tanitjobs.com/jobs/?action=search&page={i}")

async def main() -> None:
    x = TanitScraper(Tanit_cfg)
    # await x.fetch_listings_pages()
    await x.parse_job_posting('https://www.tanitjobs.com/job/1535269/customer-support-team-leader/?backPage=1&searchID=1714731665.1599')




asyncio.run(main())

print(f'{time.time() - start_time} Elapsed')
# async def main() -> None:
#     bayt_scraper = BaytScraper(bayt_cfg)
#     await bayt_scraper.run()
#     bayt_jobs = bayt_scraper.get_jobs()
#     async with Mongo() as mongodb:
#         await asyncio.gather(*(mongodb.insert_job(job,bayt_collection) for job in bayt_jobs))
#
# asyncio.run(main())
# print(f'{time.time() - start_time} Elapsed')
# await collection.create_index([("Title", pymongo.ASCENDING),
#                                ("Employer", pymongo.ASCENDING),
#                                ("posted_on", pymongo.ASCENDING)],
#                               unique=True)