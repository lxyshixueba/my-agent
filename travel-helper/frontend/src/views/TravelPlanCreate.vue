<template>
  <div class="travel-plan-create">
    <header class="page-header">
      <h1>创建旅行计划</h1>
      <p class="subtitle">填写旅行信息，AI 为你定制专属行程</p>
    </header>

    <form @submit.prevent="onSubmit" class="form-container">
      <!-- 目的地城市 -->
      <div class="form-section">
        <h3>目的地</h3>
        <CitySearch
          placeholder="搜索目的地城市"
          @select="onCitySelect"
        />
        <p v-if="errors.destination" class="error-msg">{{ errors.destination }}</p>
      </div>

      <!-- 日期选择 -->
      <div class="form-section">
        <h3>出行日期</h3>
        <DatePicker
          v-model:startDate="form.start_date"
          v-model:endDate="form.end_date"
          v-model:days="form.days"
        />
        <p v-if="errors.dates" class="error-msg">{{ errors.dates }}</p>
      </div>

      <!-- 交通方式 -->
      <div class="form-section">
        <h3>交通方式</h3>
        <TransportSelector v-model="form.transport_mode" />
        <p v-if="errors.transport" class="error-msg">{{ errors.transport }}</p>
      </div>

      <!-- 住宿偏好 -->
      <div class="form-section">
        <h3>住宿偏好</h3>
        <div class="accommodation-options">
          <div
            v-for="opt in accommodationOptions"
            :key="opt.value"
            :class="['accom-option', { active: form.accommodation === opt.value }]"
            @click="form.accommodation = opt.value"
          >
            <span class="accom-icon">{{ opt.icon }}</span>
            <span class="accom-label">{{ opt.label }}</span>
          </div>
        </div>
      </div>

      <!-- 旅行偏好标签 -->
      <div class="form-section">
        <h3>旅行偏好 <span class="optional">(可选)</span></h3>
        <PreferenceSelector v-model="form.preferences" />
      </div>

      <!-- 特殊服务要求 -->
      <div class="form-section">
        <h3>特殊服务要求 <span class="optional">(可选)</span></h3>
        <textarea
          v-model="form.special_requirements"
          placeholder="如：带老人出行，行程不宜太紧凑..."
          maxlength="500"
          rows="3"
          class="special-req-input"
        ></textarea>
        <p class="char-count">{{ (form.special_requirements || '').length }}/500</p>
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="isGenerating"
      >
        <span v-if="isGenerating" class="spinner"></span>
        {{ isGenerating ? '正在生成旅行计划...' : '生成旅行计划' }}
      </button>
    </form>

    <!-- 错误提示 -->
    <div v-if="submitError" class="error-banner">
      {{ submitError }}
      <button @click="onSubmit" class="retry-btn">重试</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import CitySearch from '@/components/CitySearch.vue'
import DatePicker from '@/components/DatePicker.vue'
import TransportSelector from '@/components/TransportSelector.vue'
import PreferenceSelector from '@/components/PreferenceSelector.vue'
import { generateTravelPlan } from '@/services/travelPlanApi'
import type { City, TravelPlanRequest, PreferenceTag } from '@/types/travelPlan'

const form = reactive({
  destination: null as CityRef | null,
  start_date: '',
  end_date: '',
  days: 0,
  transport_mode: null as string | null,
  accommodation: null as string | null,
  preferences: [] as PreferenceTag[],
  special_requirements: '',
})

const errors = reactive({
  destination: '',
  dates: '',
  transport: '',
})

const isGenerating = ref(false)
const submitError = ref('')

const accommodationOptions = [
  { value: 'economy', label: '经济型', icon: '💰' },
  { value: 'comfort', label: '舒适型', icon: '🏨' },
  { value: 'premium', label: '高档型', icon: '⭐' },
  { value: 'luxury', label: '豪华型', icon: '👑' },
  { value: 'homestay', label: '民宿', icon: '🏡' },
]

const onCitySelect = (city: City) => {
  form.destination = { name: city.name, code: city.code }
  errors.destination = ''
}

const validate = (): boolean => {
  let valid = true

  if (!form.destination) {
    errors.destination = '请选择目的地城市'
    valid = false
  } else {
    errors.destination = ''
  }

  if (!form.start_date || !form.end_date) {
    errors.dates = '请选择出行日期'
    valid = false
  } else {
    errors.dates = ''
  }

  if (!form.transport_mode) {
    errors.transport = '请选择交通方式'
    valid = false
  } else {
    errors.transport = ''
  }

  if (!form.accommodation) {
    // 住宿偏好在规范中为必填
  }

  return valid
}

const onSubmit = async () => {
  if (!validate()) return

  isGenerating.value = true
  submitError.value = ''

  try {
    const request: TravelPlanRequest = {
      destination: form.destination!,
      start_date: form.start_date,
      end_date: form.end_date,
      transport_mode: form.transport_mode as any,
      accommodation: form.accommodation as any,
      preferences: form.preferences.length > 0 ? form.preferences : undefined,
      special_requirements: form.special_requirements || undefined,
    }

    const response = await generateTravelPlan(request)
    // 计划生成成功 — 后续迭代中将跳转到结果页面
    console.log('旅行计划已生成:', response)
    alert('旅行计划生成成功！')
  } catch (err: any) {
    submitError.value = err.message || '生成失败，请稍后重试'
  } finally {
    isGenerating.value = false
  }
}
</script>

<style scoped>
.travel-plan-create {
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-section h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.optional {
  font-size: 12px;
  color: #999;
  font-weight: normal;
}

.special-req-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  outline: none;
  font-family: inherit;
  box-sizing: border-box;
}

.special-req-input:focus {
  border-color: #4a90d9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.1);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin: 0;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: #3a7bc8;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  color: #e74c3c;
  font-size: 13px;
  margin: 0;
}

.error-banner {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fdf0ef;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  color: #c0392b;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.retry-btn {
  padding: 6px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.accommodation-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.accom-option {
  flex: 1;
  min-width: 72px;
  padding: 12px 8px;
  border: 2px solid #eee;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.accom-option:hover {
  border-color: #4a90d9;
}

.accom-option.active {
  border-color: #4a90d9;
  background: #e8f0fe;
}

.accom-icon {
  font-size: 20px;
}

.accom-label {
  font-size: 12px;
  color: #333;
}
</style>
