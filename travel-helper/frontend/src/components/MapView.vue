<template>
  <el-card class="map-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon :size="20"><Location /></el-icon>
        <span>目的地地图</span>
      </div>
    </template>

    <!-- 地图加载中占位 -->
    <div v-if="loading" class="map-placeholder">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 地图配置缺失占位 -->
    <div v-else-if="!amapKey" class="map-placeholder error">
      <el-empty description="未配置地图服务">
        <template #description>
          <p class="empty-description">请在环境变量中设置 VITE_AMAP_KEY</p>
        </template>
      </el-empty>
    </div>

    <!-- 地图加载失败占位 -->
    <div v-else-if="error" class="map-placeholder error">
      <el-empty description="地图加载失败">
        <template #description>
          <p class="empty-description">{{ error }}</p>
        </template>
        <el-button type="primary" @click="initMap">重试</el-button>
      </el-empty>
    </div>

    <!-- 地图容器 -->
    <div v-show="!loading && !error && amapKey" ref="mapContainer" class="map-container"></div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Location } from '@element-plus/icons-vue'
import type { AttractionDetail, AccommodationPlan, DestinationCity } from '@/types/travelPlan'

const props = defineProps<{
  /** 目的地城市（用于地图中心点） */
  destination: DestinationCity
  /** 景点列表 */
  attractions: AttractionDetail[]
  /** 住宿安排（可选） */
  accommodation?: AccommodationPlan | null
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

/** 高德地图 API Key */
const amapKey = computed(() => import.meta.env.VITE_AMAP_KEY || '')

let mapInstance: any = null

/**
 * 初始化高德地图
 */
async function initMap() {
  // 检查 API Key
  if (!amapKey.value) {
    error.value = '未配置 VITE_AMAP_KEY 环境变量'
    loading.value = false
    return
  }

  // 检查目的地坐标
  if (!props.destination.latitude || !props.destination.longitude) {
    error.value = '目的地坐标信息缺失，无法显示地图'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    // 动态加载高德地图 JS API
    const AMapLoader = await import('@amap/amap-jsapi-loader')

    const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_JS_CODE || ''

    // 设置安全密钥（高德 2021 年 12 月后要求）
    if (securityJsCode) {
      window._AMapSecurityConfig = {
        securityJsCode,
      }
    }

    const AMap = await AMapLoader.load({
      key: amapKey,
      version: '2.0',
      plugins: [],
    })

    if (!mapContainer.value) return

    // 创建地图实例
    mapInstance = new AMap.Map(mapContainer.value, {
      center: [props.destination.longitude, props.destination.latitude],
      zoom: 12,
      resizeEnable: true,
    })

    // 添加景点标记点
    const attractionMarkers: any[] = []
    for (const attraction of props.attractions) {
      if (attraction.latitude && attraction.longitude) {
        const marker = new AMap.Marker({
          position: [attraction.longitude, attraction.latitude],
          title: attraction.name,
          label: {
            content: `<div class="map-label attraction">${attraction.name}</div>`,
            offset: new AMap.Pixel(0, -30),
          },
        })
        attractionMarkers.push(marker)
      }
    }

    // 添加住宿标记点
    if (props.accommodation && props.accommodation.latitude && props.accommodation.longitude) {
      const hotelMarker = new AMap.Marker({
        position: [props.accommodation.longitude, props.accommodation.latitude],
        title: props.accommodation.hotelName,
        label: {
          content: `<div class="map-label accommodation">🏨 ${props.accommodation.hotelName}</div>`,
          offset: new AMap.Pixel(0, -30),
        },
      })
      attractionMarkers.push(hotelMarker)
    }

    // 将所有标记点添加到地图
    if (attractionMarkers.length > 0) {
      mapInstance.add(attractionMarkers)
    }

    loading.value = false
  } catch (e: any) {
    console.error('高德地图初始化失败:', e)
    error.value = e.message || '地图加载异常'
    loading.value = false
  }
}

onMounted(() => {
  initMap()
})

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.destroy()
    mapInstance = null
  }
})
</script>

<style scoped>
.map-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
}

.map-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fa;
  border-radius: 8px;
}

.map-placeholder.error {
  background: #fef0f0;
}

.empty-description {
  font-size: 13px;
  color: #909399;
  margin: 8px 0 16px;
}
</style>

<style>
/* 地图标签样式（非 scoped） */
.map-label {
  background: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.map-label.attraction {
  border-left: 3px solid #409eff;
}

.map-label.accommodation {
  border-left: 3px solid #e6a23c;
}
</style>
