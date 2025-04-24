# 活动背景：AI 流程自动化工具

## 当前焦点

*   **实现人工审核流程**: 正在实现数据收集后的人工确认/补充信息流程。
*   **Agent 与 Tool 开发**: 涉及修改 Critic Agent、创建 Human Interaction Tool 以及调整 Orchestrator Agent 的逻辑。
*   **文档化**: 根据 `.clinerules` 要求，同步更新 Memory Bank 文档以反映代码变更。

## 近期决策与实现

*   **Critic 输出结构化**: `DataCollectionCriticAgent` 现在输出包含 `status` 和 `feedback` 的 JSON。
*   **Human Interaction Tool**: 创建了 `HumanReviewTool` (`src/tools/human_interaction_tools.py`)，使用 `LongRunningFunctionTool` 和 Events 处理人工交互。
*   **Orchestrator 协调 (修订)**: `OrchestratorAgent` (`src/agents/orchestrator.py`) 的职责调整为：在 `DetailCollectorLoop` **成功结束后**，根据最终状态（如最终 Critic 评估为 'complete'）**条件性地调用** `HumanReviewTool` 进行**最终确认**。
*   **Loop 结构确认 (修订)**: 确认 `DetailCollectorLoop` 内部包含 Collector 和 Critic。**关键修订**：如果 Critic 在循环中判断信息不完整 (`incomplete`)，`DetailCollectorLoop` **自身**将负责调用 `HumanReviewTool` 来请求用户**补充信息**，并将补充信息合并到状态中，用于后续迭代。

## 下一步计划

*   **更新 `memory-bank/systemPatterns.md`**: (已完成) 更新系统模式描述和流程图。
*   **更新 `memory-bank/activeContext.md`**: (当前步骤) 更新活动背景。
*   **更新 `memory-bank/progress.md`**: 记录文档更新和即将进行的编码工作。
*   **修改 `DetailCollectorLoop` (`src/agents/loops/detail_collector_loop.py`)**: 实现循环内部调用 `HumanReviewTool` 进行信息补充的逻辑，包括处理工具返回的补充数据。确保 `HumanReviewTool` 对 Loop 可用。
*   **修改 `OrchestratorAgent` (`src/agents/orchestrator.py`)**: 调整其指令或逻辑，使其仅在 `DetailCollectorLoop` 成功完成后处理最终确认步骤。
*   **定义/修改工作流计划**: 在工作流计划中反映 Loop 内部补充和 Orchestrator 最终确认的流程。
*   **实现事件处理与 UI/外部交互**: 开发监听 `human_confirmation_needed` 和 `human_input_needed` 事件、呈现信息给用户、捕获响应的机制。
*   **实现用户响应传递**: 将用户响应（补充数据或确认决定）通过 `human_response_received` 事件传递回 ADK 框架，以恢复 `HumanReviewTool`。
*   **测试端到端流程**: 集成所有部分进行测试。
*   (原有) 探讨如何实现 "Workflow Parser Agent"。
*   (原有) 考虑如何集成用户提到的 MCP 服务。

## 重要模式与偏好

*   **文档驱动**: 遵循 `.clinerules`，优先维护 Memory Bank 文档。
*   **模块化设计**: 将复杂功能拆分为职责单一的 Agent 和 Tool。
*   **分层交互**: 区分 Loop 内部驱动的信息补充和 Orchestrator 驱动的最终确认。
*   **事件驱动交互**: 使用 ADK Events 和 `LongRunningFunctionTool` 实现异步的人工交互。
*   **基于 ADK**: 利用 ADK 提供的核心机制（Delegation, State, Callbacks, Events, LoopAgent, LlmAgent）来实现设计。

## 项目洞察

*   将自然语言流程描述转化为机器可执行的结构化计划是本项目的核心挑战和创新点。
*   ADK 框架与项目设想高度契合，可以作为坚实的技术基础。
*   实现健壮的人工交互需要 Agent/Tool、Orchestrator 和外部事件处理/UI 之间的紧密协调。
