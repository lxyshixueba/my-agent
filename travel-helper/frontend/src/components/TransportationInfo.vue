<template>
  <el-card class="transportation-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Van /></el-icon>
        <span>交通安排</span>
      </div>
    </template>

    <el-table
      v-if="transportation && transportation.length > 0"
      :data="transportation"
      stripe
      border
      class="transportation-table"
    >
      <el-table-column label="交通类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getTransportTypeTag(row.type)" size="small">
            {{ row.type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="详情" min-width="200">
        <template #default="{ row }">
          {{ row.description }}
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-else description="暂无交通安排" />
  </el-card>
</template>

<script setup lang="ts">
import { Van } from '@element-plus/icons-vue'
import type { TransportationPlan } from '@/types/travelPlan'

const props = defineProps<{
  /** 交通安排数据 */
  transportation?: TransportationPlan[]
}>()

/**
 * 根据交通类型返回对应的 Element Plus tag 类型
 */
function getTransportTypeTag(type: string): '' | 'primary' | 'success' | 'warning' | 'info' | 'danger' {
  const typeMap: Record<string, '' | 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    '航班': 'primary',
    '火车': 'success',
    '高铁': 'success',
    '地铁': 'info',
    '公交': 'warning',
    '自驾': 'danger',
    '大巴': 'info',
  }
  return typeMap[type] || ''
}
</script>

<style scoped>
.transportation-info-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.transportation-table {
  margin-top: 8px;
}
</style>
