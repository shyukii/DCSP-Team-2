import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/base.css' // Tailwind build entry
import '@fortawesome/fontawesome-free/css/all.css'
createApp(App).use(router).mount('#app')
