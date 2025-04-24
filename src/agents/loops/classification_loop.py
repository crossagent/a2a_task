# -*- coding: utf-8 -*-
"""
Defines an example Loop Agent: Classification Confirmation Loop.

This agent manages an interactive loop to confirm or refine the classification
(e.g., type, priority) of a task or item with the user.

Relevant ADK Classes:
- google.adk.agents.LoopAgent: Base class for managing the loop logic.
- google.adk.agents.Agent/LlmAgent: The sub-agents responsible for proposing classification and processing feedback.
- google.adk.sessions.Session: Accessing state for proposed/confirmed classification.
- google.adk.events.Event: Receiving user confirmation/correction.
- google.adk.events.EventActions: Using `escalate=True` to present classification and request feedback.
"""

from google.adk.agents import LoopAgent, LlmAgent, Agent
from google.adk.sessions import Session, InMemorySessionService
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.genai import types
from typing import Optional, Dict, Any, List

# Import from executors and critics modules
from src.agents.executors.task_classifier import create_task_classifier_agent
from src.agents.critics.task_classity_critic import create_classification_critic_agent

# Constants for state keys
STATE_TASK_DETAILS = "task_details"
STATE_PROPOSED_CLASSIFICATION = "proposed_classification" 
STATE_CLASSIFICATION_FEEDBACK = "classification_feedback"
STATE_CLASSIFICATION_CONFIRMED = "classification_confirmed"

def create_classification_loop(
    classifier_model: str = "gemini-2.5-flash", 
    critic_model: str = "gemini-2.5-flash",
    max_iterations: int = 3,
    task_details_key: str = STATE_TASK_DETAILS,
    classification_key: str = STATE_PROPOSED_CLASSIFICATION,
    feedback_key: str = STATE_CLASSIFICATION_FEEDBACK,
    confirmation_key: str = STATE_CLASSIFICATION_CONFIRMED,
    state_keys_to_check: Optional[list[str]] = None
) -> LoopAgent:
    """
    Creates a Classification Loop Agent that iteratively refines task classifications.
    
    Args:
        classifier_model: Model name for the classifier agent.
        critic_model: Model name for the critic agent.
        max_iterations: Maximum number of refinement loops allowed.
        task_details_key: State key for task details.
        classification_key: State key for proposed classification.
        feedback_key: State key for user feedback.
        confirmation_key: State key for confirmation status.
        state_keys_to_check: Optional list of keys in state that indicate completion.
        
    Returns:
        A LoopAgent that manages classification refinement.
    """
    # Create the classifier agent from executors module
    classifier_agent = create_task_classifier_agent(
        model_name=classifier_model,
        task_details_key=task_details_key,
        output_key=classification_key
    )
    
    # Create the critic agent from critics module
    critic_agent = create_classification_critic_agent(
        model_name=critic_model,
        proposed_classification_key=classification_key,
        task_details_key=task_details_key,
        output_key=feedback_key
    )
    
    # Initialize sub_agents list
    sub_agents = []
    
    # Add classifier agent
    sub_agents.append(classifier_agent)
    
    # Add critic agent
    sub_agents.append(critic_agent)
    
    # Create the classification loop with all agents
    loop_agent = LoopAgent(
        name="ClassificationLoop",
        description="Interactively confirms or refines task classification with the user.",
        sub_agents=sub_agents,
        max_iterations=max_iterations
    )
    
    print(f"Classification Loop Agent created with max {max_iterations} iterations")
    print(f"Using {classifier_model} model for classifier agent")
    print(f"Using {critic_model} model for critic agent")
    
    # Print state keys to check if provided
    if state_keys_to_check:
        print(f"Loop will check for completion of these state keys: {state_keys_to_check}")
    
    return loop_agent

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
#     # Create session
#     app_name = "task_classification_app"
#     user_id = "test_user_01"
#     session_id = "test_session_01"
#     
#     session_service = InMemorySessionService()
#     session = session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
#     
#     # Set initial task details in state
#     session.state[STATE_TASK_DETAILS] = task_info
#     
#     # Create the loop agent
#     classification_loop = create_classification_loop(
#         state_keys_to_check=["task_title", "task_priority"]
#     )
#     
#     # Create runner
#     runner = Runner(agent=classification_loop, app_name=app_name, session_service=session_service)
#     
#     # Start the loop
#     content = types.Content(role='user', parts=[types.Part(text="Please classify this task")])
#     events = runner.run(user_id=user_id, session_id=session_id, new_message=content)
#     
#     # Process events
#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("Agent Response:", final_response)
