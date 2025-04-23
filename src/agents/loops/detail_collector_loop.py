# -*- coding: utf-8 -*-
"""
Defines an example Loop Agent: Detail Collector Loop.

This agent manages an interactive loop to collect necessary details for a task,
typically by coordinating a sub-agent that asks questions and processing user responses.

Relevant ADK Classes:
- google.adk.agents.LoopAgent: Base class for managing the loop logic.
- google.adk.agents.Agent: The sub-agent responsible for generating questions/processing answers.
- google.adk.sessions.Session: Accessing state to check data completeness and store collected info.
- google.adk.events.Event: Receiving user responses, signaling loop continuation/termination.
- google.adk.events.EventActions: Using `escalate=True` to request user input.
"""

from google.adk.agents import LoopAgent
from google.adk.events import EventActions
from typing import Optional

# Import creator functions for sub-agents
from src.agents.executors.data_collector import create_data_collector_agent
from src.agents.critics.data_collection_critic import create_data_collection_critic_agent

# Constants for state keys
STATE_TASK_DETAILS = "task_details"
STATE_TASK_COMPLETENESS = "task_completeness"

def create_detail_collector_loop(
    collector_model: str = "gemini-2.0-flash",
    critic_model: str = "gemini-2.0-flash",
    max_iterations: int = 5,
    task_details_key: str = STATE_TASK_DETAILS,
    completeness_key: str = STATE_TASK_COMPLETENESS,
    state_keys_to_check: Optional[list[str]] = None
) -> LoopAgent:
    """
    Factory function to create a Detail Collector Loop Agent.

    Args:
        collector_model: Model name for the data collector agent.
        critic_model: Model name for the critic validation agent.
        max_iterations: Maximum number of interaction loops allowed.
        task_details_key: State key for storing collected task details.
        completeness_key: State key for storing task completeness assessment.
        state_keys_to_check: List of keys in session state that indicate completion.

    Returns:
        An instance of LoopAgent configured for detail collection.
    """
    # Create the data collector agent internally
    data_collector_agent = create_data_collector_agent(
        model_name=collector_model,
        # Can add tools if needed
        # output_key is typically set within the agent's own creation
    )
    
    # Initialize empty sub-agents list
    sub_agents = []
    
    # Add data collector agent
    sub_agents.append(data_collector_agent)
    
    # Create expert agent
    data_collection_critic = create_data_collection_critic_agent(
        model_name=critic_model,
        collected_data_key=task_details_key,  # Map to collected data key
        required_fields_key=completeness_key,  # Map to required fields key
        output_key="data_collection_feedback"  # Example output key
    )
    sub_agents.append(data_collection_critic)
    
    # Create the loop agent using the LoopAgent class
    loop_agent = LoopAgent(
        name="DetailCollectorLoop",
        description="Interactively collects necessary task details from the user.",
        sub_agents=sub_agents,
        max_iterations=max_iterations
    )
    
    print(f"Detail Collector Loop Agent created with {len(sub_agents)} sub-agents")
    print(f"Using {collector_model} model for data collector agent")
    if state_keys_to_check:
        print(f"Loop will check for completion of these state keys: {state_keys_to_check}")
    
    return loop_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Create the loop agent directly (no need to create sub-agents separately)
#     detail_loop = create_detail_collector_loop(
#         collector_model="gemini-2.0-flash",
#         critic_model="gemini-2.0-flash",  
#         state_keys_to_check=["task_deadline", "task_priority"],
#         max_iterations=3
#     )
#     
#     # In a real application, the orchestrator would run this loop agent
