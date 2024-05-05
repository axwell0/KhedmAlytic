import json
from aiohttp import ClientSession, ServerTimeoutError, ClientResponse
from asyncio import Queue
from throttler import Throttler, Timer
import asyncio

class BaseScraper:

    def __init__(self, config, throttler: Throttler = None):
        self._config = config
        self._session = ClientSession()
        self._base_urls = []
        self._postings = Queue()
        self.jobs = []
        if throttler:
            self._throttler = throttler

    def check_timeout(self, response: ClientResponse) -> None:
        if response.status in range(400, 600):
            raise ServerTimeoutError('Request Timeout')

    async def fetch_job_postings(self, url: str):
        """Fetch the URLs of individual job postings from a single base URL."""
        pass

    async def parse_job_posting(self, url: str):
        """takes the job posting URL and extracts all relevant information about the job"""
        pass

    async def run(self, max_workers="max"):
        """Runs scraper"""

        if max_workers == "max":
            max_workers = self._config.MAX_WORKERS

        await self._fetch_base_urls()

        async with asyncio.TaskGroup() as group:
            for url in self._base_urls:
                group.create_task(self.fetch_job_postings(url))

        worker_tasks = []
        for i in range(max_workers):
            worker_tasks.append(asyncio.create_task(self._worker(i)))

        await self._postings.join()
        self.save_jobs(self._config.FILE_PATH, self.jobs)

        await self._session.close()
        return self.jobs

    async def _worker(self, worker_id: int) -> None:
        async with self._throttler:
            while True:

                timer = Timer(f'worker {worker_id}', verbose=False)
                with timer:
                    item = await self._postings.get()
                    job_listing = await self.parse_job_posting(item)
                    self.jobs.append(job_listing)
                    self._postings.task_done()

    def save_jobs(self, path, jobs: list) -> None:
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


