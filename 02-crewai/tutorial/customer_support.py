import os
import warnings
from crewai import Agent, Task, Crew, LLM
from crewai_tools import ScrapeWebsiteTool
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

# Role Playing, Focus and Cooperation (Delegation)

support_agent = Agent(
    role="Senior Support Representative",
    goal="Be the most friendly and helpful "
         "support representative in your team",
    backstory=(
        "You work at crewAI (https://crewai.com/) and "
        "are now working on providing "
        "support to {customer}, a super important customer "
        " for your company."
        "You need to make sure that you provide the best support!"
        "Make sure to provide full complete answers, "
        "and make no assumptions."
    ),
    allow_delegation=False,
    verbose=True,
    llm=uni_llm
)

support_quality_assurance_agent = Agent(
    role="Support Quality Assurance Specialist",
    goal="Get recognition for providing the "
         "best support quality assurance in your team",
    backstory=(
        "You work at crewAI (https://crewai.com/) and "
        "are now working with your team "
        "on a request from {customer} ensuring that "
        "the support representative is "
        "providing the best support possible.\n"
        "You need to make sure that the support representative "
        "is providing full "
        "complete answers, and make no assumptions."
    ),
    allow_delegation=True,
    verbose=True,
    llm=uni_llm
)

# Tools, Guardrails and Memory
docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://docs.crewai.com/v1.15.1/en/enterprise/guides/kickoff-crew"
)

# Tasks

inquiry_resolution = Task(
    description=(
        "{customer} just reached out with a super import ask:\n"
        "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
        "Make sure to use everything you know "
        "to provide the best support possible."
        "You must strive to provide a complete "
        "and accurate response to the customer's inquiry."
    ),
    expected_output=(
        "A detailed, informative response to the "
        "customer's inquery that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
        "leaving no questions unanswered, and maintain a helpful and friendly "
        "tone throughout."
    ),
    tools=[docs_scrape_tool],
    agent=support_agent,
)

quality_assurance_review = Task(
    description=(
        "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
        "high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's inquiry "
        "have been addressed "
        "thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
        "ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's inquiry, incorporating all "
        "relevant feedback and improvements.\n"
        "Don't be too formal, we are a chill and cool company "
        "but maintain a professional and friendly tone throughout."
    ),
    agent=support_quality_assurance_agent
)


def main():

    # Create the CREW
    crew = Crew(
        agents=[support_agent, support_quality_assurance_agent],
        tasks=[inquiry_resolution, quality_assurance_review],
        verbose=True,
        # Set memory to true but server is not allowing :) so embedder etc. is not called
        memory=False,
        max_rpm=15,
        embedder={
            "provider": "sentence-transformer",
            "config": {
                "model": "all-MiniLM-L6-v2"
            }
        }
    )

    inputs = {
        "customer": "DeepLearningAI",
        "person": "Andrew Ng",
        "inquiry": "I need help with setting up a Crew "
                "and kicking it off, specifically "
                "how can I add memory to my crew? "
                "Can you provide guidance?"
    }

    result = crew.kickoff(inputs)
    return result


if __name__ == "__main__":
    final_output = main()
    print(final_output)