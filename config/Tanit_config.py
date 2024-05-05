from dataclasses import dataclass
from datetime import datetime

import pymongo


@dataclass
class Tanit_cfg:
    BASE_URL: str = "https://www.tanitjobs.com/jobs/?action=search&page="
    FILE_PATH: str = f'data/Tanit/Tanit_jobs_{datetime.now().strftime("%d, %B, %Y")}.json'

    last_page_item: str = 'div#list_nav > a[href*="page="]'
    job_listing_item = "article"
    title: str = "div.media-heading.listing-item__title a.link"
    employer: str = "span.listing-item__info--item.listing-item__info--item-company"
    zone: str = "span.listing-item__info--item.listing-item__info--item-location"
    posting_date: str = "div.listing-item__date"
