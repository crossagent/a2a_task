# 系统模式：AI 流程自动化 Agent 团队

本文档描述了用于 AI 流程自动化工具的核心 Agent 团队架构。该架构旨在将用户的自然语言流程描述转化为由 AI Agent 协作执行的结构化工作流。

## 核心 Agent 角色与职责

团队由以下核心 Agent 角色组成：

1.  **Workflow Parser Agent (流程解析器)**:
    *   **职责**: 接收用户输入的**自然语言流程描述**或特定指令。利用 NLU 能力将其解析为一个**结构化的执行计划**。对于已知的、定义明确的工作流（如"记录 Notion 任务"），它可以输出一个**预定义的固定计划模板**。
    *   **输入**: 用户的自然语言流程定义或指令。
    *   **输出**: 结构化的流程计划 (存储在 Session State 中，或直接传递给 Orchestrator)。
    *   **实现**: 通常是一个 `LlmAgent`，在流程开始时首先被调用。

2.  **Orchestrator Agent (协调器 / Root Agent)**:
    *   **职责**: 读取结构化流程计划。**动态地协调和推进**工作流。管理 `Session State`。根据计划委托任务给子 Agent。**关键职责**：处理子 Agent 发出的需要用户交互或指示流程变化的 `Events`（例如 `escalate`），暂停、恢复、循环或调整工作流。
    *   **输入**: 结构化的流程计划，Session State，来自子 Agent 的 Events。
    *   **输出**: 驱动整个流程执行，处理用户交互事件，最终可能汇总结果。
    *   **实现**: 通常是 ADK 框架中的 **Root Agent**，推荐使用 `LlmAgent` 以获得处理复杂逻辑和事件响应的灵活性。

3.  **Executor Agents (执行者群体)**:
    *   **职责**: 负责执行流程计划中定义的具体任务环节。通常**职责单一、专业化**（例如，信息收集、数据分类、API 调用）。可能需要通过 `Events` 与用户进行**交互式循环**（如提问-回答）来完成任务。每个 Executor 可能拥有特定的技能 (Tools)。
    *   **输入**: 来自 Orchestrator 的任务指令，Session State 中的数据，可能还有来自用户的 Events。
    *   **输出**: 将执行结果写入 Session State，可能发出需要用户交互或指示状态的 `Events`。
    *   **实现**: ADK 框架中的 **Sub-Agents**，可以是 `LlmAgent` (需要推理或 NLU)、`CustomAgent` (固定逻辑) 或 `LoopAgent` (封装迭代逻辑)。由 Orchestrator 委托。

4.  **Expert Agent (专家 / 审核者)**:
    *   **职责**: 负责对流程中的内容进行专业性验证和审核：
        *   **任务内容验证**: 评估任务的**内容完整性、一致性和有效性**，例如验证收集的信息是否足够执行任务。
        *   **分类审核**: 验证对任务或内容的分类是否合理和准确，例如工作类型、优先级、所属领域等。
        *   **质量保证**: 评估产出内容是否符合特定领域的专业标准。
    *   **输入**: 来自 Orchestrator 的审核任务指令，Session State 中的数据。
    *   **输出**: 专业审核意见和建议，写入 Session State。可能包括验证结果、改进建议或警告标识。
    *   **实现**: 通常是 `LlmAgent`，配置有特定领域专业知识的指令集，也可能是经过专门训练的 `CustomAgent`。

## LoopAgent与用户交互

在流程执行过程中，主要通过两个LoopAgent与用户进行关键信息的补充和确认：

1. **信息收集LoopAgent**:
   * **职责**: 分析已有信息，识别缺失或不完整的部分，通过与用户交互式对话**补充必要信息**。
   * **交互机制**: 使用`Event`事件系统触发用户交互，具体表现为:
     * 发出带有`escalate: true`的事件请求用户输入
     * 事件处理器暂停执行并等待用户响应
     * 用户输入后恢复执行并处理响应
   * **结束条件**: 收集到足够完整的信息后退出循环，而非由用户决定结束
   * **实现**: 通常为`LoopAgent`，使用内部状态跟踪信息完整性

2. **分类确认LoopAgent**:
   * **职责**: 对已收集信息进行专业化分类，并确认分类结果的合理性
   * **交互机制**: 通过`Event`系统向用户展示分类结果，并请求确认或修正
   * **结束条件**: 用户确认分类正确或经过预定次数的修正后结束
   * **实现**: 可以是独立的`LoopAgent`或由Orchestrator管理的循环流程

