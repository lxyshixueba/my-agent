# Quickstart: 旅行计划详情查看与编辑

## 前置条件

- 已完成 001 模块（旅行计划创建）的开发和部署
- 本地已配置 `.env` 文件，包含以下密钥：
  - `LLM_API_KEY` — 大语言模型 API
  - `AMAP_WEB_KEY` — 高德地图 Web 服务
  - `UNSPLASH_ACCESS_KEY` — Unsplash 图片服务
  - `LANGSMITH_API_KEY` — LangSmith 追踪 API 密钥（可选）
  - `LANGSMITH_TRACING` — 是否开启追踪，默认 `true`
  - `LANGSMITH_PROJECT` — LangSmith 项目名称，默认 `travel-helper`

## LangSmith 配置

本功能使用 LangChain / LangGraph / LangSmith 技术栈进行大模型交互和可观测性。

### 启用 LangSmith 追踪

在 `backend/.env` 中配置以下环境变量：

```env
# LangSmith 追踪（可选，推荐开发环境开启）
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=travel-helper
```

- `LANGSMITH_API_KEY`: 从 [LangSmith 控制台](https://smith.langchain.com/) 获取
- `LANGSMITH_TRACING`: 默认为 `true`，设为 `false` 可关闭追踪
- `LANGSMITH_PROJECT`: 追踪数据所属的项目名称

启用后，所有 LLM 调用和 LangGraph StateGraph 执行将被自动追踪到 LangSmith 平台，
便于调试和性能分析。

> 注意: 如果 `LANGSMITH_TRACING=true` 但未配置 `LANGSMITH_API_KEY`，
> 应用启动时会输出警告，追踪功能将不可用但不影响正常运行。

## LangGraph 使用说明

本功能的重新规划功能使用 LangGraph StateGraph 编排：

```
collect_context --> call_llm --> return_result --> END
```

- **collect_context**: 验证必要输入参数，准备上下文信息
- **call_llm**: 使用 LangChain `ChatOpenAI` 调用 LLM 生成新行程
- **return_result**: 解析 LLM 返回的 JSON，提取行程数据

StateGraph 实例通过 `backend/app/agents/itinerary_agent.py` 中的 `get_replan_graph()` 获取。

当 LangSmith 追踪开启时，StateGraph 的每个节点执行和 LLM 调用都会被自动记录到 LangSmith 平台。

## 安装依赖

### 后端

```bash
cd backend
pip install -r requirements.txt
```

新增依赖（如尚未安装）：

```bash
pip install httpx
```

### 前端

```bash
cd frontend
npm install
```

新增依赖：

```bash
npm install html2canvas jspdf vuedraggable @amap/amap-jsapi-loader
```

## 启动开发服务器

### 后端

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务运行在 `http://localhost:8000`

### 前端

```bash
cd frontend
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`

## 开发流程

### 1. 从 001 模块获取旅行计划数据

001 模块创建旅行计划后，数据通过以下方式存储/传递：
- 后端：通过 API 返回生成的旅行计划 JSON 数据
- 前端：存储到 localStorage，通过计划 ID 进行访问

### 2. 访问概览页

前端路由：`/travel-plans/{id}/overview`

页面加载流程：
1. 从 localStorage 获取计划 ID
2. 调用 `GET /api/v1/travel-plans/{id}` 获取完整数据
3. 渲染预算明细、地图（高德地图嵌入）、每日行程列表

### 3. 访问逐日详情页

前端路由：`/travel-plans/{id}/day/{dayIndex}`

页面加载流程：
1. 从 URL 参数获取 dayIndex
2. 从已加载的旅行计划数据中筛选对应天的数据
3. 渲染景点详情卡片、住宿、餐饮、交通、天气信息

### 4. 编辑行程

1. 在详情页点击"编辑行程"按钮
2. 打开 EditDayDrawer 抽屉组件
3. 使用 vuedraggable 拖拽调整景点顺序
4. 点击景点卡片上的删除按钮移除景点
5. 点击"保存"提交更新（调用 `PUT /api/v1/travel-plans/{id}/day/{dayIndex}`）

### 5. 导出行程

1. 在概览页点击"导出行程"
2. 选择图片或 PDF 格式
3. 前端使用 html2canvas + jsPDF 生成文件并触发下载

### 6. 重新规划

1. 在概览页点击"重新规划"按钮
2. 弹出 ReplanConfirmModal 确认弹窗
3. 用户确认后调用 `POST /api/v1/travel-plans/{id}/replan`
4. 等待后端重新生成行程并更新页面

## API 测试

### 使用 curl 测试

```bash
# 获取旅行计划概览
curl -X GET http://localhost:8000/api/v1/travel-plans/{id}

# 获取第1天行程详情
curl -X GET http://localhost:8000/api/v1/travel-plans/{id}/day/1

# 编辑第1天行程
curl -X PUT http://localhost:8000/api/v1/travel-plans/{id}/day/1 \
  -H "Content-Type: application/json" \
  -d '{"attractions": [...], "accommodation": {...}}'

# 导出为纯文本
curl -X GET "http://localhost:8000/api/v1/travel-plans/{id}/export?fmt=text" \
  -o travel-plan.txt

# 导出为 HTML（可用浏览器打开后打印为 PDF）
curl -X GET "http://localhost:8000/api/v1/travel-plans/{id}/export?fmt=html" \
  -o travel-plan.html

# 重新规划
curl -X POST http://localhost:8000/api/v1/travel-plans/{id}/replan
```

## 高德地图配置

前端地图组件需要配置高德地图 JS API：

```typescript
// src/components/MapView.vue
import AMapLoader from '@amap/amap-jsapi-loader'

onMounted(async () => {
  const AMap = await AMapLoader.load({
    key: import.meta.env.VITE_AMAP_KEY, // 从环境变量获取
    version: '2.0',
    plugins: ['AMap.Marker', 'AMap.InfoWindow']
  })
  // 初始化地图...
})
```

环境变量（`frontend/.env`）：

```
VITE_AMAP_KEY=your_amap_web_key_here
```

## 测试运行

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```
