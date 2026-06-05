<template>
  <el-card class="accommodation-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><OfficeBuilding /></el-icon>
        <span>住宿安排</span>
      </div>
    </template>

    <el-descriptions :column="2" border class="accommodation-descriptions">
      <el-descriptions-item label="酒店名称" :span="2">
        <el-icon :size="16" color="#409eff"><Location /></el-icon>
        {{ accommodation.hotelName }}
      </el-descriptions-item>
      <el-descriptions-item label="房型">
        {{ accommodation.roomType }}
      </el-descriptions-item>
      <el-descriptions-item label="地址">
        {{ accommodation.address }}
      </el-descriptions-item>
      <el-descriptions-item label="入住日期">
        {{ formatDate(accommodation.checkIn) }}
      </el-descriptions-item>
      <el-descriptions-item label="退房日期">
        {{ formatDate(accommodation.checkOut) }}
      </el-descriptions-item>
      <el-descriptions-item v-if="accommodation.amenities" label="设施信息" :span="2">
        {{ accommodation.amenities }}
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup lang="ts">
import { OfficeBuilding, Location } from '@element-plus/icons-vue'
import type { AccommodationPlan } from '@/types/travelPlan'

const props = defineProps<{
  /** 住宿安排数据 */
  accommodation: AccommodationPlan
}>()

/**
 * 格式化日期显示
 */
function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.accommodation-info-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.accommodation-descriptions {
  margin-top: 8px;
}
</style>
