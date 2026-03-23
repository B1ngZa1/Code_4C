import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
    token: localStorage.getItem('token') || ''
  }),
  actions: {
    login(user, token) {
      this.isLoggedIn = true
      this.user = user
      this.token = token
      localStorage.setItem('token', token)
    },
    logout() {
      this.isLoggedIn = false
      this.user = null
      this.token = ''
      localStorage.removeItem('token')
    }
  }
})