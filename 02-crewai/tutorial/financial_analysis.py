import os
import warnings
from crewai import Agent, Task, Crew, Process, LLM
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


# Agents

# Manager agent since manager_llm seems to be doing the work for itself
chief_investment_officer = Agent(
    role="Chief Investment Officer (Team Manager)",
    goal="Manage the financial team and strictly delegate all research and analysis tasks.",
    backstory=(
        "You are the director of a financial simulation team. "
        "CRITICAL INSTRUCTION: YOU MUST NOT DO THE WORK YOURSELF. "
        "Your ONLY job is to read the tasks, identify which of your co-workers "
        "(Data Analyst, Strategy Developer, Trade Advisor, Risk Advisor) "
        "is best suited for the job, and use your tools to DELEGATE the work to them. "
        "When using the 'Delegate work to coworker' tool, you MUST provide ALL THREE required arguments: "
        "1. 'coworker': The EXACT title of the agent (e.g. 'Data Analyst', 'Trading Strategy Developer', 'Trade Advisor', or 'Risk Advisor'). "
        "2. 'task': The detailed description of what they need to do. "
        "3. 'context': Any background information or previous findings they need to know. "
        "Wait for their response, review it, and then delegate the next task."
    ),
    verbose=True,
    allow_delegation=True,
    llm=uni_llm
)

data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Monitor and analyze market data in real-time "
         "to identify trends and predict market movements.",
    backstory="Specializing in financial markets, this agent "
              "uses statistical modeling and machine learning "
              "to provide crucial insights. With a knack for data, "
              "the Data Analyst Agent is the cornerstone for "
              "informing trading decisions.",
    verbose=True,
    allow_delegation=False, #change from tutorial since we are using heirarchical manager_agent delegates
    tools=[scrape_tool, search_tool],
    llm=uni_llm,
)

trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test various trading strategies based "
         "on insights from the Data Analyst Agent.",
    backstory="Equipped with a deep understanding of financial "
              "markets and quantitative analysis, this agent "
              "devises and refines trading strategies. It evaluates "
              "the performance of different approaches to determine "
              "the most profitable and risk-averse options.",
    verbose=True,
    allow_delegation=False, #change from tutorial since we are using heirarchical manager_agent delegates
    tools=[scrape_tool, search_tool],
    llm=uni_llm,
)

execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies "
         "based on approved trading strategies.",
    backstory="This agent specializes in analyzing the timing, price, "
              "and logistical details of potential trades. By evaluating "
              "these factors, it provides well-founded suggestions for "
              "when and how trades should be executed to maximize "
              "efficiency and adherence to strategy.",
    verbose=True,
    allow_delegation=False, #change from tutorial since we are using heirarchical manager_agent delegates
    tools=[scrape_tool, search_tool],
    llm=uni_llm,
)

risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on the risks "
         "associated with potential trading activities.",
    backstory="Armed with a deep understanding of risk assessment models "
              "and market dynamics, this agent scrutinizes the potential "
              "risks of proposed trades. It offers a detailed analysis of "
              "risk exposure and suggests safeguards to ensure that "
              "trading activities align with the firm's risk tolerance.",
    verbose=True,
    allow_delegation=False, #change from tutorial since we are using heirarchical manager_agent delegates
    tools=[scrape_tool, search_tool],
    llm=uni_llm
)


# Tasks

# Task for Data Analyst Agent: Analyze Market Data
data_analysis_task = Task(
    description=(
        "Continuously monitor and analyze market data for "
        "the selected stock ({stock_selection}). "
        "If you need to read an entire article, pass the URL "
        "from your search results into the scrape_tool. "
        "Use statistical modeling and machine learning to "
        "identify trends and predict market movements."
    ),
    expected_output=(
        "Insights and alerts about significant market "
        "opportunities or threats for {stock_selection}."
    ),
    agent=data_analyst_agent,
)

# Task for Trading Strategy Agent: Develop Trading Solutions
strategy_development_task = Task(
    description=(
        "Develop and refine trading strategies based on "
        "the insights from the Data Analyst. "
        "You have an initial capital of {initial_capital}. "
        "Your risk tolerance is {risk_tolerance} and "
        "preference is {trading_strategy_preference}. "
        "Factor in recent news: {news_impact_consideration}."
    ),
    expected_output=(
        "A set of potential trading strategies for {stock_selection} "
        "that align with the user's risk tolerance."
    ),
    agent=trading_strategy_agent,
)

# Task for Trade Advisor Agent: Plan Trade Execution
execution_planning_task = Task(
    description=(
        "Analyze approved trading strategies to determine the "
        "best execution methods for {stock_selection}, "
        "considering current market conditions and optimal pricing."
    ),
    expected_output=(
        "Detailed execution plans suggesting how and when to "
        "execute trades for {stock_selection}."
    ),
    agent=execution_agent,
)

# Task for Risk Advisor Agent: Assess Trading Risks
risk_assessment_task = Task(
    description=(
        "Evaluate the risks associated with the proposed trading "
        "strategies and execution plans for {stock_selection}. "
        "Provide a detailed analysis of potential risks "
        "and suggest mitigation strategies."
    ),
    expected_output=(
        "A comprehensive risk analysis report detailing potential "
        "risks and mitigation recommendations for {stock_selection}."
        ""
    ),
    agent=risk_management_agent,
)


def run_financial_crew(inputs_dict):
    
    # Create the crew
    # - We use Process class which helps to delegate the workflow to the Agents (like a Manager at work)
    financial_trading_crew = Crew(
        agents=[data_analyst_agent,
                trading_strategy_agent,
                execution_agent,
                risk_management_agent],

        tasks=[data_analysis_task,
               strategy_development_task,
               execution_planning_task,
               risk_assessment_task],

        # manager_llm=uni_llm,
        manager_agent=chief_investment_officer,
        process=Process.hierarchical,
        verbose=True,
    )

    # financial_trading_inputs = {
    #     "stock_selection": "RELIANCE",
    #     "initial_capital": "20000 Rupees",
    #     "risk_tolerance": "Medium",
    #     "trading_strategy_preference": "Day Trading",
    #     "news_impact_consideration": True,
    # }

    result = financial_trading_crew.kickoff(inputs=inputs_dict)

    return result


if __name__ == "__main__":
    financial_trading_inputs = {
        "stock_selection": "RELIANCE",
        "initial_capital": "20000 Rupees",
        "risk_tolerance": "Medium",
        "trading_strategy_preference": "Day Trading",
        "news_impact_consideration": True,
    }
    final_output = run_financial_crew(financial_trading_inputs)
    
    print("\n" + "="*40)
    print("FINANCIAL TRADING REPORT")
    print("="*40 + "\n")
    print(final_output)

    # Save to markdown file
    with open("financial_report.md", "w", encoding="utf-8") as file:
        file.write(str(final_output))

    print("\n Report saved to financial_report.md")