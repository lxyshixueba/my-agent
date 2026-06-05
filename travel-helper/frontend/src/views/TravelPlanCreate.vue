<template>
  <div class="travel-plan-create">
    <header class="page-header">
      <span class="header-icon">✈️</span>
      <h1>智能旅行助手</h1>
      <p class="subtitle">基于 AI 个性化旅行规划，让每一次出行都完美无瑕</p>
    </header>

    <el-card class="form-card" shadow="always">
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="目的地城市">
              <el-autocomplete
                v-model="cityQuery"
                :fetch-suggestions="fetchCities"
                placeholder="请输入城市"
                @select="selectCity"
                value-key="name"
              >
                <template #default="{ item }">
                  <div class="city-suggestion">
                    <span class="city-name">{{ item.name }}</span>
                    <span class="city-province">{{ item.province }}</span>
                  </div>
                </template>
              </el-autocomplete>
            </el-form-item>
          </el-col>

          <el-col :span="5">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="5">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="4">
            <el-form-item label="旅行天数">
              <div class="days-control">
                <span class="days-value">{{ form.days }}</span>
                <span class="days-unit">天</span>
              </div>
            </el-form-item>
          </el-col>

          <el-col :span="4" class="submit-col">
            <el-button
              type="primary"
              size="large"
              :loading="isGenerating"
              class="submit-btn"
              @click="onSubmit"
            >
              {{ isGenerating ? '正在生成...' : '开始规划' }}
            </el-button>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          <el-icon><Setting /></el-icon>
          偏好设置
        </el-divider>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="交通方式">
              <el-select v-model="form.transport_mode" placeholder="请选择交通方式" style="width: 100%">
                <el-option
                  v-for="opt in transportOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="住宿偏好">
              <el-select v-model="form.accommodation" placeholder="请选择住宿偏好" style="width: 100%">
                <el-option
                  v-for="opt in accommodationOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="旅行偏好">
              <el-checkbox-group v-model="form.preferences">
                <el-checkbox v-for="tag in allTags" :key="tag.value" :value="tag.value">
                  {{ tag.label }}
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          <el-icon><Document /></el-icon>
          服务要求
        </el-divider>

        <el-form-item>
          <el-input
            v-model="form.special_requirements"
            type="textarea"
            :rows="3"
            placeholder="请输入您的特殊要求，例如：带小孩出行，需要儿童友好设施..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="isGenerating" class="progress-card" shadow="always">
      <el-progress
        :percentage="progress"
        :stroke-width="10"
        striped
        striped-flow
      />
      <p class="progress-hint">
        <span>💡</span>
        正在规划路线...
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Setting, Document } from '@element-plus/icons-vue'
import { PREFERENCE_CONFIG, type PreferenceTag, type City } from '@/types/travelPlan'
import { generateTravelPlan, searchCities as apiSearchCities } from '@/services/travelPlanApi'
import { savePlanId } from '@/services/storageService'

const router = useRouter()

const form = reactive({
  destination: null as City | null,
  start_date: '',
  end_date: '',
  days: 1,
  transport_mode: '',
  accommodation: '',
  preferences: [] as PreferenceTag[],
  special_requirements: '',
})

const cityQuery = ref('')

const fetchCities = async (queryString: string, cb: (results: any[]) => void) => {
  if (queryString.length < 1) {
    cb([])
    return
  }
  try {
    const results = await apiSearchCities(queryString)
    cb(results)
  } catch {
    cb([])
  }
}

const selectCity = (city: City) => {
  form.destination = city
}

// 日期联动：自动计算天数
watch([() => form.start_date, () => form.end_date], () => {
  if (form.start_date && form.end_date) {
    const s = new Date(form.start_date)
    const e = new Date(form.end_date)
    const diff = Math.round((e.getTime() - s.getTime()) / (1000 * 60 * 60 * 24)) + 1
    form.days = diff > 0 ? diff : 0
  }
})

const transportOptions = [
  { value: 'flight', label: '✈️ 飞机' },
  { value: 'high_speed_rail', label: '🚄 高铁' },
  { value: 'self_driving', label: '🚗 自驾' },
  { value: 'bus', label: '🚌 大巴' },
]

const accommodationOptions = [
  { value: 'economy', label: '经济型' },
  { value: 'comfort', label: '舒适型' },
  { value: 'premium', label: '高档型' },
  { value: 'luxury', label: '豪华型' },
  { value: 'homestay', label: '民宿' },
]

const allTags = Object.entries(PREFERENCE_CONFIG).map(([value, config]) => ({
  value: value as PreferenceTag,
  ...config,
}))

const isGenerating = ref(false)
const progress = ref(0)
let progressTimer: ReturnType<typeof setInterval> | null = null

const onSubmit = async () => {
  if (!form.destination) {
    ElMessage.warning('请选择目的地城市')
    return
  }
  if (!form.start_date || !form.end_date) {
    ElMessage.warning('请选择出行日期')
    return
  }
  if (!form.transport_mode) {
    ElMessage.warning('请选择交通方式')
    return
  }
  if (!form.accommodation) {
    ElMessage.warning('请选择住宿偏好')
    return
  }

  isGenerating.value = true
  progress.value = 0

  progressTimer = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.floor(Math.random() * 10) + 1
    }
  }, 500)

  try {
    const request = {
      destination: { name: form.destination.name, code: form.destination.code },
      start_date: form.start_date,
      end_date: form.end_date,
      transport_mode: form.transport_mode as any,
      accommodation: form.accommodation as any,
      preferences: form.preferences.length > 0 ? form.preferences : undefined,
      special_requirements: form.special_requirements || undefined,
    }

    const response = await generateTravelPlan(request)
    progress.value = 100
    console.log('旅行计划已生成:', response)
    ElMessage.success('旅行计划生成成功！')

    // 存储计划 ID 并跳转至概览页
    const planId = response.request_id
    savePlanId(planId)
    router.push({ name: 'TravelPlanOverview', params: { id: planId } })
  } catch (err: any) {
    ElMessage.error(err.message || '生成失败，请稍后重试')
  } finally {
    isGenerating.value = false
    if (progressTimer) clearInterval(progressTimer)
  }
}
</script>

<style scoped>
.travel-plan-create {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.header-icon {
  font-size: 40px;
}

.page-header h1 {
  font-size: 28px;
  color: #fff;
  margin: 8px 0;
  font-weight: 700;
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 0;
}

.form-card {
  width: 100%;
  max-width: 1100px;
  border-radius: 16px;
}

.form-card :deep(.el-card__body) {
  padding: 24px;
}

.submit-col {
  display: flex;
  align-items: flex-end;
}

.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 16px;
  font-weight: 600;
}

.days-control {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.days-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.days-unit {
  font-size: 14px;
  color: #666;
}

.el-divider {
  margin: 20px 0 16px;
}

.el-divider :deep(.el-divider__text) {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.city-suggestion {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.city-name {
  font-weight: 500;
}

.city-province {
  color: #999;
  font-size: 12px;
}

.progress-card {
  width: 100%;
  max-width: 1100px;
  margin-top: 16px;
  border-radius: 12px;
}

.progress-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  color: #666;
  font-size: 13px;
}
</style>
