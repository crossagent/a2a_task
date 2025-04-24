# 项目进展：AI 流程自动化工具

## 当前状态

*   **阶段**: 概念设计与初始文档化阶段。
*   **已完成**:
    *   初步的产品概念讨论。
    *   确定了基于 Google ADK 的技术方向。
    *   设计了核心的 Agent 团队架构 (Parser, Orchestrator, Executors, Expert)。
    *   明确了使用 Callbacks 进行格式检查的机制。
    *   初始化了 Memory Bank 的核心文档 (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`)。
    *   **实现了人工审核流程的核心代码**:
        *   修改 `DataCollectionCriticAgent` 输出结构化 JSON (`status`, `feedback`)。
        *   创建了 `HumanReviewTool` (基于 `LongRunningFunctionTool` 和 Events) 用于处理人工交互。
        *   (旧) 更新了 `OrchestratorAgent` 指令以协调 Critic 和 `HumanReviewTool` 的调用（此逻辑已修订）。
    *   **修订并更新了人工审核流程文档 (2025-04-24)**:
        *   更新 `memory-bank/systemPatterns.md`：区分了 Loop 内信息补充和 Orchestrator 最终确认两种模式，并更新了流程图。
        *   更新 `memory-bank/activeContext.md`：反映了修订后的流程决策和下一步编码计划。
        *   更新 `memory-bank/progress.md`：记录文档更新情况。

## 下一步工作 (To-Do)

*   **修改 `DetailCollectorLoop` (`src/agents/loops/detail_collector_loop.py`)**: 实现循环内部调用 `HumanReviewTool` 进行信息补充的逻辑，处理返回的补充数据。
*   **修改 `OrchestratorAgent` (`src/agents/orchestrator.py`)**: 调整逻辑，使其仅在 `DetailCollectorLoop` 成功完成后处理最终确认步骤。
*   **定义/修改工作流计划 (`workflow_plan`)**: 在计划中明确反映 Loop 内补充和 Orchestrator 最终确认的流程顺序。
*   **实现事件处理与 UI/外部交互**: 开发监听 `human_confirmation_needed` 和 `human_input_needed` 事件、呈现信息给用户、捕获响应的机制。
*   **实现用户响应传递**: 将用户响应（补充数据或确认决定）通过 `human_response_received` 事件传递回 ADK 框架，以恢复 `HumanReviewTool`。
*   **测试端到端流程**: 集成所有部分进行测试。
*   **(原有) 细化工作流示例**: 选择 1-2 个具体的工作流程，详细设计其步骤。
*   **(原有) 设计 Workflow Parser**: 深入研究 NLU 到结构化计划的转换。
*   **定义核心 Tools**: (继续) 为选定的工作流示例定义 Tools。
*   **MCP 服务集成**: (继续) 调研并思考集成 MCP 服务。
*   **原型搭建**: (远期) 基于 ADK 搭建原型。

## 已知问题与挑战

*   **自然语言理解的复杂性**: 将自由形式的自然语言精确映射到结构化流程计划是一个重大挑战。
*   **Agent 协作的鲁棒性**: 如何确保 Agent 间的信息传递、任务交接准确无误，以及如何处理执行过程中的错误和异常。
*   **状态管理的扩展性**: `InMemorySessionService` 不适用于生产环境，需要考虑持久化方案。
*   **用户交互界面**: 如何设计用户友好的界面来定义流程、监控进度和进行干预。

## 决策演变
*   (2025-04-23) 明确使用 Callbacks 负责格式检查，与 Expert Agent 的质量检查区分开。
