# 项目简报：集成 Notion 的 A2A 任务助手

## 1. 项目目标

本项目的主要目标是使用 Google Agent Development Kit (ADK / A2A 框架) 开发一个智能任务助手。该助手将帮助用户定义、分类任务，并将其记录到 Notion 数据库中。

## 2. 核心需求

*   **任务定义:** 助手必须能与用户交互，清晰地定义新任务的细节，包括内容和范围。
*   **任务分类:** 助手需要判断该任务是一个独立的项目，还是 Notion 中某个现有项目层级下的子任务。
*   **任务分配/归属:** 助手应能将任务关联到 Notion 中正确的项目，并可能分配负责人或其他相关元数据。
*   **Notion 集成:** 任务必须能够可靠地在指定的 Notion 工作区和数据库中创建，并可能支持更新。
*   **A2A 框架:** 整个系统必须基于 Google ADK 框架构建，利用其 Agent、Tool、Runner 和 Session State 等组件。

## 3. 高层架构

系统将包含两个主要 Agent，通过 ADK 的 Session State 进行协调：

1.  **任务定义 Agent:** 专注于通过自然语言与用户交互，收集所有必要的任务细节，并确定其层级（项目 vs. 任务）。
2.  **任务分配 Agent:** 从定义 Agent 处（通过 Session State）获取结构化的任务信息，使用 Notion Tool 查找/确认项目上下文，可能需要与用户进一步交互以澄清信息，最终在 Notion 中创建任务条目。

一个专门的 **Notion Tool**（使用 Python SDK 实现为 ADK Tool）将处理所有与 Notion API 的交互。

## 4. 范围

*   **范围内:**
    *   实现两个核心 Agent。
    *   开发用于核心任务创建和项目列表/查找的 Notion Tool。
    *   使用 Session State 进行基本的交互流程管理。
    *   在 ADK 框架内进行初始设置 (Runner, SessionService)。
    *   安全地处理 Notion API 密钥。
*   **范围外 (初期):**
    *   高级 Notion 功能（复杂关系、超出基础范围的特定属性类型）。
    *   复杂的错误处理和恢复逻辑。
    *   超出基本会话管理的用户认证/多用户支持。
    *   持久化会话存储 (将从 `InMemorySessionService` 开始)。
    *   部署相关的考虑。
    *   高级安全护栏 (Callbacks)，除非后续明确需要。

## 5. 关键技术

*   Python
*   Google Agent Development Kit (ADK / A2A)
*   Notion API
*   Notion Python SDK (待调研)
*   LiteLLM (可能使用，以实现 `example.md` 中展示的模型灵活性)
