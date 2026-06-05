/** 前端类型定义 — 对应后端请求/响应模型 */

/* ==========================================================================
 * 001 模块 — 旅行计划创建
 * ========================================================================== */

/** 交通方式 */
export type TransportMode = 'flight' | 'high_speed_rail' | 'self_driving' | 'bus'

/** 住宿偏好 */
export type Accommodation = 'economy' | 'comfort' | 'premium' | 'luxury' | 'homestay'

/** 旅行偏好标签 */
export type PreferenceTag =
  | 'sightseeing'
  | 'food'
  | 'nature'
  | 'history_culture'
  | 'shopping'
  | 'adventure'
  | 'cultural_experience'
  | 'leisure_entertainment'

/** 城市引用 */
export interface CityRef {
  name: string
  code: string
}

/** 城市搜索结果 */
export interface City {
  name: string
  pinyin: string
  province: string
  code: string
}

/** 旅行计划创建请求 */
export interface TravelPlanRequest {
  destination: CityRef
  start_date: string // YYYY-MM-DD
  end_date: string // YYYY-MM-DD
  transport_mode: TransportMode
  accommodation: Accommodation
  preferences?: PreferenceTag[]
  special_requirements?: string
}

/** 活动 */
export interface Activity {
  type: 'attraction' | 'restaurant' | 'shopping' | 'activity'
  name: string
  description: string
  time_slot: 'morning' | 'afternoon' | 'evening'
  duration_minutes: number
}

/** 每日行程 */
export interface DailyItinerary {
  day: number
  date: string
  theme: string
  activities: Activity[]
}

/** 旅行计划响应 */
export interface TravelPlanResponse {
  request_id: string
  destination: string
  days: number
  daily_itineraries: DailyItinerary[]
  generated_at: string
}

/** 偏好标签显示配置 */
export const PREFERENCE_CONFIG: Record<PreferenceTag, { label: string; icon: string }> = {
  sightseeing: { label: '景点观光', icon: '🏛️' },
  food: { label: '美食', icon: '🍜' },
  nature: { label: '自然风光', icon: '🏔️' },
  history_culture: { label: '历史文化', icon: '📚' },
  shopping: { label: '购物体验', icon: '🛍️' },
  adventure: { label: '探险', icon: '🧗' },
  cultural_experience: { label: '文化体验', icon: '🎭' },
  leisure_entertainment: { label: '休闲娱乐', icon: '🎡' },
}

/* ==========================================================================
 * 002 模块 — 旅行计划详情查看与编辑
 * ========================================================================== */

/** 目的地城市 */
export interface DestinationCity {
  /** 城市名称 */
  name: string
  /** 纬度 */
  latitude: number
  /** 经度 */
  longitude: number
}

/** 日期范围 */
export interface DateRange {
  /** 开始日期 YYYY-MM-DD */
  startDate: string
  /** 结束日期 YYYY-MM-DD */
  endDate: string
}

/** 旅行偏好 */
export interface TravelPreferences {
  /** 住宿类型 */
  accommodationType: string
  /** 交通方式 */
  transportation: string
  /** 偏好标签 */
  tags: string[]
  /** 特殊要求 */
  specialRequests: string
}

/** 预算明细 */
export interface BudgetBreakdown {
  /** 景点门票费用 */
  attractionTickets: number
  /** 酒店住宿费用 */
  hotelAccommodation: number
  /** 餐饮交通费用 */
  diningTransport: number
  /** 餐饮食物费用 */
  diningFood: number
  /** 总费用 */
  total: number
}

/** 时间段 */
export interface TimeSlot {
  /** 开始时间 HH:mm */
  startTime: string
  /** 结束时间 HH:mm */
  endTime: string
  /** 活动描述 */
  activity: string
}

/** 景点详情 */
export interface AttractionDetail {
  /** 景点唯一标识 */
  id: string
  /** 景点名称 */
  name: string
  /** 景点图片 URL */
  imageUrl: string
  /** 建议游玩时长 */
  playDuration: string
  /** 景点描述 */
  description: string
  /** 景点特色 */
  features: string
  /** 游玩贴士 */
  tips: string
  /** 纬度 */
  latitude: number
  /** 经度 */
  longitude: number
}

