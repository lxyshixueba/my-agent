# 后端开发指南

## 环境要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.10+ |

## 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

## 项目结构

```
backend/
├── app/
│   ├── api/routes/     # API 路由
│   ├── models/         # Pydantic 数据模型
│   ├── services/       # 业务逻辑服务
│   ├── agents/         # LLM 智能体 (prompt 构建)
│   ├── config.py       # 环境配置
│   └── main.py         # FastAPI 入口
├── data/
│   └── cities.json     # 城市静态数据
├── tests/
│   ├── unit/           # 单元测试
│   ├── integration/    # 集成测试
│   └── contract/       # 契约测试
└── requirements.txt    # Python 依赖
```

## 代码规范

### Lint & Format

```bash
# Lint 检查
ruff check .

# 格式化
black .
```

### 运行测试

```bash
pytest
pytest -v          # 详细输出
pytest --cov=app   # 覆盖率
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/travel-plans/generate` | 生成旅行计划 |
| GET | `/api/v1/cities/search?q=xxx` | 城市搜索 |
