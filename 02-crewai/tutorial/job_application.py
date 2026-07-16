import os
import warnings

from dotenv import load_dotenv, find_dotenv

# 1. LOAD ENV VARS AND PATCH THE SYSTEM FIRST!
load_dotenv(find_dotenv()) 
uni_key = os.getenv("UNIVERSITY_API_KEY", "dummy-key")
uni_url = os.getenv("UNIVERSITY_BASE_URL")

# Force the underlying OpenAI SDK to route to your university BEFORE CrewAI loads
os.environ["OPENAI_API_KEY"] = uni_key
os.environ["OPENAI_API_BASE"] = uni_url
os.environ["OPENAI_BASE_URL"] = uni_url # Newer versions of the SDK prefer this variable

# Patch ChromaDB/HuggingFace for the Searching Brain
os.environ["CHROMA_HUGGINGFACE_API_KEY"] = "dummy-key"
os.environ["HUGGINGFACE_API_KEY"] = "dummy-key" # Adding this just to be safe!

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool, ScrapeWebsiteTool, MDXSearchTool
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ddgs import DDGS


import os
import shutil
from pathlib import Path

# The sneaky places Embedchain and Chroma like to hide their caches globally
hiding_spots = [
    Path.home() / ".embedchain",
    Path.home() / ".chroma",
    Path.cwd() / "db",
    Path.cwd() / ".chroma",
]

for spot in hiding_spots:
    if spot.exists() and spot.is_dir():
        print(f"⚠️ FOUND CACHE AND DELETING: {spot}")
        shutil.rmtree(spot)

# Suppress warnings 
warnings.filterwarnings('ignore')

# Tell crewAI exactly which model to target on your university server
uni_llm = LLM(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("UNIVERSITY_API_KEY"),
    base_url=os.getenv("UNIVERSITY_BASE_URL")
)

# custom search tool based on duckduckgo
class SearchToolInput(BaseModel):
    """Input schema for the Internet Search Tool."""
    search_query: str = Field(
        ...,
        description=(
            "The search query. CRITICAL: You must search like a human. " \
            "Use broad, simple keywords (e.g., 'San Francisco large conference venues'). "
            "Do NOT use exact-match quotes."
        )
    )

class SearchTool(BaseTool):
    name: str = "internet_search"
    description: str = (
        "Search the live internet for up-to-date company facts and news. "
        "Use simple keywords like 'DeepLearning AI news'."
    )
    args_schema: type[BaseModel] = SearchToolInput

    def _run(self, search_query: str) -> str:
        raw_results = list(DDGS().text(search_query, max_results=3))

        if not raw_results:
            return (
                f"Action Failed: No internet searches found for the query '{search_query}'. "
                "CRITICAL: You must try again using completely different, simpler, and broader keywords. "
                "REMOVE all exact-match quotes."
            )

        clean_text = "Here are the search results:\n\n"
        for result in raw_results:
            clean_text += f"Title: {result.get('title')}\n"
            clean_text += f"URL: {result.get('href')}\n"
            clean_text += f"Information: {result.get('body')}\n\n"

        return clean_text
    

search_tool = SearchTool()
scrape_tool = ScrapeWebsiteTool()
read_resume = FileReadTool(file_path='./fake_resume.md')
# semantic_search_resume = MDXSearchTool(
#     mdx='./resume.md', 
#     config={
#         "llm": {
#             "provider": "openai", 
#             "config": {
#                 "model": "gpt-oss-120b", 
#                 "api_key": uni_key,
#                 "base_url": uni_url,
#             }
#         },
#         "embedding_model": {
#             "provider": "huggingface",
#             "config": {
#                 "model": "BAAI/bge-small-en-v1.5"
#             }
#         },
#         # THE SILVER BULLET: Swap to Qdrant to completely bypass ChromaDB
#         "vectordb": {
#             "provider": "qdrant",
#             "config": {} 
#         }
#     }
# )


# Agents

researcher = Agent(
    role="Tech Job Researcher",
    goal="Make sure to do amazing analysis on "
         "job posting to help job applications.",
    backstory=(
        "As a Job Researcher, your prowess in "
        "navigating and extracting critical "
        "information from job postings is unmatched. "
        "Your skills help pinpoint the necessary "
        "qualifications and skills sought "
        "by employers, forming the foundation for "
        "effective application tailoring."
    ),
    tools = [scrape_tool, search_tool],
    verbose=True,
    llm=uni_llm,
)

profiler = Agent(
    role="Peronsal Profiler for Engineers",
    goal="Do incredible research on job applicants "
    "to help them stand out in the job market.",
    backstory=(
        "Equipped with analytical prowess, you dissect "
        "and synthesize information "
        "from diverse sources to craft comprehensive "
        "personal and professional profiles, laying the "
        "groundwork for personalized resume enhancements."
    ),
    tools = [scrape_tool, search_tool, read_resume], #, semantic_search_resume],
    verbose=True,
    llm=uni_llm,
)

