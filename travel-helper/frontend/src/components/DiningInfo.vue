<template>
  <el-card class="dining-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Food /></el-icon>
        <span>餐饮安排</span>
      </div>
    </template>

    <div class="dining-sections">
      <!-- 早餐 -->
      <div class="meal-section" v-if="dining.breakfast">
        <div class="meal-header">
          <el-tag type="warning" size="small">早餐</el-tag>
        </div>
        <p class="meal-content">{{ dining.breakfast }}</p>
      </div>

      <!-- 午餐 -->
      <div class="meal-section" v-if="dining.lunch">
        <div class="meal-header">
          <el-tag type="success" size="small">午餐</el-tag>
        </div>
        <p class="meal-content">{{ dining.lunch }}</p>
      </div>

      <!-- 晚餐 -->
      <div class="meal-section" v-if="dining.dinner">
        <div class="meal-header">
          <el-tag type="danger" size="small">晚餐</el-tag>
        </div>
        <p class="meal-content">{{ dining.dinner }}</p>
      </div>

      <el-empty
        v-if="!dining.breakfast && !dining.lunch && !dining.dinner"
        description="暂无餐饮安排"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Food } from '@element-plus/icons-vue'
import type { DiningPlan } from '@/types/travelPlan'

defineProps<{
  /** 餐饮安排数据 */
  dining: DiningPlan
}>()
</script>

<style scoped>
.dining-info-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.dining-sections {
  padding: 8px 0;
}

.meal-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.meal-section:last-child {
  margin-bottom: 0;
}

.meal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.meal-content {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>
