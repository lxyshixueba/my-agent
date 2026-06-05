# Data Model: 旅行计划详情查看与编辑

## Entities

### TravelPlan (旅行计划)

代表用户的完整旅行规划方案，是 001 模块生成的核心数据实体。

| 字段 | 类型 | 描述 | 校验 |
|------|------|------|------|
| id | string (UUID) | 计划唯一标识符 | 必填，系统生成 |
| destination | DestinationCity | 目的地城市 | 必填 |
| dateRange | DateRange | 出行起止日期 | 必填 |
| description | string | 计划简介 | 可选 |
| preferences | TravelPreferences | 用户偏好 | 可选 |
| budget | BudgetBreakdown | 预算明细 | 必填 |
| dailyItineraries | DailyItinerary[] | 每日行程列表 | 必填，1-30 个 |
| createdAt | datetime | 计划创建时间 | 必填，系统生成 |
| updatedAt | datetime | 最后更新时间 | 必填，系统生成 |

### DestinationCity (目的地城市)

| 字段 | 类型 | 描述 |
|------|------|------|
| name | string | 城市名称（如"北京"） |
| latitude | float | 纬度 |
| longitude | float | 经度 |

### DateRange (日期范围)

| 字段 | 类型 | 描述 |
|------|------|------|
| startDate | date | 出发日期 |
| endDate | date | 返回日期 |

### TravelPreferences (旅行偏好)

| 字段 | 类型 | 描述 |
|------|------|------|
| accommodationType | string | 住宿偏好（经济型/舒适型/高档型/豪华/民宿） |
| transportation | string | 交通方式（飞机/高铁/自驾/大巴） |
| tags | string[] | 偏好标签列表 |
| specialRequests | string | 特殊服务要求 |

### BudgetBreakdown (预算明细)

| 字段 | 类型 | 描述 |
|------|------|------|
| attractionTickets | number | 景点门票预算（CNY） |
| hotelAccommodation | number | 酒店住宿预算（CNY） |
| diningTransport | number | 餐饮交通预算（CNY） |
| diningFood | number | 餐饮美食预算（CNY） |
| total | number | 预估总费用（CNY），自动计算 |

### DailyItinerary (每日行程)

代表某一天的完整行程安排。

| 字段 | 类型 | 描述 | 校验 |
|------|------|------|------|
| dayIndex | number | 第几天（从 1 开始） | 必填，1-30 |
| date | date | 具体日期 | 必填 |
| summary | string | 行程概要（用于概览页展示） | 必填 |
| schedule | TimeSlot[] | 日程时间线 | 必填 |
| attractions | AttractionDetail[] | 景点列表 | 必填，1-10 个 |
| accommodation | AccommodationPlan | 住宿安排 | 可选 |
| dining | DiningPlan | 餐饮安排 | 可选 |
| transportation | TransportationPlan[] | 交通安排 | 可选 |
| weather | WeatherInfo | 天气信息 | 可选，行程生成时缓存 |

### TimeSlot (时间段)

| 字段 | 类型 | 描述 |
|------|------|------|
| startTime | string | 开始时间（HH:mm 格式） |
| endTime | string | 结束时间（HH:mm 格式） |
| activity | string | 活动描述 |

### AttractionDetail (景点详情)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string (UUID) | 景点唯一标识 |
| name | string | 景点名称 |
| imageUrl | string | 景点图片 URL |
| playDuration | string | 游玩时间（如"2-3 小时"） |
| description | string | 详细描述 |
| features | string | 景点特色 |
| tips | string | 推荐信息 |
| latitude | float | 景点纬度 |
| longitude | float | 景点经度 |

### AccommodationPlan (住宿安排)

| 字段 | 类型 | 描述 |
|------|------|------|
| hotelName | string | 酒店名称 |
| roomType | string | 房型 |
| address | string | 地址 |
| checkIn | date | 入住日期 |
| checkOut | date | 退房日期 |
| amenities | string | 设施描述 |
| latitude | float | 酒店纬度 |
| longitude | float | 酒店经度 |

### DiningPlan (餐饮安排)

| 字段 | 类型 | 描述 |
|------|------|------|
| breakfast | string | 早餐推荐 |
| lunch | string | 午餐推荐 |
| dinner | string | 晚餐推荐 |

### TransportationPlan (交通安排)

| 字段 | 类型 | 描述 |
|------|------|------|
| type | string | 交通类型（航班/火车/地铁/公交） |
| description | string | 交通描述 |

### WeatherInfo (天气信息)

| 字段 | 类型 | 描述 |
|------|------|------|
| date | date | 天气日期 |
| condition | string | 天气状况（晴/多云/雨/雪等） |
| temperature | TemperatureRange | 温度范围 |
| windSpeed | string | 风速 |

### TemperatureRange (温度范围)

| 字段 | 类型 | 描述 |
|------|------|------|
| low | number | 最低温度 |
| high | number | 最高温度 |

## Relationships

```
TravelPlan (1) ─── (*) DailyItinerary
  ├── DestinationCity (1)
  ├── DateRange (1)
  ├── TravelPreferences (1)
  ── BudgetBreakdown (1)

DailyItinerary (1) ─── (*) AttractionDetail
DailyItinerary (1) ─── (1) AccommodationPlan
DailyItinerary (1) ── (1) DiningPlan
DailyItinerary (1) ─── (*) TransportationPlan
DailyItinerary (1) ─── (1) WeatherInfo
DailyItinerary (1) ─── (*) TimeSlot
```

## State Transitions

本功能不涉及状态机。旅行计划数据从 001 模块生成后，在本模块中仅支持读取和编辑，无状态流转。

## Validation Rules

- FR-003: 预算明细四个分类金额之和应等于 total（允许 ±0.01 浮点误差）
- FR-008: 景点详情至少包含名称和描述
- FR-013: 编辑操作不得删除当日全部景点（至少保留 1 个）
- A-001: 每日行程天数必须在 1-30 范围内
