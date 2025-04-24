# -*- coding: utf-8 -*-
"""
Defines an example Executor Agent: Task Classifier.

This agent is responsible for analyzing task details and proposing appropriate
classifications such as type, priority, complexity, and estimated time.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Used for NLU capabilities to analyze task descriptions.
- google.adk.tools.ToolContext: Accessing session state to read task details and write classifications.
- google.adk.events.EventActions: Potentially signaling classification results via state_delta.
"""

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import ToolContext
from google.adk.events import EventActions
from typing import Optional, List, Callable

# Constants for state keys
STATE_TASK_DETAILS = "task_details"
STATE_PROPOSED_CLASSIFICATION = "proposed_classification" 
STATE_CLASSIFICATION_FEEDBACK = "classification_feedback"

def create_task_classifier_agent(
    model_name: str = "gemini-2.0-flash",
    tools: Optional[List[Callable]] = None,
    task_details_key: str = STATE_TASK_DETAILS,
    output_key: str = STATE_PROPOSED_CLASSIFICATION,
    before_tool_cb: Optional[callable] = None,
    after_tool_cb: Optional[callable] = None,
) -> Agent:
    """
    Factory function to create the Task Classifier Agent.

    Args:
        model_name: The name of the LLM to use.
        tools: List of tools the agent can use for classification (e.g., analysis tools).
        task_details_key: The state key containing task details.
        output_key: The state key where the classification will be saved.
        before_tool_cb: Optional before_tool_callback.
        after_tool_cb: Optional after_tool_callback.

    Returns:
        An instance of the Task Classifier Agent.
    """
    instructions = f"""
    You are a Task Classification AI.
    
    Examine the task details provided in the session state key '{task_details_key}'.
    Based on the details, propose an appropriate classification for the task including:
    1. Type (e.g., "bug", "feature", "documentation", "maintenance")
    2. Priority (e.g., "critical", "high", "medium", "low")
    3. Complexity (e.g., "simple", "moderate", "complex")
    4. Estimated time (e.g., "1 hour", "1 day", "1 week")
    
    If you see feedback in '{STATE_CLASSIFICATION_FEEDBACK}', refine your classification accordingly.
    
    Use any available tools if they can help with your analysis.
    
    Output the classification as a JSON-like structure with the above fields.
    For example: {{"type": "feature", "priority": "high", "complexity": "moderate", "estimated_time": "3 days"}}
    """
    
    classifier_agent = LlmAgent(
        name="TaskClassifierAgent",
        model=model_name,
        instruction=instructions,
        description="Analyzes task details and proposes appropriate classifications.",
        tools=tools or [],
        before_tool_callback=before_tool_cb,
        after_tool_callback=after_tool_cb,
        output_key=output_key # Saves the proposed classification to state
    )
    
    print(f"Task Classifier Agent created using model: {model_name}")
    print(f"Will analyze task details in state key: '{task_details_key}'")
    print(f"Will output classification to state key: '{output_key}'")
    
    return classifier_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Sample task details
#     task_info = {
#         "title": "Implement login form",
#         "description": "Create a secure login form with username/password fields and validation",
#         "deadline": "next week",
#         "requester": "product team"
#     }
#     
#     # Define dummy tools if needed
#     # def analyze_text_sentiment(text: str) -> dict: return {"sentiment": "neutral"}
#     
#     # Create the classifier agent
#     classifier = create_task_classifier_agent(tools=[analyze_text_sentiment])
#     
#     # In a real application, this agent would be run with the state containing task_details
#     # and would output its classification to the specified output_key