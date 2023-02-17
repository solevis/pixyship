import Vue from 'vue'
import VueRouter from 'vue-router'
import VueMeta from 'vue-meta'

Vue.use(VueRouter)
Vue.use(VueMeta)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/crews',
    name: 'Crews',
    component: () => import('../views/Crews.vue')
  },
  {
    path: '/crew',
    redirect: '/crews'
  },
  {
    path: '/crew/:id',
    name: 'CrewDetail',
    component: () => import('../views/CrewDetail.vue')
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('../views/Items.vue')
  },
  {
    path: '/item/:id',
    name: 'ItemDetail',
    component: () => import('../views/ItemDetail.vue')
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: () => import('../views/Rooms.vue')
  },
  {
    path: '/ships',
    name: 'Ships',
    component: () => import('../views/Ships.vue')
  },
  {
    path: '/collections',
    name: 'Collections',
    component: () => import('../views/Collections.vue')
  },
  {
    path: '/achievements',
    name: 'Pins',
    component: () => import('../views/Achievements.vue')
  },
  {
    path: '/researches',
    name: 'Researches',
    component: () => import('../views/Researches.vue')
  },
  {
    path: '/research',
    redirect: '/researches'
  },
  {
    path: '/changes',
    name: 'Changes',
    component: () => import('../views/Changes.vue')
  },
  {
    path: '/players',
    name: 'Players',
    component: () => import('../views/Players.vue')
  },
  {
    path: '/builder',
    name: 'Builder',
    component: () => import('../views/Builder.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/changelog',
    name: 'Changelog',
    component: () => import('../views/Changelog.vue')
  },
  {
    path: '/dailysales/:from',
    name: 'DailySalesHistory',
    component: () => import('../views/DailySalesHistory.vue')
  },
  {
    path: '/crafts',
    name: 'Crafts',
    component: () => import('../views/Crafts.vue')
  },
  {
    path: '*',
    component: () => import('../views/Home.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.onError(error => {
  if (/loading chunk \d* failed./i.test(error.message)) {
    window.location.reload()
  }
})

export default router
