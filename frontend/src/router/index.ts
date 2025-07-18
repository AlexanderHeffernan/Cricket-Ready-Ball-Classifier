import { createRouter, createWebHistory } from 'vue-router'
import PredictView from '../views/PredictView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: PredictView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router