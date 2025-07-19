<template>
  <div class="rounded-xl bg-base-200 shadow-inner p-4 flex flex-col justify-between gap-3 min-h-[120px]">
    <div class="flex items-start justify-between">
      <div class="flex items-center gap-2">
        <slot name="icon">
          <!-- default icon placeholder -->
          <span class="w-3 h-3 rounded-full bg-accent block"></span>
        </slot>
        <h3 class="text-xs uppercase tracking-wide font-semibold text-base-content/70">
          {{ title }}
        </h3>
      </div>
      <slot name="spark" />
    </div>

    <div class="flex items-end gap-2">
      <p class="text-3xl font-bold leading-none">{{ value }}</p>
      <p v-if="unit" class="text-sm font-semibold mb-1 opacity-70">{{ unit }}</p>
    </div>

    <p v-if="subtitle" class="text-xs opacity-70 -mt-1">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
  unit?: string
  subtitle?: string
}>()
</script>
