<template>
  <el-card class="attraction-card" shadow="hover">
    <!-- 景点图片 -->
    <div class="attraction-image-wrapper">
      <el-image
        :src="attraction.imageUrl || ''"
        :alt="attraction.name"
        fit="cover"
        lazy
        class="attraction-image"
      >
        <!-- 图片加载失败占位 -->
        <template #error>
          <div class="image-placeholder">
            <el-icon :size="48" color="#c0c4cc"><Picture /></el-icon>
            <span class="placeholder-text">暂无图片</span>
          </div>
        </template>
        <!-- 图片加载中占位 -->
        <template #placeholder>
          <div class="image-placeholder loading">
            <el-icon :size="32" class="is-loading" color="#909399"><Loading /></el-icon>
            <span class="placeholder-text">图片加载中...</span>
          </div>
        </template>
      </el-image>
    </div>

    <!-- 景点信息 -->
    <div class="attraction-info">
      <h3 class="attraction-name">{{ attraction.name }}</h3>

      <!-- 游玩时间 -->
      <div class="play-duration">
        <el-icon :size="16" color="#909399"><Clock /></el-icon>
        <span>建议游玩时长：{{ attraction.playDuration }}</span>
      </div>

      <!-- 景点特色标签 -->
      <div v-if="attraction.features" class="features-tags">
        <el-tag
          v-for="(feature, index) in featureTags"
          :key="index"
          size="small"
          type="success"
          effect="plain"
          class="feature-tag"
        >
          {{ feature }}
        </el-tag>
      </div>

      <!-- 景点描述 -->
      <p class="attraction-description">{{ attraction.description }}</p>

      <!-- 游玩贴士 -->
      <div v-if="attraction.tips" class="attraction-tips">
        <el-icon :size="14" color="#e6a23c"><WarningFilled /></el-icon>
        <span class="tips-text">{{ attraction.tips }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Picture, Clock, Loading, WarningFilled } from '@element-plus/icons-vue'
import type { AttractionDetail } from '@/types/travelPlan'

const props = defineProps<{
  /** 景点详情数据 */
  attraction: AttractionDetail
}>()

/**
 * 将景点特色字符串拆分为标签数组
 */
const featureTags = computed<string[]>(() => {
  if (!props.attraction.features) return []
  // 支持逗号、顿号、空格分隔
  return props.attraction.features
    .split(/[、,，\s]+/)
    .filter((f) => f.trim().length > 0)
    .map((f) => f.trim())
})
</script>

<style scoped>
.attraction-card {
  margin-bottom: 16px;
  overflow: hidden;
}

.attraction-image-wrapper {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 4px;
  background: #f5f7fa;
}

.attraction-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: #f5f7fa;
  color: #c0c4cc;
  gap: 8px;
}

.image-placeholder.loading {
  background: linear-gradient(90deg, #f5f7fa 25%, #ebeef5 50%, #f5f7fa 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.placeholder-text {
  margin-top: 8px;
  font-size: 12px;
  color: #c0c4cc;
}

.attraction-info {
  padding: 16px 0 0;
}

.attraction-name {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.play-duration {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.features-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.feature-tag {
  border-radius: 4px;
}

.attraction-description {
  margin: 0 0 12px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.attraction-tips {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 12px;
  background: #fdf6ec;
  border-radius: 4px;
  border-left: 3px solid #e6a23c;
}

.tips-text {
  font-size: 13px;
  color: #e6a23c;
  line-height: 1.5;
}
</style>
