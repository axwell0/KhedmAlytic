import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt

class RetryError(Exception):
    def __init__(self, message="Maximum retries reached"):
        super().__init__(message)


system = "You are a helpful and obedient assistant."
human = """classify the industry/line of each job posting. ONLY USE ONE OF THE FOLLOWING CATEGORIES. DO NOT COME UP WITH ANOTHER CATEGORY: 
            Tradesperson,
            Engineering (THIS ONLY INCLUDES ALL COLLEGE-LEVEL Engineering disciplines except software),
            Software/IT,
            Administration/Management,
            Finance,
            Accounting
            Sales,
            Marketing
            Healthcare,
            Manufacturing,
            Customer Service,
            Arts & Design. write in this format: title:classification in a new line.DO NOT SKIP ANY JOB. The job posting titles are {batch}"""
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])



@retry(wait=wait_fixed(1), stop=stop_after_attempt(5), retry=retry_if_exception_type(RetryError))
async def label_industry(batch: list, api_key: str, classifications: dict):
    try:
        chat = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama3-8b-8192")
        chain = prompt | chat
        chat_completion = await chain.ainvoke({"batch": ','.join(batch)})
        response = chat_completion.content
        response_pre = response[response.find('\n\n') + 2:].replace('\n\n', '\n')
        jobs = response_pre.split('\n')

        for item in jobs:
            if item.find(':'):
                key = item[:item.find(':')]
                value = item[item.find(':') + 1:].strip()
                classifications[key] = value
    except:
        raise RetryError('APIs Timeout')


def get_batch(series: pd.Series, batch_size: int = 100):
    total_titles = len(series)
    for start in range(0, total_titles, batch_size):
        end = start + batch_size
        batch_titles = series[start:end]
        yield list(batch_titles)


async def get_job_industries(df: pd.DataFrame, GROQ_API_KEY:str) -> dict:
    api_keys = GROQ_API_KEY
    classifications = {}
    unique_titles = df['Title'].unique()
    batches = list(get_batch(unique_titles))
    for i, batch in enumerate(batches):
        api_key = api_keys[i % len(api_keys)]
        await label_industry(batch, api_key, classifications)
    return classifications
