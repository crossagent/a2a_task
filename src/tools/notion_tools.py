# -*- coding: utf-8 -*-
"""
Defines Tools for interacting with the Notion API.

These functions provide agents with the capability to read from or write to
Notion databases and pages. Requires Notion API key and database ID configured
(e.g., via environment variables or session state).

Relevant ADK Classes:
- google.adk.tools.ToolContext: May be used to access session state (e.g., API keys, database IDs).
- (These are standard Python functions used *by* Agents).
"""

from google.adk.tools import ToolContext
import os
import requests # Requires 'requests' library: pip install requests
import json
from typing import Dict, Any, Optional

# --- Placeholder for Notion API interaction tools ---

# TODO: Securely manage Notion API Key and Database ID
# Options: Environment variables, configuration file, or session state (less secure for keys)
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID") # Specific DB for tasks

def add_task_to_notion_database(
    task_name: str,
    status: str,
    priority: Optional[str] = None,
    due_date: Optional[str] = None, # Expected format: "YYYY-MM-DD"
    project: Optional[str] = None,
    details: Optional[str] = None,
    tool_context: Optional[ToolContext] = None # To potentially access config from state
) -> Dict[str, Any]:
    """
    Adds a new task page to a pre-configured Notion database.

    Args:
        task_name (str): The name/title of the task.
        status (str): The status of the task (e.g., 'To Do', 'In Progress').
        priority (str, optional): Task priority (e.g., 'High', 'Medium', 'Low').
        due_date (str, optional): Due date in 'YYYY-MM-DD' format.
        project (str, optional): Associated project name.
        details (str, optional): Additional details or description for the task body.
        tool_context (ToolContext, optional): Provides access to session state.

    Returns:
        dict: Contains 'status' ('success' or 'error') and either 'page_id' or 'error_message'.
    """
    print(f"--- Tool: add_task_to_notion_database called for task: {task_name} ---")

    # Get config - prioritize context if available, fallback to env vars
    api_key = tool_context.state.get("app:NOTION_API_KEY", NOTION_API_KEY) if tool_context else NOTION_API_KEY
    database_id = tool_context.state.get("app:NOTION_DATABASE_ID", NOTION_DATABASE_ID) if tool_context else NOTION_DATABASE_ID

    if not api_key or not database_id:
        error_msg = "Notion API Key or Database ID is not configured."
        print(f"--- Tool Error: {error_msg} ---")
        return {"status": "error", "error_message": error_msg}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28", # Use a recent Notion API version
    }

    # Construct Notion page properties based on database schema
    # IMPORTANT: Adjust property names ('Name', 'Status', 'Priority', etc.) and types
    #            to EXACTLY match your Notion database schema.
    properties = {
        "Name": {"title": [{"text": {"content": task_name}}]},
        "Status": {"select": {"name": status}},
        # Add other properties if they exist and are provided
    }
    if priority:
        properties["Priority"] = {"select": {"name": priority}} # Assumes 'Priority' is a Select property
    if project:
        properties["Project"] = {"relation": [{"id": project}]} # Assumes 'Project' is a Relation property - requires project page ID
        # Alternative: If 'Project' is a Text property:
        # properties["Project"] = {"rich_text": [{"text": {"content": project}}]}
    if due_date:
        properties["Due Date"] = {"date": {"start": due_date}} # Assumes 'Due Date' is a Date property

    # Construct page content (body) if details are provided
    children = []
    if details:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": details}}]
            }
        })

    # Construct the API payload
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties,
    }
    if children:
        payload["children"] = children

    create_url = "https://api.notion.com/v1/pages"

    try:
        response = requests.post(create_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        page_id = response_data.get("id")
        print(f"--- Tool Success: Notion page created with ID: {page_id} ---")
        return {"status": "success", "page_id": page_id}

    except requests.exceptions.RequestException as e:
        error_msg = f"Notion API request failed: {e}. Response: {e.response.text if e.response else 'No response'}"
        print(f"--- Tool Error: {error_msg} ---")
        return {"status": "error", "error_message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"--- Tool Error: {error_msg} ---")
        return {"status": "error", "error_message": error_msg}

# --- Example Usage (for testing) ---
# if __name__ == '__main__':
#     # Make sure NOTION_API_KEY and NOTION_DATABASE_ID are set as environment variables
#     if not NOTION_API_KEY or not NOTION_DATABASE_ID:
#         print("Please set NOTION_API_KEY and NOTION_DATABASE_ID environment variables to test.")
#     else:
#         test_result = add_task_to_notion_database(
#             task_name="Test Task from ADK Tool",
#             status="To Do",
#             priority="Medium",
#             due_date="2025-12-31",
#             details="This is a test task added via the ADK tool."
#         )
#         print(f"Test Result: {test_result}")
