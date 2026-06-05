# Research Findings: 旅行计划详情查看与编辑

## Decision 1: 高德地图 MCP 服务集成方式

**Rationale**: 高德地图提供十余个 API（POI 搜索、天气查询、路线规划、地理编码等），本项目通过后端 FastAPI 服务作为代理层调用高德 Web 服务 API（HTTP REST 接口，返回 JSON）。MCP（Model Context Protocol）服务在此项目中指后端作为 LLM Agent 的工具接口，而非独立的高德 MCP 服务器。后端通过 `httpx` 库调用高德 API，将 JSON 结果返回给前端或 LLM Agent。

**API 使用清单**:
| API | 用途 | 端点 |
|-----|------|------|
| POI 搜索 | 搜索景点和酒店位置 | `/v3/place/text` |
| 天气查询 | 获取目的地天气 | `/v3/weather/weatherInfo` |
| 路线规划 | 计算景点间路线 | `/v3/direction/driving` |
| 地理编码 | 城市名转经纬度 | `/v3/geocode/geo` |
| 逆地理编码 | 经纬度转地址 | `/v3/geocode/regeo` |

**认证**: 通过 `AMAP_WEB_KEY` 环境变量传递，作为 API 请求的 `key` 参数。

**限流**: 高德 Web 服务 API 默认限流 2000 次/天，单个 key 并发不超过 50 QPS。后端需实现简单的请求缓存和并发控制。

**Alternatives considered**:
- 前端直接调用高德 API — 不推荐，会暴露 API Key
- 使用高德 JS API 仅做前端展示 — 部分场景可行，但天气查询和 POI 搜索更适合后端代理

---

## Decision 2: 前端导出方案（html2canvas + jsPDF）

**Rationale**: 由于数据存储在 localStorage 且用户无需登录，后端无用户会话存储能力。导出功能完全在前端完成：使用 `html2canvas` 将旅行计划页面渲染为图片，使用 `jsPDF` 将内容编排为 PDF 文档。两种导出均在浏览器中完成，用户点击后直接触发文件下载。

**实现要点**:
- 图片导出: `html2canvas` 捕获目标 DOM 区域 → `canvas.toDataURL()` → 触发 `<a download>` 下载
- PDF 导出: `html2canvas` 捕获各页面区域 → `jsPDF` 逐页添加图片 → 触发下载
- 导出的内容包含: 计划概览、预算明细、每日行程摘要（不导出地图等复杂 DOM）

**Alternatives considered**:
- 后端生成 PDF — 需要后端存储用户数据并维持会话，与 localStorage 架构不符
- 仅导出图片格式 — PDF 更适合多页内容，用户体验更好

---

## Decision 3: 拖拽排序组件选型（vuedraggable + Sortable.js）

**Rationale**: `vuedraggable` 是基于 `Sortable.js` 的 Vue 3 拖拽组件，与 Vue 3 完全兼容，支持拖拽排序、拖入/拖出、跨列表拖拽等。Element Plus 2.x 项目中可安全使用 vuedraggable，不冲突。

**实现要点**:
- 编辑抽屉中使用 `<draggable v-model="attractions" item-key="id">` 包装景点卡片列表
- 拖拽完成后 v-model 自动更新景点顺序
- 每个景点卡片右上角放置删除按钮（Element Plus `el-button` type="text" icon="Delete"）
- 保存时将更新后的景点列表提交至后端（更新 localStorage 数据）

**Alternatives considered**:
- 手写拖拽逻辑 — 工作量大，不如使用成熟组件
- 上移/下移按钮 — 交互不够直观，用户学习成本高
- Element Plus 的 el-table 拖拽 — 不适合卡片式布局

---

## Decision 4: 高德地图前端嵌入方案

**Rationale**: 前端概览页的地图展示使用高德地图 JavaScript API V2.0（AMapLoader 异步加载），在 Vue 3 组件中通过 `onMounted` 生命周期初始化地图实例。地图功能包括:
- 加载目的地城市地图
- 在地图上添加标记点（Marker）标注景点和酒店位置
- 自定义标记图标（景点用景点 icon，酒店用酒店 icon）
- 标记点点击显示信息窗体（InfoWindow）展示名称和简要信息

**实现要点**:
- 使用 `@amap/amap-jsapi-loader` npm 包加载高德地图 JS API
- 地图容器为 `el-card` 内的固定高度 div
- 景点/酒店坐标通过后端高德地理编码 API 获取（城市名/地址 → 经纬度）
- 前端接收坐标数据后在地图上渲染标记

**Alternatives considered**:
- 使用高德地图 Vue 组件库 — 官方维护但功能有限，不如直接使用 JS API 灵活
- 使用其他地图服务（如 Mapbox） — 与项目已配置的高德 API Key 不一致

---

## Decision 5: 大模型交互技术栈（LangChain / LangGraph / LangSmith）

**Rationale**: 项目决定从直接使用 OpenAI SDK（`AsyncOpenAI`）切换到 LangChain / LangGraph / LangSmith 技术栈，原因如下：

1. **LangChain** — 提供标准化的 LLM 抽象层（ChatModel/Tool/Agent），支持多模型供应商切换（OpenAI、DeepSeek、Anthropic 等），内置重试、超时、流式输出等能力，替代手动编写的 `llm_service.py`
2. **LangGraph** — 提供 StateGraph 编程模型，支持多智能体协作编排（如行程规划智能体 + 景点推荐智能体 + 预算计算智能体），适合 002 模块中"重新规划"等复杂流程
3. **LangSmith** — 提供 LLM 调用追踪、Prompt 版本管理、测试评估能力，满足宪法"可观测性"原则的结构化日志要求

**架构设计**:
```
FastAPI Route → LangGraph StateGraph → LangChain Agent (LangSmith Tracing)
                     ├── 行程规划节点 (itinerary_agent)
                     ├── 景点搜索节点 (attraction_search_tool)
                     ├── 天气查询节点 (weather_query_tool)
                     └── 预算计算节点 (budget_calculator)
```

**001 模块迁移要点**:
- `llm_service.py` → 替换为 LangChain 的 `ChatOpenAI` / `ChatDeepSeek` 模型实例
- `travel_planner_agent.py` → 升级为 LangGraph 的 StateGraph，将 prompt 构建改为 LangChain 的 PromptTemplate
- `config.py` → 新增 `LANGSMITH_API_KEY`、`LANGSMITH_TRACING` 配置项
- `requirements.txt` → 新增 `langchain`、`langgraph`、`langsmith`、`langchain-openai` 等依赖

**002 模块新增**:
- `itinerary_agent.py` → LangGraph StateGraph，支持"重新规划"流程的节点状态管理
- `amap_service.py` → 封装为 LangChain Tool，供 Agent 调用高德 MCP 服务

**Alternatives considered**:
- 继续使用 OpenAI SDK + 手写重试逻辑 — 可运行但缺乏标准化、可观测性和多智能体编排能力
- 使用 AutoGen / CrewAI — 更重、学习曲线高，LangChain 生态更成熟且与 LangSmith 原生集成
- 不使用 LangSmith — 失去 LLM 调用追踪和 Prompt 版本管理能力，不利于调试和迭代
