# Tasks: 旅行计划详情查看与编辑 (Travel Plan Detail)

**Input**: Design documents from `specs/002-travel-plan-detail/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api-contract.md

**Tests**: REQUIRED — spec.md defines success criteria with measurable outcomes; backend API endpoints have explicit contract definitions; constitution principle III mandates test discipline.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- All paths are relative to the repository root `D:\spec-SDD\test\my-agent2\travel-helper\`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — install LangChain/LangGraph/LangSmith dependencies, update configuration

- [X] T001 [P] 后端：在 `backend/requirements.txt` 中添加 LangChain / LangGraph / LangSmith 依赖（`langchain`, `langgraph`, `langsmith`, `langchain-openai`, `langchain-core`）
- [X] T002 [P] 前端：在 `frontend/package.json` 中添加高德地图和导出相关依赖（`html2canvas`, `jspdf`, `vuedraggable`, `@amap/amap-jsapi-loader`）
- [X] T003 [P] 配置：在 `backend/app/config.py` 中新增 LangSmith 配置项（`langsmith_api_key`, `langsmith_tracing`, `langsmith_project`）
- [X] T004 配置：在 `backend/.env.example` 中新增 `LANGSMITH_API_KEY` 环境变量模板

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 001 模块重构 + 核心数据模型 + LangChain 基础设施。**此阶段完成后用户故事才能开始实现。**

**⚠️ CRITICAL**: 必须先将 001 模块从 OpenAI SDK 迁移到 LangChain，否则 002 模块无法基于 LangGraph 构建智能体

### 2.1 001 模块 LangChain 迁移

- [X] T005 [P] 模板：创建提示词模板模块 `backend/app/templates/__init__.py`
- [X] T006 [P] 模板：创建公共片段 `backend/app/templates/_common.py`（角色定义、输出格式约束、规划原则）
- [X] T007 [P] 模板：创建行程规划提示词 `backend/app/templates/travel_planner/__init__.py` 和 `backend/app/templates/travel_planner/create.py`（CREATE_PROMPT）
- [X] T008 模型：创建结构化输出 Pydantic 模型 `backend/app/models/travel_plan_output.py`（TravelPlanOutput、DailyItinerary、Attraction 等）
- [X] T009 服务：将 `backend/app/services/llm_service.py` 替换为 LangChain 版本（`ChatOpenAI` + `with_structured_output` + 内置重试/超时）
- [X] T010 智能体：重写 `backend/app/agents/travel_planner_agent.py`，使用 `ChatPromptTemplate` 构建 prompt + 绑定 Pydantic 输出模型

### 2.2 共享数据模型

- [X] T011 [P] 模型：扩展 `backend/app/models/travel_plan.py`，补充完整 Pydantic 模型（TravelPlanResponse、DailyItinerary、AttractionDetail、AccommodationPlan、DiningPlan、TransportationPlan、WeatherInfo、BudgetBreakdown 等字段，与 data-model.md 对齐）
- [X] T012 [P] 类型：创建前端 TypeScript 类型定义 `frontend/src/types/travelPlan.ts`（与后端 Pydantic 模型对应）

### 2.3 高德 MCP 服务

- [X] T013 服务：创建 `backend/app/services/amap_service.py`（封装高德 POI 搜索、天气查询、路线规划、地理编码/逆地理编码 API，httpx 调用，JSON 返回）
- [X] T014 [P] 服务：创建 `backend/app/services/weather_service.py`（天气数据缓存层，基于目的地城市和日期）
- [X] T015 [P] 服务：创建 `backend/app/services/unsplash_service.py`（景点图片获取，基于 `UNSPLASH_ACCESS_KEY`）

### 2.4 依赖注入

- [X] T016 API：创建 `backend/app/api/deps.py`（依赖注入：高德 MCP 客户端、LLM 客户端、LangGraph 状态图实例）

**Checkpoint**: 基础设施就绪 —— 001 模块已迁移至 LangChain，共享模型、高德服务、依赖注入已完成，用户故事可以开始并行实现

---

## Phase 3: User Story 1 - 查看旅行计划概览 (Priority: P1) 🎯 MVP

**Goal**: 用户完成旅行计划创建后，能在概览页看到：计划基本信息、预算明细（分类+总费用）、目的地地图（标注景点和住宿）、每日行程概览列表

**Independent Test**: 完成 001 模块创建旅行计划后，前端自动跳转至概览页，页面成功加载并展示预算、地图、每日行程列表；点击某一天可跳转至详情页

### Tests for User Story 1

- [X] T017 [P] [US1] 后端：API 合约测试 `backend/tests/contract/test_travel_plan_api.py`（GET `/api/v1/travel-plans/{id}` 返回完整 TravelPlanResponse）
- [X] T018 [P] [US1] 后端：单元测试 `backend/tests/unit/test_travel_plan_model.py`（Pydantic 模型字段校验，预算总额计算）
- [X] T019 [P] [US1] 前端：组件测试 `frontend/tests/unit/BudgetCard.spec.ts`（预算卡片正确渲染分类金额和总费用）

### Implementation for User Story 1

- [X] T020 API：扩展 `backend/app/api/routes/travel_plan.py`，添加 `GET /api/v1/travel-plans/{id}` 端点（返回完整旅行计划数据，含预算、地图坐标、每日概要）
- [X] T021 [P] 服务：在 `backend/app/services/travel_plan_service.py` 中实现 `get_travel_plan` 方法（从 001 模块生成的数据中查询，补充地图坐标和天气）
- [X] T022 [P] 组件：创建 `frontend/src/components/BudgetCard.vue`（预算明细卡片，Element Plus el-card + 分类金额展示）
- [X] T023 [P] 组件：创建 `frontend/src/components/MapView.vue`（高德地图嵌入，onMounted 初始化 AMap，渲染景点和住宿标记点）
- [X] T024 [P] 组件：创建 `frontend/src/components/DailyScheduleList.vue`（每日行程概览列表，Element Plus el-timeline 或 el-table，点击跳转详情页）
- [X] T025 视图：创建 `frontend/src/views/TravelPlanOverview.vue`（概览页主组件，组装 BudgetCard + MapView + DailyScheduleList，Axios 调用 GET API）
- [X] T026 路由：在 `frontend/src/router/index.ts` 中注册概览页路由 `/travel-plans/:id/overview`
- [X] T027 服务：创建 `frontend/src/services/travelPlanService.ts`（Axios 封装，调用后端旅行计划 API）
- [X] T028 服务：创建 `frontend/src/services/storageService.ts`（localStorage 读写封装，存储/获取旅行计划 ID）
- [X] T029 集成：连接 001 模块的创建成功回调，跳转至概览页（传递计划 ID）

**Checkpoint**: User Story 1 应可独立运行 —— 用户完成旅行计划创建后能看到概览页，包含预算、地图和每日行程列表，点击某一天可跳转

---

## Phase 4: User Story 2 - 查看逐日行程详情 (Priority: P2)

**Goal**: 用户在概览页点击某一天后，进入逐日详情页，看到：日程时间线、景点详情卡片（图片/名称/游玩时间/特色/描述）、住宿安排、餐饮安排、交通安排、当日天气

**Independent Test**: 从概览页点击"第1天"进入详情页后，页面加载展示当日所有行程信息板块（景点、住宿、餐饮、交通、天气）

### Tests for User Story 2

- [X] T030 [P] [US2] 后端：API 合约测试 `backend/tests/contract/test_day_detail_api.py`（GET `/api/v1/travel-plans/{id}/day/{dayIndex}` 返回当日完整行程数据）
- [X] T031 [P] [US2] 前端：组件测试 `frontend/tests/unit/AttractionCard.spec.ts`（景点卡片正确渲染图片、名称、游玩时间、特色、描述）

### Implementation for User Story 2

- [X] T032 API：在 `backend/app/api/routes/travel_plan.py` 中添加 `GET /api/v1/travel-plans/{id}/day/{dayIndex}` 端点
- [X] T033 服务：在 `backend/app/services/travel_plan_service.py` 中实现 `get_day_detail` 方法（按 dayIndex 筛选当日行程，补充天气、景点图片）
- [X] T034 [P] 组件：创建 `frontend/src/components/AttractionCard.vue`（景点详情卡片，Element Plus el-card + 图片懒加载 + 特色标签）
- [X] T035 [P] 组件：创建 `frontend/src/components/ScheduleTimeline.vue`（日程时间线，展示时间段与活动对应关系）
- [X] T036 [P] 组件：创建 `frontend/src/components/AccommodationInfo.vue`（住宿安排展示，Element Plus el-descriptions）
- [X] T037 [P] 组件：创建 `frontend/src/components/DiningInfo.vue`（餐饮安排展示，早/午/晚餐推荐）
- [X] T038 [P] 组件：创建 `frontend/src/components/TransportationInfo.vue`（交通安排展示，航班/火车/地铁信息）
- [X] T039 [P] 组件：创建 `frontend/src/components/WeatherInfo.vue`（天气信息展示，天气状况 + 温度范围 + 风速）
- [X] T040 视图：创建 `frontend/src/views/TravelPlanDayDetail.vue`（逐日详情页主组件，组装上述所有子组件）
- [X] T041 路由：在 `frontend/src/router/index.ts` 中注册详情页路由 `/travel-plans/:id/day/:dayIndex`
- [X] T042 集成：DailyScheduleList 组件的点击跳转逻辑，传递 planId 和 dayIndex 至详情页路由

**Checkpoint**: User Stories 1 AND 2 均可独立工作 —— 概览页可查看并跳转，详情页可展示当天完整行程

---

## Phase 5: User Story 3 - 编辑行程调整景点 (Priority: P3)

**Goal**: 用户可以编辑某一天的行程，通过拖拽调整景点顺序、通过删除按钮移除景点，保存后更新生效

**Independent Test**: 在详情页点击"编辑行程"打开抽屉，拖拽调整景点卡片顺序，点击删除按钮移除景点，保存后详情页展示更新后的行程

### Tests for User Story 3

- [X] T043 [P] [US3] 后端：API 合约测试 `backend/tests/contract/test_edit_day_api.py`（PUT `/api/v1/travel-plans/{id}/day/{dayIndex}` 更新当日行程数据）
- [X] T044 [P] [US3] 后端：单元测试 `backend/tests/unit/test_edit_day_validation.py`（至少保留 1 个景点的校验规则）

### Implementation for User Story 3

- [X] T045 API：在 `backend/app/api/routes/travel_plan.py` 中添加 `PUT /api/v1/travel-plans/{id}/day/{dayIndex}` 端点
- [X] T046 服务：在 `backend/app/services/travel_plan_service.py` 中实现 `update_day_itinerary` 方法（校验至少保留 1 个景点，更新 dailyItineraries 对应天的数据，更新 updatedAt）
- [X] T047 [P] 模板：创建编辑行程提示词 `backend/app/templates/travel_planner/edit_day.py`（EDIT_DAY_PROMPT，可选，用于 AI 辅助编辑场景）
- [X] T048 [P] 组件：创建 `frontend/src/components/EditDayDrawer.vue`（编辑行程抽屉，Element Plus el-drawer + vuedraggable 拖拽排序 + 删除按钮）
- [X] T049 视图：在 `frontend/src/views/TravelPlanDayDetail.vue` 中集成"编辑行程"按钮和 EditDayDrawer 抽屉组件
- [X] T050 集成：拖拽排序完成后通过 Axios 调用 PUT API 保存更新，更新后刷新详情页数据

**Checkpoint**: User Story 3 可独立测试 —— 编辑抽屉可打开、拖拽/删除景点、保存生效

---

## Phase 6: User Story 4 - 导出旅行计划 (Priority: P4)

**Goal**: 用户通过导出功能将旅行计划保存为图片或 PDF 文件

**Independent Test**: 在概览页点击"导出行程"下拉菜单，选择图片或 PDF 格式，触发文件下载

### Implementation for User Story 4

- [X] T051 [P] 组件：创建 `frontend/src/components/ExportDropdown.vue`（导出行程下拉菜单，Element Plus el-dropdown，提供图片/PDF 两个选项）
- [X] T052 服务：创建 `frontend/src/services/exportService.ts`（封装 html2canvas + jsPDF 导出逻辑：图片导出捕获 DOM → canvas.toDataURL() → 触发下载；PDF 导出逐页添加图片 → jsPDF.save()）
- [X] T053 视图：在 `frontend/src/views/TravelPlanOverview.vue` 的工具栏区域集成 ExportDropdown 组件
- [X] T054 集成：导出时自动捕获概览页和所有天的行程摘要内容（跳过地图等复杂 DOM），生成文件并触发下载

**Checkpoint**: User Story 4 可独立测试 —— 导出下拉菜单可用，图片和 PDF 格式均可正常生成和下载

---

## Phase 7: User Story 5 - 重新规划行程 (Priority: P5)

**Goal**: 用户点击"重新规划"按钮，弹出确认弹窗，确认后系统重新生成旅行计划

**Independent Test**: 在概览页点击"重新规划"按钮，出现确认弹窗提示"重新规划将覆盖当前的行程安排"，点击确认后页面重新加载生成新的行程

### Implementation for User Story 5

- [X] T055 [P] 模板：创建重新规划提示词 `backend/app/templates/travel_planner/replan.py`（REPLAN_PROMPT，注入当前行程 + 用户编辑痕迹 + 新约束）
- [X] T056 智能体：在 `backend/app/agents/itinerary_agent.py` 中实现 LangGraph StateGraph（重新规划流程的节点状态管理：收集上下文 → 调用 LLM → 返回新行程）
- [X] T057 API：在 `backend/app/api/routes/travel_plan.py` 中添加 `POST /api/v1/travel-plans/{id}/replan` 端点（调用 LangGraph StateGraph，返回新行程数据）
- [X] T058 [P] 组件：创建 `frontend/src/components/ReplanConfirmModal.vue`（重新规划确认弹窗，Element Plus el-dialog，警告提示编辑内容将丢失）
- [X] T059 视图：在 `frontend/src/views/TravelPlanOverview.vue` 的工具栏区域集成"重新规划"按钮和 ReplanConfirmModal 弹窗
- [X] T060 集成：确认弹窗点击确认后调用 POST replan API，等待响应后刷新概览页数据

**Checkpoint**: 所有用户故事均独立可工作 —— P1~P5 功能完整

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 改进影响多个用户故事的通用问题

- [X] T061 可观测性：配置 LangSmith 追踪集成（`backend/app/config.py` 设置 `LANGSMITH_TRACING=true`，在 LangGraph 调用时自动追踪）
- [X] T062 [P] 可观测性：在后端 API 路由中添加结构化日志（请求 ID、时间戳、响应状态、耗时）
- [X] T063 错误处理：统一错误响应格式（FR-018，所有 API 错误返回 `{"detail": "错误信息"}` 格式）
- [X] T064 [P] 加载状态：在所有视图组件中集成加载骨架屏/加载动画（FR-020）
- [X] T065 [P] 占位处理：景点图片缺失时展示占位图，地图加载失败时展示占位图和重试按钮
- [X] T066 [P] 前端：在 `frontend/src/components/` 下创建公共样式组件（如 loading 动画、empty 状态、error 提示）
- [X] T067 集成测试：端到端流程测试（创建 → 概览 → 详情 → 编辑 → 导出），覆盖用户完整旅程
- [X] T068 文档：更新 `specs/002-travel-plan-detail/quickstart.md`，补充 LangSmith 配置和 LangGraph 使用说明
- [X] T069 验证：运行 `quickstart.md` 中的全部启动和测试步骤，确保端到端流程正常

---

## Dependencies & Execution Order

### Phase Dependencies

| 阶段 | 依赖 | 说明 |
|------|------|------|
| **Phase 1 Setup** | 无 | 可立即开始 |
| **Phase 2 Foundational** | Phase 1 完成 | 阻塞所有用户故事 |
| **Phase 3 US1 (P1)** | Phase 2 完成 | MVP 范围 |
| **Phase 4 US2 (P2)** | Phase 2 完成 | 与 US1 并行（有 staff 时） |
| **Phase 5 US3 (P3)** | Phase 2 + US2 完成 | 详情页组件是编辑功能的前置条件 |
| **Phase 6 US4 (P4)** | Phase 2 + US1 完成 | 概览页是导出功能的前置条件 |
| **Phase 7 US5 (P5)** | Phase 2 + US1 + US3 完成 | 需要概览页按钮 + 编辑历史上下文 |
| **Phase 8 Polish** | 所有目标用户故事完成 | 跨故事通用改进 |

### User Story Dependencies

```
Phase 2 Foundational
    ├── Phase 3 US1 (P1) ─── MVP ─── Phase 6 US4 (P4)
    ├── Phase 4 US2 (P2) ─── Phase 5 US3 (P3)
    │                         │
    └─────────────────────────┴──── Phase 7 US5 (P5)
