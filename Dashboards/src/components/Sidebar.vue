<template>
  <aside
    class="relative bg-deepgreen pt-8 pb-4 transition-all duration-300 overflow-hidden border-r-2 border-[#849974]/50"
    :class="isCollapsed ? 'w-16' : 'w-44'"
    @mouseenter="isCollapsed = false"
    @mouseleave="isCollapsed = true"
  >
    <!-- Logo -->
    <transition name="fade-slide" mode="out-in" appear>
      <div
        class="transition-all duration-300"
        :class="isCollapsed
          ? 'flex justify-center items-start mt-[-15px] mb-4 h-14'
          : 'flex items-center justify-start space-x-2 px-2 mb-6'"
        :key="isCollapsed ? 'collapsed' : 'expanded'"
      >
        <img src="/logo.png" alt="Logo"
          class="transition-all duration-300 object-contain"
          :class="isCollapsed ? 'w-12 h-12' : 'w-10 h-10'" />
        <span v-show="!isCollapsed" class="font-bold text-lg transition-all duration-300">
          NutricycleAI
        </span>
      </div>
    </transition>

    <!-- Nav Items -->
    <nav class="flex flex-col gap-8 mt-4">
      <transition-group name="fade-slide" tag="div" class="flex flex-col space-y-6 transition-all duration-300">
        <router-link to="/readiness" class="no-underline text-inherit">
          <div class="flex items-center" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-6 space-x-3'">
            <i class="fas fa-leaf text-lg"></i>
            <span v-if="!isCollapsed">Readiness</span>
          </div>
        </router-link>
        <router-link to="/feed" class="no-underline text-inherit">
          <div class="flex items-center" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-6 space-x-3'">
            <i class="fas fa-apple-alt text-lg"></i>
            <span v-if="!isCollapsed">Feed</span>
          </div>
        </router-link>
        <router-link to="/savings" class="no-underline text-inherit">
          <div class="flex items-center" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-6 space-x-3'">
            <i class="fas fa-chart-line text-lg"></i>
            <span v-if="!isCollapsed">CO₂ Savings</span>
          </div>
        </router-link>
        <div class="flex items-center" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-6 space-x-3'">
          <i class="fas fa-sync text-lg"></i>
          <span v-if="!isCollapsed">Refresh</span>
        </div>
      </transition-group>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const isCollapsed = ref(true)
</script>

<style scoped>
.fade-slide-move {
  transition: all 0.3s ease;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
  position: relative;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
  position: relative;
}
</style>