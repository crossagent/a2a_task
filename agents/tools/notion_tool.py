import os
from notion_client import Client
from google.adk.tools import ToolContext

# Global client instance (or initialize within functions if preferred)
_notion_client = None

def _get_notion_client():
    """Initializes and returns the Notion client."""
    global _notion_client
    if _notion_client is None:
        notion_api_key = os.getenv("NOTION_API_KEY")
        if not notion_api_key:
            raise ValueError("NOTION_API_KEY not found in environment variables.")
        _notion_client = Client(auth=notion_api_key)
    return _notion_client

async def get_notion_database_properties(tool_context: ToolContext, database_id: str) -> dict:
    """Gets the properties of a Notion database."""
    client = _get_notion_client()
    # TODO: Implement API call to get database properties using client.databases.retrieve(database_id)
    # Extract property names and types from the response.
    print(f"Attempting to get properties for database ID: {database_id}")
    # Placeholder return
    return {
        "任务名称": "title",
        "详情": "rich_text",
        "状态": "status",
        "所属项目": "relation" # Assuming this is the relation property name
    }

async def find_notion_project(tool_context: ToolContext, project_database_id: str, project_name: str) -> str | None:
    """Finds a project page in the project database by name."""
    client = _get_notion_client()
    # TODO: Implement API call to search for a page in the project database
    # using client.databases.query(project_database_id, filter={...})
    # Filter by the 'title' property matching project_name.
    print(f"Attempting to find project '{project_name}' in database ID: {project_database_id}")
    # Placeholder return (replace with actual search logic)
    if project_name == "示例项目": # Example placeholder
        return "example_project_page_id_123"
    return None

async def create_notion_task(tool_context: ToolContext, task_database_id: str, properties: dict):
    """Creates a new task page in the task database."""
    client = _get_notion_client()
    # TODO: Implement API call to create a page in the task database
    # using client.pages.create(...)
    # The 'properties' dict should be in the format required by the Notion API.
    print(f"Attempting to create task in database ID: {task_database_id} with properties: {properties}")
    # Placeholder for creation logic
    # response = client.pages.create(
    #     parent={"database_id": task_database_id},
    #     properties=properties
    # )
    # print(f"Notion page created: {response.get('url')}")
    pass

# Note: These functions will be exposed as tools by the Agent that uses them.
# The Agent definition will list these functions in its 'tools' parameter.