```

- **US1 (P1)**: Foundational 完成后可启动 —— 无其他故事依赖
- **US2 (P2)**: Foundational 完成后可启动 —— 与 US1 并行
- **US3 (P3)**: 依赖 US2（详情页组件是编辑功能基础）
- **US4 (P4)**: 依赖 US1（概览页是导出入口）
- **US5 (P5)**: 依赖 US1 + US3（概览页按钮 + 编辑历史上下文）

### Within Each User Story

1. 测试先写并确保失败（TDD）
2. 模型 → 服务 → API 端点 → 前端组件 → 视图 → 路由
3. 核心实现先于集成
4. 每个故事完成后在 checkpoint 处独立验证

### Parallel Opportunities

- **Phase 1**: T001、T002、T003、T004 完全并行
- **Phase 2**:
  - T005~T007（模板模块）可并行
  - T008（Pydantic 模型）+ T009（LLM 服务）+ T010（智能体）可并行
  - T013（高德服务）+ T014（天气服务）+ T015（Unsplash 服务）可并行
  - T011~T012 与 T013~T015 可并行（后端 vs 前端类型定义）
- **Phase 3**: T017~T019（测试）可并行；T022~T024（前端组件）可并行
- **Phase 4**: T030~T031（测试）可并行；T034~T039（前端组件）可并行

---

## Parallel Execution Examples

### Phase 1 并行

```bash
# 同时执行：
T001: 添加 LangChain 依赖到 requirements.txt
T002: 添加前端 npm 依赖到 package.json
T003: 新增 LangSmith 配置项到 config.py
T004: 更新 .env.example 模板
```

### Phase 2 并行

```bash
# 模板组并行：
T005: templates/__init__.py
T006: templates/_common.py
T007: templates/travel_planner/create.py

