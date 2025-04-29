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

async def get_notion_database_schema(tool_context: ToolContext, database_id: str) -> dict:
    """Gets the properties of a Notion database."""
    client = _get_notion_client()
    try:
        # 调用Notion API获取数据库信息
        database = client.databases.retrieve(database_id=database_id)
        
        # 从响应中提取属性名称和类型
        properties = {}
        for prop_name, prop_details in database.get('properties', {}).items():
            prop_type = prop_details.get('type')
            properties[prop_name] = prop_type
            
        print(f"Successfully retrieved properties for database ID: {database_id}")
        return properties
    except Exception as e:
        print(f"Error retrieving database properties: {e}")
        # 在发生错误时返回一个空字典或者抛出异常
        raise ValueError(f"Failed to retrieve database properties: {e}")

async def find_notion_project(tool_context: ToolContext, project_database_id: str, project_name: str) -> str | None:
    """Finds a project page in the project database by name."""
    client = _get_notion_client()
    try:
        # 构建查询过滤条件 - 假设项目名称存储在标题属性中
        # 首先获取数据库属性，找到标题属性的名称
        properties = await get_notion_database_schema(tool_context, project_database_id)
        title_property = next((prop_name for prop_name, prop_type in properties.items() 
                              if prop_type == "title"), None)
        
        if not title_property:
            raise ValueError("Could not find title property in the database")
        
        # 构建查询过滤条件
        filter_params = {
            "property": title_property,
            "title": {
                "equals": project_name
            }
        }
        
        # 查询数据库
        response = client.databases.query(
            database_id=project_database_id,
            filter=filter_params
        )
        
        # 检查是否有匹配的项目
        results = response.get("results", [])
        if results:
            project_page_id = results[0].get("id")
            print(f"Found project '{project_name}' with ID: {project_page_id}")
            return project_page_id
        else:
            print(f"No project found with name: {project_name}")
            return None
    except Exception as e:
        print(f"Error finding project: {e}")
        return None

async def create_notion_task(tool_context: ToolContext, task_database_id: str, properties: dict):
    """Creates a new task page in the task database."""
    client = _get_notion_client()
    try:
        # 构建适合Notion API的属性格式
        formatted_properties = {}
        
        # 获取数据库属性以了解每个字段的类型
        db_properties = await get_notion_database_schema(tool_context, task_database_id)
        
        # 根据不同属性类型格式化数据
        for prop_name, prop_value in properties.items():
            if prop_name not in db_properties:
                print(f"Warning: Property '{prop_name}' not found in database schema")
                continue
                
            prop_type = db_properties[prop_name]
            
            # 根据属性类型格式化
            if prop_type == "title":
                formatted_properties[prop_name] = {
                    "title": [{"text": {"content": str(prop_value)}}]
                }
            elif prop_type == "rich_text":
                formatted_properties[prop_name] = {
                    "rich_text": [{"text": {"content": str(prop_value)}}]
                }
            elif prop_type == "status":
                formatted_properties[prop_name] = {
                    "status": {"name": str(prop_value)}
                }
            elif prop_type == "relation" and isinstance(prop_value, str):
                formatted_properties[prop_name] = {
                    "relation": [{"id": prop_value}]
                }
            elif prop_type == "relation" and isinstance(prop_value, list):
                formatted_properties[prop_name] = {
                    "relation": [{"id": item} for item in prop_value]
                }
            elif prop_type == "select":
                formatted_properties[prop_name] = {
                    "select": {"name": str(prop_value)}
                }
            elif prop_type == "date" and isinstance(prop_value, dict):
                formatted_properties[prop_name] = {
                    "date": prop_value  # 假设已经是正确格式: {"start": "2023-08-15", "end": "2023-08-20"}
                }
            elif prop_type == "checkbox" and isinstance(prop_value, bool):
                formatted_properties[prop_name] = {
                    "checkbox": prop_value
                }
            else:
                # 对于其他类型，尝试按照一般格式
                formatted_properties[prop_name] = {
                    prop_type: prop_value
                }
        
        # 创建页面
        response = client.pages.create(
            parent={"database_id": task_database_id},
            properties=formatted_properties
        )
        
        print(f"任务已成功创建，页面链接: {response.get('url')}")
        return response.get('id')
    except Exception as e:
        print(f"创建任务时出错: {e}")
        raise ValueError(f"无法创建任务: {e}")

# Note: These functions will be exposed as tools by the Agent that uses them.
# The Agent definition will list these functions in its 'tools' parameter.

async def main():
    """测试Notion工具的主要功能"""
    import asyncio
    from unittest.mock import MagicMock
    
    # 从环境变量获取必要的配置
    task_database_id = os.getenv("NOTION_TASK_DATABASE_ID")
    project_database_id = os.getenv("NOTION_PROJECT_DATABASE_ID")
    project_name = os.getenv("NOTION_TEST_PROJECT_NAME", "测试项目")
    
    if not task_database_id or not project_database_id:
        print("请设置以下环境变量:")
        print("- NOTION_API_KEY: Notion API密钥")
        print("- NOTION_TASK_DB_ID: 任务数据库ID")
        print("- NOTION_PROJECT_DB_ID: 项目数据库ID")
        print("- NOTION_TEST_PROJECT_NAME: (可选)用于测试的项目名称")
        return
    
    # 创建一个模拟的工具上下文
    mock_tool_context = MagicMock()
    
    try:
        print("=== 测试 get_notion_database_properties ===")
        task_db_properties = await get_notion_database_schema(mock_tool_context, task_database_id)
        print(f"任务数据库属性: {task_db_properties}")
        
        project_db_properties = await get_notion_database_schema(mock_tool_context, project_database_id)
        print(f"项目数据库属性: {project_db_properties}")
        
        print("\n=== 测试 find_notion_project ===")
        project_id = await find_notion_project(mock_tool_context, project_database_id, project_name)
        if project_id:
            print(f"找到项目 '{project_name}', ID: {project_id}")
        else:
            print(f"未找到项目: '{project_name}'")
        
        if project_id:
            print("\n=== 测试 create_notion_task ===")
            # 创建测试任务的属性
            task_properties = {}
            
            # 查找标题属性
            title_property = next((prop_name for prop_name, prop_type in task_db_properties.items() 
                                  if prop_type == "title"), None)
            if not title_property:
                print("未找到标题属性，无法创建任务")
                return
                
            # 查找关系属性(关联到项目)
            relation_property = next((prop_name for prop_name, prop_type in task_db_properties.items() 
                                     if prop_type == "relation"), None)
            
            # 设置任务属性
            task_properties[title_property] = f"测试任务 - {asyncio.get_event_loop().time()}"
            
            # 如果找到关系属性，添加项目关联
            if relation_property:
                task_properties[relation_property] = project_id
            
            # 查找状态属性
            status_property = next((prop_name for prop_name, prop_type in task_db_properties.items() 
                                   if prop_type == "status"), None)
            if status_property:
                task_properties[status_property] = "待处理"  # 假设存在"待处理"状态选项
            
            # 创建任务
            task_id = await create_notion_task(mock_tool_context, task_database_id, task_properties)
            print(f"创建的任务ID: {task_id}")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
