import json
from aiohttp import ClientSession, ServerTimeoutError, ClientResponse
from asyncio import Queue


class BaseScraper:

    def __init__(self, config):
        self._config = config
        self._session = ClientSession()
        self._base_urls = []
        self._postings = Queue()
        self.jobs = []

    def check_timeout(self,response: ClientResponse) -> None:
        if response.status in range(400, 500):
            raise ServerTimeoutError('Request Timeout')
    async def fetch_job_postings(self, url: str, session: ClientSession):
        """Fetch the URLs of individual job postings from a single base URL."""
        pass

    async def parse_job_posting(self, url: str, session: ClientSession):
        """takes the job posting URL and extracts all relevant information about the job"""
        pass

    def get_jobs(self):
        return self.jobs


    async def _worker(self, session):
        while not self._postings.empty():
            url = self._postings.get_nowait()
            job_listing = await self.parse_job_posting(url, session)
            self.jobs.append(job_listing)
            self._postings.task_done()

    def save_jobs(self,path, jobs: list):
        with open(path, "w", encoding='utf-8') as file:
            file.write('[')
            first = True
            for job in jobs:

                if not first:
                    file.write(',')
                else:
                    first = False
                json.dump(job, file, ensure_ascii=False, indent=4)

            file.write(']')






