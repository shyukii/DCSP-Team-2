<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">

      <!-- Main Content Area -->
      <div class="flex-1 p-5 flex flex-col space-y-2 h-full">
        <!-- Header and Year Selector (aligned together) -->
        <div class="flex justify-between items-end">
          <!-- Left: Title + Subtitle aligned to bottom -->
          <div class="flex flex-col justify-end leading-tight">
            <h1 class="text-3xl font-bold">
              <span class="opacity-70">Compost</span> Readiness Overview
            </h1>
            <p class="text-sm opacity-70 mt-1">
              Monitor key indicators like soil condition, temperature and moisture levels to assess compost maturity in real time.
            </p>
          </div>

          <!-- Right: Slicer Buttons -->
          <div class="flex space-x-2">
            <button class="btn bg-sage text-white px-10 py-2 text-sm rounded-md">Slicer</button>
            <button class="btn bg-sage text-white px-10 py-2 text-sm rounded-md">Slicer</button>
            <button class="btn bg-sage text-white px-10 py-2 text-sm rounded-md">Slicer</button>
            <button class="btn bg-sage text-white px-10 py-2 text-sm rounded-md">Slicer</button>
          </div>
        </div>

        <!-- Main Grid Content (Top and Bottom split equally) -->
        <div class="flex flex-1 flex-col gap-4">
          <!-- Top Section: KPI Cards + Line Chart (45% height) -->
          <div class="flex gap-4 h-1/2">
            <!-- 4 KPI Cards in 2x2 grid (Left, 40% width) -->
            <div class="grid grid-cols-2 grid-rows-2 gap-2.5 w-[45%]">
              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full">
                  <h2 class="card-title text-xs font-semibold">Title</h2>
                  <p class="text-sm font-medium">Value</p>
                </div>
              </div>
              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full">
                  <h2 class="card-title text-xs font-semibold">Title</h2>
                  <p class="text-sm font-medium">Value</p>
                </div>
              </div>
              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full">
                  <h2 class="card-title text-xs font-semibold">Title</h2>
                  <p class="text-sm font-medium">Value</p>
                </div>
              </div>
              <div class="card bg-sage shadow-b">
                <div class="card-body p-3 h-full">
                  <h2 class="card-title text-xs font-semibold">Title</h2>
                  <p class="text-sm font-medium">Value</p>
                </div>
              </div>
            </div>

            <!-- Right: Line Chart (60% width) -->
            <div class="card bg-sage shadow-b flex-1">
              <div class="card-body h-full">
                <h2 class="card-title">Title</h2>
                <div class="h-full flex items-center justify-center text-opacity-50">
                  [ Line Chart Placeholder ]
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Section: 2 Charts (Expenses 65%, Savings 35%) - 50% height -->
          <div class="flex gap-4 h-1/2">
            <!-- Left: Expenses Pie Chart -->
            <div class="card bg-sage shadow-b w-[65%]">
              <div class="card-body h-full">
                <h2 class="card-title">Title</h2>
                <div class="h-full flex items-center justify-center text-opacity-50">
                  [ Pie Chart Placeholder ]
                </div>
              </div>
            </div>

            <!-- Right: Savings Pie Chart -->
            <div class="card bg-sage shadow-b w-[35%]">
              <div class="card-body h-full">
                <h2 class="card-title">Title</h2>
                <div class="h-full flex items-center justify-center text-opacity-50">
                  [ Bar Chart Placeholder ]
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const isCollapsed = ref(true)
</script>

<style scoped>
.fade-slide-move {
  transition: all 0.3s ease;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
  position: relative;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
  position: relative;
}
</style>
