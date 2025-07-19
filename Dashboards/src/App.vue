<template>
  <div class="min-h-screen">
    <header class="p-4 border-b border-base-300">
      <h1 class="text-2xl font-bold">Compost Dashboard</h1>
    </header>
    <main>
      <Dashboard />
    </main>
  </div>
</template>

<script setup lang="ts">
import Dashboard from './pages/Dashboard.vue'
</script>
