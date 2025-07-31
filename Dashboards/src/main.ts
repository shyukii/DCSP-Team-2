import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/base.css' // Tailwind build entry
import '@fortawesome/fontawesome-free/css/all.css'

// Create the app
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)

// Mount the app
app.mount('#app')

// Optional: Quick test user setup (remove in production)
// Uncomment the lines below to test with a hardcoded user
/*
import { useUserStore } from '@/stores/user'

// Set up test user after mounting
setTimeout(() => {
  const userStore = useUserStore()
  userStore.setUser({
    username: 'nigga', // Replace with actual username from your database
    telegramId: 521829496,
    profile: {
      tankVolume: 50,
      soilVolume: 20,
      email: 'test@example.com',
      joinedAt: new Date().toISOString()
    }
  })
}, 100)
*/