<!--
  Sync Impact Report
  ==================
  Version change: 1.5.0 → 1.6.0
  Bump rationale: MINOR — 后端技术栈新增 LangChain/LangGraph/LangSmith
  智能体框架，并相应扩展后端编码规范中的 Agent 约束。
  Modified principles: None (all 6 principles unchanged)
  Changed sections:
    - 后端技术栈: 新增 LangChain, LangGraph, LangSmith
    - 后端编码规范: Agent 约束从通用描述改为 LangChain/LangGraph 专属规范
    - API 密钥管理: 新增 LANGCHAIN_API_KEY (LangSmith 追踪)
  Previous changes (v1.4.0 → 1.5.0):
    - 新增"技术规范"章节 (后端/前端技术栈、编码规范、API 规范)
    - Python 版本从 3.10+ 更新为 3.12
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/spec-template.md       ⚠ pending (建议添加技术约束引用)
    - .specify/templates/plan-template.md        ✅ to-update (依赖项需加入
                                                   LangChain/LangGraph/LangSmith)
    - .specify/templates/tasks-template.md       ✅ to-update (合规检查项需加入
                                                   LangChain/LangGraph 约束)
    - .specify/templates/checklist-template.md   ⚠ pending (建议添加技术规范合规
                                                   检查类别模板)
    - .specify/templates/constitution-template.md ✅ aligned (source template)
  Runtime guidance requiring updates:
    - .claude/commands/speckit.*.md              N/A (not found)
    - .codex/prompts/speckit.*.md                N/A (not found)
    - .gemini/commands/speckit.*.toml            N/A (not found)
    - .github/prompts/speckit.*.prompt.md        N/A (not found)
    - .github/agents/speckit.*.agent.md          N/A (not found)
    - skills/speckit-*/SKILL.md                  N/A (not found)
  Follow-up TODOs:
    - 更新 spec-template.md 添加技术约束引用（低优先级）
    - 更新 checklist-template.md 添加技术规范合规检查类别模板（低优先级）
-->

# Travel Helper 宪法

## 核心原则

### I. 规范驱动开发

所有功能 MUST 从规范文档开始，遵循 speckit 工作流：spec → plan → tasks → implement。

- 无规范不编码：任何功能代码 MUST 有对应的规范文档
- 规范 MUST 遵循 `.specify/templates/` 中的模板格式
- 规范 MUST 包含用户场景、验收标准和成功指标
- 宪法具有最高优先级 — 与其他项目文档冲突时以宪法为准

**理由**：规范先行确保需求清晰、可追溯，减少返工和沟通成本。

### II. 增量交付

功能 MUST 拆分为独立的、可独立测试的用户故事，按优先级增量交付。

- 每个用户故事 MUST 可独立开发、独立测试、独立部署
- P1 用户故事构成 MVP，MUST 优先交付
- 后续用户故事在 MVP 基础上增量添加，MUST NOT 破坏已有功能
- 每个用户故事交付后 MUST 独立验证

**理由**：增量交付降低风险，确保每个阶段都有可演示的价值产出。

### III. 测试纪律

测试 MUST 先于实现编写，遵循红-绿-重构循环。

- 如果规范要求测试，测试 MUST 先写并通过用户审批，确认失败后再实现
- 集成测试 MUST 覆盖：新服务契约、契约变更、跨服务通信、共享数据模式
- 测试 MUST 独立于用户故事，每个故事可独立验证
- 测试 MUST NOT 因无关功能变更而失败

**理由**：测试先行确保代码正确性，防止回归，提供持续交付信心。

### IV. 代码质量

代码 MUST 遵循项目统一的编码标准和质量门禁。

- Python 代码 MUST 使用类型注解（type hints）
- 代码 MUST 通过 lint 和 format 检查后方可提交
- 变更 MUST 经过代码审查
- 复杂性 MUST 有明确理由（记录在实现计划的复杂性追踪表中）
- 无用的死代码和注释 MUST 在提交前清理

**理由**：统一标准提升可维护性，代码审查捕获缺陷和设计问题。

### V. 可观测性

系统 MUST 提供结构化日志和错误追踪能力。

- 所有 API 请求 MUST 记录结构化日志（包含请求 ID、时间戳、响应状态）
- 错误 MUST 包含足够的上下文信息以便排查
- 日志 MUST NOT 包含敏感信息（API 密钥、用户凭证等）
- 关键业务操作 MUST 有可追踪的日志链路

**理由**：可观测性是生产环境问题排查和性能监控的基础保障。

### VI. 审查与问责

所有变更 MUST 经过审查，决策 MUST 可追溯。

- 所有代码提交 MUST 通过审查
- 宪法修正 MUST 包含：修正说明、审批记录、迁移计划
- 违反宪法的复杂性 MUST 在实现计划中记录理由
- Speckit 流程的每个阶段产出 MUST 存档于 `spec/` 目录

**理由**：审查和问责确保质量持续改进，决策有据可查。

