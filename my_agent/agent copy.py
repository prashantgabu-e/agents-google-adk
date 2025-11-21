from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Define specialized agents for a code pipeline
code_writer = LlmAgent(
    name="CodeWriter",
    model="gemini-2.5-flash",
    instruction="""Write clean Python code based on the specification.
    Output only the code, no explanations.""",
    description="Writes initial code",
    output_key="generated_code"  # Stores output in session state
)

code_reviewer = LlmAgent(
    name="CodeReviewer",
    model="gemini-2.5-flash",
    instruction="""Review the code for bugs, efficiency, and style.
    Provide specific improvement suggestions.""",
    description="Reviews code quality",
    output_key="review_comments"
)

code_refactorer = LlmAgent(
    name="CodeRefactorer",
    model="gemini-2.5-flash",
    instruction="""Refactor the code based on review comments.
    Output the improved code.""",
    description="Refactors code",
    output_key="refactored_code"
)

# Sequential pipeline: Writer -> Reviewer -> Refactorer
root_agent = SequentialAgent(
    name="CodePipeline",
    sub_agents=[code_writer, code_reviewer, code_refactorer]
)

# Run the pipeline
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="code_pipeline",
    session_service=session_service
)

content = types.Content(
    role='user',
    parts=[types.Part(text="Create a function to calculate fibonacci numbers")]
)

events = runner.run(
    user_id="dev_001",
    session_id="pipeline_1",
    new_message=content
)

for event in events:
    if event.content:
        print(f"[{event.author}]: {event.content.parts[0].text}")