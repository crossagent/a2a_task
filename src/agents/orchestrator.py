# -*- coding: utf-8 -*-
"""
Defines the Orchestrator Agent (Root Agent).

This agent coordinates the overall workflow execution based on a structured plan
retrieved from session state (or provided directly). It manages sub-agent
delegation (Executors, Experts, Loops), handles events (e.g., for user interaction),
and interacts with session state to track progress.

Relevant ADK Classes:
- google.adk.agents.LlmAgent: Likely base class for complex coordination logic.
- google.adk.agents.Agent: Core agent definition.
- google.adk.sessions.Session: Managing session state (reading plan, tracking progress).
- google.adk.events.Event: Handling events from sub-agents (e.g., escalate for user input).
- google.adk.agents.Agent: Sub-agents (Executors, Experts, Loops) are passed during creation.
"""

from typing import List, Optional
from google.adk.agents import LlmAgent, Agent
from google.adk.sessions import Session
from google.adk.events import Event
# TODO: Import WorkflowPlan model when defined
# from src.models.workflow_plan import WorkflowPlan

# Placeholder for the Orchestrator Agent definition
# This agent will need complex instructions to:
# 1. Read the workflow plan from state.
# 2. Determine the current step.
# 3. Delegate to the appropriate sub-agent (Executor, Expert, Loop).
# 4. Handle events (e.g., escalate, completion signals).
# 5. Update state with progress.

def create_orchestrator_agent(
    sub_agents: List[Agent],
    model_name: str = "gemini-2.0-flash",
    before_model_cb: Optional[callable] = None,
    after_model_cb: Optional[callable] = None,
    before_tool_cb: Optional[callable] = None,
    after_tool_cb: Optional[callable] = None,
) -> LlmAgent:
    """
    Factory function to create the Orchestrator Agent.

    Args:
        sub_agents: A list of sub-agent instances (Executors, Experts, Loops)
                    that this orchestrator can delegate to.
        model_name: The name of the LLM to use for the agent.
        before_model_cb: Optional before_model_callback function.
        after_model_cb: Optional after_model_callback function.
        before_tool_cb: Optional before_tool_callback function.
        after_tool_cb: Optional after_tool_callback function.


    Returns:
        An instance of the Orchestrator Agent.
    """
    # TODO: Define detailed instructions for orchestration logic
    instructions = (
        "You are the Orchestrator. Your primary role is to manage and execute a "
        "structured workflow plan stored in the session state (key: 'workflow_plan'). "
        "1. Read the plan and identify the current step based on state (key: 'current_step_index'). "
        "2. Based on the step type, delegate the task to the appropriate sub-agent "
        "(use their descriptions: e.g., 'Data Collector', 'Notion Writer', 'Task Expert'). "
        "3. Pass necessary data from the session state to the sub-agent. "
        "4. Handle events from sub-agents: If an 'escalate' event occurs, pause and wait for user input. "
        "5. Upon sub-agent completion, update the session state (e.g., increment 'current_step_index', store results). "
        "6. If the plan is complete, signal completion."
        # Add more specifics on plan structure and state keys
    )

    orchestrator = LlmAgent(
        name="OrchestratorAgent",
        model=model_name,
        instruction=instructions,
        description="Coordinates workflow execution by delegating tasks to specialized sub-agents based on a plan.",
        sub_agents=sub_agents, # Enable delegation
        # tools=[] # Orchestrator might need tools to manage state or plan directly
        before_model_callback=before_model_cb,
        after_model_callback=after_model_cb,
        before_tool_callback=before_tool_cb,
        after_tool_callback=after_tool_cb,
        # output_key=None # Usually doesn't have a simple text output to save
    )
    print(f"Orchestrator Agent created using model: {model_name} with {len(sub_agents)} sub-agents.")
    return orchestrator

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Need to create dummy sub-agents first
#     dummy_executor = Agent(name="DummyExecutor", description="Does dummy work.")
#     orchestrator = create_orchestrator_agent(sub_agents=[dummy_executor])
#     # Add test code here
#     pass
