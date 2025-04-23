# -*- coding: utf-8 -*-
"""
Main entry point for the AI Workflow Automation application.

Sets up the agent team, runner, and handles user interaction loop (basic example).
"""

import asyncio
import os
from dotenv import load_dotenv
from google.genai.types import Content, Part

# Load environment variables from .env file (for API keys etc.)
# Ensure you have a .env file in the root or src directory
# Example .env content:
# GOOGLE_API_KEY="your_google_api_key"
# OPENAI_API_KEY="your_openai_api_key"
# ANTHROPIC_API_KEY="your_anthropic_api_key"
# NOTION_API_KEY="your_notion_api_key"
# NOTION_DATABASE_ID="your_notion_database_id"
load_dotenv()

# Import factory functions and core components
from src.core.runner_setup import setup_runner, session_service
from src.agents.parser import create_workflow_parser_agent
from src.agents.orchestrator import create_orchestrator_agent
from src.agents.executors.data_collector import create_data_collector_agent
from src.agents.executors.notion_writer import create_notion_writer_agent
from src.agents.expert import create_expert_agent
from src.agents.loops.detail_collector_loop import create_detail_collector_loop
from src.agents.loops.classification_loop import create_classification_loop
from src.tools.notion_tools import add_task_to_notion_database
from src.tools.general_tools import get_current_datetime
from src.tools.analysis_tools import classify_text, extract_keywords
from src.callbacks.format_checkers import check_tool_input_args, check_tool_output_format
from src.callbacks.guardrails import block_sensitive_keywords_in_input, restrict_tool_by_argument_value
# TODO: Import WorkflowPlan model when needed
# from src.models.workflow_plan import WorkflowPlan, WorkflowStep

# --- Configuration ---
APP_NAME = "ai_workflow_automator"
USER_ID = "test_user_001" # Example user ID
SESSION_ID = "test_session_001" # Example session ID

# Model Selection (can be configured)
DEFAULT_MODEL = "gemini-2.0-flash" # Or choose another like "openai/gpt-4o" if keys are set

async def main():
    """Main asynchronous function to set up and run the agent system."""
    print("--- Initializing AI Workflow Automator ---")

    # --- 1. Create Tools ---
    # Gather all tools needed by the agents
    notion_tools = [add_task_to_notion_database]
    general_tools = [get_current_datetime]
    analysis_tools = [classify_text, extract_keywords]
    # Add more tools as needed

    # --- 2. Create Callbacks ---
    # Combine callbacks if needed, or select specific ones per agent
    default_before_tool_cb = check_tool_input_args # Example
    default_after_tool_cb = check_tool_output_format # Example
    default_before_model_cb = block_sensitive_keywords_in_input # Example

    # --- 3. Create Agents (Bottom-up: Executors, Experts, Loops first) ---

    # Executors
    data_collector = create_data_collector_agent(
        model_name=DEFAULT_MODEL,
        tools=analysis_tools + general_tools, # Example tools
        after_tool_cb=default_after_tool_cb
    )
    notion_writer = create_notion_writer_agent(
        notion_tools=notion_tools,
        before_tool_cb=default_before_tool_cb, # Check input before calling Notion API
        after_tool_cb=default_after_tool_cb
    )

    # Expert
    task_expert = create_expert_agent(
        model_name=DEFAULT_MODEL, # Maybe use a more powerful model?
        expertise_area="task definition quality",
        tools=analysis_tools # Expert might use analysis tools
    )

    # Loop Sub-Agents (Agents used *inside* the loops)
    # This agent asks questions for the DetailCollectorLoop
    detail_questioner_agent = create_data_collector_agent( # Reusing for simplicity
         name="DetailQuestionerAgent", # Give it a specific name
         description="Asks specific questions to gather missing task details.",
         model_name=DEFAULT_MODEL,
         # No tools needed if it only generates questions based on state
    )
    # This agent proposes classification for the ClassificationLoop
    classifier_sub_agent = create_data_collector_agent( # Reusing again
         name="ClassifierSubAgent",
         description="Proposes task classification based on details and processes user feedback.",
         model_name=DEFAULT_MODEL,
         tools=analysis_tools # Might use classify_text tool
    )


    # Loop Agents
    detail_loop = create_detail_collector_loop(
        sub_agent=detail_questioner_agent,
        state_keys_to_check=["task_name", "status"] # Example required keys
    )
    classification_loop = create_classification_loop(
        sub_agent=classifier_sub_agent,
        confirmation_key="classification_confirmed"
    )

    # Parser Agent (Created but might be invoked separately or as first step by Orchestrator)
    workflow_parser = create_workflow_parser_agent(model_name=DEFAULT_MODEL)

    # --- 4. Create Orchestrator (Root Agent) ---
    # Gather all sub-agents the orchestrator can delegate to
    all_sub_agents = [
        data_collector,
        notion_writer,
        task_expert,
        detail_loop,
        classification_loop,
        # Include the loop sub-agents if orchestrator needs to delegate directly? Usually not.
    ]
    orchestrator = create_orchestrator_agent(
        sub_agents=all_sub_agents,
        model_name=DEFAULT_MODEL, # Orchestrator might need a capable model
        before_model_cb=default_before_model_cb, # Apply guardrail to root
        # Add other callbacks as needed
    )

    # --- 5. Setup Runner ---
    runner = setup_runner(root_agent=orchestrator, app_name=APP_NAME)

    # --- 6. Create or Get Session ---
    # Using the global session_service configured in runner_setup
    try:
        session = session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
        print(f"Resumed existing session: {SESSION_ID}")
    except KeyError:
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            # state={"user:api_cost_limit": 5.0} # Example initial state
        )
        print(f"Created new session: {SESSION_ID}")
    print(f"Initial Session State: {session.state}")


    # --- 7. Basic Interaction Loop (Example) ---
    print("\n--- Starting Interaction (type 'quit' to exit) ---")
    while True:
        user_input = input(">>> User: ")
        if user_input.lower() == 'quit':
            break

        # Prepare user message
        user_message = Content(role='user', parts=[Part(text=user_input)])

        final_response_text = "Agent did not produce a final response."
        try:
            # Run the orchestrator
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
                # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}") # Debug
                if event.actions and event.actions.escalate:
                    print(f"<<< Agent needs input (Escalated): {event.content.parts[0].text if event.content else 'No message.'}")
                    # In a real UI, present this message and wait for user input
                    # For this basic loop, we'll just prompt again
                    continue # Go to next input prompt

                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.error_message:
                         final_response_text = f"Agent Error: {event.error_message}"
                    print(f"<<< Agent: {final_response_text}")
                    break # Exit async for loop after final response for this turn

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")
            # Consider adding more robust error handling

        # Print updated state (optional)
        current_session = session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
        print(f"--- Current State: {current_session.state}")


    print("\n--- Interaction ended. ---")

if __name__ == "__main__":
    # Run the main async function
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Application failed: {e}")
