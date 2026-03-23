<template>
  <div class="home">
    <header class="header">
      <div class="container">
        <div class="logo">电商平台</div>
        <nav class="nav">
          <router-link to="/">首页</router-link>
          <router-link to="/cart">购物车</router-link>
          <router-link to="/order">订单</router-link>
          <template v-if="!userStore.isLoggedIn">
            <router-link to="/login">登录</router-link>
            <router-link to="/register">注册</router-link>
          </template>
          <template v-else>
            <span>{{ userStore.user.username }}</span>
            <button @click="logout">退出</button>
          </template>
        </nav>
      </div>
    </header>
    
    <main class="main">
      <div class="container">
        <div class="search-bar">
          <input type="text" v-model="searchKeyword" placeholder="搜索商品" />
          <button @click="search">搜索</button>
        </div>
        
        <div class="product-list">
          <div v-for="product in products" :key="product.id" class="product-item">
            <router-link :to="`/product/${product.id}`">
              <div class="product-image">
                <img :src="product.image_url" :alt="product.name" />
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <p>{{ product.description }}</p>
                <div class="product-price">¥{{ product.price }}</div>
                <button @click.stop="addToCart(product)" class="add-to-cart">加入购物车</button>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../store/user'
import { useCartStore } from '../store/cart'
import api from '../api'

const userStore = useUserStore()
const cartStore = useCartStore()
const products = ref([])
const searchKeyword = ref('')

const logout = () => {
  userStore.logout()
}

const addToCart = (product) => {
  cartStore.addItem(product)
  // 显示添加成功提示
}

const search = () => {
  // 搜索逻辑
}

const fetchProducts = async () => {
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav a {
  text-decoration: none;
  color: #333;
}

.nav button {
  background-color: #f0f0f0;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.main {
  flex: 1;
  padding: 2rem 0;
}

.search-bar {
  margin-bottom: 2rem;
  display: flex;
  gap: 0.5rem;
}

.search-bar input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-bar button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.product-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.product-item {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.product-item:hover {
  transform: translateY(-5px);
}

.product-image {
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 1rem;
}

.product-info h3 {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.product-info p {
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #ff4444;
  margin-bottom: 1rem;
}

.add-to-cart {
  width: 100%;
  padding: 0.5rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.add-to-cart:hover {
  background-color: #45a049;
}
</style>