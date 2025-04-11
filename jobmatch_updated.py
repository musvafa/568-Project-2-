import time

from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("LINKEDIN_JOB_SEARCH_RAPIDAPI_KEY") # https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api/playground

def job_search(input: str):
    job_title = input.strip()
    location = "United States"

    url = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-1h"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "linkedin-job-search-api.p.rapidapi.com"
    }
    params = {
        "offset": "0",
        "title_filter": f"\"{job_title}\"",
        "location_filter": f"\"{location}\""
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("data", [])[:3]  # safer key assumption than "title"

        if not jobs:
            return "No jobs found."

        formatted_jobs = []
        for job in jobs:
            title = job.get("title", "Unknown Title")
            company = job.get("company", {}).get("name", "Unknown Company")
            location = job.get("location", "Unknown Location")
            formatted_jobs.append(f"📌 {title} at {company} ({location})")

        return "\n\n".join(formatted_jobs)

    elif response.status_code == 429:
        time.sleep(2)
        return "Rate limit hit. Please try again shortly."
    else:
        time.sleep(2)
        return f"API Error: {response.status_code}"


# Define LangChain tool
job_search_tool = Tool(
    name="job_search",
    func=job_search,
    description="Use this tool to search for jobs. Input should be a job title or keyword as a string."
)

llm = OpenAI(base_url="https://openai.vocareum.com/v1", api_key=os.getenv("SI568_OPENAI_API_KEY"), temperature=0.2)


agent = initialize_agent(
    tools=[job_search_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

if __name__ == "__main__":
    job_query = input("Enter your skills or job title: ")

    user_prompt = f"I'm looking for job listings for '{job_query}'. Use the job_search tool."

    response = agent.run(user_prompt)
    print(response)

jobmatch_1.py
Displaying jobmatch_1.py.
