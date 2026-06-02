# Tasks: 旅行计划创建 (Travel Plan Create)

**Input**: Design documents from `/specs/001-travel-plan-create/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 宪法原则 III（测试纪律）要求测试先于实现。本任务清单包含测试任务，遵循红-绿-重构循环。

**Organization**: 任务按用户故事分组（US1=P1 基础计划、US2=P2 偏好定制、US3=P3 特殊服务），每个故事可独立实现和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行（不同文件，无未完成依赖）
- **[Story]**: 所属用户故事（US1, US2, US3）
- 描述中包含精确文件路径

## Path Conventions

- **Web 应用**: 后端 `backend/`，前端 `frontend/`
- 后端: `backend/app/{api,models,services,agents}/`
- 前端: `frontend/src/{views,components,services,types}/`

---

## Phase 1: Setup (项目初始化)

**Purpose**: 创建前后端项目结构和依赖配置

- [x] T001 创建后端目录结构和 `backend/app/__init__.py`
- [x] T002 创建 `backend/requirements.txt`（FastAPI, uvicorn, pydantic, python-dotenv, openai, pytest）
- [x] T003 [P] 创建前端目录结构和 `frontend/package.json`（Vue 3 + Vite + TypeScript）
- [x] T004 [P] 创建 `frontend/tsconfig.json` 和 `frontend/vite.config.ts`
- [x] T005 [P] 配置后端 lint/format 工具（ruff + black）
- [x] T006 [P] 配置前端 lint/format 工具（ESLint + Prettier）
- [x] T007 创建 `backend/.env.example` 和 `backend/.gitignore`

---

## Phase 2: Foundational (阻塞性前置依赖)

**Purpose**: 所有用户故事实现前必须完成的核心基础设施

**⚠️ CRITICAL**: 此阶段完成前不得开始任何用户故事工作

- [x] T008 创建后端入口 `backend/app/main.py`（FastAPI 应用实例 + CORS 中间件）
- [x] T009 创建环境配置 `backend/app/config.py`（读取 `.env` 中的 LLM_API_KEY 等）
- [x] T010 [P] 创建城市静态数据 `backend/data/cities.json`（中国大陆地级市列表，含 name/pinyin/province/code）
- [x] T011 [P] 创建后端 pydantic 基础模型 `backend/app/models/__init__.py`
- [x] T012 [P] 创建前端路由配置 `frontend/src/router/index.ts`
- [x] T013 创建前端 API 服务基础 `frontend/src/services/api.ts`（Axios 实例，baseURL，拦截器）
- [x] T014 配置结构化日志（`backend/app/main.py` 中添加请求日志中间件，含 request_id）

**Checkpoint**: 基础就绪，可开始用户故事实现

---

## Phase 3: User Story 1 - 创建基础旅行计划 (Priority: P1) 🎯 MVP

**Goal**: 用户输入目的地城市、出行日期、交通方式后，提交生成一份基础旅行计划

**Independent Test**: 用户仅填写目的地、起止日期和交通方式即可成功提交并生成包含每日行程的基础旅行计划

### US1 测试（先写，确认失败后再实现） ⚠️

- [x] T015 [P] [US1] 城市搜索 API 单元测试 `backend/tests/unit/test_city_service.py`（验证搜索匹配逻辑）
- [x] T016 [P] [US1] 日期校验单元测试 `backend/tests/unit/test_travel_plan_validation.py`（验证日期合法性、天数计算）
- [x] T017 [US1] 旅行计划生成 API 集成测试 `backend/tests/integration/test_travel_plan_api.py`（完整请求-响应流程）
- [x] T018 [P] [US1] API 契约测试 `backend/tests/contract/test_api_contract.py`（验证请求/响应符合 contracts/api-contract.md）

### US1 实现

- [x] T019 [P] [US1] 创建城市数据模型 `backend/app/models/city.py`（pydantic 模型 + JSON 加载逻辑）
- [x] T020 [P] [US1] 创建旅行计划请求/响应模型 `backend/app/models/travel_plan.py`（TravelPlanCreateRequest, TravelPlanResponse）
- [x] T021 [US1] 创建城市搜索服务 `backend/app/services/city_service.py`（按名称/拼音搜索）
- [x] T022 [US1] 创建 LLM 调用服务 `backend/app/services/llm_service.py`（OpenAI SDK 封装，指数退避重试，30 秒超时）
- [x] T023 [US1] 创建旅行计划智能体 `backend/app/agents/travel_planner_agent.py`（构建系统 prompt + 用户 prompt）
- [x] T024 [US1] 创建旅行计划服务 `backend/app/services/travel_plan_service.py`（校验输入 + 调用 agent + 结构化 LLM 响应）
- [x] T025 [US1] 创建旅行计划 API 路由 `backend/app/api/routes/travel_plan.py`（POST /api/v1/travel-plans/generate, GET /api/v1/cities/search）
- [x] T026 [US1] 注册路由到 FastAPI 应用 `backend/app/main.py`（添加 router 前缀）
- [x] T027 [P] [US1] 创建前端类型定义 `frontend/src/types/travelPlan.ts`（对应后端请求/响应模型）
- [x] T028 [P] [US1] 创建前端 API 服务 `frontend/src/services/travelPlanApi.ts`（调用生成计划和城市搜索接口）
- [x] T029 [US1] 创建城市搜索组件 `frontend/src/components/CitySearch.vue`（输入框 + 自动补全下拉列表）
- [x] T030 [US1] 创建日期选择组件 `frontend/src/components/DatePicker.vue`（起止日期 + 天数自动计算）
- [x] T031 [US1] 创建交通方式选择组件 `frontend/src/components/TransportSelector.vue`（单选列表）
- [x] T032 [US1] 创建旅行计划创建表单页面 `frontend/src/views/TravelPlanCreate.vue`（整合表单 + 必填验证 + 提交 + 加载状态）
- [x] T033 [US1] 创建前端应用入口 `frontend/src/App.vue` 和主页面 `frontend/src/main.ts`

**Checkpoint**: 至此 US1 应完全可用——用户可填写目的地、日期、交通方式并生成基础旅行计划

---

## Phase 4: User Story 2 - 使用偏好定制旅行计划 (Priority: P2)

**Goal**: 用户在基础信息之上选择住宿偏好和多个旅行偏好标签，生成个性化旅行计划

**Independent Test**: 用户选择住宿偏好和多个旅行偏好标签后，生成的旅行计划中推荐的活动和路线与所选偏好匹配

### US2 测试

- [x] T034 [US1] 偏好传递集成测试 `backend/tests/integration/test_preference_flow.py`（验证偏好参数正确传递到 LLM prompt）

### US2 实现

- [x] T035 [US1] 创建偏好选择组件 `frontend/src/components/PreferenceSelector.vue`（多选标签芯片）
- [x] T036 [US1] 在表单页面 `frontend/src/views/TravelPlanCreate.vue` 中集成住宿偏好和旅行偏好选择
- [x] T037 [US1] 在旅行计划请求模型 `backend/app/models/travel_plan.py` 中添加 preferences 字段校验（枚举值验证）
- [x] T038 [US1] 在智能体 `backend/app/agents/travel_planner_agent.py` 中将偏好信息注入 prompt 模板
- [x] T039 [US1] 在旅行计划响应模型中添加基于偏好的活动匹配验证

**Checkpoint**: 至此 US1 和 US2 均可独立工作，US2 在 US1 基础上增加了偏好定制能力

---

## Phase 5: User Story 3 - 添加特殊服务要求 (Priority: P3)

**Goal**: 用户可在表单中填写特殊服务要求，系统在生成旅行计划时考虑这些需求

**Independent Test**: 用户填写特殊服务要求后提交，生成的旅行计划中体现出对特殊需求的响应

### US3 实现

- [x] T040 [US1] 在表单页面 `frontend/src/views/TravelPlanCreate.vue` 中添加特殊服务要求文本域（可选，最大 500 字符）
- [x] T041 [US1] 在旅行计划请求模型 `backend/app/models/travel_plan.py` 中添加 special_requirements 字段（可选，长度校验）
- [x] T042 [US1] 在智能体 `backend/app/agents/travel_planner_agent.py` 中将特殊服务要求注入 prompt 模板

**Checkpoint**: 所有用户故事均已可独立工作

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 跨故事的改进和优化

- [x] T043 [P] 添加前端表单整体样式和响应式布局适配（移动端 + 桌面端）
- [x] T044 [P] 添加后端错误处理统一中间件（500/504 错误格式统一，含 request_id）
- [x] T045 完善 LLM 响应解析（确保返回的 JSON 符合 TravelPlanResponse schema）
- [x] T046 [P] 编写 `backend/README.md` 和 `frontend/README.md` 开发指南
- [ ] T047 运行 quickstart.md 全流程验证（安装依赖 → 启动服务 → 提交表单 → 验证结果）
- [ ] T048 清理无用代码和注释，确保通过 lint 检查

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: 无依赖，可立即开始
- **Phase 2 Foundational**: 依赖 Phase 1 完成 → **阻塞**所有用户故事
- **Phase 3+ 用户故事**: 均依赖 Phase 2 完成
  - US1 (P1) 可并行启动（有团队人力时）
  - 或按优先级顺序执行 P1 → P2 → P3
- **Phase 6 Polish**: 依赖所有目标用户故事完成

### User Story Dependencies

- **US1 (P1)**: Phase 2 完成后可开始，无其他故事依赖
- **US2 (P2)**: Phase 2 完成后可开始，复用 US1 的基础组件（模型、服务、API 路由）
- **US3 (P3)**: Phase 2 完成后可开始，复用 US1/US2 的基础组件

### Within Each User Story

- 测试（如包含）必须先写并确认失败后再实现
- 模型 → 服务 → API 路由 → 前端组件
- 核心实现优先于集成

### Parallel Opportunities

- Phase 1 中 T003/T004/T005/T006 可并行（前后端独立配置）
- Phase 2 中 T010/T011/T012 可并行
- US1 中 T015/T016 测试可并行，T019/T020 模型可并行，T027/T028 前端类型和服务可并行
- US1 中后端服务（T021-T026）和前端组件（T029-T033）可并行开发

---

## Parallel Example: User Story 1

```bash
# 后端模型并行:
Task: "创建城市数据模型 backend/app/models/city.py"
Task: "创建旅行计划请求/响应模型 backend/app/models/travel_plan.py"

