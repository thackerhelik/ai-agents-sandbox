#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from project_progress_report.crew import ProjectProgressReport

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """

    try:
        print("🚀 Kicking off the Trello Analysis Crew...")
        
        # 1. Run the AI pipeline
        my_crew = ProjectProgressReport().crew()
        result = my_crew.kickoff()

        # 2. Extract the raw markdown text from the final task
        final_markdown_report = result.raw # type: ignore

        # 3. Save it to a file with UTF-8 encoding (to support emojis!)
        with open("sprint_progress_report.md", "w", encoding="utf-8") as f:
            f.write(final_markdown_report)
            
        print("\n✅ Success! The comprehensive sprint report has been saved to 'sprint_progress_report.md'")

        if hasattr(result, 'token_usage'):
            print("\n📊 Telemetry:")
            print(f"Total Tokens Used: {result.token_usage.total_tokens}") # type: ignore
            print(f"Prompt Tokens: {result.token_usage.prompt_tokens}") # type: ignore
            print(f"Completion Tokens: {result.token_usage.completion_tokens}") # type: ignore

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
#         ProjectProgressReport().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         ProjectProgressReport().crew().replay(task_id=sys.argv[1])

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
#         ProjectProgressReport().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

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
#         result = ProjectProgressReport().crew().kickoff(inputs=inputs)
#         return result
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew with trigger: {e}")
