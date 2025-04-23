# -*- coding: utf-8 -*-
"""
Defines the Workflow Parser Agent.

This agent is responsible for parsing natural language descriptions of workflows
or specific user commands into structured execution plans. For known, well-defined
workflows (e.g., "add Notion task"), it might output a predefined plan template.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Likely base class for NLU capabilities.
- google.adk.sessions.Session: Accessing session state if needed for context.
- src.models.workflow_plan.WorkflowPlan: The structured plan data model (to be defined).
"""

from google.adk.agents import LlmAgent
# TODO: Import WorkflowPlan model when defined
# from src.models.workflow_plan import WorkflowPlan

# Placeholder for the Workflow Parser Agent definition
# This agent will likely need specific instructions and potentially tools
# for understanding user input and generating the structured plan.

def create_workflow_parser_agent(model_name: str = "gemini-2.0-flash") -> LlmAgent:
    """
    Factory function to create the Workflow Parser Agent.

    Args:
        model_name: The name of the LLM to use for the agent.

    Returns:
        An instance of the Workflow Parser Agent.
    """
    # TODO: Define appropriate instructions for parsing workflows
    instructions = (
        "You are a Workflow Parser. Your task is to understand the user's request "
        "and convert it into a structured workflow plan. "
        "Identify the goal, steps, required roles (executors, experts), and deliverables. "
        "For simple, known tasks like 'add a notion task', output a predefined plan structure. "
        "For complex or novel requests, generate a step-by-step plan."
        # Add more detailed instructions here based on the WorkflowPlan model
    )

    parser_agent = LlmAgent(
        name="WorkflowParserAgent",
        model=model_name,
        instruction=instructions,
        description="Parses natural language workflow descriptions into structured plans.",
        # tools=[] # Add tools if needed for parsing or accessing templates
    )
    print(f"Workflow Parser Agent created using model: {model_name}")
    return parser_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     parser = create_workflow_parser_agent()
#     # Add test code here to simulate running the parser agent
#     pass
