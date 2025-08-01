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
              <span class="text-sage">Plant Moisture</span> Tracking
            </h1>
            <p class="text-sm text-sage mt-1">
              Monitor plant soil moisture levels and predict watering needs with AI-powered forecasting.
            </p>
          </div>

          <!-- Right: User Selector Dropdown -->
          <div class="flex space-x-2 items-end">
            <select 
              v-model="selectedUser" 
              @change="onUserChange"
              class="bg-sage hover:bg-[#5E936C] border-transparent text-white px-6 py-2 text-sm rounded-md transition-all duration-300 ease-in-out border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 transform hover:scale-105 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer appearance-none bg-no-repeat bg-right pr-10"
              :style="{ 
                width: `${calculateDropdownWidth(selectedUser)}px`,
                backgroundImage: 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==)',
                backgroundPosition: 'right 0.75rem center',
                backgroundSize: '1rem'
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
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-white font-semibold">💧 Current Moisture</h3>
                <span class="text-2xl">{{ getStatusEmoji(currentMoisture) }}</span>
              </div>
              <div class="text-3xl font-bold text-white mb-1">{{ currentMoisture }}%</div>
              <div class="text-cream text-sm">{{ getMoistureStatus(currentMoisture) }}</div>
              <div class="w-full bg-deepgreen rounded-full h-2 mt-2">
                <div 
                  class="h-2 rounded-full transition-all duration-300"
                  :class="getMoistureBarColor(currentMoisture)"
                  :style="`width: ${currentMoisture}%`"
                ></div>
              </div>
            </div>

            <!-- Next Watering -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-white font-semibold">🗓️ Next Watering</h3>
                <span class="text-2xl">⏰</span>
              </div>
              <div class="text-lg font-bold text-white mb-1">{{ nextWateringDay }}</div>
              <div class="text-cream text-sm">{{ nextWateringDate }}</div>
            </div>

            <!-- Watering Alerts -->
            <div v-if="upcomingAlerts.length > 0" class="bg-red-600 p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-white font-semibold">🚨 Watering Alerts</h3>
                <span class="text-2xl">⚠️</span>
              </div>
              <div class="space-y-1">
                <div v-for="alert in upcomingAlerts.slice(0, 3)" :key="alert.date" class="text-sm text-white">
                  {{ alert.day_name }}: {{ alert.moisture_level }}%
                </div>
              </div>
            </div>

            <!-- Plant Care Tips -->
            <div class="bg-sage p-4 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-white font-semibold">💡 Care Tips</h3>
                <span class="text-2xl">🌱</span>
              </div>
              <div class="text-cream text-sm leading-relaxed">
                {{ getCareTip(currentMoisture) }}
              </div>
            </div>
          </div>

          <!-- Moisture Timeline Chart -->
          <div class="col-span-12 lg:col-span-8">
            <div class="bg-sage rounded-lg p-4 h-full flex flex-col">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-white font-semibold text-lg">📈 30-Day Moisture Prediction</h3>
                <div class="flex space-x-2 text-sm">
                  <span class="flex items-center text-cream">
                    <div class="w-3 h-3 bg-blue-400 rounded mr-1"></div>
                    Historical
                  </span>
                  <span class="flex items-center text-cream">
                    <div class="w-3 h-3 bg-green-400 rounded mr-1"></div>
                    Predicted
                  </span>
                  <span class="flex items-center text-cream">
                    <div class="w-3 h-3 bg-red-400 rounded mr-1"></div>
                    Critical Zone
                  </span>
                </div>
              </div>
              <div class="flex-1 min-h-0">
                <canvas ref="moistureChart" class="w-full h-full"></canvas>
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
              <div class="text-2xl text-white font-bold">{{ averageMoisture }}%</div>
              <div class="text-cream text-sm">Average Moisture</div>
            </div>
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold">{{ daysToNextWatering }}</div>
              <div class="text-cream text-sm">Days to Next Water</div>
            </div>
            <div class="bg-sage p-4 rounded-lg text-center">
              <div class="text-2xl text-white font-bold">{{ predictedWaterings }}</div>
              <div class="text-cream text-sm">Waterings This Month</div>
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
        const response = await fetch('/api/plant-moisture-users')
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
        const response = await fetch(`/api/user/${username}/plant-moisture`)
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
            const predResponse = await fetch(`/api/user/${username}/moisture-predictions`)
            if (predResponse.ok) {
              const predResult = await predResponse.json()
              if (predResult.success && predResult.data) {
                moisturePredictions.value = predResult.data.projections || []
                upcomingAlerts.value = predResult.data.watering_alerts || []
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
            
            // Update chart
            await nextTick()
            updateChart()
          }
        }
      } catch (error) {
        console.error('Error loading user data:', error)
      } finally {
        loading.value = false
      }
    }

    const updateChart = () => {
      if (!moistureChart.value) return

      // Destroy existing chart
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }

      const ctx = moistureChart.value.getContext('2d')
      
      // Prepare data
      const historicalData = moistureHistory.value.map(log => ({
        x: new Date(log.created_at),
        y: log.plant_moisture
      }))

      const predictionData = moisturePredictions.value.map(pred => ({
        x: new Date(pred.date),
        y: pred.moisture_percentage
      }))

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
              fill: '-1',
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