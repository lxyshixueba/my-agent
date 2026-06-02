import api from './api'
import type {
  TravelPlanRequest,
  TravelPlanResponse,
  City,
} from '@/types/travelPlan'

/**
 * 搜索城市
 */
export async function searchCities(query: string): Promise<City[]> {
  const response = await api.get<{ cities: City[] }>(`/cities/search?q=${encodeURIComponent(query)}`)
  return response.cities
}

/**
 * 生成旅行计划
 */
export async function generateTravelPlan(request: TravelPlanRequest): Promise<TravelPlanResponse> {
  return api.post<TravelPlanResponse>('/travel-plans/generate', request)
}
