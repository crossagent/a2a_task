import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext

# TODO: Import prompts for Agent 2
# from . import prompts

# TODO: Import Notion Tool functions
# from ...tools.notion_tool import get_notion_database_properties, find_notion_project, create_notion_task

# Define Agent 2 (Task Assignment Agent)
task_assignment_agent = Agent(
    # TODO: Configure model
    model=os.getenv("ADK_AGENT_MODEL"), # Assuming a generic model env var
    name="task_assignment_agent",
    description="This agent takes task details and creates the task in Notion using the Notion Tool.",
    # TODO: Add instruction using prompts
    # instruction=prompts.TASK_ASSIGNMENT_INSTRUCTION,
    # TODO: Add tools used by Agent 2
    # tools=[get_notion_database_properties, find_notion_project, create_notion_task],
    # TODO: Add callbacks if necessary (e.g., to process state before/after agent call)
    # before_agent_callback=...,
    # after_agent_callback=...,
)

# TODO: Implement the logic within Agent 2's instruction and potentially callbacks
# to process task details from state, call Notion Tool functions, and report success/failure.
