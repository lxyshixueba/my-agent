/** 前端类型定义 — 对应后端请求/响应模型 */

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
