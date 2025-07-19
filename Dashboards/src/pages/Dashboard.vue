<template>
  <div class="p-6 space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <SummaryCard title="Avg Moisture" :value="45.6" unit="%" />
      <SummaryCard title="Avg CO₂" :value="380" unit="ppm" />
      <SummaryCard title="Forecasted Moisture" :value="47.2" unit="%" />
      <SummaryCard title="Status" :value="statusText" />
    </div>

    <!-- Moisture Chart -->
    <div class="bg-base-100 rounded-xl shadow p-4">
      <h3 class="text-sm font-semibold mb-2">Moisture Trend</h3>
      <MoistureChart :data="moistureData" />
    </div>

    <!-- Lower Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="col-span-2 bg-base-100 rounded-xl shadow p-4 space-y-3">
        <h3 class="text-sm font-semibold">Moisture Forecast</h3>
        <ForecastCard :forecast="forecastValues" />
      </div>
      <div class="bg-base-100 rounded-xl shadow p-4 space-y-3">
        <h3 class="text-sm font-semibold">Compost Status</h3>
        <StatusTag status="Healthy" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SummaryCard from '../components/SummaryCard.vue'
import MoistureChart from '../components/MoistureChart.vue'
import ForecastCard from '../components/ForecastCard.vue'
import StatusTag from '../components/StatusTag.vue'
const statusText = 'Healthy'

const moistureData = [
  { timestamp: '2025-07-01', value: 43 },
  { timestamp: '2025-07-02', value: 44 },
  { timestamp: '2025-07-03', value: 46 },
  { timestamp: '2025-07-04', value: 45 },
  { timestamp: '2025-07-05', value: 47 }
]

const forecastValues = [46, 47, 48, 49, 50]
</script>
