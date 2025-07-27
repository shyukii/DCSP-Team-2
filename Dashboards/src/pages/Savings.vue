<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">
      <div class="flex-1 p-5 flex flex-col space-y-4 h-full">

        <!-- Header -->
        <div class="flex justify-between items-end">
          <div class="flex flex-col justify-end leading-tight">
            <h1 class="text-3xl font-bold">
              <span class="text-sage">CO₂</span> Savings Impact
            </h1>
            <p class="text-sm text-sage mt-1">
              Track estimated CO₂ reduction through composting efforts and monitor your sustainability impact.
            </p>
          </div>
          <div class="flex space-x-2">
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition">Slicer</button>
          </div>
        </div>

        <!-- KPI Cards -->
        <div class="grid grid-cols-4 gap-4">
          <div class="card bg-sage shadow-b p-4 h-32">
            <h2 class="text-xs font-semibold">Total Savings</h2>
            <p class="text-sm font-medium">24.6 kg</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-32">
            <h2 class="text-xs font-semibold">Avg Moisture</h2>
            <p class="text-sm font-medium">68%</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-32">
            <h2 class="text-xs font-semibold">Temp Drop</h2>
            <p class="text-sm font-medium">1.8°C</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-32">
            <h2 class="text-xs font-semibold">Bins Active</h2>
            <p class="text-sm font-medium">3</p>
          </div>
        </div>

        <!-- Line Chart -->
        <div class="card bg-sage shadow-b flex-1 p-4">
          <h2 class="text-sm font-semibold mb-2">Moisture Over Time</h2>
          <VueApexCharts
            type="line"
            height="260"
            :options="lineChartOptions"
            :series="lineChartSeries"
          />
        </div>

        <!-- Bottom Row: Pie & Bar -->
        <div class="flex gap-4 h-[35%]">
          <!-- Pie -->
          <div class="card bg-sage shadow-b w-1/2 p-4">
            <h2 class="text-sm font-semibold mb-2">Compost Composition</h2>
            <div class="relative w-full h-[230px]"> <!-- 🔸 Adjust height here -->
              <Doughnut :data="pieData" :options="pieOptions" />
            </div>
          </div>

          <!-- Bar -->
          <div class="card bg-sage shadow-b w-1/2 p-4">
            <h2 class="text-sm font-semibold mb-2">CO₂ Reduction by Month</h2>
            <VChart :option="barOptions" class="h-full" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { Doughnut } from 'vue-chartjs'
import VChart from 'vue-echarts'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

// Line Chart (Apex)
const lineChartOptions = ref({
  chart: {
    type: 'line',
    toolbar: { show: false },
    zoom: { enabled: false },
    background: 'transparent',
    fontFamily: 'inherit'
  },
  grid: { borderColor: 'rgba(255, 255, 255, 0.05)' },
  xaxis: {
    categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    labels: { style: { colors: '#B2D2FB' } }
  },
  yaxis: {
    min: 0,
    max: 100,
    labels: { style: { colors: '#B2D2FB' } }
  },
  stroke: { curve: 'smooth', width: 2, colors: ['#B0C2F2'] },
  colors: ['#B0C2F2'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.15,
      opacityTo: 0,
      stops: [0, 100]
    }
  },
  markers: {
    size: 4,
    colors: ['#B0C2F2'],
    strokeColors: '#fff',
    hover: { size: 6 }
  },
  tooltip: { theme: 'dark' }
})

const lineChartSeries = ref([
  { name: 'Moisture (%)', data: [60, 75, 88, 94] }
])

// Pie Chart (Chart.js)
const pieData = {
  labels: ['Greens', 'Browns', 'Others'],
  datasets: [
    {
      label: 'Feed Ratio',
      data: [40, 35, 25],
      backgroundColor: ['#B2D2FB', '#6699D8', '#4971A5'],
      borderWidth: 0
    }
  ]
}

import type { ChartOptions } from 'chart.js'

const pieOptions: ChartOptions<'doughnut'> = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#B2D2FB',
        boxWidth: 6,
        font: { size: 12 }
      }
    }
  }
}

// Bar Chart (ECharts)
const barOptions = {
  tooltip: {},
  xAxis: {
    type: 'category',
    data: ['Apr', 'May', 'Jun', 'Jul'],
    axisLabel: { color: '#B2D2FB' },
    axisLine: { show: false },       // ⛔️ hide axis line
    axisTick: { show: false },       // ⛔️ hide ticks
    splitLine: { show: false }       // ⛔️ hide grid lines
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#B2D2FB' },
    axisLine: { show: false },       // ⛔️ hide axis line
    axisTick: { show: false },       // ⛔️ hide ticks
    splitLine: { show: false }       // ⛔️ hide grid lines
  },
  series: [
    {
      name: 'CO₂ Reduced (kg)',
      type: 'bar',
      data: [4.5, 6.2, 5.1, 7.3],
      itemStyle: {
        color: '#AACEFE',
        borderRadius: 4
      }
    }
  ],
  grid: { top: 20, bottom: 20, left: 40, right: 40 }
}
</script>
