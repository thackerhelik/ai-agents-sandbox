from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.board_data_fetcher import BoardDataFetcherTool
from .tools.card_data_fetcher import CardDataFetcherTool
import requests
import os

@CrewBase
class ProjectProgressReport():
    """ProjectProgressReport crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    board_data_fetcher_tool = BoardDataFetcherTool()
    card_data_fetcher_tool = CardDataFetcherTool()

    @property
    def uni_llm(self):
        return LLM(
            model=os.getenv("MODEL",""),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

    @agent
    def data_collection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_collection_agent'], # type: ignore[index]
            tools = [self.board_data_fetcher_tool, self.card_data_fetcher_tool],
            llm=self.uni_llm
        )
    
    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analysis_agent'], # type: ignore[index]
            llm=self.uni_llm
        )

    @task
    def data_collection(self) -> Task:
        return Task(
            config=self.tasks_config['data_collection'], # type: ignore[index]
        )

    @task
    def data_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['data_analysis'], # type: ignore[index]
        )

    @task
    def report_generation(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProjectProgressReport crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
