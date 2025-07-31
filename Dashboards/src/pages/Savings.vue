<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-3">
          <Leaf class="text-green-600" :size="40" />
          CO₂E Savings Dashboard
          <Globe class="text-blue-600" :size="40" />
        </h1>
        <p v-if="selectedUser" class="text-xl text-gray-700 mb-2">
          Viewing <span class="font-semibold text-green-600">{{ selectedUser }}</span>'s environmental impact 👋
        </p>
        <p class="text-gray-600 text-lg">Track environmental impact through composting</p>
        <p v-if="lastUpdated" class="text-sm text-gray-500 mt-2">
          Last updated: {{ formatDateTime(lastUpdated) }}
        </p>
      </div>

      <!-- User Selector -->
      <div class="max-w-md mx-auto mb-8">
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h2 class="text-lg font-semibold text-gray-800 mb-4 text-center">Select a User</h2>
          
          <div class="relative">
            <select 
              v-model="selectedUser" 
              @change="onUserChange"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="">Choose a user...</option>
              <optgroup label="Users with Composting Data" v-if="usersWithData.length > 0">
                <option 
                  v-for="user in usersWithData" 
                  :key="user.username" 
                  :value="user.username"
                >
                  {{ user.username }} ({{ user.feedingLogsCount }} logs)
                </option>
              </optgroup>
              <optgroup label="Users without Data" v-if="usersWithoutData.length > 0">
                <option 
                  v-for="user in usersWithoutData" 
                  :key="user.username" 
                  :value="user.username"
                >
                  {{ user.username }} (No data yet)
                </option>
              </optgroup>
            </select>
            <ChevronDown class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" :size="20" />
          </div>
          
          <div v-if="userStats" class="mt-4 text-sm text-gray-600 text-center">
            Total: {{ userStats.totalUsers }} users • 
            With data: {{ userStats.usersWithData }} • 
            Need to start: {{ userStats.usersWithoutData }}
          </div>
        </div>
      </div>
      <div v-if="isLoading" class="flex items-center justify-center min-h-96">
        <div class="text-center">
          <RefreshCw class="animate-spin text-green-600 mx-auto mb-4" :size="48" />
          <p class="text-gray-600 text-lg">Loading your composting data...</p>
        </div>
      </div>

      <!-- No Data State -->
      <div v-else-if="!hasData" class="max-w-4xl mx-auto">
        <div class="bg-white rounded-xl shadow-lg p-8 text-center">
          <div class="mb-6">
            <Database class="mx-auto text-gray-400" :size="80" />
          </div>
          
          <h2 class="text-2xl font-semibold text-gray-800 mb-4">
            No Composting Data Found
          </h2>
          
          <p class="text-gray-600 text-lg mb-6">
            Start tracking your environmental impact by logging your compost materials!
          </p>
          
          <div class="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg mb-6">
            <div class="flex items-start">
              <MessageCircle class="text-blue-500 mt-1 mr-3" :size="24" />
              <div class="text-left">
                <h3 class="text-blue-800 font-semibold mb-2">
                  Hey {{ userData.username || 'there' }}! 👋 Here's how to get started:
                </h3>
                <ol class="text-blue-700 space-y-2">
                  <li>1. Open your NutriBot Telegram chatbot</li>
                  <li>2. Use the <strong>Compost Feeding</strong> feature</li>
                  <li>3. Log your greens, browns, and water amounts</li>
                  <li>4. Return here to see your CO₂ impact!</li>
                </ol>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-sm">
            <div class="bg-green-50 p-4 rounded-lg">
              <div class="text-green-600 font-semibold mb-1">🥬 Greens</div>
              <div class="text-green-700">Food scraps, fresh leaves</div>
            </div>
            <div class="bg-amber-50 p-4 rounded-lg">
              <div class="text-amber-600 font-semibold mb-1">🍂 Browns</div>
              <div class="text-amber-700">Dry leaves, paper, cardboard</div>
            </div>
            <div class="bg-blue-50 p-4 rounded-lg">
              <div class="text-blue-600 font-semibold mb-1">💧 Water</div>
              <div class="text-blue-700">Moisture for decomposition</div>
            </div>
          </div>

          <button 
            @click="fetchUserData"
            :disabled="isLoading"
            class="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2 mx-auto"
          >
            <RefreshCw :class="{'animate-spin': isLoading}" :size="16" />
            {{ isLoading ? 'Checking for Data...' : 'Refresh Data' }}
          </button>
        </div>
      </div>

      <!-- Main Dashboard with Data -->
      <div v-else-if="selectedUser && hasData">
        <!-- View Toggle -->
        <div class="flex justify-center mb-6">
          <div class="bg-white rounded-lg p-1 shadow-md">
            <button
              @click="selectedView = 'personal'"
              :class="[
                'px-6 py-2 rounded-md transition-all flex items-center gap-2',
                selectedView === 'personal' 
                  ? 'bg-green-500 text-white shadow-md' 
                  : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              <User :size="16" />
              Personal Impact
            </button>
            <button
              @click="selectedView = 'global'"
              :class="[
                'px-6 py-2 rounded-md transition-all flex items-center gap-2',
                selectedView === 'global' 
                  ? 'bg-blue-500 text-white shadow-md' 
                  : 'text-gray-600 hover:bg-gray-100'
              ]"
            >
              <Globe :size="16" />
              Global Impact
            </button>
          </div>
        </div>

        <!-- Refresh Button -->
        <div class="flex justify-center mb-6">
          <button 
            @click="fetchUserData"
            :disabled="isLoading"
            class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
          >
            <RefreshCw :class="{'animate-spin': isLoading}" :size="16" />
            Refresh Data
          </button>
        </div>

        <!-- Personal View -->
        <div v-if="selectedView === 'personal'">
          <!-- Personal Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-green-100 rounded-lg">
                  <Leaf class="text-green-600" :size="24" />
                </div>
                <TrendingUp class="text-green-500" :size="20" />
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Total Food Waste</h3>
              <p class="text-2xl font-bold text-gray-900">{{ userData.totalFoodWasteKg.toFixed(2) }} kg</p>
              <p class="text-xs text-gray-500 mt-1">{{ userData.feedingLogsCount }} feeding logs</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-blue-100 rounded-lg">
                  <Globe class="text-blue-600" :size="24" />
                </div>
                <TrendingUp class="text-blue-500" :size="20" />
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">CO₂ Saved</h3>
              <p class="text-2xl font-bold text-gray-900">{{ userData.totalCO2SavedKg.toFixed(2) }} kg</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-emerald-100 rounded-lg">
                  <TreePine class="text-emerald-600" :size="24" />
                </div>
                <TrendingUp class="text-emerald-500" :size="20" />
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Trees Equivalent</h3>
              <p class="text-2xl font-bold text-gray-900">{{ userData.treesEquivalent.toFixed(1) }}</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-amber-100 rounded-lg">
                  <Car class="text-amber-600" :size="24" />
                </div>
                <TrendingUp class="text-amber-500" :size="20" />
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Car Miles Offset</h3>
              <p class="text-2xl font-bold text-gray-900">{{ userData.carMilesEquivalent.toFixed(0) }}</p>
            </div>
          </div>

          <!-- Charts Row -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Monthly Trend Chart -->
            <div class="bg-white rounded-xl shadow-lg p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Monthly CO₂ Savings Trend</h2>
              <div class="h-80">
                <!-- You'll need to install a Vue chart library like vue-chartjs or @vue/compat for charts -->
                <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
                  <p class="text-gray-500">Chart Component - Install vue-chartjs or similar</p>
                </div>
              </div>
            </div>

            <!-- Recent Feeding Logs -->
            <div class="bg-white rounded-xl shadow-lg p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Recent Feeding Logs</h2>
              <div class="space-y-3">
                <div 
                  v-for="(log, index) in feedingLogs.slice(0, 5)" 
                  :key="index"
                  class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <div class="font-medium text-gray-800">{{ formatDate(log.created_at) }}</div>
                    <div class="text-sm text-gray-600">
                      🥬 {{ log.greens }}g • 🍂 {{ log.browns }}g • 💧 {{ log.water }}ml
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="font-semibold text-green-600">{{ calculateLogFoodWaste(log).toFixed(2) }} kg</div>
                    <div class="text-xs text-gray-500">{{ calculateLogCO2(log).toFixed(2) }} kg CO₂</div>
                  </div>
                </div>
              </div>
              
              <div class="mt-6 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                <p class="text-green-800 font-medium">🌱 Keep it up, {{ selectedUser }}!</p>
                <p class="text-green-700 text-sm mt-1">
                  Continue logging compost materials in the NutriBot to track environmental impact.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Global View -->
        <div v-else class="space-y-8">
          <!-- Global Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-purple-100 rounded-lg">
                  <User class="text-purple-600" :size="24" />
                </div>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Total Users</h3>
              <p class="text-2xl font-bold text-gray-900">{{ globalStats.totalUsers.toLocaleString() }}</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-green-100 rounded-lg">
                  <Leaf class="text-green-600" :size="24" />
                </div>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Global Food Waste</h3>
              <p class="text-2xl font-bold text-gray-900">{{ globalStats.globalFoodWaste.toLocaleString() }} kg</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-blue-100 rounded-lg">
                  <Globe class="text-blue-600" :size="24" />
                </div>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Global CO₂ Saved</h3>
              <p class="text-2xl font-bold text-gray-900">{{ globalStats.globalCO2Saved.toLocaleString() }} kg</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-emerald-100 rounded-lg">
                  <TreePine class="text-emerald-600" :size="24" />
                </div>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Trees Planted Equiv.</h3>
              <p class="text-2xl font-bold text-gray-900">{{ globalStats.treesPlanted.toFixed(0) }}</p>
            </div>

            <div class="bg-white rounded-xl shadow-lg p-6">
              <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-amber-100 rounded-lg">
                  <TrendingUp class="text-amber-600" :size="24" />
                </div>
              </div>
              <h3 class="text-sm font-medium text-gray-600 mb-1">Avg per User</h3>
              <p class="text-2xl font-bold text-gray-900">{{ globalStats.avgPerUser.toFixed(1) }} kg CO₂</p>
            </div>
          </div>

          <!-- Global Impact Message -->
          <div class="bg-gradient-to-r from-green-500 to-blue-500 rounded-xl shadow-lg p-8 text-center text-white">
            <h2 class="text-3xl font-bold mb-4">🌍 Collective Impact</h2>
            <p class="text-xl mb-4">
              Together, NutriBot users have saved over <strong>{{ globalStats.globalCO2Saved.toLocaleString() }} kg of CO₂</strong>
            </p>
            <p class="text-lg opacity-90">
              That's equivalent to planting <strong>{{ globalStats.treesPlanted.toFixed(0) }} trees</strong> or 
              taking a car off the road for <strong>{{ (globalStats.globalCO2Saved / CAR_CO2_FACTOR / 365).toFixed(0) }} days</strong>!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { 
  Leaf, TreePine, Car, Droplets, TrendingUp, RefreshCw, 
  Globe, User, MessageCircle, Database, ChevronDown 
} from 'lucide-vue-next'

export default {
  name: 'CO2ESavingsDashboard',
  components: {
    Leaf, TreePine, Car, Droplets, TrendingUp, RefreshCw,
    Globe, User, MessageCircle, Database, ChevronDown
  },
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
/* Add any custom styles here if needed */
</style>