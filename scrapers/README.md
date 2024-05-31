## Modules

### 1. `BaseScraper.py`
This is the base class for all scrapers. It provides the structure and common functionalities required by the specific scrapers (`BaytScraper` and `TanitScraper`).

#### Key Components
- **Initialization (`__init__`)**: Initializes the scraper with configuration settings, an HTTP session, and a throttler for rate limiting.
- **Timeout Check (`check_timeout`)**: Checks for HTTP response status to identify and handle request timeouts.
- **Fetch Job Postings (`fetch_job_postings`)**: Abstract method to fetch URLs of individual job postings from a base URL. This method should be overridden by subclasses.
- **Parse Job Posting (`parse_job_posting`)**: Abstract method to extract job information from a job posting URL. This method should be overridden by subclasses.
- **Run (`run`)**: Main method to run the scraper. It fetches base URLs, creates tasks to fetch job postings, and manages worker tasks.
- **Worker (`_worker`)**: Implements a worker pattern for processing job postings asynchronously.

### 2. `BaytScraper.py`
This module extends `BaseScraper` to scrape job postings from the Bayt website.

### 3. `TanitScraper.py`
This module extends `BaseScraper` to scrape job postings from the Tanit website.

## High-Level Workflow

1. **Initialization**: Each scraper is initialized with configuration settings, an HTTP session, and optionally, a throttler for rate limiting.
2. **Fetching Base URLs**: The `run` method of the base scraper fetches base URLs of job listings.
3. **Fetching Job Postings**: For each base URL, the `fetch_job_postings` method is called to retrieve URLs of individual job postings.
4. **Parsing Job Postings**: Each job posting URL is processed by the `parse_job_posting` method to extract relevant job details.

## Configuration

The configuration settings for each scraper include:
- **Base URLs**: List of URLs to start scraping job postings.
- **Selectors**: HTML selectors for extracting job details.
- **Throttling**: Settings for rate limiting to avoid being blocked by the website.

## Usage

To use a scraper, instantiate it with the necessary configuration and call the `run` method. Below is an example that demonstrates how to run the scrapers.
It should be noted that the `run` method is asynchronous. It must be called within an `asyncio` event loop.

```python
from BaytScraper import BaytScraper
from TanitScraper import TanitScraper

from config.Tanit_config import Tanit_cfg
from config.bayt_config import bayt_cfg

bayt_scraper = BaytScraper(bayt_cfg)
bayt_jobs = await bayt_scraper.run()

tanit_scraper = TanitScraper(Tanit_cfg)
tanit_jobs = await tanit_scraper.run()
