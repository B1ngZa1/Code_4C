<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="settings-header">
          <h2>系统设置</h2>
          <p>管理系统配置和API密钥</p>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="API设置" name="api">
          <el-form :model="apiSettings" label-width="120px">
            <el-form-item label="Tushare API Key">
              <el-input v-model="apiSettings.tushare_api_key" placeholder="请输入Tushare API Key" show-password />
            </el-form-item>
            <el-form-item label="Binance API Key">
              <el-input v-model="apiSettings.binance_api_key" placeholder="请输入Binance API Key" show-password />
            </el-form-item>
            <el-form-item label="Binance Secret Key">
              <el-input v-model="apiSettings.binance_secret_key" placeholder="请输入Binance Secret Key" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveApiSettings" :loading="loading">保存API设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="系统配置" name="system">
          <el-form :model="systemSettings" label-width="120px">
            <el-form-item label="数据更新频率">
              <el-select v-model="systemSettings.data_update_frequency" placeholder="请选择更新频率">
                <el-option label="1分钟" value="1m" />
                <el-option label="5分钟" value="5m" />
                <el-option label="15分钟" value="15m" />
                <el-option label="30分钟" value="30m" />
                <el-option label="1小时" value="1h" />
                <el-option label="1天" value="1d" />
              </el-select>
            </el-form-item>
            <el-form-item label="回测数据保存时间">
              <el-select v-model="systemSettings.backtest_data_retention" placeholder="请选择保存时间">
                <el-option label="7天" value="7" />
                <el-option label="30天" value="30" />
                <el-option label="90天" value="90" />
                <el-option label="180天" value="180" />
                <el-option label="365天" value="365" />
              </el-select>
            </el-form-item>
            <el-form-item label="通知设置">
              <el-switch v-model="systemSettings.enable_notifications" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystemSettings" :loading="loading">保存系统配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="关于系统" name="about">
          <div class="about-content">
            <h3>个人量化分析与交易系统</h3>
            <p>版本: 1.0.0</p>
            <p>基于Vue 3和FastAPI开发</p>
            <p>功能参考qbot，支持数据获取、策略开发、回测验证、模拟交易和实盘交易</p>
            <el-divider />
            <h4>系统特性</h4>
            <ul>
              <li>多源数据获取（Tushare、Binance、模拟数据）</li>
              <li>策略开发和回测</li>
              <li>绩效分析和可视化</li>
              <li>模拟交易和实盘交易</li>
              <li>投资组合管理</li>
            </ul>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const activeTab = ref('api')
const loading = ref(false)

const apiSettings = reactive({
  tushare_api_key: '',
  binance_api_key: '',
  binance_secret_key: ''
})

const systemSettings = reactive({
  data_update_frequency: '5m',
  backtest_data_retention: '30',
  enable_notifications: true
})

onMounted(() => {
  // 从本地存储加载设置
  loadSettings()
})

const loadSettings = () => {
  const savedApiSettings = localStorage.getItem('apiSettings')
  const savedSystemSettings = localStorage.getItem('systemSettings')
  
  if (savedApiSettings) {
    Object.assign(apiSettings, JSON.parse(savedApiSettings))
  }
  
  if (savedSystemSettings) {
    Object.assign(systemSettings, JSON.parse(savedSystemSettings))
  }
}

const saveApiSettings = () => {
  loading.value = true
  try {
    // 保存到本地存储
    localStorage.setItem('apiSettings', JSON.stringify(apiSettings))
    // 这里可以添加API调用，将设置保存到服务器
    console.log('API设置保存成功:', apiSettings)
    alert('API设置保存成功')
  } catch (error) {
    console.error('API设置保存失败:', error)
  } finally {
    loading.value = false
  }
}

const saveSystemSettings = () => {
  loading.value = true
  try {
    // 保存到本地存储
    localStorage.setItem('systemSettings', JSON.stringify(systemSettings))
    // 这里可以添加API调用，将设置保存到服务器
    console.log('系统配置保存成功:', systemSettings)
    alert('系统配置保存成功')
  } catch (error) {
    console.error('系统配置保存失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 80vh;
}

.settings-card {
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.settings-header {
  text-align: center;
  margin-bottom: 20px;
}

.settings-header h2 {
  margin-bottom: 10px;
  color: #1890ff;
}

.settings-header p {
  color: #666;
  font-size: 14px;
}

.about-content {
  padding: 20px;
  line-height: 1.8;
}

.about-content h3 {
  color: #1890ff;
  margin-bottom: 10px;
}

.about-content h4 {
  margin-top: 20px;
  margin-bottom: 10px;
}

.about-content ul {
  padding-left: 20px;
}
</style>