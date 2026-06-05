/** localStorage 存储服务封装 */

const STORAGE_KEY_PLAN_ID = 'travel_plan_id'

/**
 * 存储当前旅行计划 ID
 * @param id 旅行计划 ID
 */
export function savePlanId(id: string): void {
  try {
    localStorage.setItem(STORAGE_KEY_PLAN_ID, id)
  } catch (e) {
    console.error('localStorage 写入失败:', e)
  }
}

/**
 * 获取当前旅行计划 ID
 * @returns 旅行计划 ID，不存在时返回 null
 */
export function getPlanId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY_PLAN_ID)
  } catch (e) {
    console.error('localStorage 读取失败:', e)
    return null
  }
}

/**
 * 清除当前旅行计划 ID
 */
export function clearPlanId(): void {
  try {
    localStorage.removeItem(STORAGE_KEY_PLAN_ID)
  } catch (e) {
    console.error('localStorage 清除失败:', e)
  }
}

/**
 * 存储任意数据到 localStorage
 * @param key 键名
 * @param value 值（任意可序列化类型）
 */
export function saveToStorage<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (e) {
    console.error(`localStorage 写入失败 (${key}):`, e)
  }
}

/**
 * 从 localStorage 读取数据
 * @param key 键名
 * @returns 解析后的值，失败时返回 null
 */
export function loadFromStorage<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key)
    if (raw === null) return null
    return JSON.parse(raw) as T
  } catch (e) {
    console.error(`localStorage 读取失败 (${key}):`, e)
    return null
  }
}
