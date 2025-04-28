# 项目进展：集成 Notion 的 A2A 任务助手 (初始化)

## 1. 当前状态

*   项目处于**规划和初始化阶段**。
*   核心 Memory Bank 文档已初步创建。
*   尚未编写任何业务逻辑代码 (Agent, Tool)。

## 2. 已完成功能 (What Works)

*   无 (项目刚启动)。

## 3. 待构建功能 (What's Left to Build)

*   **Notion Python SDK 调研与选型。**
*   **Notion Tool 实现:**
    *   创建任务 (`create_notion_task`)。
    *   列出项目 (`list_notion_projects`)。
    *   (可能) 按名称查找项目 (`find_notion_project_by_name`)。
    *   API 密钥的安全处理。
*   **Agent 1 (任务定义) 实现:**
    *   Agent 定义 (`agent.py`)。
    *   核心指令 (`prompts.py`)，用于引导对话、提取信息、存入 Session State。
*   **Agent 2 (任务分配) 实现:**
    *   Agent 定义 (`agent.py`)。
    *   核心指令 (`prompts.py`)，用于从 Session State 读取信息、调用 Notion Tool、处理结果、与用户确认（如果需要）、反馈最终结果。
*   **主应用入口 (`main.py`):**
    *   初始化 Runner 和 SessionService。
    *   配置根 Agent (可能是 Agent 1)。
    *   处理用户输入并启动 Runner。
*   **集成与测试:**
    *   单元测试 (特别是 Notion Tool)。
    *   端到端交互测试。

## 4. 已知问题与挑战

*   **Notion SDK/API:** 需要确认所选 SDK 的稳定性和功能覆盖范围，以及 Notion API 的具体限制。
*   **Prompt Engineering:** 设计高质量的 Agent 指令以确保流畅、准确的交互和流程控制，将是一个关键挑战。
*   **状态管理:** `InMemorySessionService` 无法持久化，长期运行需要考虑替换方案。
*   **错误处理:** 需要在 Tool 和 Agent 逻辑中添加健壮的错误处理。

## 5. 项目决策演变

*   (初始化) 确定采用指令驱动的隐式协调模型，而非显式状态标志或 `sub_agents` 委托。
*   (初始化) 决定优先使用 Python SDK 实现 Notion Tool。
