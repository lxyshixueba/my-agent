<template>
  <el-alert
    :title="title"
    :type="type"
    :closable="closable"
    :show-icon="true"
    class="error-prompt"
    @close="handleClose"
  >
    <template #default>
      <div class="error-prompt__content">
        <slot>
          <p v-if="message" class="error-prompt__message">{{ message }}</p>
        </slot>
        <div v-if="showRetry" class="error-prompt__actions">
          <el-button :type="retryType" :size="buttonSize" @click="handleRetry">
            {{ retryText }}
          </el-button>
        </div>
      </div>
    </template>
  </el-alert>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  /** 错误提示标题 */
  title: string
  /** 错误详细信息（可选，会显示在默认插槽中） */
  message?: string
  /** 提示类型，默认 'error' */
  type?: 'success' | 'warning' | 'info' | 'error'
  /** 是否可关闭，默认 true */
  closable?: boolean
  /** 是否显示重试按钮，默认 false */
  showRetry?: boolean
  /** 重试按钮文案，默认"重试" */
  retryText?: string
  /** 重试按钮类型，默认 'primary' */
  retryType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  /** 重试按钮尺寸，默认 'small' */
  buttonSize?: 'default' | 'small' | 'large'
}>(), {
  type: 'error',
  closable: true,
  showRetry: false,
  retryText: '重试',
  retryType: 'primary',
  buttonSize: 'small',
})

const emit = defineEmits<{
  /** 关闭提示时触发 */
  close: []
  /** 点击重试按钮时触发 */
  retry: []
}>()

function handleClose() {
  emit('close')
}

function handleRetry() {
  emit('retry')
}
</script>

<style scoped>
.error-prompt {
  margin-bottom: 16px;
}

.error-prompt__content {
  margin-top: 4px;
}

.error-prompt__message {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.error-prompt__actions {
  margin-top: 12px;
}
</style>
