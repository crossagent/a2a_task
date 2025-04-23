# 系统模式：AI 流程自动化 Agent 团队

本文档描述了用于 AI 流程自动化工具的核心 Agent 团队架构。该架构旨在将用户的自然语言流程描述转化为由 AI Agent 协作执行的结构化工作流。

## 核心 Agent 角色与职责

团队由以下核心 Agent 角色组成：

1.  **Workflow Parser Agent (流程解析器)**:
    *   **职责**: 接收用户输入的**自然语言流程描述**。利用强大的 NLU 能力将其解析为一个**结构化的执行计划**（例如，一个包含步骤、所需 Executor 类型、输入/输出规范、Expert 审核点的列表或图）。
    *   **输入**: 用户的自然语言流程定义。
    *   **输出**: 结构化的流程计划 (存储在 Session State 中，或直接传递给 Orchestrator)。
    *   **实现**: 可以是一个独立的 Agent，在流程开始时首先被调用。

2.  **Orchestrator Agent (协调器 / Root Agent)**:
    *   **职责**: 读取结构化流程计划。根据计划**按步骤推进**工作流。管理 `Session State`（存储中间/最终交付物、状态信息）。在每个步骤，将任务**委托 (delegate)** 给合适的 Executor Agent 或 Expert Agent。处理流程中的基本流转逻辑。
    *   **输入**: 结构化的流程计划，Session State。
    *   **输出**: 驱动整个流程执行，最终可能汇总结果。
    *   **实现**: ADK 框架中的 **Root Agent**，其核心指令是执行计划。

3.  **Executor Agents (执行者群体)**:
    *   **职责**: 负责执行流程计划中定义的具体任务环节。每个 Executor 拥有特定的技能 (Tools)。
    *   **输入**: 来自 Orchestrator 的任务指令，可能需要从 Session State 读取数据。
    *   **输出**: 将执行结果（交付物）写入 Session State。
    *   **实现**: ADK 框架中的 **Sub-Agents**，由 Orchestrator 委托。

4.  **Expert Agent (专家 / 质量审核)**:
    *   **职责**: 负责对 Executor 产出的**内容质量**进行评估和审核。根据流程计划中定义的审核点被调用。
    *   **输入**: 来自 Orchestrator 的审核任务指令，需要从 Session State 读取待审核的交付物。
    *   **输出**: 将审核结果（例如，通过/不通过、评分、修改建议）写入 Session State。
    *   **实现**: 一个专门的 **Sub-Agent**，拥有评估质量的 Tools。

## 使用 Callbacks 进行格式检查

为了确保数据在 Agent 之间流转的规范性，我们利用 ADK 的 Callbacks 机制进行格式检查：

*   **`after_tool_callback` (输出格式检查)**:
    *   **应用**: 附加在 Executor Agent 的主要产出工具上。
    *   **功能**: 在工具执行完毕、返回结果*之前*，检查输出数据的结构、类型、字段是否符合预定义的格式规范。
    *   **动作**: 格式正确则允许写入 State；错误则尝试修正、记录日志或返回错误标记。

*   **`before_tool_callback` (输入格式检查)**:
    *   **应用**: 附加在需要消费上一步产出的 Agent（下一个 Executor 或 Expert）的工具上。
    *   **功能**: 在工具即将执行*之前*，检查从 Session State 读取的输入数据格式是否符合预期。
    *   **动作**: 格式正确则允许执行；错误则阻止执行并返回错误信息。

**区分**: Callbacks 负责**程序性**的格式检查，Expert Agent 负责**实质性**的内容质量评估。

## 流程交互示意图

```mermaid
graph TD
    subgraph User Interaction
        A[User: 输入自然语言流程] --> B(Workflow Parser Agent);
    end

    subgraph Agent Team Execution
        B -- 生成结构化计划 --> C{Orchestrator Agent (Root)};
        C -- 读取计划 & 状态 --> C;
        C -- 委托任务 & 状态 --> D1(Executor Agent 1);
        D1 -- 执行任务 --> D1_Tool[Tool: Task 1];
        D1_Tool -- after_tool_callback --> D1_FormatCheck_Out{Format Check (Output)};
        D1_FormatCheck_Out -- 结果写入 --> S[(Session State)];

        C -- 委托任务 & 状态 --> D2(Executor Agent 2);
        D2 -- 读取状态 --> D2_Tool[Tool: Task 2];
        D2_Tool -- before_tool_callback --> D2_FormatCheck_In{Format Check (Input)};
        D2_FormatCheck_In -- 允许执行 --> D2_Tool;
        D2_Tool -- after_tool_callback --> D2_FormatCheck_Out{Format Check (Output)};
        D2_FormatCheck_Out -- 结果写入 --> S;

        C -- 委托审核 & 状态 --> E(Expert Agent);
        E -- 读取状态 --> E_Tool[Tool: Quality Review];
        E_Tool -- before_tool_callback --> E_FormatCheck_In{Format Check (Input)};
        E_FormatCheck_In -- 允许执行 --> E_Tool;
        E_Tool -- 审核结果写入 --> S;

        C -- 循环/结束 --> F[最终结果];
    end

    S -- 数据流 --> C;
    S -- 数据流 --> D2;
    S -- 数据流 --> E;
```

## 设计原则

*   **职责分离**: 每个 Agent 和 Callback 都有明确、单一的职责。
*   **模块化**: 易于添加、修改或替换单个 Agent 或其 Tools。
*   **可扩展性**: 结构清晰，便于未来增加更复杂的流程逻辑或 Agent 类型。
*   **可靠性**: 通过格式检查和质量审核环节保障流程的健壮性和产出质量。
