import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import PredictView from '../views/PredictView.vue'
import TrainingView from '../views/TrainingView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: PredictView
  },
  {
    path: '/training',
    name: 'training',
    component: TrainingView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
