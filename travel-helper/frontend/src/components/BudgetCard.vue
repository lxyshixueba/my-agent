<template>
  <el-card class="budget-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Money /></el-icon>
        <span>预算明细</span>
      </div>
    </template>

    <el-descriptions :column="1" border>
      <el-descriptions-item label="景点门票">
        <span class="amount">¥{{ budget.attractionTickets.toFixed(2) }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="酒店住宿">
        <span class="amount">¥{{ budget.hotelAccommodation.toFixed(2) }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="餐饮交通">
        <span class="amount">¥{{ budget.diningTransport.toFixed(2) }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="餐饮食物">
        <span class="amount">¥{{ budget.diningFood.toFixed(2) }}</span>
      </el-descriptions-item>
    </el-descriptions>

    <div class="budget-total">
      <span class="total-label">预估总费用</span>
      <el-statistic :value="budget.total" prefix="¥" :precision="2" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Money } from '@element-plus/icons-vue'
import type { BudgetBreakdown } from '@/types/travelPlan'

defineProps<{
  budget: BudgetBreakdown
}>()
</script>

<style scoped>
.budget-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.amount {
  font-weight: 600;
  color: #409eff;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
}

.total-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.budget-total :deep(.el-statistic__content) {
  font-weight: 700;
  color: #e6a23c;
  font-size: 22px;
}
</style>
