<template>
  <div class="flex gap-3">
    <button
      v-for="opt in options"
      :key="opt.value"
      class="px-5 py-2 rounded-lg font-medium transition
             bg-base-300 hover:bg-base-200"
      :class="opt.value === modelValue
        ? 'ring-2 ring-accent bg-accent/20 text-accent-content'
        : 'text-base-content/80'"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface Option {
  label: string
  value: string | number
}
defineProps<{
  modelValue: string | number
  options: Option[]
}>()
defineEmits(['update:modelValue'])
</script>
