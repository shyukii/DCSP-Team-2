<template>
  <div class="h-full flex items-end gap-6 px-4 pb-4">
    <div
      v-for="(col, i) in columns"
      :key="i"
      class="flex flex-col items-center gap-2"
    >
      <div class="flex flex-col justify-end h-56 w-14 rounded bg-base-300 overflow-hidden">
        <div
          v-for="(seg, j) in col.stack"
          :key="j"
          class="w-full"
          :style="{
            height: seg.percent + '%',
            backgroundColor: seg.color
          }"
          :title="seg.label + ' ' + seg.percent + '%'"
        ></div>
      </div>
      <p
    class="text-xs font-medium text-center w-16 leading-tight truncate"
    :title="col.label"
    >
    {{ col.label }}
    </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Segment {
  label: string
  percent: number
  color: string
}
interface Column {
  label: string
  stack: Segment[]
}
defineProps<{ columns: Column[] }>()
</script>
