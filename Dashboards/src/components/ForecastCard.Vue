<template>
  <div class="flex flex-wrap gap-2">
    <span
      v-for="(v,i) in forecast"
      :key="i"
      class="badge badge-info text-white"
    >D{{ i+1 }}: {{ v }}%</span>
  </div>
</template>
<script setup lang="ts">
defineProps<{ forecast: number[] }>()
</script>
