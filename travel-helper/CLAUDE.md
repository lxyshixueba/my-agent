# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## 语言约定

**本项目所有对话、文档、代码注释统一使用中文（简体中文）。** 这是用户的明确要求，请在所有交互中遵守。

## 项目概述

**travel-helper** 是一个智能旅行助手项目。

### 项目结构

```
├── spec/                        # 功能规范文档
│   └── <feature-name>/         # 按功能名称组织的规范目录
│       ├── spec.md             # 功能规范
│       ├── plan.md             # 实现计划
│       └── tasks.md            # 任务清单
│
├── backend/                    # 后端代码 (Python)
│   ├── app/
│   │   ├── agents/            # 智能体实现
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 服务层
│   │   └── config.py          # 配置文件
│   └── requirements.txt       # Python 依赖
│
└── frontend/                   # 前端代码 (JavaScript/TypeScript)
    ├── src/
    │   ├── views/             # 页面组件
    │   ├── services/          # API 服务
    │   ├── types/             # 类型定义
    │   └── router/            # 路由配置
    └── package.json           # npm 依赖
```

> 分层约束详见 `.specify/memory/constitution.md` 中的"项目结构"章节。

当前处于技术规范阶段，
仓库已搭建治理文档和 Speckit 模板，应用源代码尚未开始编写。

## Speckit 工作流

功能开发遵循 spec → plan → tasks → implement 流程：

1. **`speckit-specify`** — 创建/更新功能规范
2. **`speckit-plan`** — 生成实现计划
3. **`speckit-tasks`** — 生成依赖排序的任务清单
4. **`speckit-analyze`** — 跨文档一致性检查
5. **`speckit-implement`** — 执行任务清单

辅助技能：`speckit-clarify`、`speckit-checklist`、`speckit-constitution`、`speckit-baseline`

所有规范、计划和任务必须遵循 `.specify/templates/` 中的模板。

## 项目宪法

宪法位于 `.specify/memory/constitution.md`（v1.6.0），定义 6 项原则：
规范驱动开发、增量交付、测试纪律、代码质量、可观测性、审查与问责。

宪法具有最高优先级 — 与其他项目文档冲突时以宪法为准。

## 开发注意事项

- **`use-node18.bat`** — Windows 上使用 Node.js 18 的批处理脚本
- 具体的构建/测试/lint 命令将在首个功能的实现计划中确定

## 环境要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.12+ |
| Node.js | 16.0+ |
| npm | 8.0+ |

## API 密钥配置

项目需要以下 API 密钥（统一存放在 `backend/.env` 文件中）：

| 密钥 | 用途 | 注册地址 |
|------|------|---------|
| `LLM_API_KEY` | 大语言模型 API（OpenAI、DeepSeek 等） | 对应提供商控制台 |
| `LANGCHAIN_API_KEY` | LangSmith 追踪与评估平台 | https://smith.langchain.com/ |
| `AMAP_WEB_KEY` | 高德地图 Web 服务 | https://console.amap.com/ |
| `UNSPLASH_ACCESS_KEY` | Unsplash 图片服务 | https://unsplash.com/developers |

> `.env` 文件已加入 `.gitignore`，严禁提交到版本控制。
