import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Crews from '../views/Crews.vue'
import Items from '../views/Items.vue'
import Rooms from '../views/Rooms.vue'
import Ships from '../views/Ships.vue'
import Collections from '../views/Collections.vue'
import Researches from '../views/Researches.vue'
import Changes from '../views/Changes.vue'
import Players from '../views/Players.vue'
import Builder from '../views/Builder.vue'
import CrewDetail from '../views/CrewDetail.vue'
import ItemDetail from '../views/ItemDetail.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/crews',
    name: 'Crews',
    component: Crews
  },
  {
    path: '/crew/:id',
    name: 'CrewDetail',
    component: CrewDetail
  },
  {
    path: '/items',
    name: 'Items',
    component: Items
  },
  {
    path: '/item/:id',
    name: 'ItemDetail',
    component: ItemDetail
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: Rooms
  },
  {
    path: '/ships',
    name: 'Ships',
    component: Ships
  },
  {
    path: '/collections',
    name: 'Collections',
    component: Collections
  },
  {
    path: '/researches',
    name: 'Researches',
    component: Researches
  },
  {
    path: '/changes',
    name: 'Changes',
    component: Changes
  },
  {
    path: '/players',
    name: 'Players',
    component: Players
  },
  {
    path: '/builder',
    name: 'Builder',
    component: Builder
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
