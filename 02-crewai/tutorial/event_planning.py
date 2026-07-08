import os
import warnings
from crewai import Agent, Task, Crew, LLM
from crewai_tools import ScrapeWebsiteTool
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ddgs import DDGS
from dotenv import load_dotenv, find_dotenv

# Suppress warnings 
warnings.filterwarnings('ignore')

# Search for your .env file in this folder and any parent folders
load_dotenv(find_dotenv()) 

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
        raw_results = DDGS().text(search_query, max_results=3)

        clean_text = "Here are the search results:\n\n"
        for result in raw_results:
            clean_text += f"Title: {result.get('title')}\n"
            clean_text += f"URL: {result.get('href')}\n"
            clean_text += f"Information: {result.get('body')}\n\n"

        return clean_text
    
search_tool = SearchTool()
scrape_tool = ScrapeWebsiteTool()


# Agents

# Agent 1 - Venue Coordinator
venue_coordinator = Agent(
    role="Venue Coordinator",
    goal="Identify and book an appropriate venue "
         "based on event requirements",
    backstory=(
        "With a keen sense of space and "
        "understanding of event logistics, "
        "you excel at finding and securing "
        "the perfect venue that fits the event's theme, "
        "size, and budget constraints."
    ),
    tools=[search_tool, scrape_tool],
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)

# Agent 2 - Logistics Manager
logistics_manager = Agent(
    role="Logistics Manager",
    goal=(
        "Manage all logistics for the event "
        "including catering and equipment."
    ),
    backstory=(
        "Organized and detail-oriented, "
        "you ensure that every logistical aspect of the event "
        "from catering to equipment setup "
        "is flawlessly executed to create a seamless experience."
    ),
    tools=[search_tool, scrape_tool],
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)

# Agent 3 - Marketing and Communications Agent
marketing_communications_agent = Agent(
    role="Marketing and Communications Agent",
    goal="Effectively market the event and "
         "communicate with participants",
    backstory=(
        "Creative and communicative, "
        "you craft compelling messages and "
        "engage with potential attendees "
        "to maximize event exposure and participation."
    ),
    tools=[search_tool, scrape_tool],
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)


# Create Venue Pydantic Object

# Define a pydantic model for venue details
# (demonstrating output as pydantic)
class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str

venue_task = Task(
    description="Find a venue in {event_city} "
                "that meets criteria for {event_topic}. "
                "If you want to read more about a venue, pass the URL "
                "from your search results into the scrape_tool.",
    expected_output="All the details of a specifically chosen "
                    "venue you found to accommodate the event.",
    # human_input=True,
    output_json=VenueDetails,
    output_file="venue_details.json",
    agent=venue_coordinator
)

logistics_task = Task(
    description="Coordinate catering and "
                "equipment for an event "
                "with {expected_participants} participants "
                "on {tentative_date}.",
    expected_output="Confirmation of all logistics arrangements "
                    "including catering and equipment setup.",
    # human_input=True,
    async_execution=True, # Means that it can run in parallel with tasks which come after it (when we make the crew)
    agent=logistics_manager
)

marketing_task = Task(
    description="Promote the {event_topic} "
                "aiming to engage at least "
                "{expected_participants} potential attendees.",
    expected_output="Report on marketing activities "
                    "and attendee engagement formatted as markdown.",
    async_execution=False,
    output_file="marketing_report.md", # Outputs the report as Markdown a text file
    agent=marketing_communications_agent
)


def main():

    # Create the crew with agent and tasks
    event_management_crew = Crew(
        agents=[venue_coordinator,
                logistics_manager,
                marketing_communications_agent],
        tasks=[venue_task,
               logistics_task,
               marketing_task], # Order of logistics_task and marketing_task is irrelevant since we have async_execution=True
        verbose=True
    )

    event_details = {
        "event_topic": "Tech Innovation Conference",
        "event_description": "A gathering of tech innovators "
                             "and industry leaders "
                             "to explore future technologies.",
        "event_city": "San Francisco",
        "tentative_date": "2026-09-15",
        "expected_participants": 500,
        "budget": 20000,
        "venue_type": "Conference Hall"
    }

    result = event_management_crew.kickoff(inputs=event_details)

    return result

if __name__ == "__main__":
    final_output = main()
    print("\n" + "="*40)
    print("CREW FINISHED! READING FILES...")
    print("="*40 + "\n")

    # Read and print the JSON file
    import json
    try:
        with open('venue_details.json', 'r') as f:
            data = json.load(f)
            print("--- VENUE DETAILS (JSON) ---")
            print(json.dumps(data, indent=4))
    except FileNotFoundError:
        print("venue_details.json was not created.")

    print("\n")

    # Read and print the Markdown file
    try:
        with open('marketing_report.md', 'r') as f:
            markdown_content = f.read()
            print("--- MARKETING REPORT (MD) ---")
            print(markdown_content)
    except FileNotFoundError:
        print("marketing_report.md was not created.")