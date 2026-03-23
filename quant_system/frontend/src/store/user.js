import { defineStore } from 'pinia'
import api from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
    token: localStorage.getItem('token') || ''
  }),
  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/auth/login', { username, password })
        const { access_token } = response.data
        this.token = access_token
        localStorage.setItem('token', access_token)
        await this.getUserInfo()
        this.isLoggedIn = true
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },
    async register(userData) {
      try {
        await api.post('/auth/register', userData)
        return true
      } catch (error) {
        console.error('Register failed:', error)
        return false
      }
    },
    async getUserInfo() {
      try {
        const response = await api.get('/user/me')
        this.user = response.data
        return this.user
      } catch (error) {
        console.error('Get user info failed:', error)
        return null
      }
    },
    async checkLogin() {
      if (this.token) {
        const user = await this.getUserInfo()
        this.isLoggedIn = !!user
      }
    },
    logout() {
      this.isLoggedIn = false
      this.user = null
      this.token = ''
      localStorage.removeItem('token')
    }
  }
})