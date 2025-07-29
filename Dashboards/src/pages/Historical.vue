<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100 p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-deepgreen mb-2">Historical Sensor Data</h1>
      <p class="text-gray-600">Monitor 10 months of EC and moisture level trends</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Active Devices</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.active_devices || '--' }}</p>
          </div>
          <i class="fas fa-microchip text-2xl text-green-500"></i>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Active Sensors</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.active_sensors || '--' }}</p>
          </div>
          <i class="fas fa-thermometer-half text-2xl text-blue-500"></i>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Locations</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.total_locations || '--' }}</p>
          </div>
          <i class="fas fa-map-marker-alt text-2xl text-purple-500"></i>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Today's Readings</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.readings_today || '--' }}</p>
          </div>
          <i class="fas fa-chart-line text-2xl text-orange-500"></i>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
      <h3 class="text-lg font-semibold mb-4 text-gray-800">Filters</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Sensor Type</label>
          <select v-model="selectedSensorType" @change="fetchData" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
            <option value="">All Sensors</option>
            <option value="EC">EC (Electrical Conductivity)</option>
            <option value="moisture">Moisture</option>
            <option value="electrical_conductivity">Electrical Conductivity</option>
            <option value="soil_moisture">Soil Moisture</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Device</label>
          <select v-model="selectedDevice" @change="fetchData" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
            <option value="">All Devices</option>
            <option v-for="device in devices" :key="device.device_id" :value="device.device_id">
              {{ device.device_name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
          <select v-model="selectedMonths" @change="fetchData" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent">
            <option value="1">Last Month</option>
            <option value="3">Last 3 Months</option>
            <option value="6">Last 6 Months</option>
            <option value="10">Last 10 Months</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- EC Levels Chart -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">EC Levels Over Time</h3>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <span class="text-sm text-gray-600">Electrical Conductivity</span>
          </div>
        </div>
        <div class="h-64">
          <canvas ref="ecChart"></canvas>
        </div>
      </div>

      <!-- Moisture Levels Chart -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Moisture Levels Over Time</h3>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span class="text-sm text-gray-600">Soil Moisture</span>
          </div>
        </div>
        <div class="h-64">
          <canvas ref="moistureChart"></canvas>
        </div>
      </div>
    </div>

    <!-- ML Prediction Placeholder -->
    <div class="bg-gradient-to-r from-green-500 to-blue-500 rounded-xl shadow-lg p-8 text-white mb-8">
      <div class="text-center">
        <i class="fas fa-robot text-4xl mb-4 opacity-80"></i>
        <h3 class="text-2xl font-bold mb-2">AI Predictions Coming Soon</h3>
        <p class="text-green-100 mb-6">Machine Learning models are being trained to provide 3-month forecasts for EC and moisture levels</p>
        <div class="flex items-center justify-center space-x-4">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span class="text-sm">Training ML Models</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-200"></div>
            <span class="text-sm">Analyzing Patterns</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-400"></div>
            <span class="text-sm">Preparing Forecasts</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Data Table -->
    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800">Recent Sensor Readings</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Device</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sensor Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="reading in recentReadings" :key="`${reading.timestamp}-${reading.sensor_type}`" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDate(reading.timestamp) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ reading.device_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                      :class="getSensorTypeColor(reading.sensor_type)">
                  {{ reading.sensor_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ reading.value }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ reading.location_name }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 flex items-center space-x-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
        <span class="text-gray-700">Loading sensor data...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

// TypeScript interfaces
interface Stats {
  active_devices?: number
  active_sensors?: number
  total_locations?: number
  readings_today?: number
}

interface Device {
  device_id: number
  device_name: string
  description?: string
  status?: string
}

interface SensorReading {
  timestamp: string
  device_name: string
  sensor_type: string
  value: number
  location_name: string
}

interface PredictionDataPoint {
  date: string
  avgValue: number
  minValue: number
  maxValue: number
  readingsCount: number
}

// Reactive data
const loading = ref(false)
const stats = ref<Stats>({})
const devices = ref<Device[]>([])
const recentReadings = ref<SensorReading[]>([])
const predictionData = ref<Record<string, PredictionDataPoint[]>>({})

// Filter states
const selectedSensorType = ref('')
const selectedDevice = ref('')
const selectedMonths = ref('10')

// Chart instances
const ecChart = ref<HTMLCanvasElement | null>(null)
const moistureChart = ref<HTMLCanvasElement | null>(null)
let ecChartInstance: Chart | null = null
let moistureChartInstance: Chart | null = null

// API Base URL
const API_BASE = 'http://localhost:3001/api'

// Fetch all data
const fetchData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStats(),
      fetchDevices(),
      fetchHistoricalData(),
      fetchPredictionData()
    ])
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

// Fetch dashboard stats
const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/dashboard/stats`)
    const data = await response.json()
    if (data.success && data.stats) {
      stats.value = data.stats
    }
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

// Fetch devices
const fetchDevices = async () => {
  try {
    const response = await fetch(`${API_BASE}/devices`)
    const data = await response.json()
    if (data.success && Array.isArray(data.data)) {
      devices.value = data.data
    }
  } catch (error) {
    console.error('Error fetching devices:', error)
  }
}

// Fetch historical data
const fetchHistoricalData = async () => {
  try {
    const params = new URLSearchParams({
      months: selectedMonths.value,
      ...(selectedSensorType.value && { sensorType: selectedSensorType.value }),
      ...(selectedDevice.value && { deviceId: selectedDevice.value })
    })

    const response = await fetch(`${API_BASE}/historical-data?${params}`)
    const data = await response.json()
    if (data.success && Array.isArray(data.data)) {
      recentReadings.value = data.data.slice(0, 20) // Show latest 20 readings
    }
  } catch (error) {
    console.error('Error fetching historical data:', error)
  }
}

// Fetch prediction data
const fetchPredictionData = async () => {
  try {
    const response = await fetch(`${API_BASE}/prediction-data`)
    const data = await response.json()
    if (data.success && data.data) {
      predictionData.value = data.data
      await nextTick()
      createCharts()
    }
  } catch (error) {
    console.error('Error fetching prediction data:', error)
  }
}

// Create charts
const createCharts = () => {
  createECChart()
  createMoistureChart()
}

// Create EC chart
const createECChart = () => {
  if (ecChartInstance) {
    ecChartInstance.destroy()
  }

  const ctx = ecChart.value?.getContext('2d')
  if (!ctx) return

  const ecData = predictionData.value['Soil EC'] || []
  
  ecChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ecData.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [{
        label: 'Soil EC Level',
        data: ecData.map(item => item.avgValue),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

// Create moisture chart
const createMoistureChart = () => {
  if (moistureChartInstance) {
    moistureChartInstance.destroy()
  }

  const ctx = moistureChart.value?.getContext('2d')
  if (!ctx) return

  const moistureData = predictionData.value['Soil Moisture'] || []
  
  moistureChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: moistureData.map(item => new Date(item.date).toLocaleDateString()),
      datasets: [{
        label: 'Soil Moisture Level',
        data: moistureData.map(item => item.avgValue),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

// Utility functions
const formatDate = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString()
}

const getSensorTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    'EC': 'bg-green-100 text-green-800',
    'moisture': 'bg-blue-100 text-blue-800',
    'electrical_conductivity': 'bg-green-100 text-green-800',
    'soil_moisture': 'bg-blue-100 text-blue-800'
  }
  return colors[type] || 'bg-gray-100 text-gray-800'
}

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.animation-delay-200 {
  animation-delay: 0.2s;
}

.animation-delay-400 {
  animation-delay: 0.4s;
}
</style>