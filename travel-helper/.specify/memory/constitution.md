<!--
  Sync Impact Report
  ==================
  Version change: 1.5.0 → 1.6.0
  Modified principles: N/A
  Added sections:
    - Speckit 流程执行纪律 → 新增脚本缺失/执行失败时必须立即提示用户并中断流程
  Removed sections: None
  Templates requiring updates: None
  Runtime guidance requiring updates:
    - CLAUDE.md                                 ✅ reference new section
  Rationale for v1.6.0: Ensure Speckit execution errors are surfaced immediately to prevent downstream artifacts based on incomplete context.
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
- **大模型调用 MUST 通过 LangSmith 进行追踪**（包含 Prompt 版本、模型输入输出、Token 消耗、延迟）

**理由**：可观测性是生产环境问题排查和性能监控的基础保障。LangSmith 为 LLM 调用提供标准化追踪能力，满足大模型场景下的调试需求。

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
├── backend/                    # 后端 (Python 3.10+)
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

**技术栈**：

| 层级 | 技术选型 |
|------|---------|
| 后端 | Python 3.10+ / FastAPI / Pydantic |
| 大模型 | **LangChain** (Agent/Tool) / **LangGraph** (StateGraph/多智能体编排) / **LangSmith** (Tracing/调试) |
| 前端 | Vue 3 / TypeScript / **Element Plus 2.x** (UI 组件库) / Axios |
| 构建 | Vite 5 / vue-tsc |
| 测试 | pytest (后端) / Vitest (前端) |

**约束**：

- 后端 MUST NOT 直接引用前端代码，反之亦然
- 层级依赖方向：api → services → models（MUST NOT 反向依赖）
- 智能体（agents）MUST 通过服务层访问数据，MUST NOT 直接操作数据模型
- 前端表单控件优先使用 Element Plus 内建组件，MUST NOT 重复实现已有组件功能
- 新增目录或层级变更 MUST 在实现计划中说明理由

## Speckit 流程执行纪律

- Speckit 各阶段（specify / plan / tasks / implement）在执行过程中若出现 **脚本缺失、命令执行失败、环境异常** 等错误（例如 `No such file or directory`、`command not found`），MUST **立即中断当前流程并明确告知用户**，不得静默跳过或强行继续
- 报错信息 MUST 包含：失败的脚本路径、错误类型、建议的修复方向
- 用户确认处理方案后，方可继续执行后续步骤

**理由**：及时暴露环境问题，避免因缺失依赖或脚本导致后续产出（plan / tasks / 代码）基于不完整上下文生成，造成更大返工。

## 安全与环境

### 环境要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.10+ |
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
| `AMAP_WEB_KEY` | 高德地图 Web 服务 |
| `UNSPLASH_ACCESS_KEY` | Unsplash 图片服务 |
| `LANGSMITH_API_KEY` | LangSmith 追踪服务 |

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

**版本**: 1.7.0 | **批准日期**: 2026-06-05 | **最近修订**: 2026-06-05
