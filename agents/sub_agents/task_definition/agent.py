import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import TypeAlias

# 导入prompts
from . import prompts

# 从task_assignment模块导入task_assignment_agent实例而非整个模块
# from agents.sub_agents.task_assignment.agent import task_assignment_agent

# 导入Notion工具
from agents.tools.notion_tool import get_notion_database_schema

# TODO: Define any tools used directly by Agent 1 (if any, besides calling Agent 2)
# For this project, Agent 1 primarily interacts with the user and passes state to Agent 2.
# It might not need direct access to NotionTool functions, but rather call Agent 2 which uses NotionTool.

# Define Agent 1 (Task Definition Agent)
task_definition_agent = Agent(
    # TODO: Configure model
    model=os.getenv("ADK_AGENT_MODEL", 'gemini-2.0-flash-001'), # Assuming a generic model env var
    name="task_definition_agent",
    description="这个代理与用户交互，定义任务及其细节，并从Notion数据库中读取结构信息。",
    # 添加指令
    instruction=prompts.TASK_DEFINITION_INSTRUCTION,
    # 添加task_assignment_agent作为子代理
    # sub_agents=[task_assignment_agent],
    # 为代理添加Notion工具，不使用AgentTool以允许多轮对话
    tools=[get_notion_database_schema],
    # TODO: Add callbacks if necessary (e.g., to process user input or state before/after agent call)
    # before_agent_callback=...,
    # after_agent_callback=...,
)

# TODO: Implement the logic within Agent 1's instruction and potentially callbacks/tools
# to guide the conversation, extract task details, and trigger Agent 2.
