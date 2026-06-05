<template>
  <el-card class="daily-schedule-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Calendar /></el-icon>
        <span>每日行程</span>
      </div>
    </template>

    <el-timeline>
      <el-timeline-item
        v-for="day in dailyItineraries"
        :key="day.dayIndex"
        :timestamp="formatDayTimestamp(day)"
        placement="top"
        type="primary"
        hollow
      >
        <el-card
          class="day-card"
          shadow="never"
          @click="goToDayDetail(day.dayIndex)"
        >
          <div class="day-content">
            <div class="day-title">
              <el-tag size="small" type="primary">第 {{ day.dayIndex }} 天</el-tag>
              <span class="day-date">{{ formatDate(day.date) }}</span>
            </div>
            <p class="day-summary">{{ day.summary }}</p>
            <div class="day-highlights">
              <el-tag
                v-for="attraction in day.attractions.slice(0, 3)"
                :key="attraction.id"
                size="small"
                effect="plain"
                class="attraction-tag"
              >
                {{ attraction.name }}
              </el-tag>
              <el-tag v-if="day.attractions.length > 3" size="small" effect="plain">
                +{{ day.attractions.length - 3 }}
              </el-tag>
            </div>
          </div>
          <div class="day-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, ArrowRight } from '@element-plus/icons-vue'
import type { DailyItineraryFull } from '@/types/travelPlan'

const props = defineProps<{
  planId: string
  dailyItineraries: DailyItineraryFull[]
}>()

const router = useRouter()

/**
 * 格式化日期显示
 */
function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const month = d.getMonth() + 1
    const day = d.getDate()
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${month}月${day}日 ${weekdays[d.getDay()]}`
  } catch {
    return dateStr
  }
}

/**
 * 格式化时间轴时间戳
 */
function formatDayTimestamp(day: DailyItineraryFull): string {
  return `Day ${day.dayIndex} — ${formatDate(day.date)}`
}

/**
 * 跳转到详情页
 */
function goToDayDetail(dayIndex: number): void {
  router.push({
    name: 'TravelPlanDayDetail',
    params: { id: props.planId, dayIndex },
  })
}
</script>

<style scoped>
.daily-schedule-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.day-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e4e7ed;
}

.day-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
  transform: translateX(4px);
}

.day-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.day-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.day-date {
  font-size: 14px;
  color: #606266;
}

.day-summary {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.day-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.attraction-tag {
  cursor: default;
}

.day-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #c0c4cc;
  transition: color 0.2s;
}

.day-card:hover .day-arrow {
  color: #409eff;
}

.el-timeline-item {
  padding-bottom: 8px;
}
</style>
