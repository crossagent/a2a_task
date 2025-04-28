# 活动背景：集成 Notion 的 A2A 任务助手 (初始化)

## 1. 当前工作焦点

*   **项目初始化与规划:** 定义项目目标、范围、架构模式和技术选型。
*   **Memory Bank 创建:** 正在创建和完善核心 Memory Bank 文档 (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`)。

## 2. 近期变更

*   创建了 `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`。
*   根据讨论和 ADK 文档，多次修订了 `systemPatterns.md`，明确了框架职责与业务逻辑职责，特别是 Runner 的角色和 Agent 指令在流程驱动中的核心作用。

## 3. 下一步计划

1.  完成 `activeContext.md` 和 `progress.md` 的初始化。
2.  **调研 Notion Python SDK:** 查找合适的库（如 `notion-client`）并评估其功能是否满足需求（创建页面/任务、查询数据库/项目）。
3.  **设计 Notion Tool:** 基于选定的 SDK，详细设计 ADK `NotionTool` 需要包含的具体函数签名和逻辑。
4.  **设计 Agent 指令初稿:** 为 `Agent 1 (任务定义)` 和 `Agent 2 (任务分配)` 编写初步的 `instruction` prompt，体现其职责和预期的交互流程。

## 4. 当前决策与考虑

*   **交互模型:** 采用指令驱动的隐式协调模型，依赖高质量的 Agent 指令来引导流程，使用 Session State 主要传递数据。
*   **Notion 集成:** 优先尝试使用现有的 Python SDK 实现为 ADK Tool，暂不考虑 MCP Server。
*   **框架使用:** 充分利用 ADK 框架能力，避免在业务逻辑中重复造轮子（例如 Agent 间路由）。

## 5. 重要模式与偏好

*   **文档驱动:** 遵循 `.clinerules`，优先维护 Memory Bank 文档。
*   **代码结构:** 遵循用户提供的示例，将 Agent 相关代码（定义、指令、工具）按模块组织。
*   **清晰职责:** 在设计中明确框架与业务逻辑的界限。

## 6. 项目洞察与学习

*   深入理解了 ADK Runtime 的事件驱动机制和 Runner 的编排角色。
*   明确了 Agent 指令 (Prompt Engineering) 在基于 LLM 的 Agent 系统中的极端重要性，它直接影响流程控制和任务执行效果。
