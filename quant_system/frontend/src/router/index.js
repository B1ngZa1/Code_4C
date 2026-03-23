import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('../views/DataView.vue')
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('../views/StrategyView.vue')
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: () => import('../views/BacktestView.vue')
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('../views/TradingView.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue')
  },
  {
    path: '/user',
    name: 'User',
    component: () => import('../views/UserView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router