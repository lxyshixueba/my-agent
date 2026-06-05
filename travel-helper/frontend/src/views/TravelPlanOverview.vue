<template>
  <div class="travel-plan-overview" v-loading="loading || exporting || replanLoading" ref="overviewRef">
    <!-- 顶部导航栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 v-if="planData">{{ planData.destination.name }} · {{ formatDateRange(planData.dateRange) }}</h1>
        <h1 v-else>旅行计划概览</h1>
      </div>
      <div class="header-actions">
        <ExportDropdown
          @export-image="handleExportImage"
          @export-pdf="handleExportPdf"
        />
        <el-button type="danger" @click="handleReplan">
          <el-icon><RefreshLeft /></el-icon>
          重新规划
        </el-button>
      </div>
    </div>

    <!-- 错误提示 -->
    <ErrorPrompt
      v-if="error"
      title="加载失败"
      :message="error"
      show-retry
      retry-text="重新加载"
      @retry="loadPlanData"
    />

    <!-- 骨架屏加载中 — 模拟实际内容结构 -->
    <template v-if="loading">
      <!-- 基本信息骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <el-skeleton :rows="2" animated />
      </el-card>
      <!-- 预算卡片骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 100px; height: 20px;" />
        </template>
        <el-skeleton :rows="4" animated />
      </el-card>
      <!-- 地图骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 100px; height: 20px;" />
        </template>
        <el-skeleton :rows="6" animated />
      </el-card>
      <!-- 每日行程骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 100px; height: 20px;" />
        </template>
        <el-skeleton :rows="10" animated />
      </el-card>
    </template>

    <!-- 概览内容 -->
    <template v-else-if="planData">
      <!-- 基本信息 -->
      <el-descriptions class="info-section" :column="2" border>
        <el-descriptions-item label="目的地">{{ planData.destination.name }}</el-descriptions-item>
        <el-descriptions-item label="出行日期">{{ formatDateRange(planData.dateRange) }}</el-descriptions-item>
        <el-descriptions-item label="交通方式">{{ planData.preferences?.transportation || '-' }}</el-descriptions-item>
        <el-descriptions-item label="住宿偏好">{{ planData.preferences?.accommodationType || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatDateTime(planData.createdAt) }}</el-descriptions-item>
        <el-descriptions-item v-if="planData.description" label="描述" :span="2">{{ planData.description }}</el-descriptions-item>
      </el-descriptions>

      <!-- 预算明细 -->
      <BudgetCard :budget="planData.budget" />

      <!-- 地图 -->
      <div data-skip-export="true">
        <MapView
          :destination="planData.destination"
          :attractions="allAttractions"
          :accommodation="accommodation"
        />
      </div>

      <!-- 每日行程 -->
      <DailyScheduleList
        :plan-id="planId"
        :daily-itineraries="planData.dailyItineraries"
      />
    </template>

    <!-- 重新规划确认弹窗 -->
    <ReplanConfirmModal
      v-model="replanModalVisible"
      @confirm="handleReplanConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, RefreshLeft } from '@element-plus/icons-vue'
import BudgetCard from '@/components/BudgetCard.vue'
import MapView from '@/components/MapView.vue'
import DailyScheduleList from '@/components/DailyScheduleList.vue'
import ExportDropdown from '@/components/ExportDropdown.vue'
import ReplanConfirmModal from '@/components/ReplanConfirmModal.vue'
import ErrorPrompt from '@/components/ErrorPrompt.vue'
import { getTravelPlan, replan } from '@/services/travelPlanService'
import { exportAsImage, exportAsPdf } from '@/services/exportService'
import type { TravelPlanFull, AttractionDetail, AccommodationPlan } from '@/types/travelPlan'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id as string)
const planData = ref<TravelPlanFull | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const overviewRef = ref<HTMLElement | null>(null)
const exporting = ref(false)

/** 重新规划弹窗可见性 */
const replanModalVisible = ref(false)
/** 重新规划 API 调用加载中 */
const replanLoading = ref(false)

/**
 * 收集所有天的景点（用于地图标记）
 */
const allAttractions = computed<AttractionDetail[]>(() => {
  if (!planData.value) return []
  const result: AttractionDetail[] = []
  for (const day of planData.value.dailyItineraries) {
    result.push(...day.attractions)
  }
  return result
})

