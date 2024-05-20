import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import apiService from './services/api';

Vue.config.productionTip = false

apiService.getConfig().then(response => {
    const config = response.data;
    new Vue({
        vuetify,
        router,
        data() {
            return {
                config
            }
        },
        render: h => h(App),
    }).$mount('#app')
}).catch(error => {
    console.error('Error fetching config:', error);
});
