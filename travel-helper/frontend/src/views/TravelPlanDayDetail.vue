<template>
  <div class="travel-plan-day-detail" v-loading="loading">
    <!-- 顶部导航栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 v-if="dayData">
          第 {{ dayIndex }} 天 · {{ formatDate(dayData.date) }}
        </h1>
        <h1 v-else>逐日行程详情</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑行程
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
      @retry="loadDayData"
    />

    <!-- 骨架屏加载中 — 模拟实际内容结构 -->
    <template v-if="loading">
      <!-- 日程时间线骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 80px; height: 20px;" />
        </template>
        <el-skeleton :rows="6" animated />
      </el-card>
      <!-- 景点卡片骨架 -->
      <el-card class="skeleton-card skeleton-card--image" shadow="hover">
        <el-skeleton-item variant="image" style="width: 100%; height: 200px; border-radius: 4px;" />
        <el-skeleton :rows="4" animated style="margin-top: 16px;" />
      </el-card>
      <!-- 住宿/餐饮/交通/天气骨架 -->
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 80px; height: 20px;" />
        </template>
        <el-skeleton :rows="4" animated />
      </el-card>
      <el-card class="skeleton-card" shadow="hover">
        <template #header>
          <el-skeleton-item variant="h3" style="width: 80px; height: 20px;" />
        </template>
        <el-skeleton :rows="3" animated />
      </el-card>
    </template>

    <!-- 详情页内容 -->
    <template v-else-if="dayData">
      <!-- 日程时间线 -->
      <ScheduleTimeline v-if="dayData.schedule && dayData.schedule.length > 0" :schedule="dayData.schedule" />

      <!-- 景点详情卡片列表 -->
      <div v-if="dayData.attractions && dayData.attractions.length > 0" class="attractions-section">
        <h2 class="section-title">
          <el-icon :size="18"><Location /></el-icon>
          景点详情
        </h2>
        <AttractionCard
          v-for="attraction in dayData.attractions"
          :key="attraction.id"
          :attraction="attraction"
        />
      </div>
      <el-empty
        v-else
        description="暂无景点信息"
        class="empty-section"
      />

      <!-- 住宿安排 -->
      <AccommodationInfo
        v-if="dayData.accommodation"
        :accommodation="dayData.accommodation"
      />

      <!-- 餐饮安排 -->
      <DiningInfo
        v-if="dayData.dining"
        :dining="dayData.dining"
      />

      <!-- 交通安排 -->
      <TransportationInfo
        v-if="dayData.transportation && dayData.transportation.length > 0"
        :transportation="dayData.transportation"
      />

      <!-- 天气信息 -->
      <WeatherInfo
        v-if="dayData.weather"
        :weather="dayData.weather"
      />
    </template>

    <!-- 无数据状态 -->
    <template v-else>
      <el-empty description="暂无行程数据">
        <el-button type="primary" @click="goToOverview">返回概览页</el-button>
      </el-empty>
    </template>

    <!-- 编辑行程抽屉 -->
    <EditDayDrawer
      v-model="editDrawerVisible"
      :day-index="dayIndex"
      :day-data="dayData"
      @save="handleSaveAttractions"
      @cancel="handleEditCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Location } from '@element-plus/icons-vue'
import AttractionCard from '@/components/AttractionCard.vue'
import ScheduleTimeline from '@/components/ScheduleTimeline.vue'
import AccommodationInfo from '@/components/AccommodationInfo.vue'
import DiningInfo from '@/components/DiningInfo.vue'
import TransportationInfo from '@/components/TransportationInfo.vue'
import WeatherInfo from '@/components/WeatherInfo.vue'
import EditDayDrawer from '@/components/EditDayDrawer.vue'
import ErrorPrompt from '@/components/ErrorPrompt.vue'
import { getDayDetail, updateDay } from '@/services/travelPlanService'
import type { DailyItineraryFull, AttractionDetail } from '@/types/travelPlan'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id as string)
const dayIndex = computed(() => Number(route.params.dayIndex))
const dayData = ref<DailyItineraryFull | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

/** 编辑抽屉显示状态 */
const editDrawerVisible = ref(false)

/**
 * 格式化日期显示
 */
function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${weekdays[d.getDay()]}`
  } catch {
    return dateStr
  }
}

/**
 * 加载当天行程数据
 */
async function loadDayData() {
  if (!planId.value || !dayIndex.value) {
    error.value = '缺少旅行计划 ID 或天数索引'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    dayData.value = await getDayDetail(planId.value, dayIndex.value)
  } catch (e: any) {
    console.error('加载当天行程失败:', e)
    error.value = e.message || '加载当天行程失败，请稍后重试'
    dayData.value = null
  } finally {
    loading.value = false
  }
}

/**
 * 返回上一页
 */
function goBack() {
  router.back()
}

/**
 * 跳转到概览页
 */
function goToOverview() {
  router.push({ name: 'TravelPlanOverview', params: { id: planId.value } })
}

/**
 * 打开编辑行程抽屉
 */
function handleEdit() {
  editDrawerVisible.value = true
}

/**
 * 保存编辑后的景点列表
 * @param updatedAttractions 更新后的景点列表
 */
async function handleSaveAttractions(updatedAttractions: AttractionDetail[]) {
  if (!planId.value || !dayIndex.value || !dayData.value) {
    ElMessage.error('缺少旅行计划数据')
    return
  }

  try {
    // 构造更新请求体
    const requestData = {
      schedule: dayData.value.schedule || [],
      attractions: updatedAttractions,
      accommodation: dayData.value.accommodation,
      dining: dayData.value.dining,
      transportation: dayData.value.transportation,
    }

    // 调用 PUT API 保存更新
    await updateDay(planId.value, dayIndex.value, requestData)
    ElMessage.success('行程已保存')

    // 刷新详情页数据
    await loadDayData()
  } catch (e: any) {
    console.error('保存行程失败:', e)
    ElMessage.error(e.message || '保存行程失败，请稍后重试')
  }
}

/**
 * 取消编辑
 */
function handleEditCancel() {
  ElMessage.info('已取消编辑')
}

onMounted(() => {
  loadDayData()
})
</script>

<style scoped>
.travel-plan-day-detail {
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

.skeleton-card {
  margin-bottom: 16px;
  background: #fff;
}

.skeleton-card--image {
  overflow: hidden;
}

.attractions-section {
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.empty-section {
  margin-bottom: 16px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}
</style>
