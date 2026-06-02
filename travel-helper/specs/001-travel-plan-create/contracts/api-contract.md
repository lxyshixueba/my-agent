# API Contract: 旅行计划创建

## 概述

本文档定义旅行计划创建功能的 REST API 接口契约。

## 端点

### POST /api/v1/travel-plans/generate

基于用户输入的旅行偏好，生成个性化旅行计划。

#### Request

**Content-Type**: `application/json`

**Body**: `TravelPlanCreateRequest`

```json
{
  "destination": {
    "name": "北京",
    "code": "BJ"
  },
  "start_date": "2026-07-01",
  "end_date": "2026-07-05",
  "transport_mode": "high_speed_rail",
  "accommodation": "premium",
  "preferences": ["food", "history_culture"],
  "special_requirements": "带老人出行，行程不宜太紧凑"
}
```

#### Request Schema

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `destination.name` | string | ✅ | 城市名称 |
| `destination.code` | string | ✅ | 城市编码 |
| `start_date` | string (YYYY-MM-DD) | ✅ | 出行开始日期 |
| `end_date` | string (YYYY-MM-DD) | ✅ | 出行结束日期 |
| `transport_mode` | enum | ✅ | 枚举值: `flight`, `high_speed_rail`, `self_driving`, `bus` |
| `accommodation` | enum | ✅ | 枚举值: `economy`, `comfort`, `premium`, `luxury`, `homestay` |
| `preferences` | string[] | ❌ | 旅行偏好标签，为空时使用默认推荐 |
| `special_requirements` | string | ❌ | 特殊服务要求，最大 500 字符 |

#### Success Response (200)

**Content-Type**: `application/json`

```json
{
  "request_id": "req-abc-123",
  "destination": "北京",
  "days": 5,
  "daily_itineraries": [
    {
      "day": 1,
      "date": "2026-07-01",
      "theme": "历史文化之旅",
      "activities": [
        {
          "type": "attraction",
          "name": "故宫博物院",
          "description": "中国明清两代的皇家宫殿...",
          "time_slot": "morning",
          "duration_minutes": 180
        },
        {
          "type": "restaurant",
          "name": "全聚德烤鸭",
          "description": "北京传统名菜...",
          "time_slot": "afternoon",
          "duration_minutes": 90
        }
      ]
    }
  ],
  "generated_at": "2026-06-02T10:30:00+08:00"
}
```

#### Error Responses

**400 Bad Request** — 请求参数校验失败

```json
{
  "detail": [
    {
      "field": "start_date",
      "message": "出行日期不能早于今天"
    }
  ]
}
```

**404 Not Found** — 城市不存在

```json
{
  "detail": [
    {
      "field": "destination.name",
      "message": "未找到匹配的城市"
    }
  ]
}
```

**500 Internal Server Error** — 旅行计划生成失败

```json
{
  "request_id": "req-abc-123",
  "error": "旅行计划生成失败，请稍后重试"
}
```

**504 Gateway Timeout** — LLM API 超时

```json
{
  "request_id": "req-abc-123",
  "error": "生成超时，请稍后重试"
}
```

---

### GET /api/v1/cities/search?q={query}

城市搜索与自动补全。

#### Request

**Query Parameters**:
- `q` (string): 搜索关键字（城市名称或拼音前缀）

#### Success Response (200)

```json
{
  "cities": [
    {
      "name": "北京",
      "pinyin": "beijing",
      "province": "北京市",
      "code": "BJ"
    }
  ]
}
```

---

## 非功能性约定

- 所有 API 响应包含 `request_id` 字段用于日志追踪（500 错误时由中间件生成）
- 日期格式统一为 ISO 8601 (`YYYY-MM-DD`)
- 枚举值使用 `snake_case`
- 错误响应使用标准 `detail` 字段（FastAPI 默认格式）
