/** 旅行计划 API 服务封装 */

import api from './api'
import type {
  TravelPlanFull,
  DailyItineraryFull,
  EditDayRequest,
  EditDayResponse,
  ReplanResponse,
} from '@/types/travelPlan'

/**
 * 获取完整旅行计划数据
 * @param id 旅行计划 ID
 */
export async function getTravelPlan(id: string): Promise<TravelPlanFull> {
  return api.get<TravelPlanFull>(`/travel-plans/${id}`)
}

/**
 * 获取指定天的行程详情
 * @param id 旅行计划 ID
 * @param dayIndex 第几天（从 1 开始）
 */
export async function getDayDetail(id: string, dayIndex: number): Promise<DailyItineraryFull> {
  return api.get<DailyItineraryFull>(`/travel-plans/${id}/day/${dayIndex}`)
}

/**
 * 更新指定天的行程
 * @param id 旅行计划 ID
 * @param dayIndex 第几天（从 1 开始）
 * @param data 更新数据
 */
export async function updateDay(
  id: string,
  dayIndex: number,
  data: EditDayRequest,
): Promise<EditDayResponse> {
  return api.put<EditDayResponse>(`/travel-plans/${id}/day/${dayIndex}`, data)
}

/**
 * 重新规划行程
 * @param id 旅行计划 ID
 */
export async function replan(id: string): Promise<ReplanResponse> {
  return api.post<ReplanResponse>(`/travel-plans/${id}/replan`)
}
