<template>
  <div class="transport-selector">
    <label class="selector-label">交通方式</label>
    <div class="transport-options">
      <div
        v-for="option in options"
        :key="option.value"
        :class="['transport-option', { active: modelValue === option.value }]"
        @click="select(option.value)"
      >
        <span class="transport-icon">{{ option.icon }}</span>
        <span class="transport-label">{{ option.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const options = [
  { value: 'flight', label: '飞机', icon: '✈️' },
  { value: 'high_speed_rail', label: '高铁', icon: '🚄' },
  { value: 'self_driving', label: '自驾', icon: '🚗' },
  { value: 'bus', label: '大巴', icon: '🚌' },
]

const select = (value: string) => {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.transport-selector {
  width: 100%;
}

.selector-label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.transport-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.transport-option {
  flex: 1;
  min-width: 80px;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.transport-option:hover {
  border-color: #4a90d9;
  background: #f8faff;
}

.transport-option.active {
  border-color: #4a90d9;
  background: #e8f0fe;
}

.transport-icon {
  font-size: 24px;
}

.transport-label {
  font-size: 12px;
  color: #333;
}
</style>
