<template>
  <div class="city-search">
    <input
      type="text"
      v-model="query"
      :placeholder="placeholder"
      class="city-input"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />
    <ul v-if="showDropdown && cities.length > 0" class="city-dropdown">
      <li
        v-for="city in cities"
        :key="city.code"
        @mousedown="selectCity(city)"
        class="city-item"
      >
        <span class="city-name">{{ city.name }}</span>
        <span class="city-province">{{ city.province }}</span>
      </li>
    </ul>
    <p v-if="showDropdown && query.length >= 2 && cities.length === 0 && !loading" class="no-result">
      未找到匹配城市
    </p>
    <p v-if="loading" class="loading">搜索中...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { City } from '@/types/travelPlan'
import { searchCities } from '@/services/travelPlanApi'

const props = defineProps<{
  placeholder?: string
}>()

const emit = defineEmits<{
  select: [city: City]
}>()

const query = ref('')
const cities = ref<City[]>([])
const showDropdown = ref(false)
const loading = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const onInput = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (query.value.length < 1) {
    cities.value = []
    showDropdown.value = false
    return
  }

  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      cities.value = await searchCities(query.value)
    } catch {
      cities.value = []
    } finally {
      loading.value = false
      showDropdown.value = true
    }
  }, 300)
}

const onFocus = () => {
  if (cities.value.length > 0) {
    showDropdown.value = true
  }
}

const onBlur = () => {
  // 延迟关闭以允许点击选择
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

const selectCity = (city: City) => {
  query.value = city.name
  cities.value = []
  showDropdown.value = false
  emit('select', city)
}
</script>

<style scoped>
.city-search {
  position: relative;
  width: 100%;
}

.city-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.city-input:focus {
  border-color: #4a90d9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.1);
}

.city-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-top: 4px;
  max-height: 240px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  list-style: none;
  padding: 0;
}

.city-item {
  padding: 10px 14px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.city-item:hover {
  background: #f5f7fa;
}

.city-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.city-province {
  font-size: 12px;
  color: #999;
}

.no-result,
.loading {
  color: #999;
  font-size: 13px;
  padding: 8px 14px;
  margin: 0;
}
</style>
