from dataclasses import dataclass
from datetime import datetime

import pymongo


@dataclass
class bayt_cfg:
    ITEMS_PER_PAGE: int = 20
    BASE_URL: str = f"https://www.bayt.com/en/tunisia/jobs/?page="
    FILE_PATH: str = f'data/Bayt/Bayt_jobs_{datetime.now().strftime("%d, %B, %Y")}.json'

    job_count = {'name': 'b', "class_": "m20b-m"}

    job_posting_item = {"name": "a", "attrs": {'data-js-aid': 'jobID'}}
    title = {"name": "h1", 'attrs': {"id": "job_title"}}
    employer = {"name": "a", "class_": "is-black t-bold"}
    script = {'name': "script", 'attrs': {'type': "application/ld+json"}}
    datePosted = "datePosted"
    ValidThrough = "validThrough"
    details_item = {"name": "dl", "class_": "dlist is-spaced is-fitted t-small"}
    job_details_item = {'name': 'div', 'class_': 'card u-shadow'}

    unique_index = [("Title", pymongo.ASCENDING),
                    ("Employer", pymongo.ASCENDING),
                    ("posted_on", pymongo.ASCENDING)]

    MAX_WORKERS: int = 15

    RATE_LIMIT: int = 999 #Bayt is robust to frequent requests
