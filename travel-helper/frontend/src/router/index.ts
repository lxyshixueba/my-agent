import { createRouter, createWebHistory } from 'vue-router'
import TravelPlanCreate from '@/views/TravelPlanCreate.vue'

const routes = [
  {
    path: '/',
    name: 'TravelPlanCreate',
    component: TravelPlanCreate,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
