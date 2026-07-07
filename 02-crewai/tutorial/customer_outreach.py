import os
import warnings
from crewai import Agent, Task, Crew, LLM
from crewai_tools import DirectoryReadTool, FileReadTool, SerperDevTool
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

# Agents

sales_rep_agent = Agent(
    role="Sales Representative",
    goal="Identify high-value leads that match "
         "our ideal customer profile",
    backstory=(
        "As a part of the dynamic sales team at CrewAI, "
        "your mission is to scour "
        "the digital landscape for potential leads. "
        "Armed with cutting-edge tools "
        "and a strategic mindset, you analyze data, "
        "trends, and interactions to "
        "unearth opportunities that others might overlook. "
        "Your work is crucial in paving the way "
        "for meaningful engagements and driving the company's growth."
    ),
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)

lead_sales_rep_agent = Agent(
    role="Lead Sales Representative",
    goal="Nurture leads with personalized, compelling communications",
    backstory=(
        "Within the vibrant ecosystem of CrewAI's sales department, "
        "you stand out as the bridge between potential clients "
        "and the solutions they need."
        "By creating engaging, personalized messages, "
        "you not only inform leads about our offerings "
        "but also make them feel seen and heard."
        "Your role is pivotal in converting interest "
        "into action, guiding leads through the journey "
        "from curiosity to commitment."
    ),
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)

# Tools

# crewAI tools (can also use langchain tools since crewAI is built on langchain)
directory_read_tool = DirectoryReadTool(directory="./instructions")
file_read_tool = FileReadTool()
# search_tool = SerperDevTool()

# custom search tool based on duckduckgo
class SearchToolInput(BaseModel):
    """Input schema for the Internet Search Tool."""
    search_query: str = Field(
        ...,
        description="The exact plain-text keyword phrase to search for. Example: 'DeepLearningAI news'."        
    )

class SearchTool(BaseTool):
    name: str = "internet_search"
    description: str = (
        "Search the live internet for up-to-date company facts and news."
        "Use simple keywords like 'DeepLearning AI news'."
    )
    args_schema: type[BaseModel] = SearchToolInput

    def _run(self, search_query: str) -> str:
        raw_results = DDGS().text(search_query, max_results=3)

        clean_text = "Here are the search results:\n\n"
        for result in raw_results:
            clean_text += f"Title: {result.get('title')}\n"
            clean_text += f"Information: {result.get('body')}\n\n"

        return clean_text

# custom tool, just an example
class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = (
        "Analyzes the sentiment of text "
        "to ensure positive and engaging commincation."    
    )

    def _run(self, text: str) -> str:
        # Your custom code tool goes here -> code, api call etc.
        # Right now just return positive since this is a small example
        return "positive"

search_tool = SearchTool()    
sentiment_analysis_tool = SentimentAnalysisTool()


# Tasks
lead_profiling_task = Task(
    description=(
        "Conduct an in-depth analysis of {lead_name}, "
        "a company in the {industry} sector "
        "that recently showed interest in our solutions. "
        "Utilize all available data sources "
        "to compile a detailed profile, "
        "focusing on key decision-makers, recent business "
        "developments, and potential needs "
        "that align with our offerings. "
        "This task is crucial for tailoring "
        "our engagement strategy effetively.\n"
        "Don't make assumptions and "
        "only use information you are absolutely sure about."
    ),
    expected_output=(
        "A comprehensive report on {lead_name}, "
        "including company background, "
        "key personnel, recent milestones, and identified needs. "
        "Highlight potential areas where "
        "our solutions can provide value, "
        "and suggest personalized engagement strategies."
    ),
    tools=[directory_read_tool, file_read_tool, search_tool],
    agent=sales_rep_agent
)

personalized_outreach_task = Task(
    description=(
        "Using the insights gathered from "
        "the lead profiling report on {lead_name}, "
        "craft a personalized outreach campaign "
        "aimed at {key_decision_maker}, "
        "the {position} of {lead_name}. "
        "The campaign should address their recent {milestone} "
        "and how our solutions can support their goals. "
        "Your communication must resonate "
        "with {lead_name}'s company culture and values, "
        "demonstrating a deep understanding of "
        "their business and needs.\n"
        "Don't make assumptions and only "
        "use information you are absolutely sure about."
    ),
    expected_output=(
        "A series of personalized email drafts "
        "tailored to {lead_name}, "
        "specifically targeting {key_decision_maker}."
        "Each draft should include "
        "a compelling narrative that connects our solutions "
        "with their recent achievements and future goals. "
        "Ensure the tone is engaging, professional, "
        "and aligned with {lead_name}'s corporate identity."
    ),
    tools=[sentiment_analysis_tool, search_tool],
    agent=lead_sales_rep_agent
)


def main():

    # Create the crew
    crew = Crew(
        agents = [sales_rep_agent, lead_sales_rep_agent],
        tasks = [lead_profiling_task, personalized_outreach_task],
        verbose=True,
        memory=False # Keep false for now since uni server
    )

    inputs = {
        "lead_name": "DeepLearningAI",
        "industry": "Online Learning Platform",
        "key_decision_maker": "Andrew Ng",
        "position": "CEO",
        "milestone": "product launch"
    }
    result = crew.kickoff(inputs=inputs)

    return result

if __name__ == "__main__":
    final_output = main()
    print(final_output)