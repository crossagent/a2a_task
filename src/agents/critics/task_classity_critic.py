# -*- coding: utf-8 -*-
"""
Defines the Task Classification Critic Agent.

This agent is responsible for reviewing and validating the task classification
produced during the workflow, providing feedback on its appropriateness and accuracy.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Used for its reasoning capabilities to evaluate classifications.
- google.adk.tools.ToolContext: Accessing session state to read classification data.
- google.adk.events.EventActions: Writing validation results/feedback to state.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.events import EventActions
from typing import Optional

# Constants for state keys
STATE_PROPOSED_CLASSIFICATION = "proposed_classification"
STATE_CLASSIFICATION_FEEDBACK = "classification_feedback"
STATE_TASK_DETAILS = "task_details"

def create_classification_critic_agent(
    model_name: str = "gemini-2.5-flash",
    proposed_classification_key: str = STATE_PROPOSED_CLASSIFICATION,
    task_details_key: str = STATE_TASK_DETAILS,
    output_key: str = STATE_CLASSIFICATION_FEEDBACK
) -> LlmAgent:
    """
    Factory function to create the Classification Critic Agent.

    Args:
        model_name: The name of the LLM to use.
        proposed_classification_key: State key containing the proposed classification.
        task_details_key: State key containing the task details.
        output_key: State key where the critique will be saved.

    Returns:
        An instance of the Classification Critic Agent.
    """
    instructions = f"""
    You are a Classification Critic AI.
    Review the task classification provided in the session state key '{proposed_classification_key}' 
    and the task details in '{task_details_key}'.
    
    Evaluate whether the classification is:
    1. Accurate - Does it correctly represent the task type?
    2. Appropriate - Is the priority level justified?
    3. Complete - Does it include all relevant classification dimensions?
    
    Provide 1-3 brief points of feedback (e.g., "Priority should be higher given the deadline", 
    "Missing domain category", "Classification matches task description well").
    
    Output *only* your critique with no additional commentary.
    """

    critic_agent = LlmAgent(
        name="ClassificationCriticAgent",
        model=model_name,
        instruction=instructions,
        description="Reviews and validates task classifications for accuracy and appropriateness.",
        output_key=output_key  # Saves critique to state
    )
    
    print(f"Classification Critic Agent created using model: {model_name}")
    print(f"Will review classifications from state key: '{proposed_classification_key}'")
    print(f"Will save feedback to state key: '{output_key}'")
    
    return critic_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     critic = create_classification_critic_agent()
#     # For testing, you could create a mock session with sample data
#     # session.state[STATE_PROPOSED_CLASSIFICATION] = {"type": "feature_request", "priority": "high"}
#     # session.state[STATE_TASK_DETAILS] = {"title": "Add login API", "deadline": "next week"}
#     # Run the critic and check the output in session.state[STATE_CLASSIFICATION_FEEDBACK]
