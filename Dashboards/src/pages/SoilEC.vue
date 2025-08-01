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
                width: `${calculateDropdownWidth(selectedUser)}px`,
                backgroundImage: 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==)',
                backgroundPosition: 'right 0.75rem center',
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

            <!-- Reading Selector - Only show when user has multiple readings -->
            <select 
              v-if="selectedUser && ecHistory.length > 1"
              v-model="selectedReadingIndex" 
              @change="onReadingChange"
              class="bg-sage hover:bg-[#5E936C] border-transparent text-white px-4 py-2 text-sm rounded-md transition-all duration-300 ease-in-out border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 transform hover:scale-105 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer appearance-none bg-no-repeat bg-right pr-8"
              :style="{ 
                backgroundImage: 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0iI0Y3RkZGMiI+PHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNNS4yOTMgNy4yOTNhMSAxIDAgMDExLjQxNCAwTDEwIDEwLjU4NmwzLjI5My0zLjI5M2ExIDEgMCAxMTEuNDE0IDEuNDE0bC00IDRhMSAxIDAgMDEtMS40MTQgMGwtNC00YTEgMSAwIDAxMC0xLjQxNHoiIGNsaXAtcnVsZT0iZXZlbm9kZCIvPjwvc3ZnPg==)',
                backgroundPosition: 'right 0.5rem center',
                backgroundSize: '0.8rem'
              }"
            >
              <option 
                v-for="(reading, index) in ecHistory" 
                :key="index" 
                :value="index"
                class="bg-deepgreen text-cream"
              >
                {{ formatReadingDate(reading.created_at) }} - {{ reading.ec }} mS/cm
              </option>
            </select>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div class="text-sage text-xl">⚡ Loading soil EC data...</div>
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
                    <span class="text-3xl">🧪</span>
                  </div>
                  <h2 class="text-2xl font-bold text-white mb-2">Select a User</h2>
                  <p class="text-cream/90 text-sm">Choose a user from the dropdown above to explore their soil EC monitoring and compost readiness predictions</p>
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
                        <span class="text-lg">📊</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">EC Monitoring</div>
                        <div class="text-sage text-xs">Real-time conductivity tracking</div>
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
                        <span class="text-lg">🎯</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">Readiness Status</div>
                        <div class="text-sage text-xs">ML-powered forecasting</div>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-3 p-4 bg-deepgreen/20 rounded-lg border border-sage/20">
                      <div class="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="text-lg">🤖</span>
                      </div>
                      <div>
                        <div class="font-semibold text-white text-sm">AI Recommendations</div>
                        <div class="text-sage text-xs">Smart composting insights</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Footer -->
              <div class="bg-deepgreen/60 px-8 py-4 border-t border-sage/20">
                <div class="flex items-center justify-center gap-2 text-sage">
                  <span class="text-lg">🔍</span>
                  <span class="text-sm">Use the dropdown above to dive into any user's soil EC monitoring journey!</span>
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
                  <span class="text-2xl">🧪</span>
                </div>
                <h2 class="text-xl font-bold text-white mb-1">Ready to Start EC Monitoring?</h2>
                <p class="text-cream/90">{{ selectedUser }} hasn't taken any EC readings yet</p>
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
                          <div class="font-semibold text-white text-sm">Use EC Monitoring Feature</div>
                          <div class="text-sage text-xs">Find the soil EC testing option in the menu</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">3</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Record Your Readings</div>
                          <div class="text-sage text-xs">Log EC values and moisture percentages</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">4</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Monitor Compost Health</div>
                          <div class="text-sage text-xs">Return here to track readiness and get AI insights!</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Right: EC Information -->
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Understanding EC Levels</h3>
                    <div class="space-y-3">
                      <div class="text-center p-4 bg-gradient-to-r from-green-500/20 to-green-600/10 rounded-lg border border-green-500/30">
                        <div class="text-2xl mb-2">✅</div>
                        <div class="font-bold text-white text-sm mb-1">Optimal Range</div>
                        <div class="text-sage text-xs">1.5-3.0 mS/cm - Perfect for compost health</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-amber-600/20 to-amber-700/10 rounded-lg border border-amber-600/30">
                        <div class="text-2xl mb-2">⚠️</div>
                        <div class="font-bold text-white text-sm mb-1">Building/High Range</div>
                        <div class="text-sage text-xs">1.0-1.5 or 3.0-4.0 mS/cm - Monitor closely</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-red-500/20 to-red-600/10 rounded-lg border border-red-500/30">
                        <div class="text-2xl mb-2">🚨</div>
                        <div class="font-bold text-white text-sm mb-1">Critical Levels</div>
                        <div class="text-sage text-xs">Below 1.0 or above 4.0 mS/cm - Action needed</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Footer -->
              <div class="bg-deepgreen/60 px-6 py-3 text-center border-t border-sage/20">
                <div class="flex items-center justify-center gap-2 text-sage">
                  <span class="text-lg">🔬</span>
                  <span class="text-xs">Start monitoring your soil EC today for optimal compost development!</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dashboard Content -->
        <div v-else class="flex flex-1 flex-col gap-4 min-h-0 h-full">
          <!-- Top Section: Key Metrics + EC Trend Chart - 50% height -->
          <div class="flex gap-4 h-1/2 min-h-0">
            <!-- Left: Key Metrics in 2x2 Grid -->
            <div class="grid grid-cols-2 gap-3 w-80">
              <!-- Current EC Level -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">{{ getStatusEmoji(currentEC) }}</span>
                  </div>
                  <div class="text-xs opacity-80">Current</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ currentEC }}</div>
                  <div class="text-xs opacity-80">mS/cm EC Level</div>
                </div>
              </div>

              <!-- Health Score -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">💚</span>
                  </div>
                  <div class="text-xs opacity-80">Score</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ averageHealthScore }}</div>
                  <div class="text-xs opacity-80">Health Score</div>
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
                  <div class="text-xs opacity-80">EC Readings</div>
                </div>
              </div>

              <!-- Average Moisture -->
              <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                <div class="flex items-center justify-between mb-2">
                  <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                    <span class="text-sm">💧</span>
                  </div>
                  <div class="text-xs opacity-80">Avg</div>
                </div>
                <div>
                  <div class="text-xl font-bold">{{ averageMoisture }}%</div>
                  <div class="text-xs opacity-80">Moisture</div>
                </div>
              </div>
            </div>

            <!-- Right: EC Trend Chart -->
            <div class="bg-sage rounded-xl flex-1 min-h-0">
              <div class="p-3 h-full flex flex-col">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-semibold text-white">EC Trend & Predictions</h3>
                  <div class="flex items-center gap-2 text-white text-xs">
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span>Historical</span>
                    <div class="w-2 h-2 bg-green-400 rounded-full ml-2"></div>
                    <span>Predicted</span>
                    <div class="w-2 h-2 bg-red-400 rounded-full ml-2"></div>
                    <span>Optimal (1.5-3.0)</span>
                  </div>
                </div>
                <div class="flex-1 relative min-h-0">
                  <canvas ref="ecChart" class="w-full h-full"></canvas>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Section: Readiness Status + Recent Activity - 50% height -->
          <div class="flex gap-4 h-1/2 min-h-0">
            <!-- Readiness & Alerts Panel -->
            <div class="bg-sage rounded-xl flex-1 min-h-0 max-h-full">
              <div class="p-4 h-full flex flex-col min-h-0">
                <div class="flex items-center justify-between mb-3 flex-shrink-0">
                  <h3 class="text-sm font-semibold text-white">Compost Status</h3>
                  <div class="text-sage text-xs">{{ getReadinessText(readinessStatus) }}</div>
                </div>
                
                <div class="flex-1 overflow-y-auto min-h-0 space-y-3">
                  <!-- Readiness Status -->
                  <div class="bg-deepgreen/20 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">🎯</span>
                        <span class="text-white font-medium text-sm">Readiness Status</span>
                      </div>
                      <span class="text-emerald-400 font-semibold text-sm">{{ getReadinessText(readinessStatus) }}</span>
                    </div>
                    <div class="text-sage text-xs" v-if="estimatedReadyDays">
                      ~{{ estimatedReadyDays }} days to ready
                    </div>
                    <div class="text-sage text-xs" v-else>
                      Monitoring progress
                    </div>
                  </div>

                  <!-- EC Status -->
                  <div class="bg-deepgreen/20 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">{{ getStatusEmoji(currentEC) }}</span>
                        <span class="text-white font-medium text-sm">EC Status</span>
                      </div>
                      <span class="text-blue-400 font-semibold text-sm">{{ currentEC }} mS/cm</span>
                    </div>
                    <div class="text-sage text-xs">{{ getECStatus(currentEC) }}</div>
                  </div>

                  <!-- Alert Section -->
                  <div v-if="alertLevel && alertLevel !== 'none'" :class="getAlertCardClass(alertLevel)" class="rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="text-lg">{{ getAlertIcon(alertLevel) }}</span>
                        <span class="text-white font-medium text-sm">System Alert</span>
                      </div>
                    </div>
                    <div class="text-white text-xs">{{ alertMessage }}</div>
                  </div>
                </div>
                
                <!-- Motivational Footer -->
                <div class="mt-3 p-3 bg-deepgreen/20 rounded-lg">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
                      <span class="text-xs">⚡</span>
                    </div>
                    <div>
                      <p class="text-white font-medium text-xs">EC Monitoring Active</p>
                      <p class="text-sage text-xs">Keep tracking for optimal compost health</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Recommendations Panel -->
            <div class="w-64 bg-sage rounded-xl">
              <div class="p-4 h-full flex flex-col">
                <div class="text-center mb-4">
                  <div class="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                    <span class="text-lg">🤖</span>
                  </div>
                  <h3 class="text-sm font-semibold text-white mb-1">AI Recommendations</h3>
                  <div class="text-xs text-sage">Smart composting insights</div>
                </div>
                
                <div class="space-y-3 flex-1">
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="text-white text-xs leading-relaxed">{{ primaryRecommendation }}</div>
                  </div>
                  
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <span class="text-sm">📊</span>
                        <span class="text-white text-xs">Avg EC</span>
                      </div>
                      <span class="text-blue-400 font-semibold text-xs">{{ averageEC }} mS/cm</span>
                    </div>
                  </div>
                  
                  <div class="bg-deepgreen/20 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <span class="text-sm">🔮</span>
                        <span class="text-white text-xs">7-Day Forecast</span>
                      </div>
                      <span class="text-green-400 font-semibold text-xs" v-if="predictionsData.timeline">
                        {{ predictionsData.timeline.week_1 || '--' }}
                      </span>
                      <span class="text-green-400 font-semibold text-xs" v-else>--</span>
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
  name: 'SoilEC',
  setup() {
    const selectedUser = ref('')
    const selectedReadingIndex = ref(0)
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

    const calculateDropdownWidth = (username) => {
      if (!username) return 180
      
      const user = [...usersWithData.value, ...usersWithoutData.value].find(u => u.username === username)
      let displayText = username
      
      if (user) {
        if (usersWithData.value.includes(user)) {
          displayText = `${username} (${user.ecLogsCount} readings)`
        } else {
          displayText = `${username} (No data yet)`
        }
      }
      
      // Approximate 8px per character + 80px for padding and dropdown arrow
      return Math.max(displayText.length * 8 + 80, 180)
    }

    const formatReadingDate = (dateString) => {
      if (!dateString) return 'Invalid Date'
      
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Invalid Date'
      
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const year = date.getFullYear()
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${day}/${month}/${year} ${hours}:${minutes}`
    }

    const updateCurrentReadingData = () => {
      if (ecHistory.value.length === 0) return
      
      const selectedReading = ecHistory.value[selectedReadingIndex.value] || ecHistory.value[0]
      currentEC.value = selectedReading.ec || 0
      currentMoisture.value = selectedReading.moisture_percentage || 0
      
      // You could also update other related data based on the selected reading
      // For now, we'll keep the aggregate data (averages, totals) as they are
    }

    const onReadingChange = () => {
      updateCurrentReadingData()
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
            
            // Reset reading selector to show the most recent reading (index 0)
            selectedReadingIndex.value = 0
            
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
      calculateDropdownWidth,
      ecHistory,
      selectedReadingIndex,
      formatReadingDate,
      onReadingChange,
      onUserChange
    }
  }
}
</script>
