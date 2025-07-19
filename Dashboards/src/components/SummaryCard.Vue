<template>
  <div class="card bg-base-100 shadow rounded-xl p-4 space-y-1">
    <h3 class="text-xs font-semibold uppercase tracking-wide opacity-70">{{ title }}</h3>
    <div class="flex items-baseline gap-2">
      <span class="text-2xl font-bold">{{ value }}</span>
      <span v-if="unit" class="text-sm opacity-60">{{ unit }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; value: number | string; unit?: string }>()
</script>
