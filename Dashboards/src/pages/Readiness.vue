<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">

      <!-- Main Content Area -->
      <div class="flex-1 p-5 flex flex-col space-y-4 h-full">
        <!-- Header and Year Selector (aligned together) -->
        <div class="flex justify-between items-end">
          <!-- Left: Title + Subtitle aligned to bottom -->
          <div class="flex flex-col justify-end leading-tight">
            <h1 class="text-3xl font-bold">
              <span class="text-sage">Compost</span> Readiness Overview
            </h1>
            <p class="text-sm text-sage mt-1">
              Monitor key indicators like soil condition, temperature and moisture levels to assess compost maturity in real time.
            </p>
          </div>

          <!-- Right: Slicer Buttons -->
          <div class="flex space-x-2">
            <button class="btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
          </div>
        </div>

        <!-- Main Grid Content (Top and Bottom split equally) -->
        <div class="flex flex-1 flex-col gap-4">
          <!-- Top Section: KPI Cards + Line Chart (45% height) -->
          <div class="flex gap-4 h-1/2">
            <!-- 4 KPI Cards in 2x2 grid (Left, 40% width) -->
            <div class="grid grid-cols-2 grid-rows-2 gap-2.5 w-[45%]">
              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full flex flex-col justify-between">
                  <div>
                    <h2 class="card-title text-xs font-semibold">Income</h2>
                    <p class="text-sm font-medium">$163.2K</p>
                  </div>
                  <div class="h-20 mt-3">
                    
                  </div>
                </div>
              </div>

              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full flex flex-col justify-between">
                  <div>
                    <h2 class="card-title text-xs font-semibold">Expenses</h2>
                    <p class="text-sm font-medium">$89.3K</p>
                  </div>
                  <div class="h-20 mt-3">
                    
                  </div>
                </div>
              </div>

              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full flex flex-col justify-between">
                  <div>
                    <h2 class="card-title text-xs font-semibold">Savings</h2>
                    <p class="text-sm font-medium">$90.2K</p>
                  </div>
                  <div class="h-20 mt-3">
                
                  </div>
                </div>
              </div>

              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full flex flex-col justify-between">
                  <div>
                    <h2 class="card-title text-xs font-semibold">Saving %</h2>
                    <p class="text-sm font-medium">55%</p>
                  </div>
                  <div class="h-20 mt-3">
                    
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Line Chart (60% width) -->
            <div class="card bg-sage shadow-b flex-1">
              <div class="card-body h-full p-3 flex flex-col">
                <h2 class="card-title text-xs font-semibold mb-2">Readiness Trend</h2>
                <div class="flex-1 h-full">
                  
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Section: 2 Charts (Expenses 65%, Savings 35%) - 50% height -->
          <div class="flex gap-4 h-1/2">
            <!-- Bottom Section: 2 Doughnut Charts Side by Side in 1 Card -->
            <div class="card bg-sage shadow-b w-[65%]">
              <div class="card-body h-full p-3 flex flex-col">
                <h2 class="card-title text-xs font-semibold mb-2">Feed Composition | Nutrient Balance</h2>
                <div class="flex justify-between items-center flex-1 gap-4">
                  <!-- Doughnut 1 -->
                  <div class="w-1/2 h-full">
                    
                  </div>
                  <!-- Doughnut 2 -->
                  <div class="w-1/2 h-full">
                  
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Savings Bar Chart -->
            <div class="card bg-sage shadow-b w-[35%]">
              <div class="card-body h-full p-3 flex flex-col">
                <h2 class="card-title text-xs font-semibold mb-2">Readiness vs Threshold</h2>
                <div class="flex-1">
                  
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Chart.js for line & doughnut
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'
import { Doughnut } from 'vue-chartjs'
import type { ChartOptions } from 'chart.js'
import VueApexCharts from 'vue3-apexcharts'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement
)

// ECharts for bar + KPI line charts
import { use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer
])

const isCollapsed = ref(true)



</script>


