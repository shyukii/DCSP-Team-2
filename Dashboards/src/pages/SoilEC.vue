<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">
      <!-- Main Content Area -->
      <div class="flex-1 p-5 flex flex-col space-y-4 h-full">
        <!-- Header and User Selector -->
        <div class="flex justify-between items-end">
          <!-- Left: Title + Subtitle -->
          <div class="flex flex-col justify-end leading-tight relative">
            <div class="absolute -top-2 -left-2 w-8 h-8 bg-sage/20 rounded-full animate-pulse"></div>
            <h1 class="text-4xl font-bold tracking-tight">
              <span class="text-sage">⚡ Soil EC</span> <span class="text-white">Monitoring</span>
            </h1>
            <p class="text-base text-sage mt-2 font-medium">
              Track electrical conductivity levels and predict compost readiness with ML-powered forecasting.
            </p>
            <div class="flex items-center mt-3 space-x-3">
              <div class="flex items-center text-cream text-sm bg-sage/20 px-3 py-1 rounded-full">
                <div class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                Live Monitoring
              </div>
              <div class="flex items-center text-cream text-sm bg-sage/20 px-3 py-1 rounded-full">
                <div class="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                AI Predictions
              </div>
            </div>
          </div>

          <!-- Right: User Selector Dropdown -->
          <div class="flex space-x-2 items-end">
            <select 
              v-model="selectedUser" 
              @change="onUserChange"
              class="bg-gradient-to-r from-sage to-[#4A7856] hover:from-[#5E936C] hover:to-[#4A7856] border-transparent text-white px-6 py-3 text-sm rounded-xl transition-all duration-300 ease-in-out border-none outline-none ring-0 focus:ring-2 focus:ring-sage/50 focus:outline-none focus:border-none hover:border-none h-12 transform hover:scale-105 hover:shadow-xl hover:-translate-y-1 cursor-pointer appearance-none bg-no-repeat bg-right pr-12 shadow-lg backdrop-blur-sm font-semibold"
              :style="{ 
                backgroundImage: 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==)',
                backgroundPosition: 'right 1rem center',
                backgroundSize: '1.2rem'
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
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-cream opacity-90">{{ getStatusEmoji(currentEC) }} Current EC Level</span>
                <div class="w-8 h-8 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-lg">⚡</span>
                </div>
              </div>
              <div class="text-4xl font-bold text-white mb-2 tracking-tight">{{ currentEC }} <span class="text-lg font-normal text-cream/80">mS/cm</span></div>
              <div class="text-cream text-sm mb-3">{{ getECStatus(currentEC) }}</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-3 overflow-hidden">
                <div 
                  :class="getECBarColor(currentEC)"
                  class="h-3 rounded-full transition-all duration-700 ease-out shadow-inner"
                  :style="`width: ${Math.min((currentEC / 5) * 100, 100)}%`"
                ></div>
              </div>
            </div>

            <!-- Readiness Status -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-cream opacity-90">🎯 Compost Readiness</span>
                <div class="w-8 h-8 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-lg">🕐</span>
                </div>
              </div>
              <div class="text-2xl font-bold text-white mb-2">{{ getReadinessText(readinessStatus) }}</div>
              <div class="text-cream text-sm" v-if="estimatedReadyDays">
                <span class="bg-cream/20 px-2 py-1 rounded-full text-xs">~{{ estimatedReadyDays }} days to ready</span>
              </div>
              <div class="text-cream text-sm" v-else>
                <span class="bg-cream/20 px-2 py-1 rounded-full text-xs">Monitoring progress</span>
              </div>
            </div>

            <!-- Alert Section -->
            <div v-if="alertLevel && alertLevel !== 'none'" :class="getAlertCardClass(alertLevel)" class="p-6 rounded-xl shadow-lg border border-red-500/30 transform hover:scale-105 transition-all duration-300 animate-pulse">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-white">{{ getAlertIcon(alertLevel) }} System Alert</span>
                <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <span class="text-lg">⚠️</span>
                </div>
              </div>
              <div class="text-white text-sm leading-relaxed bg-black/20 p-3 rounded-lg">{{ alertMessage }}</div>
            </div>

            <!-- Health Score -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-cream opacity-90">💚 Health Score</span>
                <div class="w-8 h-8 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-lg">📊</span>
                </div>
              </div>
              <div class="text-4xl font-bold text-white mb-2">{{ averageHealthScore }}<span class="text-lg font-normal text-cream/80">/100</span></div>
              <div class="text-cream text-sm mb-3">{{ getHealthDescription(averageHealthScore) }}</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-3 overflow-hidden">
                <div 
                  class="h-3 rounded-full transition-all duration-700 ease-out shadow-inner"
                  :class="averageHealthScore >= 80 ? 'bg-green-400' : averageHealthScore >= 60 ? 'bg-yellow-400' : 'bg-red-400'"
                  :style="`width: ${averageHealthScore}%`"
                ></div>
              </div>
            </div>

            <!-- Care Recommendations -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-semibold text-cream opacity-90">💡 AI Recommendations</span>
                <div class="w-8 h-8 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-lg">🤖</span>
                </div>
              </div>
              <div class="text-cream text-sm leading-relaxed bg-deepgreen/30 p-4 rounded-lg border-l-4 border-yellow-400">
                {{ primaryRecommendation }}
              </div>
            </div>
          </div>

          <!-- EC Timeline Chart -->
          <div class="col-span-12 lg:col-span-8">
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] rounded-xl p-6 h-full flex flex-col shadow-lg border border-sage/20">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <span class="text-xl font-bold text-white">📈 EC Trend & Predictions</span>
                  <p class="text-cream text-sm opacity-90 mt-1">90-day forecast with ML-powered insights</p>
                </div>
                <div class="flex space-x-2">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-200 border border-blue-400/30">
                    📊 Historical
                  </span>
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-200 border border-green-400/30">
                    🔮 Predicted
                  </span>
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-200 border border-red-400/30">
                    ⚠️ Critical Zone
                  </span>
                </div>
              </div>
              <div class="flex-1 min-h-0 bg-deepgreen/30 rounded-lg p-4 backdrop-blur-sm border border-sage/30">
                <canvas ref="ecChart" class="w-full h-full"></canvas>
              </div>
            </div>
          </div>

          <!-- Statistics Summary -->
          <div class="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">📊</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ totalReadings }}</div>
              <div class="text-cream text-sm opacity-90">Total Readings</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-blue-400 h-1 rounded-full w-3/4"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">⚡</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ averageEC }} <span class="text-lg font-normal text-cream/80">mS/cm</span></div>
              <div class="text-cream text-sm opacity-90">Average EC</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-yellow-400 h-1 rounded-full w-2/3"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">💧</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ averageMoisture }}<span class="text-lg font-normal text-cream/80">%</span></div>
              <div class="text-cream text-sm opacity-90">Average Moisture</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-cyan-400 h-1 rounded-full w-4/5"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">🔮</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1" v-if="predictionsData.timeline">{{ predictionsData.timeline.week_1 || '--' }}</div>
              <div class="text-3xl text-white font-bold mb-1" v-else>--</div>
              <div class="text-cream text-sm opacity-90">7-Day Forecast</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-green-400 h-1 rounded-full w-1/2"></div>
              </div>
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
