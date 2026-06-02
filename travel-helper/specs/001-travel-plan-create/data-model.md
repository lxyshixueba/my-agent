# Data Model: 旅行计划创建

## Entities

### TravelPlanRequest (旅行计划请求)

用户提交旅行计划生成的请求数据。

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|---------|------|
| `destination` | City | ✅ | 非空，城市必须存在于城市数据集中 | 目的地城市 |
| `start_date` | Date | ✅ | 不能为空，不能早于今天 | 出行开始日期 |
| `end_date` | Date | ✅ | 不能为空，不能早于 start_date | 出行结束日期 |
| `days` | int | 推导值 | 1~30 | 出行天数（由日期自动计算，可由用户调整） |
| `transport_mode` | TransportMode | ✅ | 枚举值之一 | 出行交通方式 |
| `accommodation` | Accommodation | ✅ | 枚举值之一 | 住宿偏好 |
| `preferences` | string[] | ❌ | 每项为枚举值之一 | 旅行偏好标签列表 |
| `special_requirements` | string | ❌ | 最大长度 500 字符 | 特殊服务要求 |

### City (城市)

城市搜索与自动补全的数据实体。

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 城市名称（如"北京"） |
| `pinyin` | string | 拼音（如"beijing"），用于拼音搜索 |
| `province` | string | 所属省份 |
| `code` | string | 城市编码（唯一标识） |

### TravelPlanResponse (旅行计划响应)

LLM 生成的旅行计划结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `destination` | string | 目的地城市名称 |
| `days` | int | 出行天数 |
| `daily_itineraries` | DailyItinerary[] | 每日行程安排 |
| `generated_at` | string | 生成时间戳 (ISO 8601) |
| `request_id` | string | 请求唯一标识，用于日志追踪 |

### DailyItinerary (每日行程)

旅行计划中某一天的具体安排。

| 字段 | 类型 | 说明 |
|------|------|------|
| `day` | int | 第几天 (1-based) |
| `date` | string | 具体日期 (ISO 8601) |
| `theme` | string | 当日主题（如"历史文化之旅"） |
| `activities` | Activity[] | 活动列表 |

### Activity (活动)

行程中的单个活动（景点、餐饮、购物等）。

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 活动类型: attraction/restaurant/shopping/activity |
| `name` | string | 活动名称 |
| `description` | string | 活动描述 |
| `time_slot` | string | 建议时段: morning/afternoon/evening |
| `duration_minutes` | int | 预计耗时（分钟） |

## Enums

### TransportMode (交通方式)

| 值 | 说明 |
|----|------|
| `flight` | 飞机 |
| `high_speed_rail` | 高铁 |
| `self_driving` | 自驾 |
| `bus` | 大巴 |

### Accommodation (住宿偏好)

| 值 | 说明 |
|----|------|
| `economy` | 经济型酒店 |
| `comfort` | 舒适型酒店 |
| `premium` | 高档型酒店 |
| `luxury` | 豪华酒店 |
| `homestay` | 民宿 |

### PreferenceTag (旅行偏好标签)

| 值 | 说明 |
|----|------|
| `sightseeing` | 景点观光 |
| `food` | 美食 |
| `nature` | 自然风光 |
| `history_culture` | 历史文化 |
| `shopping` | 购物体验 |
| `adventure` | 探险 |
| `cultural_experience` | 文化体验 |
| `leisure_entertainment` | 休闲娱乐 |

## Validation Rules

1. **日期合法性**: `start_date` 必须 >= 今天，`end_date` 必须 >= `start_date`
2. **天数范围**: `days` (由日期差计算) 必须 <= 30
3. **枚举值校验**: `transport_mode`、`accommodation`、`preferences[]` 必须为预定义枚举值
4. **文本长度**: `special_requirements` 最大 500 字符
5. **城市存在性**: `destination.name` 必须在城市数据集中匹配

## State Transitions

本功能不涉及旅行计划的状态流转（计划生成后直接返回，不持久化）。
