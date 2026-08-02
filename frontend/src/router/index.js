import { createRouter, createWebHistory } from 'vue-router'
import MapView from '../views/MapView.vue'
import StatsView from '../views/StatsView.vue'

const routes = [
  { path: '/', name: 'map', component: MapView },
  { path: '/stats', name: 'stats', component: StatsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router