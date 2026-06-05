<template>
  <div class="content-loading" :class="{ 'content-loading--inline': inline }">
    <el-skeleton :rows="rows" :animated="true" :loading="true">
      <template #default>
        <slot v-if="$slots.content" name="content" />
      </template>
    </el-skeleton>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  /** 骨架屏行数，默认 4 */
  rows?: number
  /** 是否内联模式（不占满容器宽度），默认 false */
  inline?: boolean
}>()
</script>

<style scoped>
.content-loading {
  width: 100%;
}

.content-loading--inline {
  display: inline-block;
  width: auto;
}
</style>
