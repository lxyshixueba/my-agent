<template>
  <div class="preference-selector">
    <div class="tags-container">
      <div
        v-for="tag in allTags"
        :key="tag.value"
        :class="['tag-chip', { active: isActive(tag.value) }]"
        @click="toggle(tag.value)"
      >
        <span class="tag-icon">{{ tag.icon }}</span>
        <span class="tag-label">{{ tag.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PREFERENCE_CONFIG, type PreferenceTag } from '@/types/travelPlan'

const props = defineProps<{
  modelValue: PreferenceTag[]
}>()

const emit = defineEmits<{
  'update:modelValue': [tags: PreferenceTag[]]
}>()

const allTags = Object.entries(PREFERENCE_CONFIG).map(([value, config]) => ({
  value: value as PreferenceTag,
  ...config,
}))

const isActive = (tag: PreferenceTag) => {
  return props.modelValue.includes(tag)
}

const toggle = (tag: PreferenceTag) => {
  if (isActive(tag)) {
    emit('update:modelValue', props.modelValue.filter((t) => t !== tag))
  } else {
    emit('update:modelValue', [...props.modelValue, tag])
  }
}
</script>

<style scoped>
.preference-selector {
  width: 100%;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 8px 14px;
  border: 2px solid #eee;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.tag-chip:hover {
  border-color: #4a90d9;
}

.tag-chip.active {
  border-color: #4a90d9;
  background: #e8f0fe;
  color: #4a90d9;
}

.tag-icon {
  font-size: 16px;
}

.tag-label {
  font-size: 13px;
}
</style>
