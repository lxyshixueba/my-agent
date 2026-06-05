<template>
  <el-card class="weather-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Sunny /></el-icon>
        <span>天气信息</span>
      </div>
    </template>

    <div class="weather-content">
      <!-- 天气状况 -->
      <div class="weather-condition">
        <el-tag :type="getWeatherTagType(weather.condition)" size="large" effect="dark">
          {{ weather.condition }}
        </el-tag>
        <span class="weather-date">{{ formatDate(weather.date) }}</span>
      </div>

      <!-- 温度范围 -->
      <div class="temperature-range">
        <el-icon :size="20" color="#f56c6c"><Sunny /></el-icon>
        <span class="temp-high">{{ weather.temperature.high }}°C</span>
        <span class="temp-divider">~</span>
        <el-icon :size="20" color="#409eff"><IceCream /></el-icon>
        <span class="temp-low">{{ weather.temperature.low }}°C</span>
      </div>

      <!-- 风速 -->
      <div class="wind-speed">
        <el-icon :size="16" color="#909399"><WindPower /></el-icon>
        <span>风速：{{ weather.windSpeed }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Sunny, IceCream, WindPower } from '@element-plus/icons-vue'
import type { WeatherInfo } from '@/types/travelPlan'

const props = defineProps<{
  /** 天气信息数据 */
  weather: WeatherInfo
}>()

/**
 * 根据天气状况返回 Element Plus tag 类型
 */
function getWeatherTagType(condition: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  const typeMap: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    '晴': 'success',
    '晴天': 'success',
    '多云': 'info',
    '阴': 'info',
    '阴天': 'info',
    '小雨': 'warning',
    '中雨': 'warning',
    '大雨': 'danger',
    '暴雨': 'danger',
    '雪': 'info',
    '小雪': 'info',
    '大雪': 'info',
    '雾': 'info',
    '霾': 'danger',
  }
  return typeMap[condition] || ''
}

/**
 * 格式化日期显示
 */
function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${d.getMonth() + 1}月${d.getDate()}日 ${weekdays[d.getDay()]}`
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.weather-info-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.weather-content {
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weather-condition {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weather-date {
  font-size: 14px;
  color: #909399;
}

.temperature-range {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.temp-high {
  color: #f56c6c;
}

.temp-low {
  color: #409eff;
}

.temp-divider {
  color: #909399;
  font-weight: normal;
}

.wind-speed {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}
</style>
