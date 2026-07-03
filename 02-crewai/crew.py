import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

# Load creds
load_dotenv(dotenv_path="../.env")

# Configure CrewAI to use university model
# CrewAI uses LiteLLM under the hood, so we pass our custom URL and Key
uni_llm = LLM(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("UNIVERSITY_API_KEY"),
    base_url=os.getenv("UNIVERSITY_BASE_URL")
)

# Define your agents ("Employees")

researcher = Agent(
    role="Senior Data Researcher",
    goal="Analyze complex topics and extract key historical bullet points.",
    backstory="You are an expert historian who loves uncovering fascinating facts about European cities.",
    llm=uni_llm,
    allow_delegation=False,
    verbose=True
)

writer = Agent(
    role="Technical Communicator",
    goal="Take raw research and turn it into a short, engaging summary",
    backstory="You are a world-class travel writer. You make complex history exciting and easy to read.",
    llm=uni_llm,
    allow_delegation=False,
    verbose=True   
)


# Define your Tasks (The "Job Tickets")

research_task = Task(
    description="Research the historical significance of the city of Aachen. Give me exactly 3 key facts.",
    expected_output="A bulleted list of 3 key facts about Aachen.",
    agent=researcher
)

writing_task = Task(
    description="Using the 3 facts provided by the researcher, write a fun, 2-sentence marketing pitch for visiting Aachen.",
    expected_output="A 2-sentence promotional paragraph.",
    agent=writer
)


# Assemble the Crew (The "Company")
aachen_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential, # Run research first, then pass the data to the writer
    verbose=True
)


# Start the operation!
if __name__ == "__main__":
    print("Starting the CrewAI operation...\n")
    result = aachen_crew.kickoff()

    print("\n==============================")
    print("FINAL OUTPUT FROM THE WRITER AGENT:")
    print("==============================")
    print(result)