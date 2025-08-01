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
              <span class="text-sage">💧 Plant Moisture</span> <span class="text-white">Tracking</span>
            </h1>
            <p class="text-base text-sage mt-2 font-medium">
              Monitor plant soil moisture levels and predict watering needs with AI-powered forecasting.
            </p>
            <div class="flex items-center mt-3 space-x-3">
              <div class="flex items-center text-cream text-sm bg-sage/20 px-3 py-1 rounded-full">
                <div class="w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                Smart Watering
              </div>
              <div class="flex items-center text-cream text-sm bg-sage/20 px-3 py-1 rounded-full">
                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                Plant Health
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
                width: `${calculateDropdownWidth(selectedUser)}px`,
                backgroundImage: 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==)',
                backgroundPosition: 'right 1rem center',
                backgroundSize: '1.2rem'
              }"
            >
              <option value="" class="bg-deepgreen text-cream">Choose a user...</option>
              <optgroup label="Users with Plant Data" v-if="usersWithData.length > 0" class="bg-deepgreen text-cream">
                <option 
                  v-for="user in usersWithData" 
                  :key="user.username" 
                  :value="user.username"
                  class="bg-deepgreen text-cream"
                >
                  {{ user.username }} ({{ user.moistureLogsCount }} readings)
                </option>
              </optgroup>
              <optgroup label="Users without Plant Data" v-if="usersWithoutData.length > 0" class="bg-deepgreen text-cream">
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
          <div class="text-sage text-xl">🌱 Loading plant data...</div>
        </div>

        <!-- No User Selected -->
        <div v-else-if="!selectedUser" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="text-sage text-6xl mb-4">🪴</div>
            <div class="text-sage text-xl mb-2">Select a user to view plant moisture data</div>
            <div class="text-cream text-sm">Choose from the dropdown above to see moisture tracking and predictions</div>
          </div>
        </div>

        <!-- No Data Available -->
        <div v-else-if="!hasData" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="text-sage text-6xl mb-4">📊</div>
            <div class="text-sage text-xl mb-2">No plant moisture data available</div>
            <div class="text-cream text-sm">{{ selectedUser }} hasn't logged any plant moisture readings yet</div>
          </div>
        </div>

        <!-- Dashboard Content -->
        <div v-else class="flex-1 grid grid-cols-12 gap-4 min-h-0">
          <!-- Current Status Cards -->
          <div class="col-span-12 lg:col-span-4 space-y-4">
            <!-- Current Moisture Level -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-white font-bold text-lg mb-1">💧 Current Moisture</h3>
                  <p class="text-cream text-xs opacity-80">Real-time soil moisture level</p>
                </div>
                <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-3xl">{{ getStatusEmoji(currentMoisture) }}</span>
                </div>
              </div>
              <div class="text-4xl font-bold text-white mb-3 tracking-tight">{{ currentMoisture }}<span class="text-lg font-normal text-cream/80">%</span></div>
              <div class="text-cream text-sm mb-4 bg-deepgreen/30 px-3 py-2 rounded-lg border-l-4 border-blue-400">{{ getMoistureStatus(currentMoisture) }}</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-3 overflow-hidden">
                <div 
                  class="h-3 rounded-full transition-all duration-700 ease-out shadow-inner"
                  :class="getMoistureBarColor(currentMoisture)"
                  :style="`width: ${currentMoisture}%`"
                ></div>
              </div>
            </div>

            <!-- Next Watering -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-white font-bold text-lg mb-1">🗓️ Next Watering</h3>
                  <p class="text-cream text-xs opacity-80">Optimal watering schedule</p>
                </div>
                <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-2xl">⏰</span>
                </div>
              </div>
              <div class="text-2xl font-bold text-white mb-2">{{ nextWateringDay }}</div>
              <div class="text-cream text-sm bg-deepgreen/30 px-3 py-2 rounded-lg">{{ nextWateringDate }}</div>
            </div>

            <!-- Watering Alerts -->
            <div v-if="upcomingAlerts.length > 0" class="bg-gradient-to-br from-red-600 to-red-800 p-6 rounded-xl shadow-lg border border-red-500/30 transform hover:scale-105 transition-all duration-300 animate-pulse">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-white font-bold text-lg mb-1">🚨 Watering Alerts</h3>
                  <p class="text-red-100 text-xs opacity-80">Critical moisture levels detected</p>
                </div>
                <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <span class="text-2xl">⚠️</span>
                </div>
              </div>
              <div class="space-y-2">
                <div v-for="alert in upcomingAlerts.slice(0, 3)" :key="alert.date" class="bg-black/20 p-3 rounded-lg">
                  <div class="text-sm text-white font-medium">{{ alert.day_name }}</div>
                  <div class="text-xs text-red-100">Moisture: {{ alert.moisture_level }}%</div>
                </div>
              </div>
            </div>

            <!-- Plant Care Tips -->
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="text-white font-bold text-lg mb-1">💡 AI Care Tips</h3>
                  <p class="text-cream text-xs opacity-80">Smart recommendations</p>
                </div>
                <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center">
                  <span class="text-2xl">🌱</span>
                </div>
              </div>
              <div class="text-cream text-sm leading-relaxed bg-deepgreen/30 p-4 rounded-lg border-l-4 border-yellow-400">
                {{ getCareTip(currentMoisture) }}
              </div>
            </div>
          </div>

          <!-- Moisture Timeline Chart -->
          <div class="col-span-12 lg:col-span-8">
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] rounded-xl p-6 h-full flex flex-col shadow-lg border border-sage/20">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <h3 class="text-xl font-bold text-white mb-2">📈 30-Day Moisture Prediction</h3>
                  <p class="text-cream text-sm opacity-90">AI-powered watering schedule and moisture forecasting</p>
                </div>
                <div class="flex space-x-2 text-sm">
                  <span class="inline-flex items-center px-3 py-1 rounded-full font-medium bg-blue-500/20 text-blue-200 border border-blue-400/30">
                    <div class="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                    📊 Historical
                  </span>
                  <span class="inline-flex items-center px-3 py-1 rounded-full font-medium bg-green-500/20 text-green-200 border border-green-400/30">
                    <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    🔮 Predicted
                  </span>
                  <span class="inline-flex items-center px-3 py-1 rounded-full font-medium bg-red-500/20 text-red-200 border border-red-400/30">
                    <div class="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                    ⚠️ Critical Zone
                  </span>
                </div>
              </div>
              <div class="flex-1 min-h-0 bg-deepgreen/30 rounded-lg p-4 backdrop-blur-sm border border-sage/30">
                <canvas ref="moistureChart" class="w-full h-full"></canvas>
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
                <span class="text-2xl">💧</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ averageMoisture }}<span class="text-lg font-normal text-cream/80">%</span></div>
              <div class="text-cream text-sm opacity-90">Average Moisture</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-cyan-400 h-1 rounded-full w-2/3"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">⏳</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ daysToNextWatering }}</div>
              <div class="text-cream text-sm opacity-90">Days to Next Water</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-yellow-400 h-1 rounded-full w-1/2"></div>
              </div>
            </div>
            <div class="bg-gradient-to-br from-sage to-[#0B4F26] p-6 rounded-xl text-center shadow-lg border border-sage/20 transform hover:scale-105 transition-all duration-300">
              <div class="w-12 h-12 bg-cream/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span class="text-2xl">🚿</span>
              </div>
              <div class="text-3xl text-white font-bold mb-1">{{ predictedWaterings }}</div>
              <div class="text-cream text-sm opacity-90">Waterings This Month</div>
              <div class="w-full bg-deepgreen/50 rounded-full h-1 mt-3">
                <div class="bg-green-400 h-1 rounded-full w-4/5"></div>
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
  name: 'PlantMoisture',
  setup() {
    const selectedUser = ref('')
    const loading = ref(false)
    const hasData = ref(false)
    const usersWithData = ref([])
    const usersWithoutData = ref([])
    const moistureChart = ref(null)
    const chartInstance = ref(null)
    
    // Dashboard data
    const currentMoisture = ref(0)
    const nextWateringDay = ref('No data')
    const nextWateringDate = ref('')
    const upcomingAlerts = ref([])
    const totalReadings = ref(0)
    const averageMoisture = ref(0)
    const daysToNextWatering = ref('--')
    const predictedWaterings = ref(0)
    const moistureHistory = ref([])
    const moisturePredictions = ref([])

    // API configuration
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

    const calculateDropdownWidth = (username) => {
      const baseWidth = 200
      const extraWidth = username ? username.length * 8 : 0
      return Math.max(baseWidth, baseWidth + extraWidth)
    }

    const getStatusEmoji = (moisture) => {
      if (moisture >= 60) return '✅'
      if (moisture >= 40) return '📊'
      if (moisture >= 20) return '⚠️'
      return '🚨'
    }

    const getMoistureStatus = (moisture) => {
      if (moisture >= 60) return 'Optimal level'
      if (moisture >= 40) return 'Moderate level'
      if (moisture >= 20) return 'Low - water soon'
      return 'Critical - water now'
    }

    const getMoistureBarColor = (moisture) => {
      if (moisture >= 60) return 'bg-green-400'
      if (moisture >= 40) return 'bg-yellow-400'
      if (moisture >= 20) return 'bg-orange-400'
      return 'bg-red-400'
    }

    const getCareTip = (moisture) => {
      if (moisture >= 60) return 'Your plant is well-hydrated. Continue current watering routine and avoid overwatering.'
      if (moisture >= 40) return 'Monitor every 2-3 days. Water when top layer of soil feels dry.'
      if (moisture >= 20) return 'Plan to water within 1-2 days. Check soil with finger test.'
      return 'Water immediately with room temperature water. Check drainage to avoid waterlogging.'
    }

    const loadUsers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/plant-moisture-users`)
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
        // Load moisture data
        const response = await fetch(`${API_BASE_URL}/user/${username}/plant-moisture`)
        if (response.ok) {
          const result = await response.json()
          
          if (result.success && result.hasData && result.data && result.data.moistureLogs && result.data.moistureLogs.length > 0) {
            const data = result.data
            hasData.value = true
            currentMoisture.value = data.currentMoisture || 0
            totalReadings.value = data.totalReadings || 0
            averageMoisture.value = Math.round(data.averageMoisture || 0)
            moistureHistory.value = data.moistureLogs || []
            
            // Load predictions
            const predResponse = await fetch(`${API_BASE_URL}/user/${username}/moisture-predictions`)
            if (predResponse.ok) {
              const predResult = await predResponse.json()
              if (predResult.success && predResult.data) {
                moisturePredictions.value = predResult.data.projections || []
                upcomingAlerts.value = predResult.data.watering_alerts || []
                
                console.log('Predictions loaded:', {
                  projections: moisturePredictions.value.length,
                  alerts: upcomingAlerts.value.length
                })
              }
              
              // Calculate next watering
              const nextAlert = upcomingAlerts.value[0]
              if (nextAlert) {
                nextWateringDay.value = nextAlert.day_name
                nextWateringDate.value = nextAlert.date
                daysToNextWatering.value = Math.ceil((new Date(nextAlert.date) - new Date()) / (1000 * 60 * 60 * 24))
              }
              
              predictedWaterings.value = upcomingAlerts.value.length
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
      if (!moistureChart.value) {
        console.warn('Chart canvas not available yet')
        return
      }

      // Destroy existing chart
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }

      const ctx = moistureChart.value.getContext('2d')
      
      // Prepare data with debugging
      const historicalData = moistureHistory.value.map(log => ({
        x: new Date(log.created_at),
        y: log.plant_moisture
      }))

      const predictionData = moisturePredictions.value.map(pred => ({
        x: new Date(pred.date),
        y: pred.moisture_percentage
      }))

      console.log('Chart data:', {
        historical: historicalData,
        predictions: predictionData,
        historicalCount: historicalData.length,
        predictionCount: predictionData.length
      })

      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Historical Moisture',
              data: historicalData,
              borderColor: '#60A5FA',
              backgroundColor: 'rgba(96, 165, 250, 0.1)',
              tension: 0.4,
              pointRadius: 4,
              pointHoverRadius: 6
            },
            {
              label: 'Predicted Moisture',
              data: predictionData,
              borderColor: '#4ADE80',
              backgroundColor: 'rgba(74, 222, 128, 0.1)',
              borderDash: [5, 5],
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 5
            },
            {
              label: 'Critical Zone',
              data: [
                { x: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), y: 40 },
                { x: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), y: 40 }
              ],
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              fill: true,
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
              max: 100,
              grid: {
                color: 'rgba(247, 255, 242, 0.1)'
              },
              ticks: {
                color: '#F7FFF2',
                callback: function(value) {
                  return value + '%'
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
      moistureChart,
      currentMoisture,
      nextWateringDay,
      nextWateringDate,
      upcomingAlerts,
      totalReadings,
      averageMoisture,
      daysToNextWatering,
      predictedWaterings,
      calculateDropdownWidth,
      getStatusEmoji,
      getMoistureStatus,
      getMoistureBarColor,
      getCareTip,
      onUserChange
    }
  }
}
</script>