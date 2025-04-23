# 项目进展：AI 流程自动化工具

## 当前状态

*   **阶段**: 概念设计与初始文档化阶段。
*   **已完成**:
    *   初步的产品概念讨论。
    *   确定了基于 Google ADK 的技术方向。
    *   设计了核心的 Agent 团队架构 (Parser, Orchestrator, Executors, Expert)。
    *   明确了使用 Callbacks 进行格式检查的机制。
    *   初始化了 Memory Bank 的核心文档 (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`)。

## 下一步工作 (To-Do)

*   **细化工作流示例**: 选择 1-2 个具体的工作流程（例如，“生成市场分析报告”、“处理客户反馈”），详细设计其步骤、涉及的 Agent、Tools、状态传递和审核点。
*   **设计 Workflow Parser**: 深入研究如何将自然语言流程描述转化为结构化的执行计划。探索所需的技术（提示工程、模型选择、可能的结构化输出格式）。
*   **定义核心 Tools**: 为选定的工作流示例，初步定义 Executor 和 Expert Agent 所需的核心 Tools (Python 函数原型和 Docstrings)。
*   **MCP 服务集成**: 调研用户提到的 MCP 服务，并思考如何将其集成到 Agent 的 Tools 或整体架构中。
*   **原型搭建**: (远期) 基于 ADK 搭建一个简单的原型，实现一个基础的工作流。

## 已知问题与挑战

*   **自然语言理解的复杂性**: 将自由形式的自然语言精确映射到结构化流程计划是一个重大挑战。
*   **Agent 协作的鲁棒性**: 如何确保 Agent 间的信息传递、任务交接准确无误，以及如何处理执行过程中的错误和异常。
*   **状态管理的扩展性**: `InMemorySessionService` 不适用于生产环境，需要考虑持久化方案。
*   **用户交互界面**: 如何设计用户友好的界面来定义流程、监控进度和进行干预。

## 决策演变
*   (2025-04-23) 明确使用 Callbacks 负责格式检查，与 Expert Agent 的质量检查区分开。
