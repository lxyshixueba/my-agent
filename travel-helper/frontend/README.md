# 前端开发指南

## 环境要求

| 工具 | 最低版本 |
|------|---------|
| Node.js | 16.0+ |
| npm | 8.0+ |

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览构建结果

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   └── TravelPlanCreate.vue  # 旅行计划创建页
│   ├── components/      # 可复用组件
│   │   ├── CitySearch.vue        # 城市搜索
│   │   ├── DatePicker.vue        # 日期选择
│   │   ├── TransportSelector.vue # 交通方式选择
│   │   └── PreferenceSelector.vue # 偏好标签选择
│   ├── services/        # API 服务
│   │   ├── api.ts              # Axios 基础实例
│   │   └── travelPlanApi.ts    # 旅行计划 API
│   ├── types/           # TypeScript 类型定义
│   │   └── travelPlan.ts
│   ├── router/          # Vue Router 配置
│   │   └── index.ts
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
├── index.html           # HTML 模板
├── package.json         # npm 依赖
├── vite.config.ts       # Vite 配置
└── tsconfig.json        # TypeScript 配置
```

## 代码规范

### Lint & Format

```bash
# Lint 检查
npm run lint

# 格式化
npm run format
```

## 开发代理

开发环境下，Vite 会将 `/api` 请求代理到后端 `http://localhost:8000`。

生产环境需配置 CORS 或使用 Nginx 反向代理。
