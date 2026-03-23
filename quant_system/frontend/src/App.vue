<template>
  <div id="app">
    <el-container style="min-height: 100vh;">
      <el-header height="60px" class="header">
        <div class="logo">个人量化分析与交易系统</div>
        <el-menu :default-active="activeIndex" mode="horizontal" background-color="#001529" text-color="#fff" active-text-color="#409EFF">
          <el-menu-item index="/" @click="navigate('/')">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/data" @click="navigate('/data')">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据管理</span>
          </el-menu-item>
          <el-menu-item index="/strategy" @click="navigate('/strategy')">
            <el-icon><TrendCharts /></el-icon>
            <span>策略开发</span>
          </el-menu-item>
          <el-menu-item index="/backtest" @click="navigate('/backtest')">
            <el-icon><Histogram /></el-icon>
            <span>回测系统</span>
          </el-menu-item>
          <el-menu-item index="/trading" @click="navigate('/trading')">
            <el-icon><Selling /></el-icon>
            <span>交易管理</span>
          </el-menu-item>
          <el-menu-item index="/settings" @click="navigate('/settings')">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
          <el-menu-item index="/user" @click="navigate('/user')" style="margin-left: auto;">
            <el-icon><User /></el-icon>
            <span>{{ userStore.user?.username || '登录' }}</span>
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './store/user'
import { HomeFilled, DataAnalysis, TrendCharts, Histogram, Selling, Setting, User } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeIndex = ref('/')

const navigate = (path) => {
  router.push(path)
  activeIndex.value = path
}

onMounted(() => {
  // 检查用户登录状态
  userStore.checkLogin()
  // 设置当前激活的菜单
  activeIndex.value = router.currentRoute.value.path
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #001529;
  color: white;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  margin-right: 40px;
}

.el-main {
  padding: 20px;
  background-color: #f5f5f5;
}
</style>
