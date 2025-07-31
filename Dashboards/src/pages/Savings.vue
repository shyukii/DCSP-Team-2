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
              <span class="text-sage">CO₂E Savings</span> Dashboard
            </h1>
            <p class="text-sm text-sage mt-1">
              Track environmental impact through composting and monitor CO₂ savings across all users.
            </p>
          </div>

          <!-- Right: User Selector Dropdown -->
          <div class="flex space-x-2 items-center">
            <select 
              v-model="selectedUser" 
              @change="onUserChange"
              class="bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none min-w-48"
            >
              <option value="" class="bg-deepgreen text-cream">Choose a user...</option>
              <optgroup label="Users with Data" v-if="usersWithData.length > 0" class="bg-deepgreen text-cream">
                <option 
                  v-for="user in usersWithData" 
                  :key="user.username" 
                  :value="user.username"
                  class="bg-deepgreen text-cream"
                >
                  {{ user.username }} ({{ user.feedingLogsCount }} logs)
                </option>
              </optgroup>
              <optgroup label="Users without Data" v-if="usersWithoutData.length > 0" class="bg-deepgreen text-cream">
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
            
            <button 
              @click="selectedView = selectedView === 'personal' ? 'global' : 'personal'"
              :class="[
                'btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none',
                selectedView === 'global' ? 'bg-[#5E936C]' : ''
              ]"
            >
              {{ selectedView === 'personal' ? 'Personal' : 'Global' }} View
            </button>
            
            <button 
              @click="fetchUserData"
              :disabled="isLoading"
              class="btn bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none"
            >
              {{ isLoading ? 'Loading...' : 'Refresh' }}
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center flex-1">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-sage mx-auto mb-4"></div>
            <p class="text-sage text-lg">Loading composting data...</p>
          </div>
        </div>

        <!-- No Data State -->
        <div v-else-if="!hasData && selectedUser" class="flex items-center justify-center flex-1">
          <div class="card bg-sage shadow-b max-w-2xl w-full">
            <div class="card-body p-6 text-center">
              <h2 class="text-xl font-semibold mb-4">No Composting Data Found</h2>
              <p class="text-sm mb-6">{{ selectedUser }} hasn't started logging compost materials yet.</p>
              
              <div class="bg-deepgreen/20 rounded-lg p-4 mb-6">
                <h3 class="font-semibold mb-2">Getting Started:</h3>
                <ol class="text-sm text-left space-y-1">
                  <li>1. Open NutriBot Telegram chatbot</li>
                  <li>2. Use the Compost Feeding feature</li>
                  <li>3. Log greens, browns, and water amounts</li>
                  <li>4. Return here to see CO₂ impact!</li>
                </ol>
              </div>
              
              <div class="grid grid-cols-3 gap-4 text-xs">
                <div class="bg-deepgreen/20 p-3 rounded">
                  <div class="font-semibold">🥬 Greens</div>
                  <div>Food scraps, fresh leaves</div>
                </div>
                <div class="bg-deepgreen/20 p-3 rounded">
                  <div class="font-semibold">🍂 Browns</div>
                  <div>Dry leaves, paper, cardboard</div>
                </div>
                <div class="bg-deepgreen/20 p-3 rounded">
                  <div class="font-semibold">💧 Water</div>
                  <div>Moisture for decomposition</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No User Selected -->
        <div v-else-if="!selectedUser" class="flex items-center justify-center flex-1">
          <div class="card bg-sage shadow-b max-w-md w-full">
            <div class="card-body p-6 text-center">
              <h2 class="text-xl font-semibold mb-4">Select a User</h2>
              <p class="text-sm">Choose a user from the dropdown above to view their CO₂ savings data.</p>
              <div class="mt-4 text-xs text-sage">
                <p>Total: {{ userStats?.totalUsers || 0 }} users</p>
                <p>With data: {{ userStats?.usersWithData || 0 }} • Need to start: {{ userStats?.usersWithoutData || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Dashboard Content -->
        <div v-else-if="hasData" class="flex flex-1 flex-col gap-4">
          
          <!-- Personal View -->
          <div v-if="selectedView === 'personal'" class="flex flex-1 flex-col gap-4">
            <!-- Top Section: KPI Cards + Monthly Trend Chart -->
            <div class="flex gap-4 h-1/2">
              <!-- 4 KPI Cards in 2x2 grid -->
              <div class="grid grid-cols-2 grid-rows-2 gap-2.5 w-[45%]">
                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Total Food Waste</h2>
                      <p class="text-sm font-medium">{{ userData.totalFoodWasteKg.toFixed(2) }} kg</p>
                      <p class="text-xs text-sage mt-1">{{ userData.feedingLogsCount }} feeding logs</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">CO₂ Saved</h2>
                      <p class="text-sm font-medium">{{ userData.totalCO2SavedKg.toFixed(2) }} kg</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Trees Equivalent</h2>
                      <p class="text-sm font-medium">{{ userData.treesEquivalent.toFixed(1) }}</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Car Miles Offset</h2>
                      <p class="text-sm font-medium">{{ userData.carMilesEquivalent.toFixed(0) }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right: Monthly Trend Chart -->
              <div class="card bg-sage shadow-b flex-1">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">Monthly CO₂ Savings Trend</h2>
                  <div class="flex-1 h-full flex items-center justify-center">
                    <p class="text-xs text-sage">Chart Component Integration Needed</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom Section: Recent Logs + Impact Breakdown -->
            <div class="flex gap-4 h-1/2">
              <!-- Recent Feeding Logs -->
              <div class="card bg-sage shadow-b w-[65%]">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">Recent Feeding Logs</h2>
                  <div class="flex-1 overflow-y-auto space-y-2">
                    <div 
                      v-for="(log, index) in feedingLogs.slice(0, 8)" 
                      :key="index"
                      class="bg-deepgreen/20 rounded p-2 flex justify-between items-center"
                    >
                      <div class="flex-1">
                        <div class="text-xs font-medium">{{ formatDate(log.created_at) }}</div>
                        <div class="text-xs text-sage">
                          🥬 {{ log.greens }}g • 🍂 {{ log.browns }}g • 💧 {{ log.water }}ml
                        </div>
                      </div>
                      <div class="text-right text-xs">
                        <div class="font-medium">{{ calculateLogFoodWaste(log).toFixed(2) }} kg</div>
                        <div class="text-sage">{{ calculateLogCO2(log).toFixed(2) }} kg CO₂</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-3 p-2 bg-deepgreen/20 rounded text-center">
                    <p class="text-xs font-medium">🌱 Keep it up, {{ selectedUser }}!</p>
                    <p class="text-xs text-sage">Continue logging to track environmental impact.</p>
                  </div>
                </div>
              </div>

              <!-- Impact Summary -->
              <div class="card bg-sage shadow-b w-[35%]">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">Environmental Impact</h2>
                  <div class="flex-1 space-y-4">
                    <div class="text-center">
                      <div class="text-lg font-bold">{{ userData.totalCO2SavedKg.toFixed(1) }} kg</div>
                      <div class="text-xs text-sage">Total CO₂ Saved</div>
                    </div>
                    
                    <div class="space-y-2 text-xs">
                      <div class="flex justify-between">
                        <span>🌳 Trees planted equiv:</span>
                        <span class="font-medium">{{ userData.treesEquivalent.toFixed(1) }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>🚗 Car miles offset:</span>
                        <span class="font-medium">{{ userData.carMilesEquivalent.toFixed(0) }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>⛽ Petrol saved (L):</span>
                        <span class="font-medium">{{ userData.petrolLitresEquivalent.toFixed(1) }}</span>
                      </div>
                    </div>

                    <div class="bg-deepgreen/20 rounded p-2 text-center">
                      <div class="text-xs text-sage">Last updated:</div>
                      <div class="text-xs font-medium">{{ lastUpdated ? formatDateTime(lastUpdated) : 'Never' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Global View -->
          <div v-else class="flex flex-1 flex-col gap-4">
            <!-- Top Section: Global KPI Cards + Global Trend -->
            <div class="flex gap-4 h-1/2">
              <!-- 5 Global KPI Cards -->
              <div class="grid grid-cols-5 gap-2.5 w-[70%]">
                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Total Users</h2>
                      <p class="text-sm font-medium">{{ globalStats.totalUsers.toLocaleString() }}</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Global Food Waste</h2>
                      <p class="text-sm font-medium">{{ globalStats.globalFoodWaste.toLocaleString() }} kg</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Global CO₂ Saved</h2>
                      <p class="text-sm font-medium">{{ globalStats.globalCO2Saved.toLocaleString() }} kg</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Trees Planted Equiv.</h2>
                      <p class="text-sm font-medium">{{ globalStats.treesPlanted.toFixed(0) }}</p>
                    </div>
                  </div>
                </div>

                <div class="card bg-sage shadow-b">
                  <div class="card-body p-3 h-full flex flex-col justify-between">
                    <div>
                      <h2 class="card-title text-xs font-semibold">Avg per User</h2>
                      <p class="text-sm font-medium">{{ globalStats.avgPerUser.toFixed(1) }} kg CO₂</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right: Global Impact Summary -->
              <div class="card bg-sage shadow-b flex-1">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">🌍 Collective Impact</h2>
                  <div class="flex-1 flex flex-col justify-center text-center space-y-4">
                    <div>
                      <div class="text-2xl font-bold">{{ globalStats.globalCO2Saved.toLocaleString() }} kg</div>
                      <div class="text-xs text-sage">Total CO₂ Saved by All Users</div>
                    </div>
                    
                    <div class="space-y-2 text-xs">
                      <div>Equivalent to planting <span class="font-bold">{{ globalStats.treesPlanted.toFixed(0) }}</span> trees</div>
                      <div>Or taking a car off the road for <span class="font-bold">{{ (globalStats.globalCO2Saved / CAR_CO2_FACTOR / 365).toFixed(0) }}</span> days</div>
                    </div>

                    <div class="bg-deepgreen/20 rounded p-2">
                      <div class="text-xs">{{ globalStats.totalUsers }} users making a difference</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom Section: User Distribution + Top Contributors -->
            <div class="flex gap-4 h-1/2">
              <!-- User Statistics -->
              <div class="card bg-sage shadow-b w-[45%]">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">User Distribution</h2>
                  <div class="flex-1 flex flex-col justify-center space-y-4">
                    <div class="grid grid-cols-2 gap-4 text-center">
                      <div class="bg-deepgreen/20 rounded p-3">
                        <div class="text-lg font-bold">{{ userStats?.usersWithData || 0 }}</div>
                        <div class="text-xs text-sage">Active Users</div>
                      </div>
                      <div class="bg-deepgreen/20 rounded p-3">
                        <div class="text-lg font-bold">{{ userStats?.usersWithoutData || 0 }}</div>
                        <div class="text-xs text-sage">Need to Start</div>
                      </div>
                    </div>
                    
                    <div class="bg-deepgreen/20 rounded p-2 text-center">
                      <div class="text-xs">
                        {{ ((userStats?.usersWithData || 0) / (userStats?.totalUsers || 1) * 100).toFixed(1) }}% 
                        participation rate
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Top Contributors -->
              <div class="card bg-sage shadow-b w-[55%]">
                <div class="card-body h-full p-3 flex flex-col">
                  <h2 class="card-title text-xs font-semibold mb-2">Top Contributors (CO₂ Saved)</h2>
                  <div class="flex-1 overflow-y-auto space-y-2">
                    <div 
                      v-for="(user, index) in usersWithData.slice(0, 10)" 
                      :key="user.username"
                      class="bg-deepgreen/20 rounded p-2 flex justify-between items-center"
                    >
                      <div class="flex items-center gap-2">
                        <div class="text-xs font-bold w-6 text-center">{{ index + 1 }}</div>
                        <div class="text-xs font-medium">{{ user.username }}</div>
                      </div>
                      <div class="text-right text-xs">
                        <div class="font-medium">{{ user.feedingLogsCount }} logs</div>
                        <div class="text-sage">Estimated impact</div>
                      </div>
                    </div>
                  </div>
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
import { ref, onMounted } from 'vue'

export default {
  name: 'CO2ESavingsDashboard',
  setup() {
    // Reactive data
    const isLoading = ref(true)
    const hasData = ref(false)
    const lastUpdated = ref(null)
    const selectedView = ref('personal')
    const selectedUser = ref('')
    
    // User lists
    const allUsers = ref([])
    const usersWithData = ref([])
    const usersWithoutData = ref([])
    const userStats = ref(null)

    const userData = ref({
      username: '',
      totalFoodWasteKg: 0,
      totalCO2SavedKg: 0,
      tankVolume: 17,
      soilVolume: 10,
      treesEquivalent: 0,
      petrolLitresEquivalent: 0,
      carMilesEquivalent: 0,
      feedingLogsCount: 0
    })

    const feedingLogs = ref([])
    const monthlyData = ref([])
    const globalStats = ref({
      totalUsers: 0,
      globalFoodWaste: 0,
      globalCO2Saved: 0,
      treesPlanted: 0,
      avgPerUser: 0
    })

    // Constants
    const API_BASE_URL = 'http://localhost:3001/api'
    const FOOD_WASTE_CO2_FACTOR = 2.5
    const COMPOST_REDUCTION_FACTOR = 0.8
    const TREE_CO2_ABSORPTION = 21.9
    const PETROL_CO2_FACTOR = 2.33
    const CAR_CO2_FACTOR = 0.454
    const STP_CO2_PPM = 415.0
    const STP_AIR_CONCENTRATION_PERCENT = 21.0

    // Methods
    const calculateCO2Saved = (foodWasteKg, tankVolume, soilVolume) => {
      const airConc = STP_AIR_CONCENTRATION_PERCENT / 100
      const effectiveVolume = tankVolume - (soilVolume * airConc)
      const baselineCO2Grams = (STP_CO2_PPM / 1_000_000) * effectiveVolume * 1.8
      
      const co2SavedLandfillKg = foodWasteKg * FOOD_WASTE_CO2_FACTOR * COMPOST_REDUCTION_FACTOR
      const co2SavedLandfillG = co2SavedLandfillKg * 1000
      
      const totalSavedG = baselineCO2Grams + co2SavedLandfillG
      const totalSavedKg = totalSavedG / 1000
      
      return {
        totalCO2SavedKg: totalSavedKg,
        treesEquivalent: totalSavedKg / TREE_CO2_ABSORPTION,
        petrolLitresEquivalent: totalSavedKg / PETROL_CO2_FACTOR,
        carMilesEquivalent: totalSavedKg / CAR_CO2_FACTOR
      }
    }

    // Fetch all users with their data status
    const fetchUsers = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/users-with-data`)
        const data = await response.json()
        
        if (data.success) {
          allUsers.value = data.data.users
          usersWithData.value = data.data.users.filter(u => u.hasData)
          usersWithoutData.value = data.data.users.filter(u => !u.hasData)
          userStats.value = {
            totalUsers: data.data.totalUsers,
            usersWithData: data.data.usersWithData,
            usersWithoutData: data.data.usersWithoutData
          }
        }
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    }

    const fetchUserData = async () => {
      if (!selectedUser.value) return
      
      isLoading.value = true
      
      try {
        // Fetch personal CO2 impact data
        const personalResponse = await fetch(`${API_BASE_URL}/user/${selectedUser.value}/co2-impact`)
        const personalData = await personalResponse.json()
        
        // Fetch global statistics
        const globalResponse = await fetch(`${API_BASE_URL}/global-stats`)
        const globalData = await globalResponse.json()
        
        if (personalData.success) {
          if (personalData.hasData) {
            // User has feeding logs data
            userData.value = {
              ...userData.value,
              username: personalData.data.user.username,
              totalFoodWasteKg: personalData.data.totalFoodWasteKg,
              totalCO2SavedKg: personalData.data.totalCO2SavedKg,
              tankVolume: personalData.data.user.tankVolume,
              soilVolume: personalData.data.user.soilVolume,
              treesEquivalent: personalData.data.impact.treesEquivalent,
              petrolLitresEquivalent: personalData.data.impact.petrolLitresEquivalent,
              carMilesEquivalent: personalData.data.impact.carMilesEquivalent,
              feedingLogsCount: personalData.data.feedingLogsCount
            }

            feedingLogs.value = personalData.data.feedingLogs
            monthlyData.value = personalData.data.monthlyData
            hasData.value = true
          } else {
            // No feeding logs found
            hasData.value = false
          }
        } else {
          console.error('Error fetching personal data:', personalData.message)
          hasData.value = false
        }

        if (globalData.success) {
          globalStats.value = {
            totalUsers: globalData.data.totalUsers,
            globalFoodWaste: globalData.data.globalFoodWaste,
            globalCO2Saved: globalData.data.globalCO2Saved,
            treesPlanted: globalData.data.treesPlanted,
            avgPerUser: globalData.data.avgPerUser
          }
        }

        lastUpdated.value = new Date()
      } catch (error) {
        console.error('Error fetching data:', error)
        hasData.value = false
      }
      
      isLoading.value = false
    }

    const onUserChange = () => {
      if (selectedUser.value) {
        fetchUserData()
      } else {
        hasData.value = false
      }
    }

    const calculateLogFoodWaste = (log) => {
      return ((parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0)) / 1000
    }

    const calculateLogCO2 = (log) => {
      const foodWasteKg = calculateLogFoodWaste(log)
      const result = calculateCO2Saved(foodWasteKg, userData.value.tankVolume, userData.value.soilVolume)
      return result.totalCO2SavedKg
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (date) => {
      return date.toLocaleString()
    }

    // Lifecycle
    onMounted(async () => {
      isLoading.value = true
      await fetchUsers()
      isLoading.value = false
    })

    return {
      // Reactive data
      isLoading,
      hasData,
      lastUpdated,
      selectedView,
      selectedUser,
      userData,
      feedingLogs,
      monthlyData,
      globalStats,
      allUsers,
      usersWithData,
      usersWithoutData,
      userStats,
      
      // Constants
      CAR_CO2_FACTOR,
      
      // Methods
      fetchUsers,
      fetchUserData,
      onUserChange,
      calculateLogFoodWaste,
      calculateLogCO2,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
/* Custom utilities matching your theme */
.bg-deepgreen {
  background-color: #0D2705;
}

.bg-sage {
  background-color: #0B4F26;
}

.text-cream {
  color: #F7FFF2;
}

.text-sage {
  color: #D7EDBC;
}

.shadow-b {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Override select styling */
select option {
  background-color: #0D2705 !important;
  color: #F7FFF2 !important;
}

select optgroup {
  background-color: #0D2705 !important;
  color: #D7EDBC !important;
  font-weight: bold;
}
</style>