import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables looking up one dir level
load_dotenv(dotenv_path="../.env")

# Configure client for uni server
client = OpenAI(
    api_key=os.getenv("UNIVERSITY_API_KEY"),
    base_url=os.getenv("UNIVERSITY_BASE_URL")
)

# Create a local python tool
def get_weather(location: str) -> str:
    """ A mock function to simulate a weather API."""
    if "aachen" in location.lower():
        return "It is currently raining and 19 degrees."
    return "It is 30 degrees and sunny."

available_functions = {
    "get_weather": get_weather
}

# JSON description schema for gpt-oss-120b
tools_schema = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city, e.g. Aachen"}
            },
            "required": ["location"],
        },
    }
}]

# Core agent loop
def run_agent(user_input: str, max_iterations: int = 5):
    messages = [{"role": "user", "content": user_input}]

    for i in range(max_iterations):
        print(f"--- Iteration {i+1} ---")
    
        # Invoke the model
        response = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=messages,
            tools=tools_schema
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        # If no tool calls are requested, the agent is finished thinking
        if not assistant_message.tool_calls:
            return assistant_message.content
        
        # Parse and run requested tool
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"[AGENT ACTION] Model requested tool: '{function_name}' with args: {function_args}")

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**function_args)

            print(f"[TOOL OUTPUT] Tool returned: {function_response}\n")

            # Append output to thread history
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

    return "Agent stopped: Reached maximum iterations."
    
if __name__ == "__main__":
    print("Starting Bare-Metal Agent...")
    output = run_agent("What should I wear today in Aachen")
    print(f"\n[FINAL ANSWER]: {output}")