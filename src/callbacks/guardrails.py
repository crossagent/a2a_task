# -*- coding: utf-8 -*-
"""
Defines Callback functions for implementing safety guardrails and policy enforcement.

Used with ADK's callback mechanism (e.g., before_model_callback, before_tool_callback)
to inspect requests, arguments, or results and potentially block or modify actions
based on predefined safety rules or policies.

Relevant ADK Classes:
- google.adk.agents.callback_context.CallbackContext
- google.adk.tools.tool_context.ToolContext
- google.adk.tools.base_tool.BaseTool
- google.adk.models.llm_request.LlmRequest
- google.adk.models.llm_response.LlmResponse
- typing.Dict, typing.Any, typing.Optional
"""

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # For constructing LlmResponse content
from typing import Optional, Dict, Any

# Placeholder for guardrail callback functions

def block_sensitive_keywords_in_input(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Example before_model_callback to block requests containing sensitive keywords.

    Args:
        callback_context: Context object for the agent.
        llm_request: The request payload intended for the LLM.

    Returns:
        An LlmResponse to block the call if keywords are found, otherwise None.
    """
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_sensitive_keywords running for agent: {agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---")

    # Define sensitive keywords (example)
    sensitive_keywords = ["CONFIDENTIAL", "SECRET_PROJECT_X", "PII_DATA"] # Case-insensitive check below

    for keyword in sensitive_keywords:
        if keyword in last_user_message_text.upper():
            error_msg = f"Request blocked due to sensitive keyword '{keyword}'."
            print(f"--- Callback Error: {error_msg} ---")
            # Block the LLM call by returning an LlmResponse
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"Processing blocked due to policy violation regarding keyword: {keyword}.")]
                )
            )

    print(f"--- Callback: No sensitive keywords found. Allowing LLM call for {agent_name}. ---")
    return None # Allow the request to proceed


def restrict_tool_by_argument_value(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """
    Example before_tool_callback to restrict tool usage based on argument values.

    Args:
        tool: The tool about to be executed.
        args: The arguments dictionary intended for the tool.
        tool_context: Context object for the tool execution.

    Returns:
        None if allowed, or a dictionary to block the tool call.
    """
    tool_name = tool.name
    print(f"--- Callback: restrict_tool_by_argument running for tool '{tool_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # Example Policy: Prevent deleting items marked as 'critical'
    if tool_name == "delete_item_tool": # Assuming a hypothetical delete tool
        item_id = args.get("item_id")
        # Assume we can check the item's status (e.g., from state or another tool call - complex!)
        # For simplicity, let's check if the ID itself indicates criticality
        if item_id and "CRITICAL" in item_id.upper():
            error_msg = f"Policy violation: Deletion of critical item '{item_id}' is not allowed."
            print(f"--- Callback Error: {error_msg} Blocking tool call. ---")
            return {"status": "error", "error_message": error_msg}

    # Example Policy: Limit API calls based on cost estimate in state
    if tool_name == "expensive_api_call_tool":
        estimated_cost = args.get("estimated_cost", 0)
        cost_limit = tool_context.state.get("user:api_cost_limit", 1.00) # Get limit from user state
        if estimated_cost > cost_limit:
             error_msg = f"Estimated cost ({estimated_cost}) exceeds user limit ({cost_limit}). Blocking tool call."
             print(f"--- Callback Error: {error_msg} Blocking tool call. ---")
             return {"status": "error", "error_message": error_msg}


    print(f"--- Callback: Tool '{tool_name}' allowed by argument restriction guardrail. ---")
    return None # Allow tool execution

# --- Example Usage (how to assign in Agent definition) ---
# from google.adk.agents import LlmAgent
# secure_agent = LlmAgent(
#     name="SecureAgent",
#     model="gemini-2.0-flash",
#     tools=[some_tool, delete_item_tool, expensive_api_call_tool],
#     before_model_callback=block_sensitive_keywords_in_input,
#     before_tool_callback=restrict_tool_by_argument_value,
#     # ... other params
# )
