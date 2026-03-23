<template>
  <div class="trading-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>交易管理</span>
          <el-button type="primary" @click="showAddTradeDialog = true">创建交易</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="tradeFilter" class="mb-20">
        <el-form-item label="策略ID">
          <el-input v-model="tradeFilter.strategy_id" placeholder="策略ID" />
        </el-form-item>
        <el-form-item label="交易类型">
          <el-select v-model="tradeFilter.trade_type" placeholder="交易类型">
            <el-option label="模拟交易" value="paper" />
            <el-option label="实盘交易" value="real" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTrades">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="trades" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="strategy_id" label="策略ID" width="100" />
        <el-table-column prop="symbol" label="标的" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.direction === 'buy' ? 'success' : 'danger'">{{ scope.row.direction === 'buy' ? '买入' : '卖出' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="trade_type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.trade_type === 'paper' ? 'info' : 'warning'">{{ scope.row.trade_type === 'paper' ? '模拟' : '实盘' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="executed_at" label="执行时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" @click="cancelTrade(scope.row.id)" v-if="scope.row.status === 'pending'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>投资组合</span>
        </div>
      </template>
      <el-form :inline="true" :model="portfolioFilter" class="mb-20">
        <el-form-item label="交易类型">
          <el-select v-model="portfolioFilter.trade_type" placeholder="交易类型" @change="fetchPortfolio">
            <el-option label="模拟交易" value="paper" />
            <el-option label="实盘交易" value="real" />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="portfolio">
        <el-descriptions :column="3">
          <el-descriptions-item label="总市值">{{ portfolio.total_value }}</el-descriptions-item>
          <el-descriptions-item label="总成本">{{ portfolio.total_cost }}</el-descriptions-item>
          <el-descriptions-item label="总盈利">{{ portfolio.total_profit }}</el-descriptions-item>
          <el-descriptions-item label="总收益率">{{ portfolio.total_profit_rate.toFixed(2) }}%</el-descriptions-item>
        </el-descriptions>
        <div class="mt-20">
          <h4>持仓明细</h4>
          <el-table :data="portfolioHoldings" style="width: 100%">
            <el-table-column prop="symbol" label="标的" />
            <el-table-column prop="quantity" label="数量" />
            <el-table-column prop="avg_price" label="平均成本" />
            <el-table-column prop="current_price" label="当前价格" />
            <el-table-column prop="market_value" label="市值" />
            <el-table-column prop="profit" label="盈利" />
            <el-table-column prop="profit_rate" label="收益率(%)" />
          </el-table>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>交易统计</span>
        </div>
      </template>
      <el-form :inline="true" :model="statsFilter" class="mb-20">
        <el-form-item label="开始日期">
          <el-date-picker v-model="statsFilter.start_date" type="date" placeholder="选择开始日期" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="statsFilter.end_date" type="date" placeholder="选择结束日期" />
        </el-form-item>
        <el-form-item label="交易类型">
          <el-select v-model="statsFilter.trade_type" placeholder="交易类型">
            <el-option label="模拟交易" value="paper" />
            <el-option label="实盘交易" value="real" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTradeStats">查询</el-button>
        </el-form-item>
      </el-form>
      <div v-if="tradeStats">
        <el-descriptions :column="3">
          <el-descriptions-item label="总交易次数">{{ tradeStats.total_trades }}</el-descriptions-item>
          <el-descriptions-item label="买入次数">{{ tradeStats.total_buy }}</el-descriptions-item>
          <el-descriptions-item label="卖出次数">{{ tradeStats.total_sell }}</el-descriptions-item>
          <el-descriptions-item label="总交易金额">{{ tradeStats.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="总盈利">{{ tradeStats.profit }}</el-descriptions-item>
          <el-descriptions-item label="盈利比例">{{ tradeStats.profit_rate.toFixed(2) }}%</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 创建交易对话框 -->
    <el-dialog v-model="showAddTradeDialog" title="创建交易">
      <el-form :model="tradeForm" label-width="80px">
        <el-form-item label="标的">
          <el-input v-model="tradeForm.symbol" placeholder="请输入标的" />
        </el-form-item>
        <el-form-item label="方向">
          <el-select v-model="tradeForm.direction" placeholder="选择方向">
            <el-option label="买入" value="buy" />
            <el-option label="卖出" value="sell" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格">
          <el-input v-model="tradeForm.price" type="number" placeholder="请输入价格" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input v-model="tradeForm.quantity" type="number" placeholder="请输入数量" />
        </el-form-item>
        <el-form-item label="策略ID">
          <el-input v-model="tradeForm.strategy_id" type="number" placeholder="请输入策略ID" />
        </el-form-item>
        <el-form-item label="交易类型">
          <el-select v-model="tradeForm.trade_type" placeholder="选择交易类型">
            <el-option label="模拟交易" value="paper" />
            <el-option label="实盘交易" value="real" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddTradeDialog = false">取消</el-button>
          <el-button type="primary" @click="createTrade">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// 交易管理
const trades = ref([])
const showAddTradeDialog = ref(false)
const tradeForm = ref({
  symbol: '',
  direction: 'buy',
  price: 0,
  quantity: 0,
  strategy_id: '',
  trade_type: 'paper'
})
const tradeFilter = ref({
  strategy_id: '',
  trade_type: ''
})

// 投资组合
const portfolio = ref(null)
const portfolioFilter = ref({
  trade_type: 'paper'
})
const portfolioHoldings = ref([])

// 交易统计
const tradeStats = ref(null)
const statsFilter = ref({
  start_date: '',
  end_date: '',
  trade_type: ''
})

// 获取交易列表
const fetchTrades = async () => {
  try {
    const params = {}
    if (tradeFilter.value.strategy_id) {
      params.strategy_id = tradeFilter.value.strategy_id
    }
    if (tradeFilter.value.trade_type) {
      params.trade_type = tradeFilter.value.trade_type
    }
    const response = await api.get('/trading', { params })
    trades.value = response.data
  } catch (error) {
    console.error('获取交易列表失败:', error)
  }
}

// 创建交易
const createTrade = async () => {
  try {
    await api.post('/trading', {
      symbol: tradeForm.value.symbol,
      direction: tradeForm.value.direction,
      price: tradeForm.value.price,
      quantity: tradeForm.value.quantity,
      strategy_id: tradeForm.value.strategy_id,
      trade_type: tradeForm.value.trade_type
    })
    showAddTradeDialog.value = false
    // 重置表单
    tradeForm.value = {
      symbol: '',
      direction: 'buy',
      price: 0,
      quantity: 0,
      strategy_id: '',
      trade_type: 'paper'
    }
    // 刷新交易列表
    fetchTrades()
    // 刷新投资组合
    fetchPortfolio()
  } catch (error) {
    console.error('创建交易失败:', error)
  }
}

// 取消交易
const cancelTrade = async (id) => {
  try {
    await api.put(`/trading/${id}/cancel`)
    // 刷新交易列表
    fetchTrades()
  } catch (error) {
    console.error('取消交易失败:', error)
  }
}

// 获取投资组合
const fetchPortfolio = async () => {
  try {
    const response = await api.get('/trading/portfolio', {
      params: {
        trade_type: portfolioFilter.value.trade_type
      }
    })
    portfolio.value = response.data
    // 转换持仓数据格式
    portfolioHoldings.value = Object.entries(portfolio.value.holdings).map(([symbol, info]) => ({
      symbol,
      ...info
    }))
  } catch (error) {
    console.error('获取投资组合失败:', error)
  }
}

// 获取交易统计
const fetchTradeStats = async () => {
  try {
    const params = {}
    if (statsFilter.value.start_date) {
      params.start_date = statsFilter.value.start_date
    }
    if (statsFilter.value.end_date) {
      params.end_date = statsFilter.value.end_date
    }
    if (statsFilter.value.trade_type) {
      params.trade_type = statsFilter.value.trade_type
    }
    const response = await api.get('/trading/stats/summary', { params })
    tradeStats.value = response.data
  } catch (error) {
    console.error('获取交易统计失败:', error)
  }
}

onMounted(() => {
  fetchTrades()
  fetchPortfolio()
  fetchTradeStats()
  // 设置默认日期
  const today = new Date()
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(today.getMonth() - 1)
  statsFilter.value.start_date = oneMonthAgo
  statsFilter.value.end_date = today
})
</script>

<style scoped>
.trading-view {
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

.mb-20 {
  margin-bottom: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>