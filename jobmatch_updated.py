import time
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("LINKEDIN_JOB_SEARCH_RAPIDAPI_KEY") # https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/playground

def job_search(input: str):
    # print(f"Tool input: {input}") # for debugging
    job_query = input.strip() # Example: "developer jobs in chicago"

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": job_query,
        "page": "1",
        "num_pages": "1",
        "country": "us",
        "date_posted": "all"
    }

    response = requests.get(url, headers=headers, params=params)


    if response.status_code == 200:
        data = response.json()
        jobs = data.get("data", [])[:3]  # show top 3 jobs

        if not jobs:
            return "No jobs found."

        results = []
        for job in jobs:
            title = job.get("job_title", "N/A")
            company = job.get("employer_name", "N/A")
            location = job.get("job_location", "N/A")
            link = job.get("job_apply_link", "N/A")
            posted = job.get("job_posted_human_readable", "")
            results.append(f"{title} at {company} ({location}) — Posted {posted}\n{link}")

        return "\n\n".join(results)

    elif response.status_code == 429:
        time.sleep(2)
        return "Rate limit hit."
    else:
        time.sleep(2)
        return f"API Error: {response.status_code}"

# Define LangChain tool
job_search_tool = Tool(
    name="job_search",
    func=job_search,
    description="Use this tool to search for jobs. Input should be a job title or keyword like 'data analyst in Seattle' (include location only when the user mentioned it), summarizing from the user's query.",
    return_direct = True
)

llm = OpenAI(base_url="https://openai.vocareum.com/v1", api_key=os.getenv("SI568_OPENAI_API_KEY"), temperature=0.2)


agent = initialize_agent(
    tools=[job_search_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

if __name__ == "__main__":
    job_query = input("I'm looking for job listings for: ")

    user_prompt = f"I'm looking for job listings for {job_query}. Use the job_search tool."

    response = agent.run(user_prompt)
    print(response)

