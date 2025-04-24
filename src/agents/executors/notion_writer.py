# -*- coding: utf-8 -*-
"""
Defines an example Executor Agent: Notion Writer.

This agent is responsible for taking processed and validated data from the
session state and writing it to a Notion database or page using specific tools.

Relevant ADK Classes:
- google.adk.agents.Agent: Can be a simple Agent if logic is straightforward.
- google.adk.agents.LlmAgent: If it needs to format data before writing.
- google.adk.tools.ToolContext: Accessing session state to get the data to write.
- src.tools.notion_tools: Contains the actual functions (tools) for Notion API calls.
"""

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import ToolContext
from typing import List, Optional, Callable

# Placeholder for the Notion Writer Agent definition

def create_notion_writer_agent(
    notion_tools: List[Callable], # Expects tools like add_to_notion_database
    model_name: str = "gemini-2.0-flash", # Only used if LlmAgent is chosen
    use_llm: bool = False, # Set to True if formatting/reasoning needed
    before_tool_cb: Optional[callable] = None, # e.g., Input format check
    after_tool_cb: Optional[callable] = None,
) -> Agent:
    """
    Factory function to create the Notion Writer Agent.

    Args:
        notion_tools: A list of functions (tools) for interacting with Notion.
        model_name: The LLM model name (if use_llm is True).
        use_llm: Whether to use LlmAgent (for formatting) or a simpler Agent.
        before_tool_cb: Optional before_tool_callback.
        after_tool_cb: Optional after_tool_callback.

    Returns:
        An instance of the Notion Writer Agent.
    """
    instructions = (
        "You are a Notion Writer. Your task is to take the final, validated data "
        "from the session state (e.g., keys 'validated_task_details', 'validated_classification') "
        "and use the provided Notion tools (e.g., 'add_to_notion_database') to write this information to Notion. "
        "Ensure you pass the correct arguments to the tool based on the data in the state."
    )

    agent_name = "NotionWriterAgent"
    description = "Writes validated data to Notion using specific tools."

    if use_llm:
        writer_agent = LlmAgent(
            name=agent_name,
            model=model_name,
            instruction=instructions,
            description=description,
            tools=notion_tools,
            before_tool_callback=before_tool_cb,
            after_tool_callback=after_tool_cb,
        )
        print(f"Notion Writer Agent (LlmAgent) created using model: {model_name}")
    else:
        # If no complex formatting is needed, a simple Agent might suffice,
        # relying purely on the Orchestrator to provide exact data and tool call instructions.
        # However, LlmAgent is often more robust for mapping state data to tool args.
        # For simplicity, we'll default to LlmAgent structure but note that
        # a CustomAgent implementation could also work if the logic is fixed.
        writer_agent = LlmAgent( # Using LlmAgent for consistency, even if simple
            name=agent_name,
            model=model_name, # Still needs a model, though might not use complex reasoning
            instruction=instructions, # Instructions guide tool use
            description=description,
            tools=notion_tools,
            before_tool_callback=before_tool_cb,
            after_tool_callback=after_tool_cb,
        )
        print(f"Notion Writer Agent (LlmAgent - simple use) created.")


    return writer_agent

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Define dummy Notion tool
#     def dummy_add_to_notion(task_data: dict) -> dict:
#         print(f"TOOL: Writing to Notion: {task_data}")
#         return {"status": "success", "page_id": "12345"}
#
#     writer = create_notion_writer_agent(notion_tools=[dummy_add_to_notion])
#     # Add test code here, simulating state and running the agent
#     pass
