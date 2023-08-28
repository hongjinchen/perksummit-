/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Components
import App from './App.vue'
import Cookies from 'js-cookie';
import '@mdi/font/css/materialdesignicons.css' // Ensure you are using css-loader

// Composables
import { createApp } from 'vue'

// Plugins
import { registerPlugins } from '@/plugins'

const app = createApp(App)
app.config.globalProperties.$cookies = Cookies;

registerPlugins(app)

app.mount('#app')
