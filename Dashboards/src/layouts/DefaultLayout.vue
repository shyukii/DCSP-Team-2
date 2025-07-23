<template>
  <div class="flex h-screen bg-deepgreen text-cream overflow-hidden">
    <Sidebar />
    <div class="flex-1 overflow-y-auto">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Sidebar from '../components/Sidebar.vue'
</script>