/**
 * 获取住宿信息（取第一天的住宿，通常整个行程住同一酒店）
 */
const accommodation = computed<AccommodationPlan | null>(() => {
  if (!planData.value) return null
  for (const day of planData.value.dailyItineraries) {
    if (day.accommodation) {
      return day.accommodation
    }
  }
  return null
})

/**
 * 加载旅行计划数据
 */
async function loadPlanData() {
  if (!planId.value) {
    error.value = '缺少旅行计划 ID'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    planData.value = await getTravelPlan(planId.value)
  } catch (e: any) {
    console.error('加载旅行计划失败:', e)
    error.value = e.message || '加载旅行计划失败，请稍后重试'
    planData.value = null
  } finally {
    loading.value = false
  }
}

/**
 * 格式化日期范围
 */
function formatDateRange(dateRange: { startDate: string; endDate: string }): string {
  const start = formatDateShort(dateRange.startDate)
  const end = formatDateShort(dateRange.endDate)
  return `${start} ~ ${end}`
}

/**
 * 短日期格式
 */
function formatDateShort(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return dateStr
  }
}

/**
 * 日期时间格式
 */
function formatDateTime(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return d.toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

/**
 * 返回上一页
 */
function goBack() {
  router.back()
}

/**
 * 导出为图片
 */
async function handleExportImage() {
  if (!overviewRef.value) {
    ElMessage.error('未找到可导出的内容')
    return
  }

  exporting.value = true
  try {
    const filename = planData.value
      ? `${planData.value.destination.name}_旅行计划`
      : 'travel-plan'
    await exportAsImage(overviewRef.value, filename)
    ElMessage.success('图片导出成功')
  } catch (e: any) {
    console.error('图片导出失败:', e)
    ElMessage.error(`图片导出失败: ${e.message || '未知错误'}`)
  } finally {
    exporting.value = false
  }
}

/**
 * 导出为 PDF
 */
async function handleExportPdf() {
  if (!overviewRef.value) {
    ElMessage.error('未找到可导出的内容')
    return
  }

  exporting.value = true
  try {
    // 自动获取需要导出的 section（跳过地图等复杂 DOM）
    const sections = Array.from(overviewRef.value.children)
      .filter((child) => {
        const el = child as HTMLElement
        // 跳过标记为跳过导出的元素
        if (el.dataset.skipExport === 'true') return false
        // 跳过隐藏元素
        if (el.offsetParent === null && el.tagName !== 'TEMPLATE') return false
        return true
      }) as HTMLElement[]

    if (sections.length === 0) {
      ElMessage.warning('没有可导出的内容')
      exporting.value = false
      return
    }

    const filename = planData.value
      ? `${planData.value.destination.name}_旅行计划`
      : 'travel-plan'
    await exportAsPdf(sections, filename)
    ElMessage.success('PDF 导出成功')
  } catch (e: any) {
    console.error('PDF 导出失败:', e)
    ElMessage.error(`PDF 导出失败: ${e.message || '未知错误'}`)
  } finally {
    exporting.value = false
  }
}

/**
 * 打开重新规划确认弹窗
 */
function handleReplan() {
  replanModalVisible.value = true
}

/**
 * 确认重新规划：调用 POST replan API，等待响应后刷新概览页数据
 */
async function handleReplanConfirm() {
  if (!planId.value) {
    ElMessage.error('缺少旅行计划 ID')
    return
  }

  replanLoading.value = true
  try {
    await replan(planId.value)
    ElMessage.success('重新规划成功，正在刷新数据...')
    // 刷新概览页数据
    await loadPlanData()
  } catch (e: any) {
    console.error('重新规划失败:', e)
    // 处理 409 冲突错误（已经在重新规划中）
    if (e.response && e.response.status === 409) {
      ElMessage.warning('当前已有重新规划任务正在进行中，请稍后再试')
    } else {
      ElMessage.error(e.message || '重新规划失败，请稍后重试')
    }
  } finally {
    replanLoading.value = false
  }
}

onMounted(() => {
  loadPlanData()
})
</script>

<style scoped>
.travel-plan-overview {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 16px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  font-size: 22px;
  color: #303133;
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-section {
  margin-bottom: 16px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-card {
  margin-bottom: 16px;
  background: #fff;
}
</style>
