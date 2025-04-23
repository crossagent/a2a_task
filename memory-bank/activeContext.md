# 活动背景：AI 流程自动化工具

## 当前焦点

*   **概念设计与架构**: 我们正在定义 AI Agent 团队的核心结构和角色职责，以实现通过自然语言驱动的流程自动化。
*   **技术选型**: 确定使用 Google Agent Development Kit (ADK) 作为核心框架。
*   **文档化**: 正在根据 `.clinerules` 要求，初始化项目的 Memory Bank 核心文档。

## 近期决策

*   **Agent 团队结构**: 确定采用包含以下角色的团队结构：
    *   **Workflow Parser Agent**: 解析自然语言流程描述为结构化计划。
    *   **Orchestrator Agent (Root)**: 根据计划协调和推进流程。
    *   **Executor Agents**: 执行具体任务。
    *   **Expert Agent**: 负责内容质量审核。
*   **格式检查**: 使用 ADK Callbacks (`before_tool_callback`, `after_tool_callback`) 来负责检查 Agent 间传递数据的格式规范性。
*   **职责区分**: 明确 Callbacks 负责格式，Expert Agent 负责质量。

## 下一步计划

*   完成 Memory Bank 核心文件的初始化（创建 `progress.md`）。
*   开始细化具体的工作流程示例，以便更深入地设计 Agent 的 Tools 和交互逻辑。
*   探讨如何实现 "Workflow Parser Agent" 的自然语言理解和结构化计划生成能力。
*   考虑如何集成用户提到的 MCP 服务。

## 重要模式与偏好

*   **文档驱动**: 遵循 `.clinerules`，优先维护 Memory Bank 文档。
*   **模块化设计**: 倾向于将复杂功能拆分为职责单一的 Agent。
*   **基于 ADK**: 利用 ADK 提供的核心机制（Delegation, State, Callbacks）来实现设计。

## 项目洞察

*   将自然语言流程描述转化为机器可执行的结构化计划是本项目的核心挑战和创新点。
*   ADK 框架与项目设想高度契合，可以作为坚实的技术基础。
