# 系统模式：AI 流程自动化 Agent 团队 (基于 Agent 转移)

本文档描述了用于 AI 流程自动化工具的核心 Agent 团队架构。该架构旨在将用户的自然语言请求转化为由 AI Agent 协作执行的结构化工作流，并利用 ADK 的 `transfer_to_agent` 机制实现自然的交互点。

## 核心 Agent 角色与职责 (重构版)

团队由以下核心 Agent 角色组成：

1.  **WorkflowPlannerAgent (工作流规划器)**:
    *   **职责**: 接收用户的初始请求。分析用户意图（例如，“记录任务”、“查询信息”）。根据意图，动态生成一个结构化的**工作流计划**（Agent 执行序列，如 `['DataCollectorAgent', 'TaskClassifierAgent', 'NotionWriterAgent']`）。
    *   **输入**: 用户的自然语言请求。
    *   **输出**: 结构化的工作流计划。**此计划将通过更新 OrchestratorAgent 的 instructions 来传递**。
    *   **实现**: 通常是一个 `LlmAgent`。

2.  **OrchestratorAgent (协调器 / Root Agent)**:
    *   **职责**: 作为 Root Agent，根据 `WorkflowPlannerAgent` 在其 instructions 中设定的**当前工作流计划**，按顺序协调子 Agent 的执行。管理 `Session State`。**关键职责**：
        *   读取自身 instructions 中的工作流计划和当前执行步骤。如果不存在，就向WorkflowPlannerAgent获取。
        *   根据工作流调用 `transfer_to_agent` 将控制权转移给计划中的下一个子 Agent。
        *   在子 Agent 返回控制权后，更新执行状态，并决定下一步（转移给下一个 Agent 或结束流程）。
    *   **输入**: 更新后的 instructions (包含工作流计划)，Session State，子 Agent 返回的控制权。
    *   **输出**: 驱动整个流程按计划执行，最终可能汇总结果。
    *   **实现**: ADK 框架中的 **Root Agent** (`LlmAgent`)。其 instructions 需要包含用于存储和跟踪工作流计划及执行状态的字段。

3.  **DataCollectorAgent (信息收集器 / Sub-Agent)**:
    *   **职责**: 负责与用户进行**交互式对话**以收集完成任务所需的详细信息。
    *   **触发**: 由 `OrchestratorAgent` 通过 `transfer_to_agent` 调用。
    *   **交互**: 根据CriticAgent的判断结果，决定是否交还控制权，如果信息不完整，则继续等待用户输入。
    *   **完成**: 当判断信息收集完整时（可能通过内部调用 Critic Agent），在 Session State 中记录收集结果，并结束执行，将控制权明确交还给 `OrchestratorAgent`。
    *   **实现**: ADK 框架中的 **Sub-Agent** (`LlmAgent`)。

4.  **TaskClassifierAgent (任务分类器 / Sub-Agent)**:
    *   **职责**: 对收集到的信息进行分类，并可能需要通过**交互式对话**让用户确认或修正分类结果。
    *   **触发**: 由 `OrchestratorAgent` 通过 `transfer_to_agent` 调用。
    *   **交互**: 进行分类。如果需要用户确认，生成分类建议和提示信息，等待用户确认。
    *   **完成**: 用户确认或分类完成后，在 Session State 中记录分类结果，并结束执行，将控制权交还给 `OrchestratorAgent`。
    *   **实现**: ADK 框架中的 **Sub-Agent** (`LlmAgent`)。

5.  **NotionWriterAgent (Notion 写入器 / Sub-Agent)**:
    *   **职责**: 负责将最终确认的信息写入 Notion。处理可能的 API 交互或错误。
    *   **触发**: 由 `OrchestratorAgent` 通过 `transfer_to_agent` 调用。
    *   **交互**: 尝试写入 Notion。如果遇到问题需要用户输入（例如，API Key 无效、确认覆盖等），生成提示信息，等待用户输入。
    *   **完成**: 成功写入或处理完用户交互后，结束执行，将控制权交还给 `OrchestratorAgent`。
    *   **实现**: ADK 框架中的 **Sub-Agent** (`LlmAgent` 或 `CustomAgent`，取决于交互复杂性)。



## 基于 Agent 转移的交互流程

此架构的核心是利用 ADK 的 `transfer_to_agent` 机制来管理控制流和用户交互：

*   **自然交互点**: 当一个负责交互的子 Agent（如 `DataCollectorAgent`, `TaskClassifierAgent`, `NotionWriterAgent`）需要用户输入时，它会完成当前的处理逻辑，生成提示信息，然后等待。
*   **Orchestrator 驱动**: `OrchestratorAgent` 根据 `WorkflowPlannerAgent` 预设在其 instructions 中的计划，按部就班地将控制权转移给下一个子 Agent。
*   **状态传递**: 各 Agent 通过读写共享的 `Session State` 来传递信息。

## 示例应用：Notion 任务助手架构 (重构版)

```mermaid
graph TD
    A[User: Initial Request (e.g., "记录一个任务")] --> B(WorkflowPlannerAgent);
    B -- Analyze Intent & Generate Plan --> PlanUpdate((Update Orchestrator Instructions));
    PlanUpdate -- Plan = [DataCollector, Classifier, Writer] --> C{Orchestrator (Root)};

    subgraph Step 1: Collect Details
        C -- Reads Plan, Step 1: DataCollector --> Transfer1(transfer_to_agent: DataCollectorAgent);
        D[DataCollectorAgent] -- Needs Input --> Wait1[Wait User Input];
        UserIn1[User: Provides Input] --> D;
        D -- Data Sufficient --> Return1(Return Control);
        Return1 -- Updates State --> S[(Session State)];
        Return1 --> C;
    end

    subgraph Step 2: Classify Task
        C -- Reads Plan, Step 2: Classifier --> Transfer2(transfer_to_agent: TaskClassifierAgent);
        E[TaskClassifierAgent] -- Needs Confirmation --> Wait2[Wait User Input];
        UserIn2[User: Confirms/Corrects] --> E;
        E -- Classification Done --> Return2(Return Control);
        Return2 -- Updates State --> S;
        Return2 --> C;
    end

    subgraph Step 3: Write to Notion
        C -- Reads Plan, Step 3: Writer --> Transfer3(transfer_to_agent: NotionWriterAgent);
        F[NotionWriterAgent] -- Reads State --> S;
        F -- Execute Write --> API[(Notion API)];
        API -- Success/Failure --> F;
        F -- Needs Input (e.g., API Key?) --> Wait3[Wait User Input];
        UserIn3[User: Provides Input] --> F;
        F -- Write Complete --> Return3(Return Control);
        Return3 --> C;
    end

    C --> H[Process Complete];

    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#9cf,stroke:#333,stroke-width:2px
```

## 设计原则

*   **职责分离**: 每个 Agent 都有明确、单一的职责。
*   **Agent 转移优先**: 优先使用 `transfer_to_agent` 处理涉及多轮交互或需要独立上下文的任务环节。
*   **自然交互**: 通过 Agent 回合结束来创造等待用户输入的时机。
*   **Orchestrator 协调**: Root Agent 负责根据动态计划驱动流程。
*   **状态共享**: 通过 Session State 在 Agent 间传递数据。
*   **模块化与可扩展性**: 易于添加、修改或替换单个 Agent。

---
*旧内容（LoopAgent 与阻塞式交互）已被移除。*
