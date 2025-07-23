import { createRouter, createWebHistory } from 'vue-router'
import Readiness from '../pages/Readiness.vue'
import Feed from '../pages/Feed.vue'
import Savings from '../pages/Savings.vue'

const routes = [
  { path: '/readiness', name: 'Readiness', component: Readiness },
  { path: '/feed', name: 'Feed', component: Feed },
  { path: '/savings', name: 'Savings', component: Savings },
  { path: '/', redirect: '/readiness' } // optional: default route
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
