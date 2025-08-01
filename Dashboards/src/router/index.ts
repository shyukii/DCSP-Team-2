import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '../layouts/DefaultLayout.vue'
import Savings from '../pages/Savings.vue'
import PlantMoisture from '../pages/PlantMoisture.vue'
import SoilEC from '../pages/SoilEC.vue'

const routes = [
  {
    path: '/',
    component: DefaultLayout, // 🔹 Wrap all routes in your sidebar layout
    children: [
      { path: '', redirect: '/savings' },
      { path: 'savings', name: 'Savings', component: Savings },
      { path: 'plant-moisture', name: 'PlantMoisture', component: PlantMoisture },
      { path: 'soil-ec', name: 'SoilEC', component: SoilEC },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
