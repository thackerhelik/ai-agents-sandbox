#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from automated_project.crew import AutomatedProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """

    team_members = """
    - John Doe (Project Manager)
    - Jane Doe (Software Engineer)
    - Bob Smith (Designer)
    - Alice Johnson (QA Engineer)
    - Tom Brown (QA Engineer)
    """

    project_requirements = """
    - Create a responsive design that works well on desktop and mobile devices
    - Implement a modern, visually appealing user interface with a clean look
    - Develop a user-friendly navigation system with intuitive menu structure
    - Include an "About Us" page highlighting the company's history and values
    - Design a "Services" page showcasing the business's offerings with descriptions
    - Create a "Contact Us" page with a form and integrated map for communication
    - Implement a blog section for sharing industry news and company updates
    - Ensure fast loading times and optimize for search engines (SEO)
    - Integrate social media links and sharing capabilities
    - Include a testimonials section to showcase customer feedback and build trust
    """

    inputs = {
        'project_type': 'Website',
        'project_objectives': 'Create a website for small business',
        'industry': 'Technology',
        'team_members': team_members.strip(),
        'project_requirements': project_requirements.strip(),
    }

    try:
        result = AutomatedProject().crew().kickoff(inputs=inputs)

        print("\n" + "="*50)
        print("✅ PROJECT PLAN GENERATED")
        print("="*50 + "\n")

        # 1. Print the actual Pydantic Data (Nicely formatted JSON)
        if result.pydantic:
            # Pydantic v2 uses model_dump_json() to create a clean string
            clean_json_output = result.pydantic.model_dump_json(indent=4)
            print(clean_json_output)
            
            # PRO TIP: Save it to a real file so you have a permanent record!
            with open("final_project_plan.json", "w") as f:
                f.write(clean_json_output)
                print("\n💾 Saved to 'final_project_plan.json'")

        # 2. Print Token Telemetry (Skip the dollar cost math)
        # Note: CrewAI attaches usage metrics to the raw result object
        if hasattr(result, 'token_usage'):
            print("\n📊 Telemetry:")
            print(f"Total Tokens Used: {result.token_usage.total_tokens}")
            print(f"Prompt Tokens: {result.token_usage.prompt_tokens}")
            print(f"Completion Tokens: {result.token_usage.completion_tokens}")

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         AutomatedProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         AutomatedProject().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }

#     try:
#         AutomatedProject().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")

# def run_with_trigger():
#     """
#     Run the crew with trigger payload.
#     """
#     import json

#     if len(sys.argv) < 2:
#         raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

#     try:
#         trigger_payload = json.loads(sys.argv[1])
#     except json.JSONDecodeError:
#         raise Exception("Invalid JSON payload provided as argument")

#     inputs = {
#         "crewai_trigger_payload": trigger_payload,
#         "topic": "",
#         "current_year": ""
#     }

#     try:
#         result = AutomatedProject().crew().kickoff(inputs=inputs)
#         return result
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew with trigger: {e}")
