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
            
            <!-- Reading Selector (only show if user has multiple readings) -->
            <select 
              v-if="selectedUser && moistureHistory.length > 1"
              v-model="selectedReadingIndex"
              @change="onReadingChange"
              class="bg-sage hover:bg-[#5E936C] border-transparent text-white px-4 py-2 text-sm rounded-md transition-all duration-300 ease-in-out border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 transform hover:scale-105 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer appearance-none bg-no-repeat bg-right pr-8"
              style="
                width: 180px;
                background-image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==);
                background-position: right 0.5rem center;
                background-size: 0.875rem;
              "
            >
              <option 
                v-for="(reading, index) in moistureHistory" 
                :key="index" 
                :value="index"
                class="bg-deepgreen text-cream"
              >
                {{ formatReadingDate(reading.created_at) }}
              </option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div class="text-sage text-xl">🌱 Loading plant data...</div>
        </div>

        <!-- No User Selected -->
        <div v-else-if="!selectedUser" class="flex items-center justify-center flex-1 p-4">
          <div class="max-w-2xl w-full mx-auto">
            <!-- Main Card -->
            <div class="bg-sage/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-sage/30 overflow-hidden">
              <!-- Header Section -->
              <div class="bg-gradient-to-r from-sage to-[#5E936C] p-8 text-center relative">
                <!-- Background pattern -->
                <div class="absolute inset-0 opacity-10">
                  <svg class="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                      <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                        <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" stroke-width="0.5"/>
                      </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                  </svg>
                </div>
                
                <div class="relative z-10">
                  <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/30">
                    <span class="text-3xl">🌱</span>
                  </div>
                  <h2 class="text-2xl font-bold text-white mb-2">Select a User</h2>
                  <p class="text-cream/90 text-sm">Choose a user from the dropdown above to explore their plant moisture monitoring and watering predictions</p>
                </div>
              </div>
              
              <!-- Content Section -->
              <div class="p-8">
                <!-- User Statistics Overview -->
                <div class="grid grid-cols-3 gap-4 mb-6">
                  <div class="text-center p-4 bg-deepgreen/30 rounded-xl border border-sage/20">
                    <div class="text-2xl font-bold text-white mb-1">{{ (usersWithData.length + usersWithoutData.length) || 0 }}</div>
                    <div class="text-sage text-xs">Total Users</div>
                  </div>
                  
                  <div class="text-center p-4 bg-emerald-500/20 rounded-xl border border-emerald-500/30">
                    <div class="text-2xl font-bold text-emerald-400 mb-1">{{ usersWithData.length || 0 }}</div>
                    <div class="text-sage text-xs">Active Monitors</div>
                  </div>
                  
                  <div class="text-center p-4 bg-amber-500/20 rounded-xl border border-amber-500/30">
                    <div class="text-2xl font-bold text-amber-400 mb-1">{{ usersWithoutData.length || 0 }}</div>
                    <div class="text-sage text-xs">Ready to Start</div>
                  </div>
                </div>

                <!-- Features Preview -->
                <div class="space-y-4">
                  <h3 class="text-lg font-semibold text-white text-center mb-4">What You'll See</h3>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div class="flex items-center gap-3 p-4 bg-deepgreen/20 rounded-lg border border-sage/20">
                      <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-lg">💧</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">Moisture Tracking</div>
                        <div class="text-sage text-xs">Real-time soil moisture levels</div>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3 p-4 bg-deepgreen/20 rounded-lg border border-sage/20">
                      <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-lg">📈</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">Trend Analysis</div>
                        <div class="text-sage text-xs">Historical & predicted data</div>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3 p-4 bg-deepgreen/20 rounded-lg border border-sage/20">
                      <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-lg">🚰</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">Watering Alerts</div>
                        <div class="text-sage text-xs">AI-powered watering guidance</div>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3 p-4 bg-deepgreen/20 rounded-lg border border-sage/20">
                      <div class="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-lg">🤖</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">AI Recommendations</div>
                        <div class="text-sage text-xs">Smart plant care insights</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Footer -->
              <div class="bg-deepgreen/60 px-8 py-4 border-t border-sage/20">
                <div class="flex items-center justify-center gap-2 text-sage">
                  <span class="text-lg">🔍</span>
                  <span class="text-sm">Use the dropdown above to dive into any user's plant moisture monitoring journey!</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Data Available -->
        <div v-else-if="!hasData" class="flex items-center justify-center flex-1 p-4">
          <div class="max-w-4xl w-full mx-auto">
            <!-- Main Card -->
            <div class="bg-sage/80 backdrop-blur-sm rounded-2xl shadow-2xl border border-sage/30 overflow-hidden">
              <!-- Header Section -->
              <div class="bg-gradient-to-r from-sage to-[#5E936C] p-6 text-center">
                <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span class="text-2xl">🌱</span>
                </div>
                <h2 class="text-xl font-bold text-white mb-1">Ready to Start Plant Monitoring?</h2>
                <p class="text-cream/90">{{ selectedUser }} hasn't logged any plant moisture readings yet</p>
              </div>
              
              <!-- Content Section -->
              <div class="p-6">
                <div class="flex gap-8">
                  <!-- Left: Getting Started Steps -->
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Getting Started is Easy!</h3>
                    <div class="space-y-3">
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">1</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Open NutriBot Telegram</div>
                          <div class="text-sage text-xs">Launch the chatbot to get started</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">2</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Use Plant Monitoring Feature</div>
                          <div class="text-sage text-xs">Find the plant moisture testing option in the menu</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">3</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Record Moisture Levels</div>
                          <div class="text-sage text-xs">Log plant soil moisture percentages regularly</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">4</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Track Plant Health</div>
                          <div class="text-sage text-xs">Return here to monitor watering needs and get AI insights!</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Right: Moisture Information -->
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Understanding Moisture Levels</h3>
                    <div class="space-y-3">
                      <div class="text-center p-4 bg-gradient-to-r from-green-500/20 to-green-600/10 rounded-lg border border-green-500/30">
                        <div class="text-2xl mb-2">💚</div>
                        <div class="font-bold text-white text-sm mb-1">Healthy Range</div>
                        <div class="text-sage text-xs">Above 40% - Plants are well hydrated</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-amber-600/20 to-amber-700/10 rounded-lg border border-amber-600/30">
                        <div class="text-2xl mb-2">⚠️</div>
                        <div class="font-bold text-white text-sm mb-1">Watch Zone</div>
                        <div class="text-sage text-xs">30-40% - Monitor closely, prepare to water</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-red-500/20 to-red-600/10 rounded-lg border border-red-500/30">
                        <div class="text-2xl mb-2">🚨</div>
                        <div class="font-bold text-white text-sm mb-1">Critical - Water Now!</div>
                        <div class="text-sage text-xs">Below 40% - Immediate watering needed</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Footer -->
              <div class="bg-deepgreen/60 px-6 py-3 text-center border-t border-sage/20">
                <div class="flex items-center justify-center gap-2 text-sage">
                  <span class="text-lg">🌿</span>
                  <span class="text-xs">Start monitoring your plant moisture today for healthier, happier plants!</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dashboard Content -->
        <div v-else class="flex flex-1 flex-col gap-4 min-h-0 h-full">
          <!-- Top Section: Key Metrics + Moisture Trend Chart - 50% height -->
          <div class="flex gap-4 h-1/2 min-h-0">
            <!-- Left: Key Metrics in 2x2 Grid -->
            <div class="grid grid-cols-2 gap-3 w-80">
              <!-- Current Moisture Level -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">{{ getStatusEmoji(currentMoisture) }}</span>
                  </div>
                  <div class="text-xs opacity-80">Current</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ currentMoisture }}%</div>
                  <div class="text-xs opacity-80">Soil Moisture</div>
                </div>
              </div>

              <!-- Next Watering -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">⏰</span>
                  </div>
                  <div class="text-xs opacity-80">Next</div>
                </div>
                <div>
                  <div class="text-lg font-bold">{{ daysToNextWatering }}</div>
                  <div class="text-xs opacity-80">Days to Water</div>
                </div>
              </div>

              <!-- Total Readings -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">📊</span>
                  </div>
                  <div class="text-xs opacity-80">Total</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ totalReadings }}</div>
                  <div class="text-xs opacity-80">Readings</div>
                </div>
              </div>

              <!-- Monthly Waterings -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">🚿</span>
                  </div>
                  <div class="text-xs opacity-80">Monthly</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ predictedWaterings }}</div>
                  <div class="text-xs opacity-80">Waterings</div>
                </div>
              </div>
            </div>

            <!-- Right: Moisture Prediction Chart -->
            <div class="bg-sage rounded-xl flex-1 min-h-0">
              <div class="p-3 h-full flex flex-col">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-semibold text-white">30-Day Moisture Prediction</h3>
                  <div class="flex items-center gap-2 text-white text-xs">
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span>Historical</span>
                    <div class="w-2 h-2 bg-green-400 rounded-full ml-2"></div>
                    <span>Predicted</span>
                    <div class="w-2 h-2 bg-red-400 rounded-full ml-2"></div>
                    <span>Critical (40%)</span>
                  </div>
                </div>
                <div class="flex-1 relative min-h-0">
                  <canvas ref="moistureChart" class="w-full h-full"></canvas>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Section: Watering Status + Care Tips - 50% height -->
          <div class="flex gap-4 h-1/2 min-h-0">
            <!-- Watering Alerts & Status Panel -->
            <div class="bg-sage rounded-xl flex-1 min-h-0 max-h-full">
              <div class="p-4 h-full flex flex-col min-h-0">
                <div class="flex items-center justify-between mb-3 flex-shrink-0">
                  <h3 class="text-sm font-semibold text-white">Watering Schedule</h3>
                  <div class="text-sage text-xs">{{ nextWateringDay }}</div>
                </div>
                
                <div class="flex-1 overflow-y-auto min-h-0 space-y-3">
                  <!-- Next Watering -->
                  <div class="bg-deepgreen/20 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">🗓️</span>
                        <span class="text-white font-medium text-sm">Next Watering</span>
                      </div>
                      <span class="text-blue-400 font-semibold text-sm">{{ nextWateringDay }}</span>
                    </div>
                    <div class="text-sage text-xs">{{ nextWateringDate }}</div>
                  </div>

                  <!-- Moisture Status -->
                  <div class="bg-deepgreen/20 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">{{ getStatusEmoji(currentMoisture) }}</span>
                        <span class="text-white font-medium text-sm">Moisture Status</span>
                      </div>
                      <span class="text-cyan-400 font-semibold text-sm">{{ currentMoisture }}%</span>
                    </div>
                    <div class="text-sage text-xs">{{ getMoistureStatus(currentMoisture) }}</div>
                  </div>

                  <!-- Watering Alerts -->
                  <div v-if="upcomingAlerts.length > 0" class="bg-red-600/20 border border-red-500/30 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">🚨</span>
                        <span class="text-white font-medium text-sm">Watering Alerts</span>
                      </div>
                    </div>
                    <div class="space-y-1">
                      <div v-for="alert in upcomingAlerts.slice(0, 3)" :key="alert.date" class="text-red-200 text-xs">
                        {{ alert.day_name }}: {{ alert.moisture_level }}%
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Motivational Footer -->
                <div class="mt-3 p-3 bg-deepgreen/20 rounded-lg">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center">
                      <span class="text-xs">💧</span>
                    </div>
                    <div>
                      <p class="text-white font-medium text-xs">Plant Health Tracking</p>
                      <p class="text-sage text-xs">Optimal watering for healthy growth</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Plant Care Tips Panel -->
            <div class="w-64 bg-sage rounded-xl">
              <div class="p-4 h-full flex flex-col">
                <div class="text-center mb-4">
                  <div class="w-12 h-12 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span class="text-lg">🌱</span>
                  </div>
                  <h3 class="text-sm font-semibold text-white mb-1">Plant Care Tips</h3>
                  <div class="text-xs text-sage">Smart watering insights</div>
                </div>
                
                <div class="space-y-3 flex-1">
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="text-white text-xs leading-relaxed">{{ getCareTip(currentMoisture) }}</div>
                  </div>
                  
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <span class="text-sm">📊</span>
                        <span class="text-white text-xs">Avg Moisture</span>
                      </div>
                      <span class="text-cyan-400 font-semibold text-xs">{{ averageMoisture }}%</span>
                    </div>
                  </div>
                  
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <span class="text-sm">🚿</span>
                        <span class="text-white text-xs">This Month</span>
                      </div>
                      <span class="text-green-400 font-semibold text-xs">{{ predictedWaterings }} waterings</span>
                    </div>
                  </div>
                </div>

                <!-- Last Updated -->
                <div class="mt-3 pt-3 border-t border-sage/20 text-center">
                  <div class="text-sage text-xs">Last reading</div>
                  <div class="text-white text-xs font-medium">{{ selectedUser || 'No user selected' }}</div>
                </div>
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
    const selectedReadingIndex = ref(0)

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
            
            // Reset reading selector to show the most recent reading (index 0)
            selectedReadingIndex.value = 0
            
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

    const formatReadingDate = (timestamp) => {
      if (!timestamp) return 'Invalid Date'
      
      const date = new Date(timestamp)
      if (isNaN(date.getTime())) return 'Invalid Date'
      
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const updateCurrentReadingData = (readingIndex) => {
      if (!moistureHistory.value || moistureHistory.value.length === 0) return
      
      const reading = moistureHistory.value[readingIndex]
      if (!reading) return
      
      // Update current data based on selected reading
      currentMoisture.value = reading.plant_moisture || 0
      // Note: For plant moisture, we might not have as much per-reading data
      // as we do for soil EC, so we may need to keep some aggregated values
    }

    const onReadingChange = () => {
      updateCurrentReadingData(selectedReadingIndex.value)
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
      moistureHistory,
      selectedReadingIndex,
      formatReadingDate,
      onReadingChange,
      onUserChange
    }
  }
}
</script>