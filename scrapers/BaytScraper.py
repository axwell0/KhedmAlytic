import asyncio
import json
import math

import aiohttp
import bs4
from aiohttp import ServerTimeoutError
from tenacity import retry, retry_if_exception_type
from throttler import Throttler
from scrapers.BaseScraper import BaseScraper


class BaytScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config, Throttler(999))

    async def _fetch_base_urls(self) -> None:
        """Fetches URLs of pages containing listings and updates _base_urls"""
        async with self._session.get(self._config.BASE_URL + "1") as response:
            self.check_timeout(response)

            soup = bs4.BeautifulSoup(await response.text(), 'lxml')
            count_element = soup.find(**self._config.job_count).string
            n_jobs = int(count_element.strip().split()[0])
            print(f'{n_jobs} jobs found')
            self._base_urls = [f"{self._config.BASE_URL}{i}" for i in
                               range(1, math.ceil(n_jobs / self._config.ITEMS_PER_PAGE) + 1)]






    @retry(retry=retry_if_exception_type(ServerTimeoutError))
    async def fetch_job_postings(self, url: str) -> None:
        """Fetch the URLs of individual job postings from a single base URL."""
        async with self._session.get(url) as response:
            self.check_timeout(response)

            soup = bs4.BeautifulSoup(await response.text(), 'lxml')
            for job_posting in soup.find_all(**self._config.job_posting_item):
                self._postings.put_nowait(f"https://www.bayt.com{job_posting.get('href')}")

    async def parse_description(self, soup: bs4.BeautifulSoup) -> dict[str]:
        """ TO BE WORKED ON!!!!!
        Method specific to Bayt. Scrapes description of a job_posting
        @rtype: dict[str]
        @param soup:
        @return:
        """

        dic = {}
        paragraphs = soup.find_all('p')
        current_key = ""
        for i in range(len(paragraphs)):
            if any(child.name != 'br' for child in paragraphs[i].find_all(recursive=False)):
                current_key = paragraphs[i].get_text(strip=True)
                continue
            if not (paragraphs[i].find('br')):
                dic[current_key] = dic.get(current_key, '') + ' ' + paragraphs[i].string.strip()
        return dic

    @retry(retry=(retry_if_exception_type(AttributeError) | retry_if_exception_type(
        aiohttp.ClientConnectorError) | retry_if_exception_type(ServerTimeoutError) | retry_if_exception_type(
        aiohttp.ServerDisconnectedError)))
    async def parse_job_posting(self, url: str) -> dict[str, str | None | dict]:
        """takes the job posting URL and extracts all relevant information about the job"""
        async with self._session.get(url) as response:
            self.check_timeout(response)
            job_page_content = await response.text()
            job_page_soup = bs4.BeautifulSoup(job_page_content, 'lxml')
            try:
                title = job_page_soup.find(**self._config.title).string.strip()
                employer = job_page_soup.find(**self._config.employer).string.strip()
                script_json = json.loads(job_page_soup.find(**self._config.script).string)
                posted_on = script_json[self._config.datePosted]
                valid_through = script_json[self._config.ValidThrough]
                list_item = job_page_soup.find(**self._config.details_item)
                job_details_item = job_page_soup.find_all(**self._config.job_details_item)[1]
                try:
                    description = await self.parse_description(job_details_item)
                except:
                    description = "unavailable"

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
