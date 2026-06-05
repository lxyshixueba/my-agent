# Implementation Plan: 旅行计划详情查看与编辑 (Travel Plan Detail)

**Branch**: `002-travel-plan-detail` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-travel-plan-detail/spec.md`

## Summary

本功能为 001 模块（旅行计划创建）的后续流程，用户在创建旅行计划后查看和管理行程详情。核心包括：旅行计划概览页（预算明细、目的地地图、每日行程列表）、逐日行程详情页（景点详情、住宿、餐饮、交通、天气）、行程编辑（拖拽排序/删除景点）、导出（图片/PDF）和重新规划。

**技术路线**：前端使用 Vue 3 + TypeScript + Element Plus 2.x 构建概览和详情页面，通过 Axios 调用后端 API；后端使用 FastAPI + Pydantic 提供 RESTful API；**大模型交互全面采用 LangChain / LangSmith / LangGraph 技术栈**（替代原有的直接调用 OpenAI SDK 方案）；数据存储在浏览器 localStorage；高德地图 MCP 服务通过 `AMAP_WEB_KEY` 提供 POI 搜索、天气查询、路线规划等能力；景点图片通过 Unsplash 获取。

## Technical Context

**Language/Version**: Python 3.10+ (后端) / TypeScript 5.x (前端)

**Primary Dependencies**:
- 后端: FastAPI, Pydantic, httpx (高德 MCP 服务代理调用), python-dotenv, **LangChain**, **LangGraph**, **LangSmith**
- 前端: Vue 3, TypeScript, Element Plus 2.x, Axios, vue-router, html2canvas/jsPDF (导出), vuedraggable (拖拽排序), @amap/amap-jsapi-loader (高德地图)
- 大模型: LangChain (Orchestrator/Agent) + LangGraph (StateGraph/多智能体编排) + LangSmith (Tracing/调试)
- 高德地图 MCP 服务: POI 搜索 API、天气查询 API、路线规划 API（均返回 JSON）

**Storage**: 浏览器 localStorage（客户端存储，无需后端数据库）

**Testing**: pytest (后端) / Vitest (前端)

**Target Platform**: Web 浏览器（桌面端和移动端响应式）

**Project Type**: Web 应用（前后端分离）

**Performance Goals**:
- 概览页首屏加载 < 3 秒
- 逐日详情页加载 < 5 秒
- 景点图片懒加载，首屏图片加载 < 2 秒
- 拖拽排序交互响应 < 100ms

**Constraints**:
- 高德地图 API 有调用频率限制（需考虑缓存和限流）
- 无用户身份验证（依赖 localStorage），数据无持久化保证
- 天气数据在行程生成时缓存，不实时更新
- 导出功能需在前端完成（图片/PDF 生成），不依赖后端

**Scale/Scope**:
- 单用户单次使用场景，无并发要求
- 行程天数合理范围 1-30 天
- 每日景点数量 1-10 个

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪法原则 | 检查项 | 状态 |
|---------|-------|------|
| I. 规范驱动开发 | 功能规范已完成 (spec.md)，遵循 speckit 工作流 | ✅ 通过 |
| II. 增量交付 | 功能可拆分为 5 个独立用户故事 (P1-P5)，P1 概览查看构成 MVP | ✅ 通过 |
| III. 测试纪律 | 后端 API 需编写 pytest 测试，前端组件需编写 Vitest 测试 | ✅ 通过 |
| IV. 代码质量 | Python 使用类型注解，TypeScript 使用类型系统，通过 lint/format 检查 | ✅ 通过 |
| V. 可观测性 | API 请求需记录结构化日志，关键操作有日志链路 | ✅ 通过 |
| VI. 审查与问责 | Speckit 流程产出存档于 spec/ 目录，变更需审查 | ✅ 通过 |
| 项目结构-分层 | 后端 api → services → models 正向依赖，前端优先使用 Element Plus | ✅ 通过 |
| 项目结构-目录 | 新增功能文件放入已有分层目录，无需新增顶层目录 | ✅ 通过 |
| 安全与环境 | API 密钥通过 `.env` 管理，不硬编码，日志不泄露密钥 | ✅ 通过 |

## Project Structure

### Documentation (this feature)

```text
specs/002-travel-plan-detail/
├── plan.md                     # This file (/speckit-plan command output)
├── research.md                 # Phase 0 output (/speckit-plan command)
├── data-model.md               # Phase 1 output (/speckit-plan command)
├── quickstart.md               # Phase 1 output (/speckit-plan command)
├── contracts/                  # Phase 1 output (/speckit-plan command)
├── spec.md                     # Feature specification (already exists)
├── prototype-requirements.md   # Prototype extraction (already exists)
└── tasks.md                    # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ── travel_plan.py      # 旅行计划相关 API 路由
│   │   └── deps.py                 # 依赖注入（高德 MCP 客户端、LLM 客户端）
│   ├── services/
│   │   ├── amap_service.py         # 高德地图 MCP 服务封装（POI、天气、路线）
│   │   ├── itinerary_service.py    # 行程规划生成服务
│   │   └── weather_service.py      # 天气数据缓存与查询服务
│   ├── models/
│   │   └── travel_plan.py          # 旅行计划数据模型（Pydantic）
│   ├── agents/
│   │   └── itinerary_agent.py      # 行程规划智能体
│   └── config.py                   # 配置管理
└── requirements.txt

