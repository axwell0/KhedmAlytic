# JobScraper

This project is designed for web scraping and data analysis, specifically for the tunisian job market. It is deployed using Streamlit for interactive data visualization and processing.

## Folder Structure


- **<span style="color:yellow;">APIs</span>**: API interaction scripts.
  - **<span style="color:green;">geo_api.py</span>**: Geolocation API integration.
  - **<span style="color:green;">industry_classification.py</span>**: Industry classification logic using Llama3 API.

- **<span style="color:yellow;">config</span>**: Configuration settings for scrapers.

- **<span style="color:yellow;">data</span>**: Directory for storing raw data files.

- **<span style="color:yellow;">database</span>**: Database interaction scripts.
  - **<span style="color:green;">database.py</span>**: Wrapper around motor (MongoDB).

- **<span style="color:yellow;">scrapers</span>**: Web scraping scripts.
  - **<span style="color:green;">BaseScraper.py</span>**: Base scraper class with common functionalities.
  - **<span style="color:green;">BaytScraper.py</span>**: Specific scraper for Bayt.com.
  - **<span style="color:green;">TanitScraper.py</span>**: Specific scraper for TanitJobs.

- **<span style="color:yellow;">streamlit_app</span>**: Streamlit app components for the web interface.
  - **<span style="color:green;">introduction.py</span>**: Introductory page of the Streamlit app.
  - **<span style="color:green;">processing.py</span>**: Data processing scripts for the app.
  - **<span style="color:green;">visualization.py</span>**: Data visualization components for the app.

- **<span style="color:yellow;">utils</span>**: Utility functions.
  - **<span style="color:green;">utils.py</span>**: Helper functions used across the project.

- **<span style="color:yellow;">.env</span>**: Environment variables file.
- **<span style="color:yellow;">app.py</span>**: Streamlit application script for running the project.
- **<span style="color:yellow;">scrape.py</span>**: Script to initiate the web scraping process.

