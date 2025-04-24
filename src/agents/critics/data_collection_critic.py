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

import json
import logging
from google.adk.agents import LlmAgent
from google.adk.tools import Tool, ToolContext
from google.adk.events import EventActions
from typing import Optional, List, Dict, Any

# Import the specific tool
from src.tools.human_interaction_tools import HumanReviewTool

logger = logging.getLogger(__name__)

# Constants for state keys
STATE_COLLECTED_DATA = "collected_task_details"
STATE_DATA_CRITIQUE = "data_collection_critique" # Renamed for clarity
STATE_REQUIRED_FIELDS = "required_data_fields"

def create_data_collection_critic_agent(
    model_name: str = "gemini-2.0-flash",
    collected_data_key: str = STATE_COLLECTED_DATA,
    required_fields_key: str = STATE_REQUIRED_FIELDS,
    output_key: str = STATE_DATA_CRITIQUE, # Updated default output key
) -> LlmAgent:
    """
    Factory function to create the Data Collection Critic Agent.

    This agent internally includes and uses HumanReviewTool to request
    supplementary data when the critique status is 'incomplete'.

    Args:
        model_name: The name of the LLM to use.
        collected_data_key: State key containing the collected data.
        required_fields_key: State key containing the list of required fields (if available).
        output_key: State key where the critique will be saved.

    Returns:
        An instance of the Data Collection Critic Agent.
    """
    # Internally create and include the HumanReviewTool
    human_review_tool = HumanReviewTool() # Assuming default constructor is sufficient
    tools: List[Tool] = [human_review_tool]
    tool_name = human_review_tool.name # Get the actual tool name

    human_interaction_instructions = f"""

IMPORTANT ADDITIONAL STEP:
After generating the critique JSON:
1. Check the 'status' field in the critique you just generated.
2. If the 'status' is "incomplete":
   a. Call the tool '{tool_name}' to request human input.
   b. Pass the *entire critique JSON you just generated* as the 'critique' argument to the '{tool_name}' tool.
   c. The tool will return a response, potentially containing a 'supplementary_data' dictionary.
   d. Read the current data dictionary from the session state key '{collected_data_key}'.
   e. If the tool response contains 'supplementary_data' and it's a dictionary, merge this supplementary data into the current data dictionary (update the existing dictionary).
   f. Write the *updated* data dictionary back to the session state key '{collected_data_key}'.
   g. Log that you have requested and merged human input.
3. **CRITICAL**: Regardless of whether you called the '{tool_name}' tool, your final output for this agent execution MUST be the *original critique JSON* you generated initially (with 'status' and 'feedback'). Do NOT output the merged data or the tool's response as the final result for the '{output_key}'.
"""

    instructions = f"""
You are a Data Completeness Critic AI. Your goal is to evaluate collected data and potentially trigger a human review process if data is missing.

**Primary Task: Evaluate Data Completeness**
1. Review the collected data provided in the session state key '{collected_data_key}'. This data is expected to be a dictionary.
2. If available, check against the list of required field names in the session state key '{required_fields_key}'.
3. Evaluate whether the data is complete, clear, and consistent based on the required fields (if provided) and general understanding.
4. Determine the overall status:
   - "complete": If all required fields are present and the information seems sufficient and clear.
   - "incomplete": If required fields are missing, or the information is vague, ambiguous, or contradictory.
5. Provide concise feedback explaining the status (e.g., "Missing deadline and priority.", "Description needs more detail.", "All required information is present.").

**Output Format:**
Generate *only* a JSON object containing your evaluation with the following structure:
{{
  "status": "complete" | "incomplete",
  "feedback": "Your concise feedback here."
}}

Example Output (Incomplete):
{{
  "status": "incomplete",
  "feedback": "Missing deadline information. Description is too vague."
}}

Example Output (Complete):
{{
  "status": "complete",
  "feedback": "All required fields are present and clear."
}}
{human_interaction_instructions}
"""

    critic_agent = LlmAgent(
        name="DataCollectionCriticAgent",
        model=model_name,
        instruction=instructions,
        description=(
            "Reviews collected task data for completeness and quality, "
            "outputting a structured critique. If data is incomplete, "
            "it internally triggers human input collection via HumanReviewTool."
        ),
        tools=tools,
        output_key=output_key  # Saves the *original* structured critique to state
    )

    print(f"Data Collection Critic Agent created using model: {model_name}")
    print(f"Will review data from state key: '{collected_data_key}'")
    # Updated print statement to reflect internal tool inclusion
    print(f"Internally equipped with tool: '{tool_name}' for human input on incompleteness.")
    print(f"Will save structured critique to state key: '{output_key}'")

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
#     # Run the critic and check the output in session.state[STATE_DATA_CRITIQUE]
