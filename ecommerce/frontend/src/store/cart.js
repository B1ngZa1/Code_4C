import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: []
  }),
  getters: {
    totalPrice: (state) => {
      return state.items.reduce((total, item) => total + item.price * item.quantity, 0)
    },
    totalItems: (state) => {
      return state.items.reduce((total, item) => total + item.quantity, 0)
    }
  },
  actions: {
    addItem(product, quantity = 1) {
      const existingItem = this.items.find(item => item.id === product.id)
      if (existingItem) {
        existingItem.quantity += quantity
      } else {
        this.items.push({ ...product, quantity })
      }
    },
    removeItem(productId) {
      this.items = this.items.filter(item => item.id !== productId)
    },
    updateQuantity(productId, quantity) {
      const item = this.items.find(item => item.id === productId)
      if (item) {
        item.quantity = quantity
      }
    },
    clearCart() {
      this.items = []
    }
  }
})