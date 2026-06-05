import { createRouter, createWebHistory } from 'vue-router'
import TravelPlanCreate from '@/views/TravelPlanCreate.vue'
import TravelPlanOverview from '@/views/TravelPlanOverview.vue'

const routes = [
  {
    path: '/',
    name: 'TravelPlanCreate',
    component: TravelPlanCreate,
  },
  {
    path: '/travel-plans/:id/overview',
    name: 'TravelPlanOverview',
    component: TravelPlanOverview,
    props: true,
  },
  // 预留详情页路由（后续用户故事实现）
  {
    path: '/travel-plans/:id/day/:dayIndex',
    name: 'TravelPlanDayDetail',
    component: () => import('@/views/TravelPlanDayDetail.vue'),
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
