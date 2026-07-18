from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field
import os


class TaskEstimate(BaseModel):
    task_id: str = Field(..., description="A unique identifier for this task (e.g., 'T-01', 'T-02')")
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours.")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task.")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of the exact task_ids (e.g., 'T-01') associated with this milestone")

class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")

@CrewBase
class AutomatedProject():
    """AutomatedProject crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @property
    def uni_llm(self):
        return LLM(
            model=os.getenv("MODEL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

    @agent
    def project_planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['project_planning_agent'], # type: ignore[index]
            llm=self.uni_llm
        )

    @agent
    def estimation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['estimation_agent'], # type: ignore[index]
            llm=self.uni_llm
        )
    
    @agent
    def resource_allocation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_allocation_agent'], # type: ignore[index]
            llm=self.uni_llm
        )

    @task
    def task_breakdown(self) -> Task:
        return Task(
            config=self.tasks_config['task_breakdown'], # type: ignore[index]
        )

    @task
    def time_resource_estimation(self) -> Task:
        return Task(
            config=self.tasks_config['time_resource_estimation'], # type: ignore[index]
            context=[self.task_breakdown()]
        )

    @task
    def resource_allocation(self) -> Task:
        return Task(
            config=self.tasks_config['resource_allocation'], # type: ignore[index]
            context=[self.task_breakdown(), self.time_resource_estimation()],
            output_pydantic=ProjectPlan
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AutomatedProject crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
