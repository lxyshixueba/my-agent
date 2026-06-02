# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (backend), TypeScript 5.7.3 (frontend)

**Primary Dependencies**: FastAPI 0.115.0, LangChain 0.3.0, LangGraph 0.2.0,
LangSmith 0.1.0, FastMCP 2.0.0,
Vue 3 3.5.13, Ant Design Vue 4.2.6

**Storage**: MySQL 8.0 (via SQLAlchemy 2.0.0 + PyMySQL 1.1.0, Alembic 1.14.0)

**Testing**: pytest 8.0.0 (backend), Vitest or ESLint 9.0.0 (frontend)

**Lint/Type Check**: Ruff 0.8.0 + mypy 1.13.0 (backend),
ESLint 9.0.0 + Prettier 3.4.0 (frontend)

**Logging**: Loguru 0.7.0

**Target Platform**: Linux server (backend), Modern browsers (frontend)

**Project Type**: Web application (前后端分离)

**Performance Goals**: [domain-specific, e.g., 100 req/s, <200ms p95 API response]

**Constraints**: [domain-specific, e.g., <500ms p95, mobile-friendly, offline-capable]

**Scale/Scope**: [domain-specific, e.g., 1k users, 50 routes, 20 pages]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **P1 规范驱动开发**: 功能有对应的 spec.md
- [ ] **P2 增量交付**: 用户故事可独立开发/测试/部署
- [ ] **P3 测试纪律**: 测试先于实现编写（如规范要求）
- [ ] **P4 代码质量**:
  - 后端: 类型注解、Ruff/mypy 通过、依赖注入、自定义异常
  - 前端: 无未解释的 any、Composition API、services/ 层封装
- [ ] **P5 可观测性**: 结构化日志(Loguru)、错误上下文、无敏感信息
- [ ] **P6 审查与问责**: 变更经过审查，复杂性有理由
- [ ] **技术规范合规**:
  - 后端编码规范: Pydantic Schema 区分、依赖注入、自定义异常、
    异步 SQLAlchemy session, pydantic-settings 配置、Alembic 迁移、
    LangGraph Agent 工作流、LangChain Tool 定义、LangSmith 追踪、
    FastMCP 协议
  - 前端编码规范: PascalCase 命名、scoped CSS、
    类型定义与后端 Schema 一致
  - API 规范: RESTful 路径、统一错误格式、/api/v1/ 版本控制、
    标准分页参数

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Web application (前后端分离 — 本项目采用此结构)
backend/
├── app/
│   ├── agents/            # 智能体实现
│   ├── api/               # FastAPI 路由
│   ├── models/            # SQLAlchemy 数据模型
│   ├── schemas/           # Pydantic 请求/响应 Schema
│   ├── services/          # 服务层（依赖注入）
│   ├── mcp/               # FastMCP 协议端点
│   └── config.py          # pydantic-settings 配置
├── migrations/            # Alembic 迁移脚本
└── tests/

frontend/
├── src/
│   ├── views/             # 页面组件 (PascalCase)
│   ├── components/        # 通用组件
│   ├── services/          # API 服务封装 (Axios)
│   ├── types/             # TypeScript 类型定义
│   └── router/            # Vue Router 路由配置
└── tests/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
