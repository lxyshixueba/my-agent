<template>
  <el-dialog
    v-model="visible"
    title="重新规划旅行计划"
    width="480px"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    @close="handleCancel"
  >
    <div class="replan-confirm">
      <el-alert
        title="重新规划将覆盖当前的行程安排"
        type="warning"
        :closable="false"
        show-icon
        class="warning-alert"
      >
        <template #default>
          <p class="warning-text">此操作将覆盖当前的行程安排，您所做的编辑内容将会丢失。请确认后再继续操作。</p>
        </template>
      </el-alert>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="danger" @click="handleConfirm">确认重新规划</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  /** 弹窗是否可见 */
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  /** 用户点击确认重新规划 */
  'confirm': []
}>()

/** 双向绑定 visible 状态 */
const visible = computed<boolean>({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})

/**
 * 处理取消操作
 */
function handleCancel() {
  visible.value = false
}

/**
 * 处理确认操作，触发 confirm 事件由父组件执行重新规划
 */
function handleConfirm() {
  visible.value = false
  emit('confirm')
}
</script>

<style scoped>
.replan-confirm {
  padding: 8px 0;
}

.warning-alert {
  margin-bottom: 8px;
}

.warning-text {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
