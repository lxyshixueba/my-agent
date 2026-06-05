<template>
  <el-card class="schedule-timeline-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Calendar /></el-icon>
        <span>日程安排</span>
      </div>
    </template>

    <el-timeline>
      <el-timeline-item
        v-for="(slot, index) in schedule"
        :key="index"
        :timestamp="`${slot.startTime} - ${slot.endTime}`"
        placement="top"
        :type="getTimeSlotType(index)"
        :color="getTimeSlotColor(index)"
        size="large"
      >
        <div class="time-slot-content">
          <span class="activity-text">{{ slot.activity }}</span>
        </div>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-if="!schedule || schedule.length === 0" description="暂无日程安排" />
  </el-card>
</template>

<script setup lang="ts">
import { Calendar } from '@element-plus/icons-vue'
import type { TimeSlot } from '@/types/travelPlan'

const props = defineProps<{
  /** 日程时间线数据 */
  schedule: TimeSlot[]
}>()

/**
 * 根据时间槽位置返回Element Plus时间轴类型
 */
function getTimeSlotType(index: number): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const types: Array<'primary' | 'success' | 'warning' | 'danger' | 'info'> = [
    'primary',
    'success',
    'warning',
    'info',
    'danger',
  ]
  return types[index % types.length]
}

/**
 * 根据时间槽位置返回Element Plus时间轴颜色
 */
function getTimeSlotColor(index: number): string {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#909399', '#f56c6c']
  return colors[index % colors.length]
}
</script>

<style scoped>
.schedule-timeline-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.time-slot-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
</style>