/** 住宿安排 */
export interface AccommodationPlan {
  /** 酒店名称 */
  hotelName: string
  /** 房型 */
  roomType: string
  /** 地址 */
  address: string
  /** 入住日期 YYYY-MM-DD */
  checkIn: string
  /** 退房日期 YYYY-MM-DD */
  checkOut: string
  /** 设施信息 */
  amenities: string
  /** 纬度 */
  latitude: number
  /** 经度 */
  longitude: number
}

/** 餐饮安排 */
export interface DiningPlan {
  /** 早餐 */
  breakfast: string
  /** 午餐 */
  lunch: string
  /** 晚餐 */
  dinner: string
}

/** 交通安排 */
export interface TransportationPlan {
  /** 交通方式 */
  type: string
  /** 交通描述 */
  description: string
}

/** 温度范围 */
export interface TemperatureRange {
  /** 最低温度 */
  low: number
  /** 最高温度 */
  high: number
}

/** 天气信息 */
export interface WeatherInfo {
  /** 日期 YYYY-MM-DD */
  date: string
  /** 天气状况 */
  condition: string
  /** 温度范围 */
  temperature: TemperatureRange
  /** 风速 */
  windSpeed: string
}

/** 每日行程（完整版，对应 GET /api/v1/travel-plans/{id} 响应中的 dailyItineraries 元素） */
export interface DailyItineraryFull {
  /** 第几天（从 1 开始） */
  dayIndex: number
  /** 日期 YYYY-MM-DD */
  date: string
  /** 当日行程概要 */
  summary: string
  /** 时间段安排 */
  schedule: TimeSlot[]
  /** 景点列表 */
  attractions: AttractionDetail[]
  /** 住宿安排（可选） */
  accommodation?: AccommodationPlan
  /** 餐饮安排（可选） */
  dining?: DiningPlan
  /** 交通安排（可选） */
  transportation?: TransportationPlan[]
  /** 天气信息（可选） */
  weather?: WeatherInfo
}

/** 旅行计划完整响应（对应 GET /api/v1/travel-plans/{id}） */
export interface TravelPlanFull {
  /** 旅行计划 ID */
  id: string
  /** 目的地城市 */
  destination: DestinationCity
  /** 日期范围 */
  dateRange: DateRange
  /** 旅行计划描述 */
  description: string
  /** 旅行偏好 */
  preferences: TravelPreferences
  /** 预算明细 */
  budget: BudgetBreakdown
  /** 每日行程列表 */
  dailyItineraries: DailyItineraryFull[]
  /** 创建时间 ISO 8601 */
  createdAt: string
  /** 更新时间 ISO 8601 */
  updatedAt: string
}

/** 编辑每日行程请求体（对应 PUT /api/v1/travel-plans/{id}/day/{dayIndex}） */
export interface EditDayRequest {
  /** 时间段安排 */
  schedule: TimeSlot[]
  /** 景点列表 */
  attractions: AttractionDetail[]
  /** 住宿安排（可选） */
  accommodation?: AccommodationPlan
  /** 餐饮安排（可选） */
  dining?: DiningPlan
  /** 交通安排（可选） */
  transportation?: TransportationPlan[]
}

/** 编辑每日行程响应（对应 PUT /api/v1/travel-plans/{id}/day/{dayIndex} 200） */
export interface EditDayResponse {
  /** 操作结果消息 */
  message: string
  /** 编辑的天数索引 */
  dayIndex: number
  /** 更新时间 ISO 8601 */
  updatedAt: string
}

/** 重新规划行程响应（对应 POST /api/v1/travel-plans/{id}/replan 200） */
export interface ReplanResponse {
  /** 操作结果消息 */
  message: string
  /** 预估完成时间 */
  estimatedTime: string
}

/** API 错误响应格式 */
export interface ApiErrorResponse {
  /** 错误描述信息 */
  detail: string
}
