import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import TypeAlias

# 导入prompts
from . import prompts

# 导入子代理
from agents.sub_agents.task_definition.agent import task_definition_agent
#from agents.sub_agents.task_assignment.agent import task_assignment_agent

# 导入Notion工具
from agents.tools.notion_tool import get_notion_database_schema, find_notion_project

# 定义Root Agent (任务管理代理)
root_agent = Agent(
    model=os.getenv("ADK_AGENT_MODEL", 'gemini-2.0-flash-001'),
    name="task_management_agent",
    description="这个代理作为任务管理的入口点，负责处理任务查询和跳转到任务创建。",
    instruction=prompts.ROOT_AGENT_INSTRUCTION,
    # 添加子代理，用于任务定义和任务分配
    sub_agents=[task_definition_agent, 
                #task_assignment_agent
                ],
    # 为代理添加Notion工具，用于查询任务
    tools=[get_notion_database_schema, find_notion_project],
)