这两个循环都通过明确的信息需求和目标引导用户输入，使交互更加高效。用户的输入直接用于补充信息和验证分类，而非简单的"是/否"确认。

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

**区分**: Callbacks 负责**程序性**的格式检查（如数据类型、结构），Expert Agent 负责**实质性**的内容质量或专业性评估，而用户交互则通过**LoopAgent和事件系统**实现有针对性的信息补充和确认。

## 示例应用：Notion 任务助手架构

以下是应用上述模式构建一个具体的"Notion 任务助手"的架构示例，该助手能交互式地收集任务信息、分类、获得专业验证并写入 Notion。

1.  **Workflow Parser Agent (`LlmAgent`)**: 输出固定的 Notion 任务处理计划。
2.  **Orchestrator Agent (`LlmAgent` - Root)**: 接收用户请求，获取加任务的标准流程，协调以下子 Agent，处理用户交互事件。
3.  **TaskDetailLoop (`LoopAgent`)**:
    *   **Sub-Agent: `TaskDetailCollectorAgent` (`LlmAgent`)**: 分析现有信息，判断哪些关键信息缺失，针对性地生成提问。
    *   **交互**: 通过 `Events` 发送具体的信息请求（而非简单确认），例如"请提供任务完成的期限"、"这个任务的优先级如何？"等，持续收集直至信息完整。
    *   **目标**: 确保任务信息的**完整性和充分性**，而非简单确认。
4.  **TaskClassificationLoop (`LoopAgent`)**:
    *   **Sub-Agent: `TaskClassifierAgent` (`LlmAgent`)**: 对收集到的任务细节进行专业化分类（工作类型/优先级/部门）。
    *   **交互**: 通过 `Events` 向用户展示详细的分类理由和结果，例如"根据任务涉及到代码重构，建议分类为'技术债务'类型，优先级为'中'，请确认或调整"。
    *   **目标**: 确保分类的**准确性和合理性**，接受用户的专业判断。
5.  **TaskExpertAgent (`LlmAgent`)**:
    *   执行任务内容和分类的专业审核，验证任务描述的完整性、分类的合理性以及优先级设置的适当性。
    *   提供专业建议，如"此任务缺少明确的完成标准"或"建议提高优先级，因为它阻碍了关键功能的开发"。
6.  **NotionWriterAgent (`CustomAgent`)**:
    *   调用 `add_to_notion` Tool，将最终经过专家验证的任务信息写入 Notion。

### Notion 任务助手流程交互示意图

```mermaid
graph TD
    A[User: Initial Request] --> B(Workflow Parser);
    B -- Fixed Plan --> C{Orchestrator (Root - LlmAgent)};

    subgraph Step 1: Collect Details (Loop)
        C -- Delegate --> L1{TaskDetailLoop};
        L1 --> D(Exec: TaskDetailCollector);
        D -- Analysis Result --> Status1{Details Complete?};
        Status1 -- No --> NeedInput1[Generate Specific Question];
        NeedInput1 -- Event: Ask User --> UI1[User Interface];
        UI1 -- Event: User Answer --> L1;
        Status1 -- Yes --> L1End{Loop End};
        L1End -- Collected Details --> S[(Session State)];
    end

    subgraph Step 2: Classify Task (Loop)
        C -- Delegate --> L2{TaskClassificationLoop};
        L2 --> F(Exec: TaskClassifier);
        F -- Classification with Rationale --> UI2[User Interface];
        UI2 -- Event: User Feedback/Adjustment --> F;
        F -- Final Classification --> L2End{Loop End};
        L2End -- Confirmed Classification --> S;
    end

    subgraph Step 3: Expert Validation
        C -- Delegate (using Collected Data) --> K(Expert: TaskExpertAgent);
        K -- Reads Data --> S;
        K -- Professional Assessment --> K;
        K -- Validation Results & Recommendations --> S;
    end

     subgraph Step 4: Write to Notion
        C -- Delegate (using Validated Data) --> H(Exec: NotionWriter);
        H -- Reads Validated Data --> S;
        H -- Call Tool --> I[Tool: add_to_notion];
        I -- Notion API --> J[(Notion Database)];
        I -- Result --> H;
        H -- Completion --> C;
     end

    C -- Final Status --> UI3[User Interface];
```

## 设计原则

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
*   **可靠性**: 通过格式检查、专业验证环节与清晰的用户交互模式保障流程的健壮性和产出质量。
