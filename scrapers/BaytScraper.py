import asyncio
import json
import math

import aiohttp
import bs4
import motor.motor_asyncio
from aiohttp import ServerTimeoutError
from aiohttp.client_exceptions import ClientPayloadError
from tenacity import retry, retry_if_exception_type
from throttler import Throttler
from scrapers.BaseScraper import BaseScraper
from aiohttp_client_cache import CachedSession



class BaytScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config, Throttler(config.RATE_LIMIT))

    async def _fetch_base_urls(self) -> None:
        """Fetches URLs of pages containing listings and updates _base_urls"""

        async with self._session.get(self._config.BASE_URL + "1") as response:
            self.check_timeout(response)

            soup = bs4.BeautifulSoup(await response.text(), 'lxml')
            count_element = soup.find(**self._config.job_count).string
            n_jobs = int(count_element.strip().split()[0])
            print(f'{n_jobs} Bayt jobs found')
            self._base_urls = [f"{self._config.BASE_URL}{i}" for i in
                               range(1, math.ceil(n_jobs / self._config.ITEMS_PER_PAGE) + 1)]


    @retry(retry=retry_if_exception_type(ServerTimeoutError))
    async def fetch_job_postings(self, url: str, collection: motor.motor_asyncio.AsyncIOMotorCollection) -> None:
        """Fetch the URLs of individual job postings from a single base URL."""
        async with self._session.get(url) as response:
            self.check_timeout(response)

            soup = bs4.BeautifulSoup(await response.text(), 'lxml')
            for job_posting in soup.find_all(**self._config.job_posting_item):
                url = f"https://www.bayt.com{job_posting.get('href')}"
                if await collection.find_one({"job_link": url}) is None:
                    self._postings.put_nowait(url)
                else:
                    print(f'BAYT: {url} already exists in the DB')

    @retry(retry=(retry_if_exception_type(AttributeError) | retry_if_exception_type(
        aiohttp.ClientConnectorError) | retry_if_exception_type(ServerTimeoutError) | retry_if_exception_type(
        aiohttp.ServerDisconnectedError) | retry_if_exception_type(ClientPayloadError)))
    async def parse_job_posting(self, url: str) -> dict[str, str | None | dict]:
        """takes the job posting URL and extracts all relevant information about the job"""
        async with self._session.get(url) as response:
            self.check_timeout(response)
            job_page_content = await response.text()
            job_page_soup = bs4.BeautifulSoup(job_page_content, 'lxml')
            if not(job_page_soup.find('div.t-danger')):
                try:
                    title = job_page_soup.find(**self._config.title).string.strip()
                    employer = job_page_soup.find(**self._config.employer).string.strip()
                    script_json = json.loads(job_page_soup.find(**self._config.script).string)
                    posted_on = script_json[self._config.datePosted]
                    valid_through = script_json[self._config.ValidThrough]
                    list_item = job_page_soup.find(**self._config.details_item)
                    job_details_item = job_page_soup.find_all(**self._config.job_details_item)[1]
                    description = job_details_item.find('div',class_="t-break").get_text(separator="|")

                    job_dictionary = \
                    {
                        "Title": title,
                        "Job Location": None,
                        "Employer": employer,
                        "Employment Type": None,
                        "Job Role": None,
                        "Company Type": None,
                        "Company Industry": None,
                        "Monthly Salary Range": None,
                        "Number of Vacancies": None,
                        "Description": description,
                        "posted_on": posted_on,
                        "Valid_Through": valid_through,
                        "job_link": url
                    }
                    for item in list_item.find_all('div'):
                        job_dictionary[item.dt.string.strip()] = item.dd.string.strip()
                    print(f'Bayt {job_dictionary}')
                    return job_dictionary

                except:
                    print(f'Error with {url}')
                    print(f'{job_page_content}')
