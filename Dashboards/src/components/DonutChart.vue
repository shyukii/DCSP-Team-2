<template>
  <div class="relative flex items-center justify-center h-full">
    <div class="w-40 h-40 rounded-full border-[14px] border-accent/40 relative">
      <div class="absolute inset-0 rounded-full border-[14px] border-accent rotate-45 clip-path" />
      <div class="absolute inset-6 rounded-full bg-base-200 flex items-center justify-center">
        <span class="text-sm font-semibold">{{ centerText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ centerText?: string }>()
</script>

<style scoped>
/* purely decorative placeholder ‘segment’ */
.clip-path {
  clip-path: inset(0 0 50% 0);
}
</style>
