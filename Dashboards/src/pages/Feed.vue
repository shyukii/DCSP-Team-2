<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="flex-1 flex flex-col p-5 space-y-4">
      <!-- Header Section -->
      <div class="flex justify-between items-end">
        <div>
          <h1 class="text-3xl font-bold">
            <span class="text-sage">Compost</span> Feed Insights
          </h1>
          <p class="text-sage text-sm mt-1">
            Track feedstock usage, nutrient breakdown, and composting impact across time.
          </p>
        </div>

        <!-- Right: Slicer Buttons -->
        <div class="flex space-x-2">
          <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
        </div>
      </div>

      <!-- Body Section: Left (metrics & charts) + Right (table) -->
      <div class="flex flex-1 gap-4">
        <!-- Left: 50% Width -->
        <div class="flex flex-col w-1/2 space-y-3">
          <!-- Top Row: 3 KPI Cards -->
          <div class="flex gap-2.5">
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Feed Volume</h2>
              <p class="text-2xl font-bold">1.2T</p>
              <apexchart type="bar" height="40" :options="miniBarOptions" :series="miniBarSeries" />
            </div>
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Avg EC Level</h2>
              <p class="text-2xl font-bold">3.4 dS/m</p>
              <apexchart type="bar" height="40" :options="miniBarOptions" :series="miniBarSeries" />
            </div>
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Moisture</h2>
              <p class="text-2xl font-bold">68%</p>
              <apexchart type="bar" height="40" :options="miniBarOptions" :series="miniBarSeries" />
            </div>
          </div>

          <!-- Middle Card: Bar Chart -->
          <div class="card bg-sage shadow-b flex-1 p-4">
            <h2 class="text-sm font-semibold mb-2">Feed Comparison by Source</h2>
            <VChart :option="comparisonBarOptions" class="h-full" />
          </div>

          <!-- Bottom Card: Circular Segments -->
          <div class="card bg-sage shadow-b flex-1 p-4 grid grid-cols-3 gap-4 items-center">
            <apexchart type="radialBar" height="120" :options="gaugeOptions('Household')" :series="[43]" />
            <apexchart type="radialBar" height="120" :options="gaugeOptions('Commercial')" :series="[69]" />
            <apexchart type="radialBar" height="120" :options="gaugeOptions('Self')" :series="[9]" />
          </div>
        </div>

        <!-- Right: Table Placeholder -->
        <div class="w-1/2 flex flex-col">
          <div class="card bg-sage shadow-b flex-1 p-4">
            <h2 class="text-sm font-semibold mb-2">Feed Subcategories</h2>
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="text-khaki/70 border-b border-khaki/30">
                  <th class="py-2">Subcategory</th>
                  <th class="py-2">Value</th>
                  <th class="py-2">Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableData" :key="row.label" class="border-b border-khaki/30">
                  <td class="py-2">{{ row.label }}</td>
                  <td class="py-2 font-semibold">{{ row.value }}kg</td>
                  <td class="py-2 w-[120px]">
                    <apexchart type="bar" height="40" :options="miniBarOptions" :series="[{ data: row.trend }]" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ApexCharts from 'vue3-apexcharts'
import VChart from 'vue-echarts'

const miniBarOptions = {
  chart: { type: 'bar', sparkline: { enabled: true } },
  colors: ['#9C7BF9'],
  plotOptions: {
    bar: { columnWidth: '70%', borderRadius: 2 }
  },
  tooltip: { enabled: false },
  xaxis: { labels: { show: false } },
  yaxis: { show: false }
}

const miniBarSeries = [
  { data: [1, 2, 3, 2, 4, 5, 4] }
]

const comparisonBarOptions = {
  tooltip: {},
  legend: { data: ['Greens', 'Browns'] },
  xAxis: {
    type: 'category',
    data: ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Greens',
      type: 'bar',
      data: [120, 200, 150, 80],
      itemStyle: { color: '#9C7BF9' }
    },
    {
      name: 'Browns',
      type: 'bar',
      data: [90, 180, 110, 60],
      itemStyle: { color: '#F6C2EF' }
    }
  ]
}

const gaugeOptions = (label: string) => ({
  chart: { type: 'radialBar' },
  plotOptions: {
    radialBar: {
      hollow: { size: '60%' },
      dataLabels: {
        name: { show: true, fontSize: '12px', offsetY: -10 },
        value: { fontSize: '16px', offsetY: 5 }
      }
    }
  },
  labels: [label],
  colors: ['#9C7BF9']
})

const tableData = [
  { label: 'Fruit Waste', value: 120, trend: [5, 6, 7, 5, 8, 9] },
  { label: 'Leaves', value: 95, trend: [3, 5, 6, 4, 5, 7] },
  { label: 'Vegetable Scraps', value: 80, trend: [4, 4, 6, 5, 7, 6] },
  { label: 'Paper Shreds', value: 60, trend: [2, 3, 4, 3, 4, 5] }
]
</script>