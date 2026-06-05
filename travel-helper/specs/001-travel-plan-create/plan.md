# Implementation Plan: 旅行计划创建 (Travel Plan Create)

**Branch**: `001-travel-plan-create` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-travel-plan-create/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

实现旅行计划创建功能的前端表单页面和后端 API 服务。用户通过表单输入目的地城市、出行日期、交通方式、住宿偏好、旅行偏好和特殊服务要求，后端调用大语言模型 API 生成个性化旅行规划方案。前端负责表单收集、输入验证和提交；后端负责数据校验、LLM 调用和结构化响应返回。

## Technical Context

**Language/Version**: Python 3.10+ (后端), TypeScript 5+ (前端)

**Primary Dependencies**: 
- 后端: FastAPI (API 框架), pydantic (数据校验), anthropic/openai SDK (LLM 调用), python-dotenv (环境变量)
- 前端: Vue 3 (前端框架), **Element Plus 2.x (UI 组件库)**, @element-plus/icons-vue (图标库), Axios (HTTP 客户端), date-fns (日期处理), vue-router (路由)

**Storage**: 本功能不持久化存储旅行计划数据，LLM 生成的结果通过 API 响应直接返回给前端。城市数据可存储为静态 JSON 文件。

**Testing**: pytest (后端), Vitest/Jest (前端)

**Target Platform**: Web 浏览器 (桌面端 + 移动端响应式), Linux/macOS 服务器

**Project Type**: web-service (前后端分离的 Web 应用)

**Performance Goals**: 
- 城市搜索自动补全响应延迟 < 1 秒 (SC-005)
- 表单填写到提交 < 2 分钟 (SC-001)
- LLM 生成响应时间 < 30 秒 (SC-004)

**Constraints**: 
- 无需用户认证 (A-005)
- 生成的旅行计划为静态文本，不包含交易功能 (A-006)
- LLM API 调用可能超时，需处理失败重试 (FR-012)
- 出行天数上限 30 天

**Scale/Scope**: 
- 本功能面向中国大陆用户，城市数据覆盖地级市及以上
- 无需支持高并发，但 LLM API 调用需考虑速率限制

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪法原则 | 合规状态 | 说明 |
|---------|---------|------|
| I. 规范驱动开发 | ✅ PASS | 已有 spec.md 规范文档，本文件为 plan.md 实现计划 |
| II. 增量交付 | ✅ PASS | 用户故事按 P1/P2/P3 分级，P1 可独立交付 MVP |
| III. 测试纪律 | ✅ PASS | 实现阶段将先写测试，遵循红-绿-重构 |
| IV. 代码质量 | ✅ PASS | Python 代码使用类型注解，前后端均有 lint 流程 |
| V. 可观测性 | ✅ PASS | API 请求日志、LLM 调用日志包含请求 ID 和状态 |
| VI. 审查与问责 | ✅ PASS | 所有提交经代码审查，本 plan.md 存档于 specs/ 目录 |

## Project Structure

### Documentation (this feature)

```text
specs/001-travel-plan-create/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-contract.md  # API interface contract
└── tasks.md             # Phase 2 output (by /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── travel_plan.py      # 旅行计划创建 API 端点
│   ├── models/
│   │   ├── travel_plan.py          # 旅行计划请求/响应模型 (pydantic)
│   │   └── city.py                 # 城市数据模型
│   ├── services/
│   │   ├── travel_plan_service.py  # 旅行计划生成业务逻辑
│   │   ├── llm_service.py          # LLM API 调用封装
│   │   └── city_service.py         # 城市搜索服务
│   ├── agents/
│   │   └── travel_planner_agent.py # 旅行规划智能体 (LLM prompt 构建)
│   ├── config.py                   # 应用配置
│   └── main.py                     # FastAPI 入口
├── data/
│   └── cities.json                 # 城市静态数据 (地级市列表)
├── tests/
│   ├── unit/
│   │   ├── test_city_service.py
│   │   ├── test_llm_service.py
│   │   └── test_travel_plan_service.py
│   ├── integration/
│   │   └── test_travel_plan_api.py
│   └── contract/
│       └── test_api_contract.py
└── requirements.txt

frontend/
├── src/
│   ├── views/
│   │   └── TravelPlanCreate.vue    # 旅行计划创建表单页面
│   ├── components/
│   │   ├── CitySearch.vue          # 城市搜索组件
│   │   ├── DatePicker.vue          # 日期选择组件
│   │   ├── PreferenceSelector.vue  # 偏好标签选择组件
│   │   └── TransportSelector.vue   # 交通方式选择组件
│   ├── services/
│   │   └── travelPlanApi.ts        # API 调用封装
│   ├── types/
│   │   └── travelPlan.ts           # 前端类型定义
│   ├── router/
│   │   └── index.ts                # 路由配置
│   └── App.vue
├── package.json
└── vite.config.ts                  # 构建配置
```

**Structure Decision**: 采用宪法规定的"前后端分离"架构（Option 2: Web application）。后端使用 FastAPI 提供 REST API，前端使用 **Vue 3 + Element Plus 2.x** 构建 SPA，以 Element Plus 内建组件（el-form、el-autocomplete、el-date-picker、el-select 等）替代手写表单控件。城市数据以静态 JSON 文件存储，无需数据库。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 无 | 本功能为首次实现，无历史负担，结构符合宪法分层约束 | N/A |
