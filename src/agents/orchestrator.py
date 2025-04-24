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

import json
from typing import List, Optional, Dict, Any
from google.adk.agents import LlmAgent, Agent
from google.adk.sessions import Session, ToolContext # Added ToolContext
from google.adk.events import Event
# TODO: Import WorkflowPlan model when defined
# from src.models.workflow_plan import WorkflowPlan

# Import the human review tool CLASS and relevant state keys
from src.tools.human_interaction_tools import HumanReviewTool, STATE_DATA_CRITIQUE, STATE_HUMAN_RESPONSE
from src.agents.critics.data_collection_critic import STATE_COLLECTED_DATA, STATE_DATA_CRITIQUE # Import critic output key

# Placeholder for the Orchestrator Agent definition
# This agent will need complex instructions to:
# 1. Read the workflow plan from state.
# 2. Determine the current step.
# 3. Delegate to the appropriate sub-agent (Executor, Expert, Loop).
# 4. Handle events (e.g., escalate, completion signals).
# 5. Update state with progress.

def create_orchestrator_agent(
    sub_agents: List[Agent],
    model_name: str = "gemini-2.5-flash",
    # Optional tools can still be passed, but HumanReviewTool is added internally
    extra_tools: Optional[List[Any]] = None,
    before_model_cb: Optional[callable] = None,
    after_model_cb: Optional[callable] = None,
    before_tool_cb: Optional[callable] = None,
    after_tool_cb: Optional[callable] = None,
) -> LlmAgent:
    """
    Factory function to create the Orchestrator Agent.

    Args:
        sub_agents: A list of sub-agent instances (Executors, Experts, Loops) that this orchestrator can delegate to.
        model_name: The name of the LLM to use for the agent.
        extra_tools: Optional list of *additional* tools the orchestrator can use directly. HumanReviewTool is added automatically.
        before_model_cb: Optional before_model_callback function.
        after_model_cb: Optional after_model_callback function.
        before_tool_cb: Optional before_tool_callback function.
        after_tool_cb: Optional after_tool_callback function.

    Returns:
        An instance of the Orchestrator Agent.
    """
    # Internally create the HumanReviewTool for final confirmation
    human_review_tool_instance = HumanReviewTool()
    tool_name_confirm = human_review_tool_instance.name

    # Define detailed instructions including the human review step
    instructions = f"""
    You are the Orchestrator Agent, responsible for executing a workflow plan.
    The plan is stored in session state (key: 'workflow_plan').
    Track progress using state key 'current_step_index'.

    Workflow Steps:
    1.  Read the plan and identify the current step using 'current_step_index'.
    2.  Based on the step type:
        *   If it's a data collection step (e.g., involving 'DetailCollectorLoop'):
            a. Delegate to the 'DetailCollectorLoop' sub-agent. Assume the loop runs until the internal critic deems the data complete or max iterations are reached.
            b. **After the loop completes successfully**, read the **final** critique result from state key '{STATE_DATA_CRITIQUE}'.
            c. **Check the final critique status**:
                i.  If the final status is 'complete':
                    - Call the tool '{tool_name_confirm}' for **final confirmation**.
                    - Pass the final critique dictionary as the 'critique' argument to provide context for the confirmation request.
                    - Wait for the tool to finish (it's long-running).
                    - Read the human response, expecting a 'decision' field (e.g., from state key '{STATE_HUMAN_RESPONSE}' or directly from the tool's return value if configured).
                    - **Process the decision**: If 'approved', proceed to the next step in the plan. If 'rejected', stop the workflow or follow alternative steps defined in the plan (e.g., request clarification).
                ii. If the final status is 'incomplete' (this might indicate the loop hit max iterations without success) or missing/invalid, log an error or handle according to the plan (e.g., stop workflow).
        *   If it's another task type (e.g., writing data using 'NotionWriterAgent', classification using 'TaskClassifierAgent'):
            a. Delegate to the appropriate sub-agent based on the plan step and sub-agent descriptions.
            b. Pass necessary data from session state.
    3.  Handle events from sub-agents: If an 'escalate' event occurs during delegation, pause and wait for user input (the framework handles this).
    4.  Upon successful completion of a step (including human review if applicable), update 'current_step_index' in the session state.
    5.  Store any results from the step into the appropriate session state keys as defined by the plan.
    6.  If all steps in the plan are complete, indicate workflow completion.

    Use the provided sub-agents for delegation and the available tools (like {tool_name_confirm}) directly when needed.
    Be precise in reading from and writing to the specified session state keys.
    """

    # Combine internally created tool with any extra tools provided
    all_tools = [human_review_tool_instance]
    if extra_tools:
        all_tools.extend(extra_tools)

    orchestrator = LlmAgent(
        name="OrchestratorAgent",
        model=model_name,
        instruction=instructions,
        description="Coordinates workflow execution, including data critique and human review steps.",
        sub_agents=sub_agents, # Enable delegation
        tools=all_tools, # Make tools available
        before_model_callback=before_model_cb,
        after_model_callback=after_model_cb,
        before_tool_callback=before_tool_cb,
        after_tool_callback=after_tool_cb,
        # output_key=None # Usually doesn't have a simple text output to save
    )
    print(f"Orchestrator Agent created using model: {model_name} with {len(sub_agents)} sub-agents and {len(all_tools)} tools.")
    # Print available tools for verification
    tool_names = [t.name for t in all_tools] # type: ignore
    print(f"Orchestrator available tools: {tool_names}")
    return orchestrator

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Need to create dummy sub-agents first
#     dummy_executor = Agent(name="DummyExecutor", description="Does dummy work.")
#     orchestrator = create_orchestrator_agent(sub_agents=[dummy_executor])
#     # Add test code here
#     pass