# 数据组并行：
T008: models/travel_plan_output.py
T011: models/travel_plan.py 扩展
T012: types/travelPlan.ts

# 服务组并行：
T009: services/llm_service.py (LangChain 版本)
T013: services/amap_service.py
T014: services/weather_service.py
T015: services/unsplash_service.py
```

### Phase 4 前端组件并行

```bash
# 所有展示型组件可并行创建：
T034: AttractionCard.vue
T035: ScheduleTimeline.vue
T036: AccommodationInfo.vue
T037: DiningInfo.vue
T038: TransportationInfo.vue
T039: WeatherInfo.vue
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1: Setup（4 tasks）
2. 完成 Phase 2: Foundational（16 tasks）
3. 完成 Phase 3: User Story 1（13 tasks）
4. **STOP AND VALIDATE**: 独立测试 US1 —— 用户完成创建后可看到概览页（预算、地图、每日列表）
5. Deploy/demo if ready

### Incremental Delivery

| 阶段 | 任务数 | 累计 | 交付物 |
|------|--------|------|--------|
| Phase 1 Setup | 4 | 4 | 依赖安装完成 |
| Phase 2 Foundational | 16 | 20 | 001 迁移 + 共享模型 + 高德服务 |
| Phase 3 US1 | 13 | 33 | 🎯 **MVP**: 概览页 |
| Phase 4 US2 | 12 | 45 | 逐日详情页 |
| Phase 5 US3 | 8 | 53 | 编辑行程 |
| Phase 6 US4 | 4 | 57 | 导出功能 |
| Phase 7 US5 | 6 | 63 | 重新规划 |
| Phase 8 Polish | 9 | **72** | 可观测性、错误处理、文档 |

### Parallel Team Strategy

With 2 developers:
1. 共同完成 Phase 1 + Phase 2
2. Phase 2 完成后：
   - Developer A: Phase 3 (US1) + Phase 6 (US4)
   - Developer B: Phase 4 (US2) + Phase 5 (US3) + Phase 7 (US5)
3. Phase 8 共同完成

---

## Format Validation

✅ ALL 72 tasks follow the checklist format:
- `- [ ]` checkbox prefix
- Sequential Task ID (T001 ~ T072)
- `[P]` marker for parallelizable tasks
- `[US1]`~`[US5]` labels for user story phase tasks only
- Description with exact file path
- No missing format components

## Notes

- 任务总数: **72**
- MVP 范围 (US1): **33** tasks (Phase 1 + 2 + 3)
- 可并行任务: 约 **28** 个（标记 [P]）
- 每个用户故事都有明确的 Independent Test 标准
- 001 模块的 LangChain 迁移是 002 模块的阻塞前置条件（Phase 2 必须完成）
