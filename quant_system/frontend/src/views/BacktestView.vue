<template>
  <div class="backtest-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>回测管理</span>
        </div>
      </template>
      <el-table :data="backtests" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="strategy_id" label="策略ID" width="100" />
        <el-table-column prop="start_date" label="开始日期" width="150" />
        <el-table-column prop="end_date" label="结束日期" width="150" />
        <el-table-column prop="performance" label="收益率(%)" width="120" />
        <el-table-column prop="max_drawdown" label="最大回撤(%)" width="120" />
        <el-table-column prop="sharpe_ratio" label="夏普比率" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="analyzeBacktest(scope.row.id)">分析</el-button>
            <el-button size="small" type="danger" @click="deleteBacktest(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>运行回测</span>
        </div>
      </template>
      <el-form :model="backtestForm" label-width="100px">
        <el-form-item label="策略选择">
          <el-select v-model="backtestForm.strategy_id" placeholder="选择策略">
            <el-option v-for="strategy in strategies" :key="strategy.id" :label="strategy.name" :value="strategy.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="backtestForm.start_date" type="date" placeholder="选择开始日期" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="backtestForm.end_date" type="date" placeholder="选择结束日期" />
        </el-form-item>
        <el-form-item label="策略参数">
          <el-input
            v-model="backtestForm.parameters"
            type="textarea"
            :rows="3"
            placeholder="请输入策略参数（JSON格式）"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runBacktest">运行回测</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 回测分析结果 -->
    <el-card shadow="hover" class="mt-20" v-if="backtestAnalysis">
      <template #header>
        <div class="card-header">
          <span>回测分析结果</span>
        </div>
      </template>
      <div class="backtest-analysis">
        <el-descriptions :column="3">
          <el-descriptions-item label="回测ID">{{ backtestAnalysis.backtest_id }}</el-descriptions-item>
          <el-descriptions-item label="策略ID">{{ backtestAnalysis.strategy_id }}</el-descriptions-item>
          <el-descriptions-item label="回测周期">{{ backtestAnalysis.start_date }} 至 {{ backtestAnalysis.end_date }}</el-descriptions-item>
          <el-descriptions-item label="总收益率">{{ backtestAnalysis.total_return.toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="年化收益率">{{ backtestAnalysis.annual_return.toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="最大回撤">{{ backtestAnalysis.max_drawdown.toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="夏普比率">{{ backtestAnalysis.sharpe_ratio.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="索提诺比率">{{ backtestAnalysis.sortino_ratio.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="卡玛比率">{{ backtestAnalysis.calmar_ratio.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="波动率">{{ backtestAnalysis.volatility.toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="胜率">{{ backtestAnalysis.win_rate.toFixed(2) }}%</el-descriptions-item>
          <el-descriptions-item label="总交易次数">{{ backtestAnalysis.total_trades }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="chart-container" style="margin-top: 20px;">
          <h4>权益曲线</h4>
          <div id="equityChart" style="width: 100%; height: 400px;"></div>
        </div>
        
        <div v-if="backtestAnalysis.signals && backtestAnalysis.signals.length > 0" style="margin-top: 20px;">
          <h4>交易信号</h4>
          <el-table :data="backtestAnalysis.signals" style="width: 100%">
            <el-table-column prop="symbol" label="标的" />
            <el-table-column prop="signal" label="信号" />
            <el-table-column prop="price" label="价格" />
            <el-table-column prop="quantity" label="数量" />
            <el-table-column prop="timestamp" label="时间" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

// 回测管理
const backtests = ref([])
const strategies = ref([])
const backtestForm = ref({
  strategy_id: '',
  start_date: '',
  end_date: '',
  parameters: ''
})
const backtestAnalysis = ref(null)
let equityChart = null

// 获取回测列表
const fetchBacktests = async () => {
  try {
    const response = await api.get('/backtest')
    backtests.value = response.data
  } catch (error) {
    console.error('获取回测列表失败:', error)
  }
}

// 获取策略列表
const fetchStrategies = async () => {
  try {
    const response = await api.get('/strategy')
    strategies.value = response.data
  } catch (error) {
    console.error('获取策略列表失败:', error)
  }
}

// 运行回测
const runBacktest = async () => {
  try {
    let parameters = {}
    if (backtestForm.value.parameters) {
      try {
        parameters = JSON.parse(backtestForm.value.parameters)
      } catch (e) {
        console.error('参数格式错误:', e)
        return
      }
    }
    await api.post('/backtest', {
      strategy_id: backtestForm.value.strategy_id,
      start_date: backtestForm.value.start_date,
      end_date: backtestForm.value.end_date,
      parameters: parameters
    })
    // 刷新回测列表
    fetchBacktests()
  } catch (error) {
    console.error('运行回测失败:', error)
  }
}

// 删除回测
const deleteBacktest = async (id) => {
  try {
    await api.delete(`/backtest/${id}`)
    // 刷新回测列表
    fetchBacktests()
  } catch (error) {
    console.error('删除回测失败:', error)
  }
}

// 分析回测
const analyzeBacktest = async (id) => {
  try {
    const response = await api.get(`/backtest/${id}/analysis`)
    backtestAnalysis.value = response.data
    // 渲染图表
    setTimeout(() => {
      renderEquityChart()
    }, 100)
  } catch (error) {
    console.error('分析回测失败:', error)
  }
}

// 渲染权益曲线
const renderEquityChart = () => {
  if (backtestAnalysis.value && backtestAnalysis.value.equity_curve) {
    if (equityChart) {
      equityChart.dispose()
    }
    equityChart = echarts.init(document.getElementById('equityChart'))
    
    const option = {
      title: {
        text: '策略权益曲线',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: backtestAnalysis.value.dates || Array(backtestAnalysis.value.equity_curve.length).fill('')
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data: backtestAnalysis.value.equity_curve,
        type: 'line',
        smooth: true
      }]
    }
    
    equityChart.setOption(option)
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      equityChart.resize()
    })
  }
}

onMounted(() => {
  fetchBacktests()
  fetchStrategies()
  // 设置默认日期
  const today = new Date()
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  backtestForm.value.start_date = oneYearAgo
  backtestForm.value.end_date = today
})

// 监听回测分析结果变化
watch(backtestAnalysis, () => {
  if (backtestAnalysis.value) {
    setTimeout(() => {
      renderEquityChart()
    }, 100)
  }
}, { deep: true })
</script>

<style scoped>
.backtest-view {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mt-20 {
  margin-top: 20px;
}

.backtest-analysis {
  margin-top: 20px;
}

.chart-container {
  margin-top: 20px;
}
</style>
