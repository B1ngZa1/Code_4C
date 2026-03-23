<template>
  <div class="home">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>系统概览</span>
        </div>
      </template>
      <div class="overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dataCount }}</div>
                <div class="stat-label">数据条数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ strategyCount }}</div>
                <div class="stat-label">策略数量</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon><Histogram /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ backtestCount }}</div>
                <div class="stat-label">回测次数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon">
                <el-icon><Selling /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ tradeCount }}</div>
                <div class="stat-label">交易次数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>市场概览</span>
        </div>
      </template>
      <div class="market-overview">
        <div id="marketChart" style="width: 100%; height: 400px;"></div>
      </div>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>最近策略</span>
        </div>
      </template>
      <div class="recent-strategies">
        <el-table :data="recentStrategies" style="width: 100%">
          <el-table-column prop="name" label="策略名称" width="180" />
          <el-table-column prop="type" label="策略类型" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="performance" label="绩效" width="100" />
          <el-table-column label="操作">
            <template #default>
              <el-button size="small" type="primary">查看</el-button>
              <el-button size="small">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { DataAnalysis, TrendCharts, Histogram, Selling } from '@element-plus/icons-vue'

const dataCount = ref(10000)
const strategyCount = ref(20)
const backtestCount = ref(150)
const tradeCount = ref(80)

const recentStrategies = ref([
  {
    name: 'MACD策略',
    type: '趋势',
    created_at: '2026-03-20',
    status: '运行中',
    performance: '12.5%'
  },
  {
    name: 'RSI策略',
    type: '震荡',
    created_at: '2026-03-18',
    status: '已停止',
    performance: '8.2%'
  },
  {
    name: '布林带策略',
    type: '突破',
    created_at: '2026-03-15',
    status: '运行中',
    performance: '15.3%'
  },
  {
    name: '均值回归策略',
    type: '均值回归',
    created_at: '2026-03-10',
    status: '已停止',
    performance: '5.7%'
  }
])

let marketChart = null

const initMarketChart = () => {
  if (marketChart) {
    marketChart.dispose()
  }
  marketChart = echarts.init(document.getElementById('marketChart'))
  
  const option = {
    title: {
      text: '市场指数走势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['上证指数', '深证成指'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['03-15', '03-16', '03-17', '03-18', '03-19', '03-20', '03-21']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '上证指数',
        type: 'line',
        data: [3200, 3250, 3220, 3300, 3350, 3400, 3450]
      },
      {
        name: '深证成指',
        type: 'line',
        data: [12000, 12200, 12100, 12500, 12800, 13000, 13200]
      }
    ]
  }
  
  marketChart.setOption(option)
}

onMounted(() => {
  initMarketChart()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    marketChart.resize()
  })
})
</script>

<style scoped>
.home {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview {
  margin-top: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.stat-icon {
  font-size: 48px;
  color: #409EFF;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.mt-20 {
  margin-top: 20px;
}

.market-overview {
  margin-top: 20px;
}

.recent-strategies {
  margin-top: 20px;
}
</style>
