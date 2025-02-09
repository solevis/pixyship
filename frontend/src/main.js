import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import apiService from './services/api'

// Import des styles nécessaires pour Vuetify 3
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createHead } from '@vueuse/head'

apiService.getConfig().then(response => {
    const config = response.data

    const app = createApp(App)
    const head = createHead()


    // Alternative: utiliser provide/inject
    app.provide('config', config)

    app.use(vuetify)
    app.use(router)
    app.use(head)

    app.mount('#app')
}).catch(error => {
    console.error('Error fetching config:', error)
})