resume_strategist = Agent(
    role="Resume Strategist for Engineers",
    goal="Final all the best ways to make a "
         "resume stand out in the job market.",
    backstory=(
        "With a strategic mind and an eye for detail, you "
        "excel at refining resumes to highlight the most "
        "relevant skills and experiences, ensuring they "
        "resonate perfectly with the job's requirements."
    ),
    tools=[scrape_tool, search_tool, read_resume], #, semantic_search_resume],
    verbose=True,
    llm=uni_llm,
)

interview_preparer = Agent(
    role="Engineering Interview Preparer",
    goal="Create interview questions and talking points "
         "based on the resume and job requirements.",
    backstory=(
        "Your role is cruicial in anticipating the dynamics of "
        "interviews. With your ability to formulate key questions "
        "and talking points, you prepare candidates for success, "
        "ensuring they can confidently address all aspects of the "
        "job they are applying for."
    ),
    tools=[scrape_tool, search_tool, read_resume], #, semantic_search_resume],
    verbose=True,
    llm=uni_llm,
)


# Tasks

# Task for Researcher agent: extract job requirements.
research_task = Task(
    description=(
        "Analyze the job posting URL provided ({job_posting_url}) "
        "to extract key skills, experiences, and qualifications "
        "required. Use the tools to gather content and identify "
        "and categorize the requirements."
    ),
    expected_output=(
        "A structured list of job requirements, including necessary "
        "skills, qualifications, and experiences."
    ),
    agent=researcher,
    async_execution=True,
)

# Task for Profiler agent: compile comprehensive profile
profile_task = Task(
    description=(
        "Compile a detailed personal and professional profile "
        "using the GitHub ({github_url}) URLs, and personal write-up "
        "({personal_writeup}). Utilize tools to extract and "
        "synthesize information from these sources."
    ),
    expected_output=(
        "A comprehensive profile document that includes skills "
        "project experiences, contributions, interests, and "
        "communication style."
    ),
    agent=profiler,
    async_execution=True,
)

# Task for Resume Strategist agent: Align resume with job requirements
resume_strategy_task = Task(
    description=(
        "Using the profile and job requirements obtained from "
        "previous tasks, tailor the resume to highlight the most "
        "relevant areas. Employ tools to adjust and enhance the "
        "resume content. Make sure this is the best resume even but "
        "don't make up any information. Update every section, "
        "including the initial summary, work experience, skills, "
        "and education. All to better reflect the candidate\'s "
        "abilities and how it matches the job posting"
    ),
    expected_output=(
        "An updated resume that effectively highlights the candidate\'s "
        "qualifications and experiences relevant to the job."
    ),
    output_file="tailored_resume.md",
    context=[research_task, profile_task], # we provide the list of tasks as context, this task now takes into account the output of such tasks in the list.
    agent=resume_strategist,
)

# Task for Interview Preparer agent: develop interview materials
interview_preparation_task = Task(
    description=(
        "Create a set of potential interview questions and talking "
        "points based on the tailored resume and job requirements. "
        "Utilize tools to generate relevant questions and discussion "
        "points. Make sure to use these question and talking points to "
        "help the candidate highlight the main points of the resume "
        "and how it matches the job posting."
    ),
    expected_output=(
        "A document containing key questions and talking points "
        "that the candidate should prepare for the initial interview."
    ),
    output_file="interview_materials.md",
    context=[research_task, profile_task, resume_strategy_task],
    agent=interview_preparer
)


def job_application_crew(job_application_inputs):

    job_application_crew = Crew(
        agents=[researcher, profiler, resume_strategist, interview_preparer],
        tasks=[research_task, profile_task, resume_strategy_task, interview_preparation_task],
        verbose=True,
    )

    result = job_application_crew.kickoff(inputs=job_application_inputs)

    return result

if __name__ == "__main__":
    job_application_inputs = {
        'job_posting_url': 'https://jobs.lever.co/AIFund/33bd1d6c-5091-42f8-99c0-6e97292782be',
        'github_url': 'https://github.com/joaomdmoura',
        'personal_writeup': """Noah is an accomplished Software 
        Engineering Leader with 18 years of experience, specializing in
        managing remote and in-office teams, and expert in multiple
        programming languages and frameworks. He holds an MBA and a strong
        background in AI and data science. Noah has successfully led
        major tech initiatives and startups, proving his ability to drive
        innovation and growth in the tech industry. Ideal for leadership
        roles that require a strategic and innovative approach."""
    }

    final_output = job_application_crew(job_application_inputs)

    print("\n" + "="*40)
    print("OUTPUT")
    print("="*40 + "\n")
    print(final_output)

    # # Save to markdown file
    # with open("tailored_resume.md", "w", encoding="utf-8") as file:
    #     file.write(str(final_output))

    # print("\n Report saved to tailored_resume.md")

