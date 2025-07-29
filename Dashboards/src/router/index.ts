import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '../layouts/DefaultLayout.vue'
import Readiness from '../pages/Readiness.vue'
import Feed from '../pages/Feed.vue'
import Savings from '../pages/Savings.vue'
import Historical from '../pages/Historical.vue'

const routes = [
  {
    path: '/',
    component: DefaultLayout, // 🔹 Wrap all routes in your sidebar layout
    children: [
      { path: '', redirect: '/readiness' },
      { path: 'readiness', name: 'Readiness', component: Readiness },
      { path: 'feed', name: 'Feed', component: Feed },
      { path: 'savings', name: 'Savings', component: Savings },
      { path: 'historical', name: 'Historical', component: Historical },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
