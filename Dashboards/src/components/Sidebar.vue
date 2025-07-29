<template>
  <aside
    class="relative bg-deepgreen pt-8 pb-4 transition-all duration-300 overflow-hidden border-r-2 border-[#0B4F26]"
    :class="isCollapsed ? 'w-16' : 'w-44'"
    @mouseenter="isCollapsed = false"
    @mouseleave="isCollapsed = true"
  >
    <!-- Logo -->
    <transition name="fade-slide" mode="out-in" appear>
      <div
        class="transition-all duration-300 flex items-start mb-4 h-12 mt-[-15px]"
        :class="isCollapsed
          ? 'justify-center px-2'
          : 'justify-start space-x-2 px-2'"
        :key="isCollapsed ? 'collapsed' : 'expanded'"
      >
        <img src="/logo.png" alt="Logo"
          class="transition-all duration-300 object-contain"
          :class="isCollapsed ? 'w-12 h-12' : 'w-10 h-12'" />
        <span v-show="!isCollapsed" class="font-bold text-lg transition-all duration-300 text-cream self-center">
          NutricycleAI
        </span>
      </div>
    </transition>

    <!-- Nav Items -->
    <nav class="flex flex-col mt-2">
      <transition-group name="fade-slide" tag="div" class="flex flex-col transition-all duration-300">
        <router-link to="/readiness" class="no-underline text-inherit sidebar-link">
          <div class="flex items-center sidebar-item" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-4 space-x-3'">
            <i class="fas fa-leaf text-lg"></i>
            <span v-if="!isCollapsed">Readiness</span>
          </div>
        </router-link>

        <router-link to="/feed" class="no-underline text-inherit sidebar-link">
          <div class="flex items-center sidebar-item" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-4 space-x-3'">
            <i class="fas fa-apple-alt text-lg"></i>
            <span v-if="!isCollapsed">Feed</span>
          </div>
        </router-link>

        <router-link to="/savings" class="no-underline text-inherit sidebar-link">
          <div class="flex items-center sidebar-item" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-4 space-x-3'">
            <i class="fas fa-chart-line text-lg"></i>
            <span v-if="!isCollapsed">CO₂ Savings</span>
          </div>
        </router-link>

        <router-link to="/historical" class="no-underline text-inherit sidebar-link">
          <div class="flex items-center sidebar-item" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-4 space-x-3'">
            <i class="fas fa-chart-area text-lg"></i>
            <span v-if="!isCollapsed">Historical</span>
          </div>
        </router-link>

        <div class="sidebar-link">
          <div class="flex items-center sidebar-item" :class="isCollapsed ? 'justify-center px-0' : 'justify-start px-4 space-x-3'">
            <i class="fas fa-sync text-lg"></i>
            <span v-if="!isCollapsed">Refresh</span>
          </div>
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

/* Sidebar link wrapper for proper spacing */
.sidebar-link {
  @apply px-3 py-1;
}

/* Enhanced hover animation with rounded edges and smaller size */
.sidebar-item {
  @apply transition-all duration-300 ease-in-out py-3 rounded-lg relative;
  transform-origin: center;
}

.sidebar-item:hover {
  @apply bg-[#0B4F26] text-accent;
  transform: scale(0.95);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(11, 79, 38, 0.3);
}

/* Optional: Add a subtle glow effect */
.sidebar-item:hover::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  pointer-events: none;
}

/* Smooth transition for icons */
.sidebar-item i {
  @apply transition-all duration-300;
}

.sidebar-item:hover i {
  transform: scale(1.1);
}
</style>