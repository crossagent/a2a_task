# -*- coding: utf-8 -*-
"""
Defines an example Executor Agent: Data Collector.

This agent is responsible for gathering specific information needed for a task,
potentially interacting with the user via the Orchestrator if information is missing.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: If complex reasoning or NLU is needed to determine what data to collect.
- google.adk.agents.Agent: Base class if logic is simpler or custom.
- google.adk.tools.ToolContext: Accessing session state to read existing data or write collected data.
- google.adk.events.EventActions: Potentially signaling missing info via state_delta or custom events.
"""

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import ToolContext
from google.adk.events import EventActions
from typing import Optional

# Placeholder for the Data Collector Agent definition
# This agent might use tools to fetch data from external sources or analyze
# existing state to determine what's missing.

def create_data_collector_agent(
    model_name: str = "gemini-2.0-flash",
    tools: Optional[list] = None,
    before_tool_cb: Optional[callable] = None,
    after_tool_cb: Optional[callable] = None,
) -> Agent:
    """
    Factory function to create the Data Collector Agent.

    Args:
        model_name: The name of the LLM to use (if LlmAgent).
        tools: List of tools the agent can use to collect data.
        before_tool_cb: Optional before_tool_callback.
        after_tool_cb: Optional after_tool_callback (e.g., for format check).

    Returns:
        An instance of the Data Collector Agent.
    """
    # TODO: Define specific instructions for data collection based on task context
    instructions = (
        "You are a Data Collector. Your goal is to gather specific pieces of information "
        "required for the current task, based on instructions provided (e.g., from the orchestrator). "
        "Use your available tools to find the information. "
        "If information is missing and cannot be found with tools, clearly state what is missing in your output."
        # "If interactive collection is needed, this agent might be part of a LoopAgent."
    )

    # Using LlmAgent as an example, could be a simpler Agent if logic is fixed
    collector_agent = LlmAgent(
        name="DataCollectorAgent",
        model=model_name,
        instruction=instructions,
        description="Collects specific data required for a task using available tools.",
        tools=tools or [],
        before_tool_callback=before_tool_cb,
        after_tool_callback=after_tool_cb,
        # output_key="collected_data" # Example: Save result to state
    )
    print(f"Data Collector Agent created using model: {model_name}")
    return collector_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Define dummy tools if needed
#     # def dummy_search_tool(query: str) -> dict: return {"result": f"Data for {query}"}
#     collector = create_data_collector_agent(tools=[dummy_search_tool])
#     # Add test code here
#     pass
