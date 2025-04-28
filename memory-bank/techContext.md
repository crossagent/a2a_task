# 技术背景：集成 Notion 的 A2A 任务助手

## 1. 核心框架

*   **Google Agent Development Kit (ADK / A2A):** 项目的基础框架，用于构建和运行 Agent 应用。我们将利用其 Agent 定义、Tool 集成、Runner、SessionService 和事件驱动机制。

## 2. 编程语言

*   **Python:** ADK 框架的主要语言，所有业务逻辑（Agent 指令处理逻辑、Tool 实现）将使用 Python 编写。

## 3. 关键库与依赖

*   **`google-adk`:** 核心 ADK 库。
*   **Notion Python SDK:** (待调研) 需要选择一个合适的 Python 库来与 Notion API 进行交互。常见的可能有 `notion-client` 或其他社区维护的库。调研后将在此处明确。
*   **`litellm`:** (可选) 如果需要支持多种 LLM 模型（如 `example.md` 所示），将引入此库。初期可能先使用 ADK 默认支持的 Gemini 模型。
*   **LLM API 客户端:** 根据选择的 LLM，可能需要相应的客户端库（例如 `google-generativeai`）。

## 4. 开发设置与环境

*   **Python 版本:** 需要确定一个兼容 ADK 和所选 Notion SDK 的 Python 版本 (例如 Python 3.9+)。(当前项目 `.python-version` 文件指定了 3.11.5)
*   **包管理:** 使用 `uv` (根据 `uv.lock` 和 `pyproject.toml` 文件推断) 进行依赖管理和虚拟环境管理。
*   **API 密钥管理:** 遵循安全最佳实践，将 Notion API 密钥、LLM API 密钥等敏感信息通过环境变量或其他安全方式（如 Colab Secrets, .env 文件配合 `python-dotenv`）进行管理，避免硬编码。

## 5. 技术约束与考虑

*   **Notion API 限制:** 需要了解并遵守 Notion API 的速率限制、功能限制等。
*   **LLM 依赖:** Agent 的流程控制和任务理解能力高度依赖所选 LLM 的性能和对指令的理解能力。需要精心设计 Prompt (指令)。
*   **状态管理:** 初期使用 `InMemorySessionService`，会话状态在服务重启后会丢失。如果需要持久化，后续需要考虑替换为数据库支持的 SessionService。
*   **异步编程:** ADK 核心是异步的 (`asyncio`)，Tool 的实现和主应用逻辑应尽可能采用异步方式以获得最佳性能，特别是涉及 I/O 操作（如 API 调用）时。

## 6. 工具使用模式

*   **Notion Tool:** 将作为 ADK `FunctionTool` 实现，封装对 Notion SDK 的调用。
*   **Agent 指令:** 将是驱动 Agent 行为和流程的主要“工具”。
