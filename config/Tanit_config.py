from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import pymongo


@dataclass
class Tanit_cfg:
    BASE_URL: str = "https://www.tanitjobs.com/jobs/?action=search&page="
    FILE_PATH: str = f'data/Tanit/Tanit_jobs_{datetime.now().strftime("%d, %B, %Y")}.json'

    last_page_item: str = 'div#list_nav > a[href*="page="]'

    job_offer_item: str = 'div.detail-offre'
    job_details_item: str = 'div.infos_job_details'
    job_listing_item: str = "article"
    heading_details = {"name": "div", "class_": "col-md-4"}
    body_details: str = 'div.details-body__content.content-text'

    title: str = "div.media-heading.listing-item__title a.link"
    employer: str = "span.listing-item__info--item.listing-item__info--item-company"
    zone: str = "span.listing-item__info--item.listing-item__info--item-location"
    posting_date: str = "div.listing-item__date"

    """Rate limiting (to avoid overloading the server)"""
    RATE_LIMIT: int = 5  # 5 requests per second
    MAX_WORKERS: int = 10
