# API Contract: 旅行计划详情查看与编辑

## Base Path

```
/api/v1/travel-plans
```

## Endpoints

### 1. GET `/api/v1/travel-plans/{id}` — 获取旅行计划概览

获取指定旅行计划的完整数据（用于概览页和详情页加载）。

**Path Parameters**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | string (UUID) | 旅行计划 ID（来自 localStorage） |

**Response (200 OK)**:
```json
{
  "id": "uuid-string",
  "destination": {
    "name": "北京",
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "dateRange": {
    "startDate": "2025-11-10",
    "endDate": "2025-11-25"
  },
  "description": "旅行计划包含15天行程...",
  "preferences": {
    "accommodationType": "高档型酒店",
    "transportation": "高铁",
    "tags": ["景点观光", "美食"],
    "specialRequests": ""
  },
  "budget": {
    "attractionTickets": 1130,
    "hotelAccommodation": 1200,
    "diningTransport": 730,
    "diningFood": 300,
    "total": 3360
  },
  "dailyItineraries": [
    {
      "dayIndex": 1,
      "date": "2025-11-10",
      "summary": "故宫 - 鸟巢一日游",
      "schedule": [
        {"startTime": "08:00", "endTime": "10:00", "activity": "前往故宫并游览"},
        {"startTime": "10:30", "endTime": "12:00", "activity": "继续游览故宫"},
        {"startTime": "13:00", "endTime": "15:00", "activity": "前往鸟巢游览"},
        {"startTime": "14:00", "endTime": "16:00", "activity": "继续游览鸟巢"}
      ],
      "attractions": [
        {
          "id": "uuid-1",
          "name": "北京故宫",
          "imageUrl": "https://images.unsplash.com/...",
          "playDuration": "2-3小时",
          "description": "...",
          "features": "...",
          "tips": "...",
          "latitude": 39.9163,
          "longitude": 116.3972
        }
      ],
      "accommodation": {
        "hotelName": "北京万豪酒店",
        "roomType": "豪华标准间",
        "address": "北京市朝阳区xxx路xxx号",
        "checkIn": "2025-11-10",
        "checkOut": "2025-11-12",
        "amenities": "免费WiFi、停车位、商务中心、健身房",
        "latitude": 39.9200,
        "longitude": 116.4100
      },
      "dining": {
        "breakfast": "北京传统早餐 豆浆油条、煎饼果子等",
        "lunch": "北京烤鸭 全聚德或便宜坊的招牌菜",
        "dinner": "北京炸酱面 老北京炸酱面是经典的北京小吃"
      },
      "transportation": [
        {"type": "地铁", "description": "地铁1号线 天安门东站 → 奥林匹克公园站"}
      ],
      "weather": {
        "date": "2025-11-10",
        "condition": "晴",
        "temperature": {"low": 5, "high": 15},
        "windSpeed": "微风"
      }
    }
  ],
  "createdAt": "2025-11-01T10:00:00Z",
  "updatedAt": "2025-11-01T10:00:00Z"
}
```

**Response (404 Not Found)**:
```json
{
  "detail": "Travel plan not found"
}
```

---

### 2. PUT `/api/v1/travel-plans/{id}/day/{dayIndex}` — 编辑每日行程

更新指定天的行程数据（景点顺序调整、景点删除等）。

**Path Parameters**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | string (UUID) | 旅行计划 ID |
| dayIndex | integer | 第几天（1-30） |

**Request Body**:
```json
{
  "schedule": [
    {"startTime": "08:00", "endTime": "10:00", "activity": "前往故宫并游览"},
    {"startTime": "10:30", "endTime": "12:00", "activity": "继续游览故宫"}
  ],
  "attractions": [
    {
      "id": "uuid-1",
      "name": "北京故宫",
      "imageUrl": "https://images.unsplash.com/...",
      "playDuration": "2-3小时",
      "description": "...",
      "features": "...",
      "tips": "...",
      "latitude": 39.9163,
      "longitude": 116.3972
    }
  ],
  "accommodation": {
    "hotelName": "北京万豪酒店",
    "roomType": "豪华标准间",
    "address": "北京市朝阳区xxx路xxx号",
    "checkIn": "2025-11-10",
    "checkOut": "2025-11-12",
    "amenities": "免费WiFi、停车位、商务中心、健身房",
    "latitude": 39.9200,
    "longitude": 116.4100
  },
  "dining": {
    "breakfast": "北京传统早餐 豆浆油条",
    "lunch": "北京烤鸭",
    "dinner": "北京炸酱面"
  },
  "transportation": [
    {"type": "地铁", "description": "地铁1号线 天安门东站 → 奥林匹克公园站"}
  ]
}
```

**Response (200 OK)**:
```json
{
  "message": "Day itinerary updated successfully",
  "dayIndex": 1,
  "updatedAt": "2025-11-01T11:00:00Z"
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "At least one attraction must remain"
}
```

---

### 3. POST `/api/v1/travel-plans/{id}/replan` — 重新规划行程

触发重新生成旅行计划。

**Path Parameters**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | string (UUID) | 旅行计划 ID |

**Request Body**:
```json
{}
```

**Response (200 OK)**:
```json
{
  "message": "Replanning initiated",
  "estimatedTime": "30s"
}
```

**Response (409 Conflict)**:
```json
{
  "detail": "A replanning task is already in progress"
}
```

---

### 4. GET `/api/v1/travel-plans/{id}/export` — 导出旅行计划

获取旅行计划的导出数据（前端使用此数据生成图片或 PDF）。

**Path Parameters**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | string (UUID) | 旅行计划 ID |

**Query Parameters**:
| 参数 | 类型 | 描述 | 可选值 |
|------|------|------|--------|
| format | string | 导出格式 | `image` / `pdf` |

**Response (200 OK) — image 格式**:
Content-Type: `image/png`
Body: 图片二进制数据

**Response (200 OK) — pdf 格式**:
Content-Type: `application/pdf`
Body: PDF 二进制数据

**Response (400 Bad Request)**:
```json
{
  "detail": "Invalid format. Use 'image' or 'pdf'"
}
```

---

## Error Response Format

所有错误响应统一格式：

```json
{
  "detail": "错误描述信息"
}
```

## Authentication

本功能无需用户认证（延续 001 模块假设）。API 请求通过旅行计划 ID（存储在 localStorage）进行资源定位。

## Rate Limiting

- 高德地图 API 代理调用: 不超过 50 QPS（高德限制）
- 行程重新规划: 同一计划 5 分钟内最多 1 次
