# 技术背景：AI 流程自动化工具

## 核心框架

*   **Google Agent Development Kit (ADK)**: 本项目将基于 Google ADK 进行构建。ADK 提供了构建多 Agent 系统所需的核心组件，包括：
    *   Agent 定义与管理
    *   Tool (工具/技能) 集成
    *   多 LLM 支持 (通过 LiteLLM)
    *   Agent 间委托 (Delegation / Auto Flow)
    *   会话状态管理 (Session State)
    *   回调机制 (Callbacks) 用于流程控制和安全防护

## 编程语言

*   **Python**: ADK 是一个 Python 框架，因此项目的主要开发语言将是 Python。

## 关键依赖

*   `google-adk`: 核心 Agent 框架。
*   `litellm`: 用于支持多种 LLM (Gemini, GPT, Claude 等)。
*   mcp服务
*   (可能) 其他用于特定 Tools 的库 (例如，API 客户端、数据处理库等)。

## 开发环境与设置

*   需要配置 Python 环境。
*   需要获取并配置所使用的 LLM 的 API Keys (例如 Google AI Studio, OpenAI Platform, Anthropic Console)。
*   开发将在支持 Python 的环境中进行 (例如 VS Code)。

## 技术约束与考虑

*   **自然语言到结构化计划的转换**: 这是技术上的核心挑战之一，需要强大的 NLU 能力，可能需要结合特定的提示工程、模型微调或额外的解析逻辑。
*   **状态管理**: ADK 的 `InMemorySessionService` 适用于简单场景，对于生产环境或需要持久化状态的场景，可能需要实现自定义的 Session Service (例如，对接数据库)。
*   **错误处理与鲁棒性**: 需要设计健壮的错误处理机制，应对 Agent 执行失败、工具调用异常、API 错误等情况。
*   **可观测性**: 需要考虑如何监控 Agent 的行为、流程的执行状态、资源消耗等。

## 工具使用模式

*   Agent 的能力主要通过定义 Python 函数作为 Tools 来实现。
*   Tool 的 Docstring 对于 Agent 正确理解和使用 Tool 至关重要。
*   Tool 可以通过 `ToolContext` 访问和修改 `Session State`。
