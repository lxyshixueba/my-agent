<template>
  <el-drawer
    v-model="visible"
    title="编辑行程"
    size="520px"
    direction="rtl"
    :close-on-click-modal="false"
    @close="handleCancel"
  >
    <template #header>
      <div class="drawer-header">
        <h3>编辑行程 - 第 {{ dayIndex }} 天</h3>
        <span class="drawer-hint">拖拽调整景点顺序，点击删除按钮移除景点</span>
      </div>
    </template>

    <div v-loading="saving" class="drawer-body">
      <!-- 景点列表 -->
      <div class="attractions-list">
        <draggable
          v-model="localAttractions"
          item-key="id"
          tag="div"
          class="draggable-container"
          handle=".drag-handle"
          animation="200"
        >
          <template #item="{ element: attraction, index }">
            <div class="attraction-item">
              <!-- 拖拽手柄 -->
              <el-icon class="drag-handle" size="18">
                <Rank />
              </el-icon>

              <!-- 序号 -->
              <span class="item-index">{{ index + 1 }}</span>

              <!-- 景点信息 -->
              <div class="item-info">
                <div class="item-name">{{ attraction.name }}</div>
                <div class="item-duration">
                  <el-icon size="12"><Clock /></el-icon>
                  {{ attraction.playDuration }}
                </div>
              </div>

              <!-- 删除按钮 -->
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDeleteAttraction(attraction)"
                :disabled="localAttractions.length <= 1"
              >
                删除
              </el-button>
            </div>
          </template>
        </draggable>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="localAttractions.length === 0" description="暂无景点" />
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving" :disabled="localAttractions.length < 1">
          保存
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank, Delete, Clock } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import type { AttractionDetail, DailyItineraryFull } from '@/types/travelPlan'

const props = defineProps<{
  /** 是否显示抽屉 */
  modelValue: boolean
  /** 第几天索引 */
  dayIndex: number
  /** 当日行程完整数据 */
  dayData: DailyItineraryFull | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  /** 保存成功后触发，携带更新后的景点列表 */
  save: [attractions: AttractionDetail[]]
  /** 取消编辑 */
  cancel: []
}>()

/** 抽屉可见状态 */
const visible = ref(false)
/** 本地景点列表副本（用于拖拽编辑） */
const localAttractions = ref<AttractionDetail[]>([])
/** 保存中状态 */
const saving = ref(false)

/**
 * 同步父组件传入的 modelValue
 */
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.dayData) {
    // 打开抽屉时，初始化本地景点列表副本
    localAttractions.value = [...props.dayData.attractions]
  }
})

/**
 * 同步本地可见状态到父组件
 */
watch(visible, (val) => {
  emit('update:modelValue', val)
})

/**
 * 删除景点（需要确认）
 */
async function handleDeleteAttraction(attraction: AttractionDetail) {
  // 至少保留 1 个景点
  if (localAttractions.value.length <= 1) {
    ElMessage.warning('至少需要保留 1 个景点')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除景点"${attraction.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    // 从本地列表中移除
    const idx = localAttractions.value.findIndex((a) => a.id === attraction.id)
    if (idx !== -1) {
      localAttractions.value.splice(idx, 1)
    }
    ElMessage.success('已删除景点')
  } catch {
    // 用户取消操作
  }
}

/**
 * 保存编辑结果
 */
async function handleSave() {
  // 校验：至少保留 1 个景点
  if (localAttractions.value.length < 1) {
    ElMessage.warning('至少需要保留 1 个景点')
    return
  }

  saving.value = true
  try {
    emit('save', [...localAttractions.value])
    visible.value = false
  } finally {
    saving.value = false
  }
}

/**
 * 取消编辑
 */
function handleCancel() {
  visible.value = false
  emit('cancel')
}
</script>

<style scoped>
.drawer-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.drawer-hint {
  font-size: 12px;
  color: #909399;
}

.drawer-body {
  min-height: 200px;
  padding: 0 4px;
}

.attractions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.draggable-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attraction-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  transition: box-shadow 0.2s;
}

.attraction-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.drag-handle {
  cursor: grab;
  color: #909399;
  flex-shrink: 0;
}

.drag-handle:active {
  cursor: grabbing;
}

.item-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
