# -*- coding: utf-8 -*-
"""
Defines the Expert Agent.

This agent is responsible for reviewing and validating the content or classification
produced during the workflow, based on specific domain knowledge or quality criteria.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Typically used for its reasoning capabilities.
- google.adk.tools.ToolContext: Accessing session state to get the data to review.
- google.adk.events.EventActions: Writing validation results/feedback to state.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.events import EventActions
from typing import Optional, List, Callable

# Placeholder for the Expert Agent definition

def create_expert_agent(
    model_name: str = "gemini-2.0-flash", # Consider more powerful models for expertise
    expertise_area: str = "general task validation", # Be specific in real use
    tools: Optional[List[Callable]] = None, # Tools might help expert analyze data
    before_tool_cb: Optional[callable] = None,
    after_tool_cb: Optional[callable] = None,
) -> LlmAgent:
    """
    Factory function to create the Expert Agent.

    Args:
        model_name: The name of the LLM to use.
        expertise_area: A description of the agent's specific expertise.
        tools: Optional list of tools the expert can use.
        before_tool_cb: Optional before_tool_callback.
        after_tool_cb: Optional after_tool_callback.

    Returns:
        An instance of the Expert Agent.
    """
    # TODO: Define detailed instructions based on the specific expertise needed
    instructions = (
        f"You are an Expert Agent specializing in {expertise_area}. "
        "Your task is to review the data provided in the session state "
        "(e.g., keys 'collected_task_details', 'proposed_classification'). "
        "Evaluate the data based on criteria such as completeness, coherence, accuracy, and relevance "
        f"to the standards of {expertise_area}. "
        "Provide clear feedback, identify issues, and suggest improvements. "
        "Output your assessment (e.g., 'validation_status': 'approved'/'needs_revision', 'feedback': '...') "
        "which will be saved to the session state."
    )

    expert_agent = LlmAgent(
        name="ExpertAgent",
        model=model_name,
        instruction=instructions,
        description=f"Provides expert review and validation for {expertise_area}.",
        tools=tools or [],
        before_tool_callback=before_tool_cb,
        after_tool_callback=after_tool_cb,
        output_key="expert_assessment" # Example: Save assessment to state
    )
    print(f"Expert Agent created for {expertise_area} using model: {model_name}")
    return expert_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     expert = create_expert_agent(expertise_area="software task definition quality")
#     # Add test code here, simulating state and running the agent
#     pass
