<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">
      <!-- Main Content Area -->
      <div class="flex-1 p-5 flex flex-col space-y-4 h-full">
        <!-- Header and User Selector -->
        <div class="flex justify-between items-end">
          <!-- Left: Title + Subtitle -->
          <div class="flex flex-col justify-end leading-tight">
            <h1 class="text-3xl font-bold">
              <span class="text-sage">Soil EC</span> Monitoring
            </h1>
            <p class="text-sm text-sage mt-1">
              Track electrical conductivity levels and predict compost readiness with ML-powered forecasting.
            </p>
          </div>

          <!-- Right: User Selector Dropdown -->
          <div class="flex space-x-2 items-end">
            <select 
              v-model="selectedUser" 
              @change="onUserChange"
              class="bg-sage hover:bg-[#5E936C] border-transparent text-white px-6 py-2 text-sm rounded-md transition-all duration-300 ease-in-out border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 transform hover:scale-105 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer appearance-none bg-no-repeat bg-right pr-10"
              :style="{ 
                backgroundSize: '1rem'
              }"
            >
              <option value="" class="bg-deepgreen text-cream">Choose a user...</option>
              <optgroup label="Users with EC Data" v-if="usersWithData.length > 0" class="bg-deepgreen text-cream">
                <option 
                  v-for="user in usersWithData" 
                  :key="user.username" 
                  :value="user.username"
                  class="bg-deepgreen text-cream"
                >
                  {{ user.username }} ({{ user.ecLogsCount }} readings)
                </option>
              </optgroup>
              <optgroup label="Users without EC Data" v-if="usersWithoutData.length > 0" class="bg-deepgreen text-cream">
                <option 
                  v-for="user in usersWithoutData" 
                  :key="user.username" 
                  :value="user.username"
                  class="bg-deepgreen text-cream"
                >
                  {{ user.username }} (No data yet)
                </option>
              </optgroup>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div class="text-sage text-xl">⚡ Loading soil EC data...</div>
        </div>

        <!-- No User Selected -->
        <div v-else-if="!selectedUser" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="text-sage text-6xl mb-4">🧪</div>
            <div class="text-sage text-xl mb-2">Select a user to view soil EC monitoring</div>
            <div class="text-cream text-sm">Choose from the dropdown above to see EC trends and predictions</div>
          </div>
        </div>

        <!-- No Data Available -->
        <div v-else-if="!hasData" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="text-sage text-6xl mb-4">📊</div>
            <div class="text-sage text-xl mb-2">No soil EC data available</div>
            <div class="text-cream text-sm">{{ selectedUser }} hasn't taken any EC readings yet</div>
          </div>
        </div>

        <!-- Dashboard Content -->
        <div v-else class="flex-1 grid grid-cols-12 gap-4 min-h-0">
          <!-- Current Status Cards -->
          <div class="col-span-12 lg:col-span-4 space-y-4">
            <!-- Current EC Level -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-cream">{{ getStatusEmoji(currentEC) }} Current EC Level</span>
              </div>
              <div class="text-3xl font-bold text-white mb-1">{{ currentEC }} mS/cm</div>
              <div class="text-cream text-sm">{{ getECStatus(currentEC) }}</div>
              <div class="w-full bg-deepgreen rounded-full h-2 mt-2">
                <div 
                  :class="getECBarColor(currentEC)"
                  class="h-2 rounded-full transition-all duration-500"
                  :style="`width: ${Math.min((currentEC / 5) * 100, 100)}%`"
                ></div>
              </div>
            </div>

            <!-- Readiness Status -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-cream">🎯 Compost Readiness</span>
              </div>
              <div class="text-lg font-bold text-white mb-1">{{ getReadinessText(readinessStatus) }}</div>
              <div class="text-cream text-sm" v-if="estimatedReadyDays">
                ~{{ estimatedReadyDays }} days to ready
              </div>
              <div class="text-cream text-sm" v-else>
                Monitoring progress
              </div>
            </div>

            <!-- Alert Section -->
            <div v-if="alertLevel && alertLevel !== 'none'" :class="getAlertCardClass(alertLevel)" class="p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-white">{{ getAlertIcon(alertLevel) }} Alert</span>
              </div>
              <div class="text-white text-sm">{{ alertMessage }}</div>
            </div>

            <!-- Health Score -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-cream">💚 Health Score</span>
              </div>
              <div class="text-2xl font-bold text-white mb-1">{{ averageHealthScore }}/100</div>
              <div class="text-cream text-sm">{{ getHealthDescription(averageHealthScore) }}</div>
            </div>

            <!-- Care Recommendations -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-cream">💡 Recommendations</span>
              </div>
              <div class="text-cream text-sm leading-relaxed">
                {{ primaryRecommendation }}
              </div>
            </div>
          </div>

          <!-- EC Timeline Chart -->
          <div class="col-span-12 lg:col-span-8">
            <div class="bg-sage rounded-lg p-4 h-full flex flex-col">
              <div class="flex items-center justify-between mb-4">
                <span class="text-sm font-medium text-cream">📈 EC Trend & Predictions</span>
                <div class="flex space-x-2">
                  <span class="text-xs text-cream bg-blue-500 px-2 py-1 rounded">Historical</span>
                  <span class="text-xs text-cream bg-green-500 px-2 py-1 rounded">Predicted</span>
                  <span class="text-xs text-cream bg-red-500 px-2 py-1 rounded">Optimal Range</span>
                </div>
              </div>
              <div class="flex-1 min-h-0">
                <canvas ref="ecChart" class="w-full h-full"></canvas>
              </div>
            </div>
          </div>

          <!-- Statistics Summary -->
          <div class="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold">{{ totalReadings }}</div>
              <div class="text-cream text-sm">Total Readings</div>
            </div>
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold">{{ averageEC }} mS/cm</div>
              <div class="text-cream text-sm">Average EC</div>
            </div>
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold">{{ averageMoisture }}%</div>
              <div class="text-cream text-sm">Average Moisture</div>
            </div>
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold" v-if="predictionsData.timeline">{{ predictionsData.timeline.week_1 || '--' }}</div>
              <div class="text-2xl text-white font-bold" v-else>--</div>
              <div class="text-cream text-sm">7-Day Forecast</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(...registerables)

