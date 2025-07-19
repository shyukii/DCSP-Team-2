<template>
  <div class="h-64">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend
)

const props = defineProps<{
  data: { timestamp: string; value: number }[]
}>()

/**
 * Build reactive chart data.
 */
const chartData = computed(() => ({
  labels: props.data.map(d => d.timestamp),
  datasets: [
    {
      label: 'Moisture (%)',
      data: props.data.map(d => d.value),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.25)',
      fill: true,
      tension: 0.3,
      pointRadius: 3
    }
  ]
}))

/**
 * Chart options with correct typing.
 */
import type { ChartOptions } from 'chart.js'

const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    x: {
      ticks: { color: '#9ca3af' },
      grid: { display: false }
    },
    y: {
      ticks: { color: '#9ca3af' },
      grid: { color: 'rgba(0,0,0,0.05)' }
    }
  }
}
</script>
