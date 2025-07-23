<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="flex-1 flex flex-col p-6 space-y-4">
      <!-- Header Section -->
      <div class="flex justify-between items-end">
        <div>
          <h1 class="text-3xl font-bold">
            <span class="opacity-70">Compost</span> Feed Insights
          </h1>
          <p class="opacity-70 text-sm mt-1">
            Track feedstock usage, nutrient breakdown, and composting impact across time.
          </p>
        </div>

        <!-- Right: Slicer Buttons -->
        <div class="flex space-x-2">
          <button class="btn bg-transparent border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
          <button class="btn bg-transparent border-transparent text-white px-6 py-2 text-sm rounded-md">Slicer</button>
        </div>
      </div>

      <!-- Body Section: Left (metrics & charts) + Right (table) -->
      <div class="flex flex-1 gap-4">
        <!-- Left: 50% Width -->
        <div class="flex flex-col w-1/2 space-y-3">
          <!-- Top Row: 3 KPI Cards -->
          <div class="flex gap-2.5">
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Feed Volume</h2>
              <p class="text-2xl font-bold">1.2T</p>
              <div class="h-10 mt-2 bg-khaki/30 rounded">[ Mini Chart ]</div>
            </div>
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Avg EC Level</h2>
              <p class="text-2xl font-bold">3.4 dS/m</p>
              <div class="h-10 mt-2 bg-khaki/30 rounded">[ Mini Chart ]</div>
            </div>
            <div class="card bg-sage shadow-b p-4 flex-1">
              <h2 class="text-sm font-semibold">Moisture</h2>
              <p class="text-2xl font-bold">68%</p>
              <div class="h-10 mt-2 bg-khaki/30 rounded">[ Mini Chart ]</div>
            </div>
          </div>

          <!-- Middle Card: Bar Chart -->
          <div class="card bg-sage shadow-b flex-1 p-4">
            <h2 class="text-sm font-semibold mb-2">Feed Comparison by Source</h2>
            <div class="h-full bg-khaki/30 rounded flex items-center justify-center text-xs text-khaki/70">
              [ Bar Chart Placeholder ]
            </div>
          </div>

          <!-- Bottom Card: Circular Segments -->
          <div class="card bg-sage shadow-b flex-1 p-4">
            <h2 class="text-sm font-semibold mb-2">By Collection Type</h2>
            <div class="grid grid-cols-3 gap-4">
              <div class="text-center">
                <h4 class="text-sm text-khaki">Household</h4>
                <p class="text-xl font-bold">430kg</p>
              </div>
              <div class="text-center">
                <h4 class="text-sm text-khaki">Commercial</h4>
                <p class="text-xl font-bold">690kg</p>
              </div>
              <div class="text-center">
                <h4 class="text-sm text-khaki">Self-collected</h4>
                <p class="text-xl font-bold">95kg</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Table Placeholder -->
        <div class="w-1/2 flex flex-col">
          <div class="card bg-sage shadow-b flex-1 p-4">
            <h2 class="text-sm font-semibold mb-2">Feed Subcategories</h2>
            <div class="h-full bg-khaki/20 rounded flex items-center justify-center text-sm text-khaki/70">
              [ Subcategory Table Placeholder ]
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Static layout – no interactivity yet
</script>