# 前端类型和服务并行:
Task: "创建前端类型定义 frontend/src/types/travelPlan.ts"
Task: "创建前端 API 服务 frontend/src/services/travelPlanApi.ts"

# 测试并行:
Task: "城市搜索 API 单元测试 backend/tests/unit/test_city_service.py"
Task: "日期校验单元测试 backend/tests/unit/test_travel_plan_validation.py"
```

---

## Implementation Strategy

### MVP First (仅 US1)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（关键——阻塞所有故事）
3. 完成 Phase 3: User Story 1
4. **停止并验证**: 独立测试 US1——用户可填写目的地、日期、交通方式并生成基础旅行计划
5. 部署/演示

### Incremental Delivery

1. Setup + Foundational → 基础就绪
2. 添加 US1 → 独立测试 → 部署/演示（MVP！）
3. 添加 US2 → 独立测试 → 部署/演示
4. 添加 US3 → 独立测试 → 部署/演示
5. 每个故事增加价值且不破坏已有功能

### Parallel Team Strategy

多人开发时：
1. 团队共同完成 Setup + Foundational
2. Foundational 完成后：
   - 开发者 A: US1（后端服务 + API）
   - 开发者 B: US1（前端组件 + 页面）
3. US1 完成后：
   - 开发者 A: US2 后端（偏好 prompt 注入）
   - 开发者 B: US2 前端（偏好组件）

---

## Notes

- [P] 任务 = 不同文件，无依赖，可并行
- [US1/US2/US3] 标签映射到对应用户故事，可追溯
- 每个用户故事应可独立完整和测试
- 测试先写并确认失败后再实现
- 每个任务或逻辑组完成后提交
- 可在任何 Checkpoint 停止以独立验证故事
- 避免：模糊任务、同一文件冲突、跨故事依赖破坏独立性
