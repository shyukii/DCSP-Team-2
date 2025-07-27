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
            <button class="btn bg-sage hover:bg-[#B2D2FB]/25 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#B2D2FB]/25 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#B2D2FB]/25 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-sage hover:bg-[#B2D2FB]/25 border-transparent text-white px-10 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
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
                    <VChart :option="miniLineOptions1" autoresize class="w-full h-full" />
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
                    <VChart :option="miniLineOptions2" autoresize class="w-full h-full" />
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
                    <VChart :option="miniLineOptions3" autoresize class="w-full h-full" />
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
                    <VChart :option="miniLineOptions4" autoresize class="w-full h-full" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Line Chart (60% width) -->
            <div class="card bg-sage shadow-b flex-1">
              <div class="card-body h-full p-3 flex flex-col">
                <h2 class="card-title text-xs font-semibold mb-2">Readiness Trend</h2>
                <div class="flex-1 h-full">
                  <VueApexCharts type="area" height="100%" :options="lineChartOptions" :series="lineChartSeries" />
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
                    <Doughnut :data="doughnutData1" :options="doughnutOptions" />
                  </div>
                  <!-- Doughnut 2 -->
                  <div class="w-1/2 h-full">
                    <Doughnut :data="doughnutData2" :options="doughnutOptions" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Savings Bar Chart -->
            <div class="card bg-sage shadow-b w-[35%]">
              <div class="card-body h-full p-3 flex flex-col">
                <h2 class="card-title text-xs font-semibold mb-2">Readiness vs Threshold</h2>
                <div class="flex-1">
                  <VChart class="w-full h-full" :option="echartsOptions" autoresize />
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


// =======================
// 📊 Chart Data
// =======================

const lineChartSeries = [
  {
    name: 'Readiness %',
    data: [55, 30, 68, 86]
  }
]

// Doughnut Chart: Feed Composition
const doughnutData1 = {
  labels: ['Greens', 'Browns', 'Others'],
  datasets: [{
    data: [40, 45, 15],
    backgroundColor: ['#ABC1F0', '#6797DF', '#4971A5'],
    borderWidth: 0
  }]
}

const doughnutData2 = {
  labels: ['Nitrogen', 'Phosphorus', 'Potassium'],
  datasets: [{
    data: [30, 45, 25],
    backgroundColor: ['#ABC1F0', '#6797DF', '#4971A5'],
    borderWidth: 0
  }]
}

// ✅ ECharts Mini Line Area Charts for KPI cards
const baseMiniLineOption = {
  grid: { top: 0, left: 0, right: 0, bottom: 0 },
  xAxis: { type: 'category', show: false, data: ['1', '2', '3', '4'] },
  yAxis: { type: 'value', show: false, min: 0, max: 100 },
  tooltip: { show: false },
  series: [{
    type: 'line',
    data: [],
    step: 'end',
    areaStyle: { color: 'rgba(176, 194, 242, 0.15)' },
    lineStyle: { color: '#ffffff', width: 2 },
    symbol: 'none'
  }]
}

function cloneMiniLine(data: number[]) {
  return {
    ...baseMiniLineOption,
    series: [{
      ...baseMiniLineOption.series[0],
      data
    }]
  }
}

const miniLineOptions1 = cloneMiniLine([10, 10, 70, 70])
const miniLineOptions2 = cloneMiniLine([90, 85, 65, 60])
const miniLineOptions3 = cloneMiniLine([40, 55, 75, 90])
const miniLineOptions4 = cloneMiniLine([20, 30, 45, 55])

// ECharts Bar Chart (Readiness vs Threshold with overlap)
const echartsOptions = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  legend: {
    textStyle: { color: '#ffffff' },
    top: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Tank 1', 'Tank 2'],
    axisLabel: { color: '#ffffff' },
    axisLine: { lineStyle: { color: '#212C42' } }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#ffffff' },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    axisLine: { lineStyle: { color: '#ffffff' } }
  },
  series: [
    {
      name: 'Threshold',
      type: 'bar',
      data: [80, 85],
      barGap: '-75%', // ✅ true overlap
      barWidth: 100,
      itemStyle: { color: '#ABC1F0' }
    },
    {
      name: 'Readiness',
      type: 'bar',
      data: [60, 70],
      barWidth: 100,
      itemStyle: { color: '#4A70A1' }
    }
  ]
}

// =======================
// ⚙️ Chart.js + Apex Options
// =======================

const lineChartOptions = {
  chart: {
    type: 'area',
    toolbar: { show: false },
    zoom: { enabled: false },
    foreColor: '#ffffff',
    offsetX: 10,
    offsetY: 10,
    parentHeightOffset: 0 // ✅ prevents clipping
  },
  stroke: {
    curve: 'smooth',
    width: 3,
    colors: ['#ffffff']
  },
  fill: {
    type: 'solid',
    opacity: 0.15,
    colors: ['#B0C2F2']
  },
  xaxis: {
    categories: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    tickPlacement: 'on', // aligns point with label center
    labels: {
      style: { colors: '#ffffff' },
      offsetX: 0
    },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: {
    min: 0,
    show: false
  },
  grid: {
    padding: {
      left: 20,
      right: 15,
      top: 0,
      bottom: 0
    },
    show: false
  },
  dataLabels: {
    enabled: false
  },
  markers: {
    size: 0
  },
  tooltip: {
    enabled: true,
    shared: false,
    theme: 'dark',
    style: {
      fontSize: '12px'
    },
    marker: {
      show: false
    }
  }
}

const doughnutOptions: ChartOptions<'doughnut'> = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  layout: {
    padding: {
      top: 0,
      bottom: 20,
      left: 0,
      right: 0
    }
  },
  plugins: {
    legend: {
      position: 'right',
      labels: { color: '#ffffff' }
    }
  }
}

const miniLineOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  elements: {
    line: { tension: 0 },
    point: { radius: 0 }
  },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false }
  },
  scales: {
    x: { display: false },
    y: {
      display: false,
      min: 0,
      max: 100
    }
  }
}
</script>