export default {
  name: 'SoilEC',
  setup() {
    const selectedUser = ref('')
    const loading = ref(false)
    const hasData = ref(false)
    const usersWithData = ref([])
    const usersWithoutData = ref([])
    const ecChart = ref(null)
    const chartInstance = ref(null)
    
    // Dashboard data
    const currentEC = ref(0)
    const currentMoisture = ref(0)
    const totalReadings = ref(0)
    const averageEC = ref(0)
    const averageMoisture = ref(0)
    const averageHealthScore = ref(0)
    const currentStatus = ref('Unknown')
    const readinessStatus = ref('Unknown')
    const estimatedReadyDays = ref(null)
    const primaryRecommendation = ref('Continue monitoring')
    const alertLevel = ref('none')
    const alertMessage = ref('')
    const ecHistory = ref([])
    const predictionsData = ref({})

    // API configuration
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

    const getStatusEmoji = (ec) => {
      if (ec >= 1.5 && ec <= 3.0) return '✅'
      if ((ec >= 1.0 && ec < 1.5) || (ec > 3.0 && ec <= 4.0)) return '⚠️'
      return '🚨'
    }

    const getECStatus = (ec) => {
      if (ec >= 1.5 && ec <= 3.0) return 'Optimal range'
      if (ec < 1.0) return 'Low - building nutrients'
      if (ec < 1.5) return 'Building up'
      if (ec <= 4.0) return 'High - stabilizing'
      return 'Very high - needs attention'
    }

    const getECBarColor = (ec) => {
      if (ec >= 1.5 && ec <= 3.0) return 'bg-green-400'
      if ((ec >= 1.0 && ec < 1.5) || (ec > 3.0 && ec <= 4.0)) return 'bg-yellow-400'
      return 'bg-red-400'
    }

    const getReadinessText = (status) => {
      switch (status) {
        case 'ready_soon': return 'Ready Soon!'
        case 'short_term': return 'Short Term'
        case 'medium_term': return 'Medium Term'
        case 'long_term': return 'Long Term'
        case 'needs_attention': return 'Needs Attention'
        default: return 'Monitoring'
      }
    }

    const getAlertIcon = (level) => {
      switch (level) {
        case 'critical': return '🚨'
        case 'warning': return '⚠️'
        case 'info': return 'ℹ️'
        default: return '📢'
      }
    }

    const getAlertCardClass = (level) => {
      switch (level) {
        case 'critical': return 'bg-red-600'
        case 'warning': return 'bg-orange-600'
        case 'info': return 'bg-blue-600'
        default: return 'bg-gray-600'
      }
    }

    const getHealthDescription = (score) => {
      if (score >= 85) return 'Excellent conditions'
      if (score >= 70) return 'Good health'
      if (score >= 50) return 'Fair condition'
      return 'Needs attention'
    }

    const loadUsers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/soil-ec-users`)
        if (response.ok) {
          const result = await response.json()
          if (result.success && result.data) {
            usersWithData.value = result.data.usersWithData || []
            usersWithoutData.value = result.data.usersWithoutData || []
          } else {
            usersWithData.value = []
            usersWithoutData.value = []
          }
        } else {
          console.error('Failed to load users:', response.status, response.statusText)
          usersWithData.value = []
          usersWithoutData.value = []
        }
      } catch (error) {
        console.error('Error loading users:', error)
        usersWithData.value = []
        usersWithoutData.value = []
      }
    }

    const loadUserData = async (username) => {
      if (!username) return

      loading.value = true
      hasData.value = false

      try {
        // Load EC data
        const response = await fetch(`${API_BASE_URL}/user/${username}/soil-ec`)
        if (response.ok) {
          const result = await response.json()
          
          if (result.success && result.hasData && result.data && result.data.ecLogs && result.data.ecLogs.length > 0) {
            const data = result.data
            hasData.value = true
            currentEC.value = data.currentEC || 0
            currentMoisture.value = data.currentMoisture || 0
            totalReadings.value = data.totalReadings || 0
            averageEC.value = data.averageEC || 0
            averageMoisture.value = data.averageMoisture || 0
            averageHealthScore.value = data.averageHealthScore || 0
            currentStatus.value = data.currentStatus
            readinessStatus.value = data.readinessStatus
            estimatedReadyDays.value = data.estimatedReadyDays
            primaryRecommendation.value = data.primaryRecommendation
            alertLevel.value = data.alertLevel
            alertMessage.value = data.alertMessage
            ecHistory.value = data.ecLogs || []
            
            // Load predictions
            const predResponse = await fetch(`${API_BASE_URL}/user/${username}/ec-predictions`)
            if (predResponse.ok) {
              const predResult = await predResponse.json()
              if (predResult.success && predResult.data) {
                predictionsData.value = predResult.data
                
                console.log('EC Predictions loaded:', {
                  forecasts: predictionsData.value.forecasts?.length || 0,
                  timeline: predictionsData.value.timeline
                })
              }
            }
            
            // Update chart after data is loaded
            await nextTick()
            setTimeout(() => {
              updateChart()
            }, 100)
          }
        }
      } catch (error) {
        console.error('Error loading user data:', error)
      } finally {
        loading.value = false
      }
    }

    const updateChart = () => {
      if (!ecChart.value) {
        console.warn('Chart canvas not available yet')
        return
      }

      // Destroy existing chart
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }

      const ctx = ecChart.value.getContext('2d')
      
      // Prepare historical data
      const historicalData = ecHistory.value.map(log => ({
        x: new Date(log.created_at),
        y: log.ec
      }))

      // Prepare prediction data
      const predictionData = (predictionsData.value.forecasts || []).map(pred => ({
        x: new Date(pred.date),
        y: pred.predicted_ec
      }))

      console.log('Chart data:', {
        historical: historicalData.length,
        predictions: predictionData.length
      })

      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Historical EC',
              data: historicalData,
              borderColor: '#60A5FA',
              backgroundColor: 'rgba(96, 165, 250, 0.1)',
              tension: 0.4,
              pointRadius: 4,
              pointHoverRadius: 6
            },
            {
              label: 'Predicted EC',
              data: predictionData,
              borderColor: '#4ADE80',
              backgroundColor: 'rgba(74, 222, 128, 0.1)',
              borderDash: [5, 5],
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 5
            },
            {
              label: 'Optimal Range (1.5-3.0)',
              data: [
                { x: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), y: 1.5 },
                { x: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), y: 1.5 }
              ],
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.05)',
              fill: '+1',
              tension: 0,
              pointRadius: 0
            },
            {
              label: 'Optimal Range Upper',
              data: [
                { x: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), y: 3.0 },
                { x: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), y: 3.0 }
              ],
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.05)',
              tension: 0,
              pointRadius: 0
            }
          ]
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
            x: {
              type: 'time',
              time: {
                unit: 'day',
                displayFormats: {
                  day: 'MMM dd'
                }
              },
              grid: {
                color: 'rgba(247, 255, 242, 0.1)'
              },
              ticks: {
                color: '#F7FFF2'
              }
            },
            y: {
              min: 0,
              max: 6,
              grid: {
                color: 'rgba(247, 255, 242, 0.1)'
              },
              ticks: {
                color: '#F7FFF2',
                callback: function(value) {
                  return value + ' mS/cm'
                }
              }
            }
          },
          elements: {
            point: {
              backgroundColor: '#F7FFF2'
            }
          }
        }
      })
    }

    const onUserChange = () => {
      if (selectedUser.value) {
        loadUserData(selectedUser.value)
      } else {
        hasData.value = false
      }
    }

    onMounted(async () => {
      await loadUsers()
      
      // Auto-select user from URL params
      const urlParams = new URLSearchParams(window.location.search)
      const userParam = urlParams.get('user')
      if (userParam && (usersWithData.value.some(u => u.username === userParam) || usersWithoutData.value.some(u => u.username === userParam))) {
        selectedUser.value = userParam
        await loadUserData(userParam)
      }
    })

    return {
      selectedUser,
      loading,
      hasData,
      usersWithData,
      usersWithoutData,
      ecChart,
      currentEC,
      currentMoisture,
      totalReadings,
      averageEC,
      averageMoisture,
      averageHealthScore,
      currentStatus,
      readinessStatus,
      estimatedReadyDays,
      primaryRecommendation,
      alertLevel,
      alertMessage,
      predictionsData,
      getStatusEmoji,
      getECStatus,
      getECBarColor,
      getReadinessText,
      getAlertIcon,
      getAlertCardClass,
      getHealthDescription,
      onUserChange
    }
  }
}
</script>