## 项目结构

项目采用前后端分离架构，代码按职责分层：

```
├── spec/                        # 功能规范文档
│   └── <feature-name>/         # 按功能名称组织
│       ├── spec.md             # 功能规范
│       ├── plan.md             # 实现计划
│       └── tasks.md            # 任务清单
│
├── backend/                    # 后端 (Python 3.12)
│   ├── app/
│   │   ├── agents/            # 智能体实现
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 服务层
│   │   └── config.py          # 配置文件
│   └── requirements.txt       # Python 依赖
│
└── frontend/                   # 前端 (JavaScript/TypeScript)
    ├── src/
    │   ├── views/             # 页面组件
    │   ├── services/          # API 服务
    │   ├── types/             # 类型定义
    │   └── router/            # 路由配置
    └── package.json           # npm 依赖
```

**约束**：

- 后端 MUST NOT 直接引用前端代码，反之亦然
- 层级依赖方向：api → services → models（MUST NOT 反向依赖）
- 智能体（agents）MUST 通过服务层访问数据，MUST NOT 直接操作数据模型
- 新增目录或层级变更 MUST 在实现计划中说明理由

## 技术规范

### 后端技术栈

| 技术 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.12 | 运行时（从 .venv 推断） |
| FastAPI | >=0.115.0 | Web 框架 |
| Uvicorn | >=0.32.0 | ASGI 服务器 |
| LangChain | >=0.3.0 | LLM 编排框架（Chain/Tool/Retriever） |
| LangGraph | >=0.2.0 | 有状态多步 Agent 工作流引擎 |
| LangSmith | >=0.1.0 | LLM 追踪、评估与调试平台 |
| Pydantic | >=2.0.0 | 数据校验与序列化 |
| pydantic-settings | >=2.0.0 | 环境配置管理 |
| httpx | >=0.27.0 | 异步 HTTP 客户端（测试 + 外部 API 调用） |
| aiohttp | >=3.10.0 | 异步 HTTP 客户端（流式/长连接场景） |
| FastMCP | >=2.0.0 | MCP 协议支持 |
| Loguru | >=0.7.0 | 结构化日志 |
| python-dotenv | >=1.0.0 | 环境变量加载 |
| SQLAlchemy | >=2.0.0 | ORM 框架 |
| PyMySQL | >=1.1.0 | MySQL 驱动 |
| Alembic | >=1.14.0 | 数据库迁移 |
| huggingface_hub | — | HuggingFace 模型/资源访问 |
| python-dateutil | — | 日期时间处理 |
| uv | — | Python 包管理器 |
| pytest | >=8.0.0 | 测试框架 |
| Ruff | >=0.8.0 | Lint + Format |
| mypy | >=1.13.0 | 静态类型检查 |

### 前端技术栈

| 技术 | 最低版本 | 用途 |
|------|---------|------|
| Vue 3 | 3.5.13 | 前端框架 |
| Vite | 6.0.7 | 构建工具 |
| TypeScript | 5.7.3 | 开发语言 |
| Ant Design Vue | 4.2.6 | UI 组件库 |
| Vue Router | 4.5.0 | 路由管理 |
| Axios | 1.7.9 | HTTP 客户端 |
| AMap（高德地图） | 1.0.1 | 地图服务 |
| jsPDF | 3.0.3 | PDF 导出 |
| html2canvas | 1.4.1 | 截图渲染 |
| ESLint | 9.0.0 | 代码检查 |
| Prettier | 3.4.0 | 代码格式化 |

### 数据存储

| 技术 | 最低版本 | 用途 |
|------|---------|------|
| MySQL | 8.0 | 主数据库 |

### 后端编码规范

- Python 代码 MUST 使用类型注解（type hints），所有公开函数 MUST 标注参数和返回类型
- MUST 使用 Ruff 进行 lint 和 format，配置文件为 `backend/pyproject.toml`
- MUST 使用 mypy 进行静态类型检查，CI 流水线 MUST 包含 mypy 检查步骤
- API 路由 MUST 使用 FastAPI 路由装饰器（`@router.get`/`@router.post` 等），并定义 Pydantic 响应模型
- 数据模型 MUST 区分职责：SQLAlchemy Model 用于数据库映射，Pydantic Schema 用于请求/响应校验
- 服务层 MUST 通过 FastAPI 依赖注入（`Depends`）获取，MUST NOT 在路由中直接实例化
- 异步操作 MUST 使用 `async`/`await`，数据库访问 MUST 使用异步 SQLAlchemy session
- 错误处理 MUST 使用自定义异常类 + FastAPI `@app.exception_handler`，MUST NOT 在路由中直接返回裸异常
- 环境配置 MUST 通过 `app/config.py` 管理，使用 pydantic-settings + python-dotenv，MUST NOT 在代码中硬编码配置值
- 数据库迁移 MUST 使用 Alembic 管理，MUST NOT 手动修改数据库结构
- Agent（智能体）MUST 使用 LangGraph 构建有状态工作流，MUST 通过服务层访问数据，MUST NOT 直接操作数据模型
- LLM 调用 MUST 通过 LangChain 封装，MUST NOT 直接使用裸 HTTP 请求调用 LLM API
- LangChain Tool MUST 定义清晰的输入/输出类型（Pydantic BaseModel），MUST 包含中文描述
- LangGraph 状态 MUST 使用 TypedDict 或 Pydantic Model 定义，MUST NOT 使用裸 dict
- 所有 LLM 交互 MUST 通过 LangSmith 追踪，MUST 在 `app/config.py` 中配置 `LANGCHAIN_API_KEY` 和 `LANGCHAIN_PROJECT`
- LangSmith 追踪 MUST 在生产环境启用，MUST NOT 在日志中泄露追踪 URL 中的敏感参数
- MCP 协议端点 MUST 使用 FastMCP 实现，MUST 遵循 MCP 规范的消息格式
- 日志 MUST 使用 Loguru，MUST 输出结构化格式，MUST NOT 包含敏感信息

