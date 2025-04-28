import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext

# 导入Agent 2的prompts
from . import prompts

# 导入Notion工具函数
from ....tools.notion_tool import get_notion_database_properties, find_notion_project, create_notion_task

# 定义Agent 2 (任务分配代理)
task_assignment_agent = Agent(
    # 配置模型
    model=os.getenv("ADK_AGENT_MODEL"), # 假设使用通用模型环境变量
    name="task_assignment_agent",
    description="该代理接收任务详情并使用Notion工具在Notion中创建任务。",
    # 使用从prompts模块导入的指令
    instruction=prompts.TASK_ASSIGNMENT_INSTRUCTION,
    # 添加Agent 2使用的工具
    tools=[get_notion_database_properties, find_notion_project, create_notion_task],
    # TODO: 如有需要添加回调函数(例如，在代理调用前/后处理状态)
    # before_agent_callback=...,
    # after_agent_callback=...,
)

# TODO: 在Agent 2的指令和可能的回调中实现逻辑
# 处理来自状态的任务详情，调用Notion工具函数，并报告成功/失败。
