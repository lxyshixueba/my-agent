<template>
  <el-dropdown trigger="click" @command="handleCommand">
    <el-button type="primary">
      <el-icon><Download /></el-icon>
      导出行程
      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="image">
          <el-icon><Picture /></el-icon>
          导出为图片
        </el-dropdown-item>
        <el-dropdown-item command="pdf">
          <el-icon><Document /></el-icon>
          导出为 PDF
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { Download, ArrowDown, Picture, Document } from '@element-plus/icons-vue'

const emit = defineEmits<{
  'export-image': []
  'export-pdf': []
}>()

/**
 * 处理导出下拉菜单命令
 * @param command 'image' | 'pdf'
 */
function handleCommand(command: 'image' | 'pdf') {
  if (command === 'image') {
    emit('export-image')
  } else if (command === 'pdf') {
    emit('export-pdf')
  }
}
</script>
