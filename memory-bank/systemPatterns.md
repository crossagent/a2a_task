# 系统模式：集成 Notion 的 A2A 任务助手

## 1. 架构概览与职责划分

本系统基于 Google ADK (A2A) 框架，采用多 Agent 架构。理解框架与业务逻辑的界限至关重要。

*   **ADK 框架提供 (我们配置和使用):**
    *   `Agent` 类: Agent 的基本结构。
    *   `Tool` 基类/接口: 工具规范。
    *   `Runner`: **核心事件循环编排器**。接收用户输入，驱动 Agent 执行，处理 Agent/Tool/Callback 产生的 `Event`，与 `Service` 交互提交状态/历史，并将事件传递给上游。
    *   `SessionService`: 管理会话状态和历史记录的接口 (如 `InMemorySessionService`)。
    *   `Session State`: 会话状态存储机制 (字典)，主要用于**跨事件/Agent 传递数据**。
    *   `ToolContext`: 工具访问会话状态的机制。
    *   回调机制: 提供生命周期钩子。
    *   模型集成 (`LiteLlm`): 连接 LLM。
    *   **事件驱动机制:** 框架通过 `yield` 实现 Agent 逻辑的暂停/恢复，确保状态变更在 `Runner` 处理 `Event` 后才对后续逻辑可见。

*   **业务逻辑实现 (我们需要编码):**
    *   **Agent 实例定义 (`agent.py`):**
        *   创建 `Agent 1 (任务定义)` 和 `Agent 2 (任务分配)` 实例，配置 `name`, `model`, `description`。
    *   **Agent 指令 (`prompts.py`):**
        *   **极其关键**: 为每个 Agent 编写**高度清晰、明确、无歧义**的 `instruction`。
        *   指令必须精确描述 Agent 的职责、工作流程、何时调用哪个 `Tool`、如何处理 Tool 的结果、何时任务完成，以及**完成任务后预期的最终状态和输出**。
        *   **Agent 间的流程依赖 LLM 对这些指令的理解
        *   **Notion Tool 实现 (`tools.py`):**
            *   编写与 Notion SDK/API 交互的 Python 函数，并封装为 ADK `Tool`。这是核心的外部交互逻辑。
        *   **(无需业务编码) 主应用入口与运行:**
            *   ADK 框架通过 CLI (`adk web`, `adk run`) 或测试框架处理 `Runner` 和 `SessionService` 的初始化及交互启动。我们只需正确组织 Agent 代码和配置。

**架构图 (修正职责):**

```mermaid
graph TD
    subgraph ADK_Framework [ADK 框架 (提供)]
        direction LR
        F_Runner(Runner - 事件循环编排)
        F_SessionService(SessionService Interface)
        F_AgentBase(Agent Base Class)
        F_ToolBase(Tool Base Class)
        F_SessionState(Session State - 数据传递)
        F_ToolContext(ToolContext)
        F_Callbacks(Callback Hooks)
        F_LiteLlm(Model Integration)
        F_EventLoop(Event-Driven Mechanism)
    end

    subgraph Business_Logic [业务逻辑 (需编码)]
        direction LR
        BL_Agent1Def(Agent 1 定义 & 精确指令);
        BL_Agent2Def(Agent 2 定义 & 精确指令);
        BL_NotionToolImpl(Notion Tool 实现);
    end

    UserInterface(用户接口) -- ADK CLI --> F_Runner; # 用户通过 CLI 与 Runner 交互
    F_Runner -- 配置/使用 --> F_SessionService; # Runner 内部使用 Service
    F_Runner -- 驱动 (基于指令解释) --> BL_Agent1Def;
    F_Runner -- 驱动 (基于指令解释) --> BL_Agent2Def;
    BL_Agent1Def -- 读/写数据 --> F_SessionState;
    BL_Agent2Def -- 读/写数据 --> F_SessionState;
    BL_Agent2Def -- 调用 --> BL_NotionToolImpl;
    BL_NotionToolImpl -- 使用 --> F_ToolBase;
    BL_NotionToolImpl -- (可选) 使用 --> F_ToolContext;


    style ADK_Framework fill:#e6f2ff,stroke:#333
    style Business_Logic fill:#d4edda,stroke:#333
```

## 2. Agent 交互模式：指令驱动的隐式协调

我们将完全依赖**高质量的 Agent 指令**来驱动流程。LLM 对指令的理解是实现 Agent 间自动流转的关键。`Session State` 用于在流转过程中可靠地传递必要的数据。

## 3. Tool 集成模式 (业务逻辑重点)

`NotionTool` 的实现是核心业务逻辑，负责与外部系统交互。

## 4. 代码结构模式 (业务逻辑组织)

保持按模块组织业务代码 (`agent.py`, `prompts.py`, `tools.py`)。