### 前端编码规范

- MUST 使用 TypeScript，MUST NOT 使用 `any` 类型（除非有明确理由并在注释中说明原因）
- MUST 使用 Composition API + `<script setup>` 语法，MUST NOT 使用 Options API
- 组件文件 MUST 使用 PascalCase 命名（如 `TripPlan.vue`），目录 MUST 使用 kebab-case（如 `trip-plan/`）
- 组件 MUST 按 Ant Design Vue 规范使用，MUST NOT 直接操作 DOM
- API 调用 MUST 通过 `services/` 层封装，MUST NOT 在组件中直接调用 Axios
- 路由 MUST 在 `router/` 中集中配置，MUST NOT 在组件中硬编码路径
- 类型定义 MUST 放在 `types/` 目录，MUST 与后端 Pydantic Schema 保持一致
- MUST 使用 ESLint + Prettier 进行代码规范检查，配置文件为 `frontend/.eslintrc.*` 和 `frontend/.prettierrc`
- 样式 MUST 使用 Scoped CSS 或 CSS Modules，MUST NOT 使用全局样式污染

### API 规范

- API MUST 遵循 RESTful 设计，资源路径使用复数名词（如 `/api/v1/trips`）
- MUST 使用 OpenAPI 3.0 规范（FastAPI 自动生成），文档 MUST 在开发环境可访问
- 请求/响应 MUST 使用 Pydantic 模型定义，MUST NOT 使用裸 dict
- MUST 统一错误响应格式：

```json
{
  "error": {
    "code": "TRIP_NOT_FOUND",
    "message": "指定的行程不存在",
    "detail": {}
  }
}
```

- MUST 使用 API 版本控制，路径前缀为 `/api/v1/`，破坏性变更 MUST 递增主版本号
- 分页查询 MUST 支持标准参数：`page`、`page_size`、`sort_by`、`order`
- 列表响应 MUST 包含分页元信息：`total`、`page`、`page_size`

## 安全与环境

### 环境要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.12+ |
| Node.js | 16.0+ |
| npm | 8.0+ |

### API 密钥管理

- API 密钥 MUST 统一存放于 `backend/.env` 文件
- `.env` 文件 MUST 已加入 `.gitignore`，严禁提交到版本控制
- 代码中 MUST NOT 硬编码任何密钥或敏感信息
- 日志输出 MUST NOT 包含 API 密钥

项目所需的 API 密钥：

| 密钥 | 用途 |
|------|------|
| `LLM_API_KEY` | 大语言模型 API（OpenAI、DeepSeek 等） |
| `LANGCHAIN_API_KEY` | LangSmith 追踪与评估平台 |
| `AMAP_WEB_KEY` | 高德地图 Web 服务 |
| `UNSPLASH_ACCESS_KEY` | Unsplash 图片服务 |

## 治理

### 宪法地位

- 本宪法具有最高优先级 — 与其他项目文档冲突时以宪法为准
- CLAUDE.md 中的项目指引以本宪法为根基

### 修正程序

1. 提出修正建议，说明理由和影响范围
2. 更新宪法文档，记录变更内容
3. 按语义化版本规则递增版本号
4. 传播一致性检查：更新受影响的模板、指引和文档
5. 产出同步影响报告

### 版本策略

- **主版本（MAJOR）**：原则删除、重新定义或向后不兼容的治理变更
- **次版本（MINOR）**：新增原则/章节或实质性扩展指引
- **修订版（PATCH）**：澄清、措辞优化、错别字修正

### 合规审查

- 所有 PR/代码审查 MUST 验证宪法合规性
- Speckit 流程的 Constitution Check 门禁 MUST 在设计和实现阶段通过
- 违反宪法的变更 MUST 在复杂性追踪表中记录理由

**版本**: 1.6.0 | **批准日期**: 2026-06-02 | **最近修订**: 2026-06-02
