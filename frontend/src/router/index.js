import 'material-design-icons-iconfont/dist/material-design-icons.css' // Ensure you are using css-loader
import Vue from 'vue'
import Router from 'vue-router'
import VueAnalytics from 'vue-analytics'
import Vuetify from 'vuetify'

// *** DONT FORGET TO ADD NEW ROUTES TO FLASK TOO !
const routerOptions = [
  {path: '/crew', component: 'Chars'},
  {path: '/items', component: 'Items'},
  {path: '/rooms', component: 'Rooms'},
  {path: '/crew/:id', component: 'CrewDetail'},
  {path: '/ships', component: 'Ships'},
  {path: '/builder', component: 'Builder'},
  {path: '/changes', component: 'Changes'},
  {path: '/collections', component: 'Collections'},
  {path: '/research', component: 'Research'},
  {path: '/players', component: 'Players'},
  {path: '/', component: 'Home'},
  {path: '*', component: 'NotFound'}
]

const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`)
  }
})

Vue.use(Router);
Vue.use(Vuetify);

const router = new Router({
  routes,
  mode: 'history'
})

Vue.use(VueAnalytics, {
  id: 'UA-67866007-2',
  router
})

export default router
