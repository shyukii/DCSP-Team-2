<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <div class="relative w-full flex">
      
      <!-- Main Content Area -->
      <div class="flex-1 p-5 flex flex-col space-y-4 h-full">
        <!-- Header and Year Selector -->
        <div class="flex justify-between items-end">
          <!-- Title + Subtitle -->
          <div class="flex flex-col justify-end leading-tight">
            <h1 class="text-3xl font-bold">
              <span class="text-sage">CO₂</span> Savings Impact
            </h1>
            <p class="text-sm text-sage mt-1">
              Track estimated CO₂ reduction through composting efforts and monitor your sustainability impact.
            </p>
          </div>

          <!-- Slicer Buttons -->
          <div class="flex space-x-2">
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
            <button class="btn bg-transparent hover:bg-[#B2D2FB]/25 border-transparent text-white px-6 py-2 text-sm rounded-md hover:bg-sage/20 transition border-none outline-none ring-0 focus:ring-0 focus:outline-none focus:border-none hover:border-none">Slicer</button>
          </div>
        </div>

        <!-- Top Row: 4 KPI Cards -->
        <div class="grid grid-cols-4 gap-4">
          <div class="card bg-sage shadow-b p-4 h-36">
            <h2 class="text-xs font-semibold">Title</h2>
            <p class="text-sm font-medium">Value</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-36">
            <h2 class="text-xs font-semibold">Title</h2>
            <p class="text-sm font-medium">Value</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-36">
            <h2 class="text-xs font-semibold">Title</h2>
            <p class="text-sm font-medium">Value</p>
          </div>
          <div class="card bg-sage shadow-b p-4 h-36">
            <h2 class="text-xs font-semibold">Title</h2>
            <p class="text-sm font-medium">Value</p>
          </div>
        </div>

        <!-- Middle Row: Full Width Chart -->
        <div class="card bg-sage shadow-b flex-1 p-4">
          <h2 class="text-sm font-semibold">Title</h2>
          <div class="h-full flex items-center justify-center text-opacity-50">
            [ Line Chart Placeholder ]
          </div>
        </div>

        <!-- Bottom Row: 2 Cards Side-by-Side -->
        <div class="flex gap-4 h-[40%]">
          <div class="card bg-sage shadow-b w-1/2 p-4">
            <h2 class="text-sm font-semibold">Title</h2>
            <div class="h-full flex items-center justify-center text-opacity-50">
              [ Pie Chart Placeholder ]
            </div>
          </div>
          <div class="card bg-sage shadow-b w-1/2 p-4">
            <h2 class="text-sm font-semibold">Title</h2>
            <div class="h-full flex items-center justify-center text-opacity-50">
              [ Bar Chart Placeholder ]
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