frontend/
├── src/
│   ├── views/
│   │   ├── TravelPlanOverview.vue      # 旅行计划概览页
│   │   └── TravelPlanDayDetail.vue     # 逐日行程详情页
│   ├── components/
│   │   ├── BudgetCard.vue              # 预算明细卡片
│   │   ├── MapView.vue                 # 地图展示组件
│   │   ├── DailyScheduleList.vue       # 每日行程概览列表
│   │   ├── AttractionCard.vue          # 景点详情卡片
│   │   ├── ScheduleTimeline.vue        # 日程时间线
│   │   ├── AccommodationInfo.vue       # 住宿安排展示
│   │   ├── DiningInfo.vue              # 餐饮安排展示
│   │   ├── TransportationInfo.vue      # 交通安排展示
│   │   ├── WeatherInfo.vue             # 天气信息展示
│   │   ├── EditDayDrawer.vue           # 编辑行程抽屉（拖拽排序 + 删除）
│   │   ├── ReplanConfirmModal.vue      # 重新规划确认弹窗
│   │   └── ExportDropdown.vue          # 导出行程下拉菜单
│   ├── services/
│   │   ├── travelPlanService.ts        # 旅行计划 API 服务
│   │   └── storageService.ts           # localStorage 存储服务
│   ├── types/
│   │   └── travelPlan.ts               # TypeScript 类型定义
│   └── router/
│       └── index.ts                    # 路由配置
└── package.json
```

**Structure Decision**: 采用 Web 应用前后端分离架构。后端在已有 `backend/app/` 分层结构下新增旅行计划相关的路由、服务、模型和智能体文件；前端在已有 `frontend/src/` 结构下新增视图组件、服务、类型定义和路由。所有文件放入已有目录层级，无需新增顶层目录，符合宪法"项目结构"章节约束。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 高德地图 MCP 服务需后端代理 | API Key 不可暴露给前端 | 前端直接调用会泄露密钥 |
| 前端导出需引入 html2canvas + jsPDF | 无后端文件存储能力 | 后端生成需要用户会话存储，与 localStorage 架构不符 |
| LangChain/LangGraph/LangSmith 技术栈 | 需要复杂的多智能体编排（行程规划/景点推荐/预算计算）和可观测性 | 直接调用 OpenAI SDK 无法支持多智能体协作和链路追踪，LangChain 生态提供标准化 Agent 框架 |
