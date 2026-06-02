# Quickstart: 旅行计划创建

## 环境准备

### 前置要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.10+ |
| Node.js | 16.0+ |
| npm | 8.0+ |

### 1. 安装后端依赖

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
LLM_API_KEY=your_api_key_here
LLM_API_BASE_URL=https://api.openai.com/v1  # 或其他 OpenAI 兼容端点
AMAP_WEB_KEY=your_amap_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
```

> `.env` 文件已加入 `.gitignore`，严禁提交到版本控制。

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动开发服务器

**后端**（监听 `http://localhost:8000`）：

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API 文档：`http://localhost:8000/docs`

**前端**（监听 `http://localhost:3000`）：

```bash
cd frontend
npm run dev
```

### 5. 验证功能

1. 打开 `http://localhost:3000` 进入旅行计划创建页面
2. 输入目的地城市（如"北京"），选择日期和偏好
3. 点击"生成旅行计划"，验证返回结果

或直接在终端调用 API：

```bash
curl -X POST http://localhost:8000/api/v1/travel-plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "destination": {"name": "北京", "code": "BJ"},
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
    "transport_mode": "high_speed_rail",
    "accommodation": "premium",
    "preferences": ["food", "history_culture"]
  }'
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```
