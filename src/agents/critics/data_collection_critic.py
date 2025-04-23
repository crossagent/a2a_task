# -*- coding: utf-8 -*-
"""
Defines the Data Collection Critic Agent.

This agent is responsible for reviewing the completeness and quality of collected data,
providing feedback on what might be missing or needs improvement.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Used for its reasoning capabilities to evaluate data completeness.
- google.adk.tools.ToolContext: Accessing session state to read collected data.
- google.adk.events.EventActions: Writing validation results/feedback to state.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.events import EventActions
from typing import Optional

# Constants for state keys
STATE_COLLECTED_DATA = "collected_task_details"
STATE_DATA_FEEDBACK = "data_collection_feedback"
STATE_REQUIRED_FIELDS = "required_data_fields"

def create_data_collection_critic_agent(
    model_name: str = "gemini-2.0-flash",
    collected_data_key: str = STATE_COLLECTED_DATA,
    required_fields_key: str = STATE_REQUIRED_FIELDS,
    output_key: str = STATE_DATA_FEEDBACK
) -> LlmAgent:
    """
    Factory function to create the Data Collection Critic Agent.

    Args:
        model_name: The name of the LLM to use.
        collected_data_key: State key containing the collected data.
        required_fields_key: State key containing the list of required fields (if available).
        output_key: State key where the critique will be saved.

    Returns:
        An instance of the Data Collection Critic Agent.
    """
    instructions = f"""
    You are a Data Completeness Critic AI.
    Review the collected data provided in the session state key '{collected_data_key}'.
    If available, check against the required fields in '{required_fields_key}'.
    
    Evaluate whether the data is:
    1. Complete - Are all necessary fields present?
    2. Clear - Is the information specific and unambiguous?
    3. Consistent - Does the data contain contradictions?
    
    Provide 1-3 brief points of feedback (e.g., "Missing deadline information", 
    "Description is too vague", "All required fields are present and clear").
    
    Output *only* your critique with no additional commentary.
    """

    critic_agent = LlmAgent(
        name="DataCollectionCriticAgent",
        model=model_name,
        instruction=instructions,
        description="Reviews collected task data for completeness and quality.",
        output_key=output_key  # Saves critique to state
    )
    
    print(f"Data Collection Critic Agent created using model: {model_name}")
    print(f"Will review data from state key: '{collected_data_key}'")
    print(f"Will save feedback to state key: '{output_key}'")
    
    return critic_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     critic = create_data_collection_critic_agent()
#     # For testing, you could create a mock session with sample data
#     # session.state[STATE_COLLECTED_DATA] = {
#     #    "title": "Implement login page",
#     #    "description": "Create a secure login form"
#     #    # Note: missing deadline, priority, etc.
#     # }
#     # session.state[STATE_REQUIRED_FIELDS] = ["title", "description", "deadline", "priority"]
#     # Run the critic and check the output in session.state[STATE_DATA_FEEDBACK]
