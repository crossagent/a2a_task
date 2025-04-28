import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

# TODO: Import prompts for Agent 1
# from . import prompts

# TODO: Import Agent 2 (Task Assignment Agent)
# from .sub_agents.task_assignment import agent as task_assignment_agent

# TODO: Define any tools used directly by Agent 1 (if any, besides calling Agent 2)
# For this project, Agent 1 primarily interacts with the user and passes state to Agent 2.
# It might not need direct access to NotionTool functions, but rather call Agent 2 which uses NotionTool.

# async def example_tool_for_agent1(question: str, tool_context: ToolContext):
#     """Example tool if Agent 1 needed one."""
#     pass

# Define Agent 1 (Task Definition Agent)
task_definition_agent = Agent(
    # TODO: Configure model
    model=os.getenv("ADK_AGENT_MODEL"), # Assuming a generic model env var
    name="task_definition_agent",
    description="This agent interacts with the user to define a task and its details.",
    # TODO: Add instruction using prompts
    # instruction=prompts.TASK_DEFINITION_INSTRUCTION,
    # TODO: Add tools if necessary (e.g., a tool to call Agent 2)
    # tools=[AgentTool(agent=task_assignment_agent)],
    # TODO: Add sub_agents if necessary (Agent 2 is a sub-agent)
    # sub_agents=[task_assignment_agent],
    # TODO: Add callbacks if necessary (e.g., to process user input or state before/after agent call)
    # before_agent_callback=...,
    # after_agent_callback=...,
)

# TODO: Implement the logic within Agent 1's instruction and potentially callbacks/tools
# to guide the conversation, extract task details, and trigger Agent 2.
