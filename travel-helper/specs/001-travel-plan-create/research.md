# Research: 旅行计划创建技术决策

## 1. 前端框架选择

**Decision**: Vue 3 + Vite + TypeScript

**Rationale**: 
- 本项目定位为 Web 应用，Vue 3 在国内开发者社区使用广泛，组件生态成熟
- Vite 提供快速开发和热更新，适合小型表单类应用
- TypeScript 提供类型安全，与后端 pydantic 模型形成端到端类型约束
- 相较于 React，Vue 3 的表单和组件开发模式更直观，适合快速原型开发

**Alternatives considered**:
- React + Vite: 生态更大但学习曲线稍陡，需要额外的状态管理库
- 原生 HTML/CSS/JS: 轻量但缺乏组件复用能力，后续功能扩展困难

## 2. 后端框架选择

**Decision**: FastAPI + pydantic + python-dotenv

**Rationale**:
- FastAPI 原生支持 async/await，适合 LLM API 的异步调用场景
- pydantic 提供强类型数据校验，与 OpenAPI 规范自动生成兼容
- python-dotenv 管理 `.env` 中的 API 密钥，符合宪法安全要求
- FastAPI 自带 Swagger/OpenAPI 文档，便于前后端协作调试

**Alternatives considered**:
- Flask: 更轻量但缺少原生 async 和自动 OpenAPI 文档
- Django: 功能全面但过重，本功能无需 ORM 和管理后台

## 3. LLM API 提供商与 SDK

**Decision**: 使用 OpenAI 兼容接口（OpenAI SDK 或兼容 SDK），通过环境变量配置 `LLM_API_KEY` 和 API 基础 URL

**Rationale**:
- OpenAI SDK 的 `openai` Python 包支持 OpenAI 兼容接口，可对接多种 LLM（GPT-4、DeepSeek、Claude 等）
- 通过环境变量 `LLM_API_BASE_URL` 灵活切换提供商，不锁定单一服务
- 支持流式响应，可用于后续迭代中实现渐进式展示

**Alternatives considered**:
- 直接使用 HTTP 请求（requests/httpx）: 灵活但需手动处理认证、重试、错误
- Anthropic SDK: 仅支持 Claude 模型，提供商锁定风险

## 4. 城市数据源方案

**Decision**: 使用静态 JSON 文件（`backend/data/cities.json`）存储中国大陆地级市列表

**Rationale**:
- 城市列表变动频率极低，静态文件无需数据库或外部 API
- JSON 格式轻量，前端可直接加载实现自动补全
- 可包含城市名称、拼音、所属省份、经纬度等搜索所需字段
- 无需第三方 API 密钥依赖

**Alternatives considered**:
- 调用高德地图城市编码 API: 需要额外 API 密钥，增加复杂度
- 数据库存储: 过度设计，无运行时变更需求

## 5. 日期处理方案

**Decision**: 前端使用原生 HTML5 `<input type="date">` + 轻量日期工具（date-fns），后端使用 Python 标准库 `datetime`

**Rationale**:
- HTML5 日期输入框已提供基本的日期选择能力，移动端体验良好
- date-fns 轻量且提供日期计算（天数差、日期加减等）
- Python `datetime` 足够处理日期校验逻辑

**Alternatives considered**:
- dayjs: 与 date-fns 功能类似，选择 date-fns 因其 TypeScript 原生支持
- 第三方日历组件: 功能过重，原生输入框 + 简单校验即可满足需求

## 6. 前端表单验证策略

**Decision**: 前端使用原生 HTML5 表单验证 + 自定义 TypeScript 校验逻辑

**Rationale**:
- 表单字段数量有限（7 个字段），无需引入大型表单验证库（如 Formik/VeeValidate）
- 自定义校验逻辑与后端 pydantic 校验保持一致的验证规则
- 降低依赖体积，提升加载速度

**Alternatives considered**:
- VeeValidate: 功能全面但对简单表单过度设计
- Zod: 类型安全但增加额外依赖

## 7. 错误处理与重试机制

**Decision**: LLM 调用失败时实现指数退避重试（最多 3 次，初始延迟 2 秒，每次翻倍），超时设置 30 秒

**Rationale**:
- LLM API 偶发超时或限流，自动重试可提升 SC-003 中 95% 成功率指标
- 指数退避是标准重试策略，避免对 API 造成额外压力
- 30 秒超时与 SC-004 响应时间要求一致

**Alternatives considered**:
- 无重试，直接报错: 成功率无法达到 95% 指标
- 线性重试: 退避策略更激进但可能浪费资源
