<template>
  <div class="empty-state">
    <el-empty
      :description="description"
      :image="image"
      :image-size="imageSize"
    >
      <slot />
      <template #description>
        <slot name="description">
          <p class="empty-state__description">{{ description }}</p>
        </slot>
      </template>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  /** 空状态描述文案，默认"暂无数据" */
  description?: string
  /** 自定义图片 URL（可选） */
  image?: string
  /** 图片大小（像素），默认 120 */
  imageSize?: number
}>()

withDefaults(defineProps<{
  description?: string
  image?: string
  imageSize?: number
}>(), {
  description: '暂无数据',
  imageSize: 120,
})
</script>

<style scoped>
.empty-state {
  padding: 32px 16px;
  background: #fff;
  border-radius: 8px;
  text-align: center;
}

.empty-state__description {
  color: #909399;
  font-size: 14px;
  margin: 8px 0;
}
</style>
