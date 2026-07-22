from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
import os

@CrewBase
class EmailEngagement():
    """EmailEngagement crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @property
    def uni_llm(self):
        return LLM(
            model=os.getenv("MODEL",""),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

    @agent
    def email_content_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['email_content_specialist'], # type: ignore[index]
            verbose=True,
            llm=self.uni_llm
        )

    @agent
    def engagement_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['engagement_strategist'], # type: ignore[index]
            verbose=True,
            llm=self.uni_llm
        )

    @task
    def email_drafting(self) -> Task:
        return Task(
            config=self.tasks_config['email_drafting'], # type: ignore[index]
        )

    @task
    def engagement_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['engagement_optimization'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the EmailEngagement crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            # process=Process.sequential,
            verbose=True,
        )
