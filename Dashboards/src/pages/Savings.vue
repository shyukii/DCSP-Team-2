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

          <!-- Right: User Selector Dropdown - Fixed Alignment -->
          <div class="flex space-x-2 items-end">
            <!-- User Selector - Only show in Personal View -->
            <select 
              v-if="selectedView === 'personal'"
              v-model="selectedUser" 
              @change="onUserChange"
              class="bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 transition-all duration-300"
              :style="{ width: `${calculateDropdownWidth(selectedUser)}px` }"
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
                'bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10',
                selectedView === 'global' ? 'bg-[#5E936C]' : ''
              ]"
            >
              {{ selectedView === 'personal' ? 'Personal' : 'Global' }} View
            </button>
            
            <button 
              @click="selectedView === 'personal' ? fetchUserData() : fetchGlobalData()"
              :disabled="isLoading"
              class="bg-sage hover:bg-[#5E936C]/50 border-transparent text-white px-6 py-2 text-sm rounded-md transition-colors border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none h-10 disabled:opacity-50 disabled:cursor-not-allowed"
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

        <!-- No Data State - Only show in Personal View when user has no data -->
        <div v-else-if="!hasData && selectedUser && selectedView === 'personal'" class="flex items-center justify-center flex-1 p-4">
          <div class="max-w-4xl w-full mx-auto">
            <!-- Main Card -->
            <div class="bg-sage/80 backdrop-blur-sm rounded-2xl shadow-2xl border border-sage/30 overflow-hidden">
              <!-- Header Section -->
              <div class="bg-gradient-to-r from-sage to-[#5E936C] p-6 text-center">
                <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span class="text-2xl">🌱</span>
                </div>
                <h2 class="text-xl font-bold text-white mb-1">Ready to Start Composting?</h2>
                <p class="text-cream/90">{{ selectedUser }} hasn't logged any compost materials yet</p>
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
                          <div class="font-semibold text-white text-sm">Use Compost Feeding Feature</div>
                          <div class="text-sage text-xs">Find the composting option in the menu</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">3</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Log Your Materials</div>
                          <div class="text-sage text-xs">Record greens, browns, and water amounts</div>
                        </div>
                      </div>
                      
                      <div class="flex items-center gap-3 p-3 bg-deepgreen/40 rounded-lg border border-sage/20">
                        <div class="w-6 h-6 bg-sage rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs">4</div>
                        <div>
                          <div class="font-semibold text-white text-sm">Track Your Impact</div>
                          <div class="text-sage text-xs">Return here to see your CO₂ savings!</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Right: Material Types -->
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Material Types</h3>
                    <div class="space-y-3">
                      <div class="text-center p-4 bg-gradient-to-r from-green-500/20 to-green-600/10 rounded-lg border border-green-500/30">
                        <div class="text-2xl mb-2">🥬</div>
                        <div class="font-bold text-white text-sm mb-1">Greens</div>
                        <div class="text-sage text-xs">Food scraps, fresh leaves, vegetable peels</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-amber-600/20 to-amber-700/10 rounded-lg border border-amber-600/30">
                        <div class="text-2xl mb-2">🍂</div>
                        <div class="font-bold text-white text-sm mb-1">Browns</div>
                        <div class="text-sage text-xs">Dry leaves, paper, cardboard, twigs</div>
                      </div>
                      
                      <div class="text-center p-4 bg-gradient-to-r from-blue-500/20 to-blue-600/10 rounded-lg border border-blue-500/30">
                        <div class="text-2xl mb-2">💧</div>
                        <div class="font-bold text-white text-sm mb-1">Water</div>
                        <div class="text-sage text-xs">Moisture for optimal decomposition</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Footer -->
              <div class="bg-deepgreen/60 px-6 py-3 text-center border-t border-sage/20">
                <div class="flex items-center justify-center gap-2 text-sage">
                  <span class="text-lg">🌍</span>
                  <span class="text-xs">Start composting today and make a positive environmental impact!</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No User Selected - Only show in Personal View -->
        <div v-else-if="!selectedUser && selectedView === 'personal'" class="flex items-center justify-center flex-1">
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
        <div v-else-if="(hasData && selectedView === 'personal') || selectedView === 'global'" class="flex flex-1 flex-col gap-4">
          
          <!-- Personal View -->
          <div v-if="selectedView === 'personal'" class="flex flex-1 flex-col gap-4">
            <!-- Top Section: Hero Stats + Monthly Trend Chart - 50% height -->
            <div class="flex gap-4 flex-1">
              <!-- Left: Key Metrics in 2x2 Grid -->
              <div class="grid grid-cols-2 gap-3 w-80">
                <!-- Total Food Waste -->
                <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-sm">🥬</span>
                    </div>
                    <div class="text-xs opacity-80">Total</div>
                  </div>
                  <div>
                    <div class="text-xl font-bold">{{ formatNumber(userData.totalFoodWasteKg) }}</div>
                    <div class="text-xs opacity-80">kg Food Waste</div>
                  </div>
                </div>

                <!-- CO₂ Saved -->
                <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-sm">🌍</span>
                    </div>
                    <div class="text-xs opacity-80">Saved</div>
                  </div>
                  <div>
                    <div class="text-xl font-bold">{{ formatNumber(userData.totalCO2SavedKg) }}</div>
                    <div class="text-xs opacity-80">kg CO₂ Saved</div>
                  </div>
                </div>

                <!-- Trees Equivalent -->
                <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-sm">🌳</span>
                    </div>
                    <div class="text-xs opacity-80">Equiv.</div>
                  </div>
                  <div>
                    <div class="text-xl font-bold">{{ formatNumber(userData.treesEquivalent, 2) }}</div>
                    <div class="text-xs opacity-80">Trees Planted</div>
                  </div>
                </div>

                <!-- Car Miles Offset -->
                <div class="bg-sage rounded-xl p-4 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-sm">🚗</span>
                    </div>
                    <div class="text-xs opacity-80">Offset</div>
                  </div>
                  <div>
                    <div class="text-xl font-bold">{{ formatNumber(userData.carMilesEquivalent, 1) }}</div>
                    <div class="text-xs opacity-80">Car Miles</div>
                  </div>
                </div>
              </div>

              <!-- Right: CO₂ Savings Trend Chart -->
              <div class="bg-sage rounded-xl flex-1">
                <div class="p-3 h-full flex flex-col">
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm font-semibold text-white">CO₂ Savings Trend</h3>
                    <div class="flex items-center gap-2 text-white text-xs">
                      <div class="w-2 h-2 bg-white rounded-full"></div>
                      <span>Each Log</span>
                    </div>
                  </div>
                  <div class="flex-1 relative min-h-0">
                    <!-- Chart Container -->
                    <div v-if="feedingLogs && feedingLogs.length > 0" class="h-full w-full">
                      <svg class="w-full h-full" viewBox="0 0 480 120" preserveAspectRatio="xMidYMid meet">
                        <defs>
                          <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.3"/>
                            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.1"/>
                          </linearGradient>
                        </defs>
                        
                        <!-- Area under the curve -->
                        <path v-if="getLogChartPath()"
                              :d="getLogChartPath() + ` L ${getLogChartPoints()[getLogChartPoints().length - 1]?.x || 0} 75 L 50 75 Z`"
                              fill="url(#chartGradient)"
                              opacity="0.8" />

                        <!-- Main trend line -->
                        <path v-if="getLogChartPath()"
                              :d="getLogChartPath()"
                              stroke="#ffffff"
                              stroke-width="2"
                              fill="none"
                              stroke-linecap="round"
                              stroke-linejoin="round" />

                        <!-- Data points -->
                        <g v-for="(point, index) in getLogChartPoints()" :key="`point-${index}`">
                          <circle :cx="point.x" :cy="point.y" r="3" 
                                  fill="#ffffff" stroke="#0B4F26" stroke-width="1.5" />
                          <!-- Hover tooltip background -->
                          <circle :cx="point.x" :cy="point.y" r="6" 
                                  fill="transparent" class="cursor-pointer hover:fill-white hover:fill-opacity-10" />
                        </g>

                        <!-- Y-axis labels -->
                        <g fill="#F7FFF2" font-size="8" text-anchor="end" opacity="0.8">
                          <text v-for="i in 4" :key="`y-label-${i}`"
                                :x="35" :y="19 + (i-1) * 20">
                            {{ formatNumber(getMaxLogCO2Value() * (1 - (i-1)/3), 2) }}
                          </text>
                        </g>

                        <!-- X-axis labels (log dates) -->
                        <g fill="#F7FFF2" font-size="7" text-anchor="middle" opacity="0.8">
                          <text v-for="(log, index) in getRecentLogs().slice(0, 8)" :key="`x-label-${index}`"
                                :x="50 + (index * (380 / Math.max(getRecentLogs().slice(0, 8).length - 1, 1)))" 
                                :y="100">
                            {{ formatLogDate(log.created_at) }}
                          </text>
                        </g>
                      </svg>
                    </div>
                    
                    <!-- No data state -->
                    <div v-else class="h-full flex items-center justify-center">
                      <div class="text-center">
                        <div class="w-8 h-8 bg-sage/20 rounded-full flex items-center justify-center mx-auto mb-1">
                          <span class="text-sm">📈</span>
                        </div>
                        <p class="text-cream/60 text-xs">Start logging to see trends</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom Section: Recent Activity + Impact Summary - 50% height -->
            <div class="flex gap-4 flex-1 min-h-0">
              <!-- Recent Feeding Logs -->
              <div class="bg-sage rounded-xl flex-1">
                <div class="p-4 h-full flex flex-col">
                  <div class="flex items-center justify-between mb-3">
                    <h3 class="text-sm font-semibold text-white">Recent Activity</h3>
                    <div class="text-sage text-xs">Last {{ Math.min(feedingLogs.length, 8) }} entries</div>
                  </div>
                  
                  <div class="flex-1 overflow-y-auto space-y-0 min-h-0">
                    <div 
                      v-for="(log, index) in feedingLogs.slice(0, 8)" 
                      :key="index"
                      :class="[
                        'bg-deepgreen/20 hover:bg-deepgreen/30 rounded-lg p-3 transition-colors',
                        index !== feedingLogs.slice(0, 8).length - 1 ? 'border-b border-sage/20 mb-2' : ''
                      ]"
                    >
                      <div class="flex justify-between items-start">
                        <div class="flex-1">
                          <div class="text-white font-medium text-xs mb-1">{{ formatDate(log.created_at) }}</div>
                          <div class="flex items-center gap-3 text-xs">
                            <div class="flex items-center gap-1">
                              <span>🥬</span>
                              <span class="text-sage">{{ log.greens }}g</span>
                            </div>
                            <div class="flex items-center gap-1">
                              <span>🍂</span>
                              <span class="text-sage">{{ log.browns }}g</span>
                            </div>
                            <div class="flex items-center gap-1">
                              <span>💧</span>
                              <span class="text-sage">{{ log.water }}ml</span>
                            </div>
                          </div>
                        </div>
                        <div class="text-right ml-3">
                          <div class="text-white font-semibold text-xs">{{ formatNumber(calculateLogFoodWaste(log)) }} kg</div>
                          <div class="text-emerald-400 text-xs">{{ formatNumber(calculateLogCO2(log)) }} kg CO₂</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Motivational Footer -->
                  <div class="mt-3 p-3 bg-deepgreen/20 rounded-lg">
                    <div class="flex items-center gap-2">
                      <div class="w-6 h-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
                        <span class="text-xs">🌱</span>
                      </div>
                      <div>
                        <p class="text-white font-medium text-xs">Great work, {{ selectedUser }}!</p>
                        <p class="text-sage text-xs">Keep logging to maximize your environmental impact</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Environmental Impact Summary -->
              <div class="w-64 bg-sage rounded-xl">
                <div class="p-4 h-full flex flex-col">
                  <div class="text-center mb-4">
                    <div class="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
                      <span class="text-lg">🌍</span>
                    </div>
                    <h3 class="text-sm font-semibold text-white mb-1">Environmental Impact</h3>
                    <div class="text-2xl font-bold text-emerald-400">{{ formatNumber(userData.totalCO2SavedKg, 2) }}</div>
                    <div class="text-sage text-xs">kg CO₂ Saved</div>
                  </div>
                  
                  <div class="space-y-3 flex-1">
                    <div class="bg-deepgreen/20 rounded-lg p-3">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm">🌳</span>
                          <span class="text-white text-xs">Trees planted equiv.</span>
                        </div>
                        <span class="text-green-400 font-semibold text-xs">{{ formatNumber(userData.treesEquivalent, 2) }}</span>
                      </div>
                    </div>
                    
                    <div class="bg-deepgreen/20 rounded-lg p-3">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm">🚗</span>
                          <span class="text-white text-xs">Car miles offset</span>
                        </div>
                        <span class="text-blue-400 font-semibold text-xs">{{ formatNumber(userData.carMilesEquivalent, 1) }}</span>
                      </div>
                    </div>
                    
                    <div class="bg-deepgreen/20 rounded-lg p-3">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm">⛽</span>
                          <span class="text-white text-xs">Petrol saved (L)</span>
                        </div>
                        <span class="text-orange-400 font-semibold text-xs">{{ formatNumber(userData.petrolLitresEquivalent, 1) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Last Updated -->
                  <div class="mt-3 pt-3 border-t border-sage/20 text-center">
                    <div class="text-sage text-xs">Last updated</div>
                    <div class="text-white text-xs font-medium">{{ lastUpdated ? formatDateTime(lastUpdated) : 'Never' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Global View -->
          <div v-else class="flex flex-1 flex-col gap-6">
            <!-- Top Section: Global Metrics + Impact Summary -->
            <div class="flex gap-6 h-80">
              <!-- Left: Global KPI Cards -->
              <div class="grid grid-cols-3 gap-4 flex-1">
                <!-- Total Users -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">👥</span>
                    </div>
                    <div class="text-xs opacity-80">Users</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ globalStats.totalUsers.toLocaleString() }}</div>
                    <div class="text-xs opacity-80">Total Users</div>
                  </div>
                </div>

                <!-- Global Food Waste -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">🥬</span>
                    </div>
                    <div class="text-xs opacity-80">Global</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ globalStats.globalFoodWaste.toLocaleString() }}</div>
                    <div class="text-xs opacity-80">kg Food Waste</div>
                  </div>
                </div>

                <!-- Global CO₂ Saved -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">🌍</span>
                    </div>
                    <div class="text-xs opacity-80">Saved</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ globalStats.globalCO2Saved.toLocaleString() }}</div>
                    <div class="text-xs opacity-80">kg CO₂ Saved</div>
                  </div>
                </div>

                <!-- Trees Planted Equivalent -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">🌳</span>
                    </div>
                    <div class="text-xs opacity-80">Equiv.</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ globalStats.treesPlanted.toFixed(0) }}</div>
                    <div class="text-xs opacity-80">Trees Planted</div>
                  </div>
                </div>

                <!-- Average per User -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">📊</span>
                    </div>
                    <div class="text-xs opacity-80">Average</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ globalStats.avgPerUser.toFixed(1) }}</div>
                    <div class="text-xs opacity-80">kg CO₂ per User</div>
                  </div>
                </div>

                <!-- Participation Rate -->
                <div class="bg-sage rounded-xl p-6 text-white shadow-lg">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                      <span class="text-lg">📈</span>
                    </div>
                    <div class="text-xs opacity-80">Rate</div>
                  </div>
                  <div>
                    <div class="text-2xl font-bold">{{ ((userStats?.usersWithData || 0) / (userStats?.totalUsers || 1) * 100).toFixed(1) }}%</div>
                    <div class="text-xs opacity-80">Participation</div>
                  </div>
                </div>
              </div>

              <!-- Right: Collective Impact -->
              <div class="w-72 bg-sage rounded-xl h-full">
                <div class="p-4 h-full flex flex-col text-center overflow-hidden">
                  <div class="mb-2">
                    <h3 class="text-lg font-semibold text-white mb-1">Collective Impact</h3>
                  </div>
                  
                  <div class="flex-1 flex flex-col justify-center space-y-1">
                    <div class="mb-2">
                      <div class="text-lg font-bold text-emerald-400 mb-1">{{ globalStats.globalCO2Saved.toLocaleString() }}</div>
                      <div class="text-sage text-xs">kg CO₂ Saved by All Users</div>
                    </div>
                    
                    <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2 mb-1">
                      <div class="text-green-400 font-semibold text-xs">{{ globalStats.treesPlanted.toFixed(0) }}</div>
                      <div class="text-sage text-xs">Trees planted equivalent</div>
                    </div>
                    
                    <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2 mb-1">
                      <div class="text-blue-400 font-semibold text-xs">{{ (globalStats.globalCO2Saved / CAR_CO2_FACTOR / 365).toFixed(0) }}</div>
                      <div class="text-sage text-xs">Days of car emissions offset</div>
                    </div>
                    
                    <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-2">
                      <div class="text-emerald-400 font-semibold text-xs">{{ globalStats.totalUsers }}</div>
                      <div class="text-sage text-xs">Users making a difference</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom Section: User Statistics + Top Contributors -->
            <div class="flex gap-6 flex-1">
              <!-- User Distribution -->
              <div class="w-80 bg-sage rounded-xl">
                <div class="p-6 h-full flex flex-col">
                  <h3 class="text-lg font-semibold text-white mb-4 text-center">User Distribution</h3>
                  
                  <div class="flex-1 flex flex-col justify-center space-y-4">
                    <!-- Donut Chart -->
                    <div class="flex justify-center mb-4">
                      <div class="relative w-32 h-32">
                        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                          <defs>
                            <linearGradient id="activeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stop-color="#10b981"/>
                              <stop offset="100%" stop-color="#059669"/>
                            </linearGradient>
                            <linearGradient id="inactiveGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stop-color="#f97316"/>
                              <stop offset="100%" stop-color="#ea580c"/>
                            </linearGradient>
                          </defs>
                          
                          <!-- Background circle -->
                          <circle cx="60" cy="60" r="40" fill="none" stroke="#0D2705" stroke-width="8"/>
                          
                          <!-- Active users arc -->
                          <circle 
                            cx="60" 
                            cy="60" 
                            r="40" 
                            fill="none" 
                            stroke="url(#activeGradient)" 
                            stroke-width="8"
                            :stroke-dasharray="`${(userStats?.usersWithData || 0) / (userStats?.totalUsers || 1) * 251.2} 251.2`"
                          />
                          
                          <!-- Inactive users arc -->
                          <circle 
                            cx="60" 
                            cy="60" 
                            r="40" 
                            fill="none" 
                            stroke="url(#inactiveGradient)" 
                            stroke-width="8"
                            :stroke-dasharray="`${(userStats?.usersWithoutData || 0) / (userStats?.totalUsers || 1) * 251.2} 251.2`"
                            :stroke-dashoffset="`-${(userStats?.usersWithData || 0) / (userStats?.totalUsers || 1) * 251.2}`"
                          />
                        </svg>
                      </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3">
                      <div class="bg-gradient-to-br from-green-500/20 to-green-600/10 rounded-lg p-3 text-center">
                        <div class="text-xl font-bold text-green-400 mb-1">{{ userStats?.usersWithData || 0 }}</div>
                        <div class="text-sage text-xs">Active Users</div>
                        <div class="text-xs text-green-300 mt-1">With data</div>
                      </div>
                      
                      <div class="bg-gradient-to-br from-orange-500/30 to-red-500/20 rounded-lg p-3 text-center shadow-lg">
                        <div class="text-xl font-bold text-orange-300 mb-1">{{ userStats?.usersWithoutData || 0 }}</div>
                        <div class="text-orange-200 text-xs font-medium">Need to Start</div>
                        <div class="text-xs text-orange-300 mt-1 font-medium">No data yet</div>
                      </div>
                    </div>
                    
                    <div class="bg-gradient-to-r from-emerald-500/10 to-green-500/10 rounded-lg p-3 text-center">
                      <div class="text-emerald-400 font-bold text-lg">
                        {{ ((userStats?.usersWithData || 0) / (userStats?.totalUsers || 1) * 100).toFixed(1) }}%
                      </div>
                      <div class="text-sage text-xs">Participation Rate</div>
                      <div class="text-xs text-emerald-300 mt-1">Users actively composting</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Top Contributors -->
              <div class="bg-sage rounded-xl flex-1">
                <div class="p-6 h-full flex flex-col">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-white">Top Contributors</h3>
                    <div class="text-sage text-sm">Most active users</div>
                  </div>
                  
                  <div class="flex-1 overflow-y-auto space-y-3">
                    <div 
                      v-for="(user, index) in usersWithData.slice(0, 8)" 
                      :key="user.username"
                      class="bg-sage/10 hover:bg-sage/20 rounded-lg p-3 transition-colors"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-3">
                          <div class="w-6 h-6 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full flex items-center justify-center text-white font-bold text-xs">
                            {{ index + 1 }}
                          </div>
                          <div class="text-white font-medium text-sm">{{ user.username }}</div>
                        </div>
                        <div class="text-emerald-400 font-semibold text-sm">{{ user.feedingLogsCount }} logs</div>
                      </div>
                      
                      <!-- Horizontal Bar -->
                      <div class="w-full bg-deepgreen/30 rounded-full h-2">
                        <div 
                          class="bg-gradient-to-r from-[#D7EDBC] to-[#AEC5B5] h-2 rounded-full transition-all duration-500"
                          :style="{ width: `${Math.max((user.feedingLogsCount / Math.max(...usersWithData.slice(0, 8).map(u => u.feedingLogsCount))) * 100, 8)}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Global Motivation Footer -->
                  <div class="mt-4 p-4 bg-gradient-to-r from-emerald-600/20 to-green-600/20 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center">
                        <span class="text-sm">🌍</span>
                      </div>
                      <div>
                        <p class="text-white font-medium text-sm">Together We're Making a Difference!</p>
                        <p class="text-sage text-xs">Every log contributes to our collective environmental impact</p>
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

    // Constants - Match Python exactly
    const API_BASE_URL = 'http://localhost:3001/api'
    const TREE_CO2_ABSORPTION = 25.0  // Match Python: 25.0
    const PETROL_CO2_FACTOR = 2.3     // Match Python: 2.3
    const CAR_CO2_FACTOR = 0.4        // Match Python: 0.4

    // Methods
    const calculateCO2Saved = (foodWasteKg, tankVolume, soilVolume) => {
      // Match Python constants exactly
      const STP_CO2_PPM = 415.0
      const STP_AIR_CONCENTRATION_PERCENT = 21.0
      const FOOD_WASTE_CO2_FACTOR = 2.5
      const COMPOST_REDUCTION_FACTOR = 0.8
      
      const co2_ppm = STP_CO2_PPM
      const air_conc = STP_AIR_CONCENTRATION_PERCENT / 100
      
      const effective_volume = tankVolume - (soilVolume * air_conc)
      const baseline_co2_grams = (co2_ppm / 1_000_000) * effective_volume * 1.8
      
      // 1kg food waste → ~2.5kg CO₂, composting reduces 80%
      const co2_saved_landfill_kg = foodWasteKg * FOOD_WASTE_CO2_FACTOR * COMPOST_REDUCTION_FACTOR
      const co2_saved_landfill_g = co2_saved_landfill_kg * 1000
      
      const total_saved_g = baseline_co2_grams + co2_saved_landfill_g
      const total_saved_kg = total_saved_g / 1000
      
      return {
        totalCO2SavedKg: total_saved_kg,
        treesEquivalent: total_saved_kg / TREE_CO2_ABSORPTION,
        petrolLitresEquivalent: total_saved_kg / PETROL_CO2_FACTOR,
        carMilesEquivalent: total_saved_kg / CAR_CO2_FACTOR
      }
    }

    const formatNumber = (num, decimals = 2) => {
      // Convert to number first, then use toFixed and parseFloat to remove trailing zeros
      const rounded = Number(num).toFixed(decimals)
      return parseFloat(rounded).toString()
    }

    const getDisplayText = (username) => {
      if (!username) return "Choose a user..."
      
      const user = allUsers.value.find(u => u.username === username)
      if (!user) return username
      
      if (user.hasData) {
        return `${username} (${user.feedingLogsCount} logs)`
      } else {
        return `${username} (No data yet)`
      }
    }

    const calculateDropdownWidth = (username) => {
      const displayText = getDisplayText(username)
      // Approximate 8px per character + 80px for padding and dropdown arrow
      return Math.max(displayText.length * 8 + 80, 180)
    }

    const fetchGlobalData = async () => {
      isLoading.value = true
      
      try {
        // Fetch global statistics
        const globalResponse = await fetch(`${API_BASE_URL}/global-stats`)
        const globalData = await globalResponse.json()
        
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
        console.error('Error fetching global data:', error)
      }
      
      isLoading.value = false
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
              // User has feeding logs data - Use backend calculated values directly
              userData.value = {
                ...userData.value,
                username: personalData.data.user.username,
                totalFoodWasteKg: personalData.data.totalFoodWasteKg,
                totalCO2SavedKg: personalData.data.totalCO2SavedKg,
                tankVolume: parseFloat(personalData.data.user.tankVolume),
                soilVolume: parseFloat(personalData.data.user.soilVolume),
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
      // For individual log calculations, use the simplified version
      const foodWasteKg = calculateLogFoodWaste(log)
      const FOOD_WASTE_CO2_FACTOR = 2.5
      const COMPOST_REDUCTION_FACTOR = 0.8
      
      // Simplified calculation for individual logs (just the landfill savings part)
      const co2_saved_landfill_kg = foodWasteKg * FOOD_WASTE_CO2_FACTOR * COMPOST_REDUCTION_FACTOR
      return co2_saved_landfill_kg
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (date) => {
      return date.toLocaleString()
    }

    // Chart helper methods
    const getMaxCO2Value = () => {
      if (!monthlyData.value || monthlyData.value.length === 0) return 1
      const maxValue = Math.max(...monthlyData.value.map(item => item.co2Saved))
      // Add 20% padding to the max value for better visualization, minimum of 1
      return Math.max(maxValue * 1.2, 1)
    }

    const getChartPoints = () => {
      if (!monthlyData.value || monthlyData.value.length === 0) return []
      
      const maxValue = getMaxCO2Value()
      const chartWidth = 320 // Chart area width (370 - 50)
      const chartHeight = 160 // Chart area height (180 - 20)
      const startX = 50 // Chart area start X
      const startY = 20 // Chart area start Y
      
      return monthlyData.value.map((item, index) => {
        const x = startX + (index * (chartWidth / Math.max(monthlyData.value.length - 1, 1)))
        const y = startY + chartHeight - ((item.co2Saved / maxValue) * chartHeight)
        return { x, y }
      })
    }

    const getChartPath = () => {
      const points = getChartPoints()
      if (points.length === 0) return ''
      
      let path = `M ${points[0].x} ${points[0].y}`
      
      for (let i = 1; i < points.length; i++) {
        // Create smooth curves between points
        const prevPoint = points[i - 1]
        const currentPoint = points[i]
        const controlPointOffset = Math.min(30, (currentPoint.x - prevPoint.x) / 2)
        
        path += ` C ${prevPoint.x + controlPointOffset} ${prevPoint.y}, ${currentPoint.x - controlPointOffset} ${currentPoint.y}, ${currentPoint.x} ${currentPoint.y}`
      }
      
      return path
    }

    // New chart methods for individual feeding logs
    const getRecentLogs = () => {
      if (!feedingLogs.value || feedingLogs.value.length === 0) return []
      // Return the most recent 8 logs for the chart
      return feedingLogs.value.slice(0, 8).reverse() // reverse to show chronological order
    }

    const getMaxLogCO2Value = () => {
      const recentLogs = getRecentLogs()
      if (recentLogs.length === 0) return 1
      const maxValue = Math.max(...recentLogs.map(log => calculateLogCO2(log)))
      // Add 20% padding to the max value for better visualization, minimum of 0.1
      return Math.max(maxValue * 1.2, 0.1)
    }

    const getLogChartPoints = () => {
      const recentLogs = getRecentLogs()
      if (recentLogs.length === 0) return []
      
      const maxValue = getMaxLogCO2Value()
      const chartWidth = 380 // Chart area width in pixels (430 - 50)
      const chartHeight = 60 // Chart area height in pixels (75 - 15)
      const startX = 50 // Chart area start X in pixels
      const startY = 15 // Chart area start Y in pixels
      
      return recentLogs.map((log, index) => {
        const co2Value = calculateLogCO2(log)
        const x = startX + (index * (chartWidth / Math.max(recentLogs.length - 1, 1)))
        const y = startY + chartHeight - ((co2Value / maxValue) * chartHeight)
        return { x, y }
      })
    }

    const getLogChartPath = () => {
      const points = getLogChartPoints()
      if (points.length === 0) return ''
      
      let path = `M ${points[0].x} ${points[0].y}`
      
      for (let i = 1; i < points.length; i++) {
        // Create smooth curves between points
        const prevPoint = points[i - 1]
        const currentPoint = points[i]
        const controlPointOffset = Math.min(20, (currentPoint.x - prevPoint.x) / 2)
        
        path += ` C ${prevPoint.x + controlPointOffset} ${prevPoint.y}, ${currentPoint.x - controlPointOffset} ${currentPoint.y}, ${currentPoint.x} ${currentPoint.y}`
      }
      
      return path
    }

    const formatLogDate = (dateString) => {
      const date = new Date(dateString)
      return date.getDate() + '/' + (date.getMonth() + 1)
    }

    // Lifecycle
    onMounted(async () => {
      isLoading.value = true
      await fetchUsers()
      // Load global data by default
      await fetchGlobalData()
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
      fetchGlobalData,
      onUserChange,
      calculateLogFoodWaste,
      calculateLogCO2,
      formatDate,
      formatDateTime,
      getDisplayText,
      calculateDropdownWidth,
      formatNumber,
      getMaxCO2Value,
      getChartPoints,
      getChartPath,
      // New methods for individual log charts
      getRecentLogs,
      getMaxLogCO2Value,
      getLogChartPoints,
      getLogChartPath,
      formatLogDate
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