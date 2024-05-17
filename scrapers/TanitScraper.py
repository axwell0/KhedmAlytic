import asyncio
import re

import motor.motor_asyncio
from unicodedata import normalize
import aiohttp
import bs4
from throttler import Throttler
from aiohttp.client_exceptions import ClientPayloadError
from aiohttp import ServerTimeoutError
from tenacity import retry, retry_if_exception_type
from scrapers.BaseScraper import BaseScraper


class TanitScraper(BaseScraper):

    def __init__(self, config):
        super().__init__(config, Throttler(config.RATE_LIMIT))

    async def fetch_last_listings_page(self) -> int:
        """Returns the number indicating the last base URL page"""

        async with self._session.get(self._config.BASE_URL + "1") as response:
            print(self._config.BASE_URL + "1")
            self.check_timeout(response)
            soup = bs4.BeautifulSoup(await response.text(), 'lxml')

            last_page_link = soup.select_one(self._config.last_page_item)
            n_jobs_element = soup.select_one('h1.search-results__title.col-sm-offset-3.col-xs-offset-0')
            n_jobs = re.search(r'\d+', n_jobs_element.string.strip()).group()
            print(f"{n_jobs} Tanit jobs found")
            last_page = re.search(r'page=(\d+)', last_page_link['href']).group(1)
            assert last_page.isdigit(), f"The string {last_page} cannot be converted to an integer"
            return int(last_page)

    async def _fetch_base_urls(self) -> None:
        """Fetches URLs of pages containing listings and updates _base_urls"""
        last_page = await self.fetch_last_listings_page()
        print(last_page)
        self._base_urls = [f'{self._config.BASE_URL}{i}' for i in range(1, int(last_page) + 1)]

    @retry(retry=retry_if_exception_type(ServerTimeoutError))
    async def fetch_job_postings(self, url: str, collection: motor.motor_asyncio.AsyncIOMotorCollection) -> None:
        async with self._throttler:
            async with self._session.get(url) as response:
                self.check_timeout(response)
                soup = bs4.BeautifulSoup(await response.text(), 'lxml',
                                         parse_only=bs4.SoupStrainer(name=self._config.job_listing_item))
                for listing in soup.find_all(self._config.job_listing_item):
                    """I opted to add dictionaries continaing job title, zone and posting date in _postings here."""
                    url = listing.find("a")["href"]
                    job_info = {
                        "Title": f"{listing.select_one(self._config.title).string.strip()}",
                        "Employer": f'{listing.select_one(self._config.employer).string.strip()}',
                        "Zone": f"{listing.select_one(self._config.zone).string.strip()}",
                        "posting_date": f"{listing.select_one(self._config.posting_date).string.strip()}",
                        "url": f'{url[:url.find("?")]}'
                    }
                    if await collection.find_one({"url": job_info['url']}) is None:
                        self._postings.put_nowait(job_info)
                    else:
                        print(f"TANIT: {job_info['url']} already exists in the DB")

    @retry(retry=(retry_if_exception_type(AttributeError) | retry_if_exception_type(
        aiohttp.ClientConnectorError) | retry_if_exception_type(ServerTimeoutError) | retry_if_exception_type(
        aiohttp.ServerDisconnectedError) | retry_if_exception_type(ClientPayloadError)))
    async def parse_job_posting(self, listing: dict[str]):
        try:
            async with self._throttler:
                async with self._session.get(listing['url']) as response:
                    self.check_timeout(response)
                    soup = bs4.BeautifulSoup(await response.text(), "lxml",
                                             parse_only=bs4.SoupStrainer('div')).select_one(
                        self._config.job_offer_item)
                    job_details_item = soup.select_one(self._config.job_details_item)
                    job_listing = {
                        "Postes vacants": None,
                        "Niveau d'étude": None,
                        "Type d'emploi désiré": None,
                        "Rémunération proposée": None,
                        "Langue": None,
                        "Experience": None,
                        "Genre": None,
                    }
                    for item in job_details_item.find_all(**self._config.heading_details):
                        detail_title = str(item.find('dt').string.strip())
                        detail_content = item.find('dd').string.strip()
                        job_listing[detail_title[:detail_title.find(':')].strip()] = detail_content

                    for title, content in zip(soup.find_all('h3'), soup.select(self._config.body_details)):
                        job_listing[title.string.strip()] = normalize("NFKD",
                                                                      content.get_text(strip=True, separator=""))
                    listing.update(job_listing)
                    print(f'Tanit {listing}')
                    return listing
        except asyncio.TimeoutError:
            print(f'Request Timed out')
