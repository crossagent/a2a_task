"""
Agent creation module for creating and configuring the root agent.
"""

from google.adk.agents import Agent

# 导入必要的组件
from src.agents.parser import create_workflow_parser_agent
from src.agents.orchestrator import create_orchestrator_agent
from src.agents.executors.notion_writer import create_notion_writer_agent
from src.agents.loops.detail_collector_loop import create_detail_collector_loop
from src.agents.loops.classification_loop import create_classification_loop
from src.tools.notion_tools import add_task_to_notion_database
from src.tools.general_tools import get_current_datetime
from src.tools.analysis_tools import classify_text, extract_keywords
from src.callbacks.format_checkers import check_tool_input_args, check_tool_output_format
from src.callbacks.guardrails import block_sensitive_keywords_in_input

def create_root_agent():
    """创建根代理（orchestrator）及其所有子代理"""
    
    # --- 1. 创建工具 ---
    notion_tools = [add_task_to_notion_database]
    general_tools = [get_current_datetime]
    analysis_tools = [classify_text, extract_keywords]
    
    # --- 2. 创建回调 ---
    default_before_tool_cb = check_tool_input_args
    default_after_tool_cb = check_tool_output_format
    default_before_model_cb = block_sensitive_keywords_in_input
    
    # --- 3. 创建代理（自下而上：先创建执行器、专家、循环代理） ---
    # 创建 Notion 写入代理
    notion_writer = create_notion_writer_agent(
        notion_tools=notion_tools,
        before_tool_cb=default_before_tool_cb,
        after_tool_cb=default_after_tool_cb
    )
    
    # 创建循环代理
    detail_loop = create_detail_collector_loop(
        collector_model="gemini-2.0-flash",
        expert_model="gemini-2.0-flash",
        max_iterations=5,
        state_keys_to_check=["task_name", "status"]
    )
    
    classification_loop = create_classification_loop(
        classifier_model="gemini-2.0-flash",
        critic_model="gemini-2.0-flash",
        max_iterations=3,
        state_keys_to_check=["task_type", "task_priority"]
    )
    
    # 创建解析器代理
    workflow_parser = create_workflow_parser_agent(model_name="gemini-2.0-flash")
    
    # --- 4. 创建协调器（根代理） ---
    all_sub_agents = [
        notion_writer,
        detail_loop,
        classification_loop,
        workflow_parser
    ]
    
    orchestrator = create_orchestrator_agent(
        sub_agents=all_sub_agents,
        model_name="gemini-2.0-flash",
        before_model_cb=default_before_model_cb,
    )
    
    return orchestrator

# 提前创建根代理
root_agent = create_root_agent()