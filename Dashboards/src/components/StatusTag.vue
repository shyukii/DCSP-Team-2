<template>
  <span
    class="badge"
    :class="{
      'badge-success': status === 'Healthy',
      'badge-warning': status === 'Dry',
      'badge-error': status === 'Too Wet'
    }"
  >{{ status }}</span>
</template>
<script setup lang="ts">
defineProps<{ status: string }>()
</script>
