<template>
  <div class="date-picker">
    <div class="date-inputs">
      <div class="date-field">
        <label>出发日期</label>
        <input
          type="date"
          :value="startDate"
          :min="today"
          @input="onStartDateChange"
          class="date-input"
        />
      </div>
      <div class="date-field">
        <label>返回日期</label>
        <input
          type="date"
          :value="endDate"
          :min="startDate || today"
          @input="onEndDateChange"
          class="date-input"
        />
      </div>
    </div>
    <div class="days-display" v-if="days > 0">
      出行天数：<strong>{{ days }}</strong> 天
    </div>
    <div class="days-adjust" v-if="days > 0">
      <label>调整天数：</label>
      <button @click="decreaseDays" :disabled="days <= 1">−</button>
      <span>{{ days }}</span>
      <button @click="increaseDays">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { format, addDays } from 'date-fns'

const props = defineProps<{
  startDate: string
  endDate: string
  days: number
}>()

const emit = defineEmits<{
  'update:startDate': [date: string]
  'update:endDate': [date: string]
  'update:days': [days: number]
}>()

const today = format(new Date(), 'yyyy-MM-dd')

const onStartDateChange = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  emit('update:startDate', value)
  if (props.endDate && value >= props.endDate) {
    const newEnd = format(addDays(new Date(value), 1), 'yyyy-MM-dd')
    emit('update:endDate', newEnd)
    emit('update:days', 2)
  } else if (props.endDate && value) {
    const newDays = calculateDays(value, props.endDate)
    emit('update:days', newDays)
  }
}

const onEndDateChange = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  emit('update:endDate', value)
  if (props.startDate && value) {
    const newDays = calculateDays(props.startDate, value)
    emit('update:days', newDays)
  }
}

const calculateDays = (start: string, end: string): number => {
  const s = new Date(start)
  const e = new Date(end)
  return Math.round((e.getTime() - s.getTime()) / (1000 * 60 * 60 * 24)) + 1
}

const decreaseDays = () => {
  if (props.days <= 1) return
  const newDays = props.days - 1
  if (props.startDate) {
    const newEnd = format(addDays(new Date(props.startDate), newDays - 1), 'yyyy-MM-dd')
    emit('update:endDate', newEnd)
  }
  emit('update:days', newDays)
}

const increaseDays = () => {
  if (props.days >= 30) return
  const newDays = props.days + 1
  if (props.startDate) {
    const newEnd = format(addDays(new Date(props.startDate), newDays - 1), 'yyyy-MM-dd')
    emit('update:endDate', newEnd)
  }
  emit('update:days', newDays)
}
</script>

<style scoped>
.date-picker {
  width: 100%;
}

.date-inputs {
  display: flex;
  gap: 12px;
}

.date-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-field label {
  font-size: 13px;
  color: #666;
}

.date-input {
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.date-input:focus {
  border-color: #4a90d9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.1);
}

.days-display {
  margin-top: 8px;
  font-size: 14px;
  color: #333;
}

.days-adjust {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.days-adjust label {
  font-size: 13px;
  color: #666;
}

.days-adjust button {
  width: 28px;
  height: 28px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.days-adjust button:hover:not(:disabled) {
  background: #f5f7fa;
}

.days-adjust button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.days-adjust span {
  font-size: 14px;
  min-width: 24px;
  text-align: center;
}
</style>
