<template>
  <div class="p-6 space-y-6 max-w-[1600px] mx-auto">
    <!-- HEADER -->
    <div class="flex flex-wrap items-start justify-between gap-6">
      <div>
        <h1 class="text-3xl font-bold">
          <span class="text-accent">Youth</span> Wellness Overview
        </h1>
        <p class="text-sm mt-1 max-w-xl opacity-80">
          Insights into addiction, health, and lifestyle trends among Singaporean youths.
        </p>
      </div>

      <SegmentButtons
        v-model="gender"
        :options="[
          { label: 'Male', value: 'male' },
            { label: 'Female', value: 'female' },
            { label: 'Other', value: 'other' }
        ]"
      />
    </div>

    <!-- KPI ROW -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
      <KpiCard title="Avg Smokers/Day" :value="10" />
      <KpiCard title="Avg Drinks/Week" :value="5" />
      <KpiCard title="Poor Mental Health" value="33%" subtitle="" />
      <KpiCard title="Health Issue" value="49.7%" />
    </div>

    <!-- MAIN CHART + (optionally more KPIs if needed) -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 bg-base-200 rounded-xl shadow-inner p-4 flex flex-col">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold">Daily Smoking Frequency Across Age Groups</h3>
          <div class="text-xs opacity-70">Dummy Line Chart</div>
        </div>
        <!-- line chart placeholder -->
        <div class="flex-1">
          <div class="h-72 rounded-lg bg-base-300 flex items-center justify-center text-sm opacity-70">
            [Line Chart Placeholder]
          </div>
        </div>
      </div>

      <!-- Right side could hold extra KPI or mini charts -->
      <div class="space-y-6 xl:space-y-6">
        <!-- optional extra block -->
      </div>
    </div>

    <!-- LOWER PANELS -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Donut 1 -->
      <div class="bg-base-200 rounded-xl shadow-inner p-4 flex flex-col">
        <h3 class="font-semibold mb-3">Mental Health Breakdown</h3>
        <div class="flex-1 flex items-center justify-center">
          <DonutChart centerText="Good / Avg / Poor" />
        </div>
      </div>

      <!-- Donut 2 -->
      <div class="bg-base-200 rounded-xl shadow-inner p-4 flex flex-col">
        <h3 class="font-semibold mb-3">Therapy Experience Among Youths</h3>
        <div class="flex-1 flex items-center justify-center">
          <DonutChart centerText="None / Past / Current" />
        </div>
      </div>

      <!-- Stacked Bars -->
      <div class="bg-base-200 rounded-xl shadow-inner p-4 flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold">Sleep Quality by Employment Status</h3>
          <div class="text-xs flex gap-3 items-center">
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-[#A6E3B8] inline-block"></span> High</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-[#5DAA73] inline-block"></span> Normal</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-[#244732] inline-block"></span> Low</span>
          </div>
        </div>
        <div class="flex-1">
          <StackedBarChart :columns="sleepColumns" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SegmentButtons from '../components/SegmentButtons.vue'
import KpiCard from '../components/KpiCard.vue'
import DonutChart from '../components/DonutChart.vue'
import StackedBarChart from '../components/StackedBarChart.vue'

const gender = ref('male')

const sleepColumns = [
  {
    label: 'Employed',
    stack: [
      { label: 'High', percent: 33.04, color: '#A6E3B8' },
      { label: 'Normal', percent: 42.56, color: '#5DAA73' },
      { label: 'Low', percent: 24.41, color: '#244732' }
    ]
  },
  {
    label: 'Unemployed',
    stack: [
      { label: 'High', percent: 33.61, color: '#A6E3B8' },
      { label: 'Normal', percent: 42.68, color: '#5DAA73' },
      { label: 'Low', percent: 23.72, color: '#244732' }
    ]
  },
  {
    label: 'Student',
    stack: [
      { label: 'High', percent: 33.67, color: '#A6E3B8' },
      { label: 'Normal', percent: 42.87, color: '#5DAA73' },
      { label: 'Low', percent: 23.45, color: '#244732' }
    ]
  },
  {
    label: 'Retired',
    stack: [
      { label: 'High', percent: 33.57, color: '#A6E3B8' },
      { label: 'Normal', percent: 42.62, color: '#5DAA73' },
      { label: 'Low', percent: 23.81, color: '#244732' }
    ]
  },
  {
    label: 'Self-Employed',
    stack: [
      { label: 'High', percent: 33.71, color: '#A6E3B8' },
      { label: 'Normal', percent: 42.60, color: '#5DAA73' },
      { label: 'Low', percent: 23.69, color: '#244732' }
    ]
  }
]
</script>
