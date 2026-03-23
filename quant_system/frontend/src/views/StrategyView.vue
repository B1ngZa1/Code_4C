<template>
  <div class="strategy-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>策略管理</span>
          <el-button type="primary" @click="showAddStrategyDialog = true">创建策略</el-button>
        </div>
      </template>
      <el-table :data="strategies" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="type" label="策略类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">{{ scope.row.status === 'active' ? '运行中' : '已停止' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editStrategy(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="executeStrategy(scope.row.id)">执行</el-button>
            <el-button size="small" type="danger" @click="deleteStrategy(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>策略编辑器</span>
        </div>
      </template>
      <el-form :model="strategyForm" label-width="80px">
        <el-form-item label="策略名称">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-input v-model="strategyForm.type" placeholder="请输入策略类型" />
        </el-form-item>
        <el-form-item label="策略代码">
          <el-input
            v-model="strategyForm.code"
            type="textarea"
            :rows="10"
            placeholder="请输入策略代码"
          />
        </el-form-item>
        <el-form-item label="策略参数">
          <el-input
            v-model="strategyForm.parameters"
            type="textarea"
            :rows="3"
            placeholder="请输入策略参数（JSON格式）"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveStrategy">保存策略</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 执行策略结果 -->
    <el-card shadow="hover" class="mt-20" v-if="executionResult">
      <template #header>
        <div class="card-header">
          <span>策略执行结果</span>
        </div>
      </template>
      <div class="execution-result">
        <el-descriptions :column="2">
          <el-descriptions-item label="策略ID">{{ executionResult.strategy_id }}</el-descriptions-item>
          <el-descriptions-item label="策略名称">{{ executionResult.strategy_name }}</el-descriptions-item>
          <el-descriptions-item label="执行状态">{{ executionResult.status }}</el-descriptions-item>
          <el-descriptions-item label="执行时间">{{ new Date().toLocaleString() }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="executionResult.signals && executionResult.signals.length > 0">
          <h4>交易信号</h4>
          <el-table :data="executionResult.signals" style="width: 100%">
            <el-table-column prop="symbol" label="标的" />
            <el-table-column prop="signal" label="信号" />
            <el-table-column prop="price" label="价格" />
            <el-table-column prop="quantity" label="数量" />
            <el-table-column prop="timestamp" label="时间" />
          </el-table>
        </div>
        <div v-if="executionResult.error">
          <el-alert
            title="执行错误"
            :description="executionResult.error"
            type="error"
            show-icon
          />
        </div>
      </div>
    </el-card>

    <!-- 创建策略对话框 -->
    <el-dialog v-model="showAddStrategyDialog" title="创建策略">
      <el-form :model="strategyForm" label-width="80px">
        <el-form-item label="策略名称">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-input v-model="strategyForm.type" placeholder="请输入策略类型" />
        </el-form-item>
        <el-form-item label="策略代码">
          <el-input
            v-model="strategyForm.code"
            type="textarea"
            :rows="10"
            placeholder="请输入策略代码"
          />
        </el-form-item>
        <el-form-item label="策略参数">
          <el-input
            v-model="strategyForm.parameters"
            type="textarea"
            :rows="3"
            placeholder="请输入策略参数（JSON格式）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddStrategyDialog = false">取消</el-button>
          <el-button type="primary" @click="addStrategy">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑策略对话框 -->
    <el-dialog v-model="showEditStrategyDialog" title="编辑策略">
      <el-form :model="strategyForm" label-width="80px">
        <el-form-item label="策略名称">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-input v-model="strategyForm.type" placeholder="请输入策略类型" />
        </el-form-item>
        <el-form-item label="策略代码">
          <el-input
            v-model="strategyForm.code"
            type="textarea"
            :rows="10"
            placeholder="请输入策略代码"
          />
        </el-form-item>
        <el-form-item label="策略参数">
          <el-input
            v-model="strategyForm.parameters"
            type="textarea"
            :rows="3"
            placeholder="请输入策略参数（JSON格式）"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="strategyForm.status" placeholder="选择状态">
            <el-option label="运行中" value="active" />
            <el-option label="已停止" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditStrategyDialog = false">取消</el-button>
          <el-button type="primary" @click="updateStrategy">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// 策略管理
const strategies = ref([])
const showAddStrategyDialog = ref(false)
const showEditStrategyDialog = ref(false)
const strategyForm = ref({
  name: '',
  type: '',
  code: '',
  parameters: '',
  status: 'inactive'
})
const editingStrategyId = ref(null)
const executionResult = ref(null)

// 获取策略列表
const fetchStrategies = async () => {
  try {
    const response = await api.get('/strategy')
    strategies.value = response.data
  } catch (error) {
    console.error('获取策略列表失败:', error)
  }
}

// 添加策略
const addStrategy = async () => {
  try {
    let parameters = {}
    if (strategyForm.value.parameters) {
      try {
        parameters = JSON.parse(strategyForm.value.parameters)
      } catch (e) {
        console.error('参数格式错误:', e)
        return
      }
    }
    await api.post('/strategy', {
      name: strategyForm.value.name,
      type: strategyForm.value.type,
      code: strategyForm.value.code,
      parameters: parameters
    })
    showAddStrategyDialog.value = false
    // 重置表单
    resetForm()
    // 刷新策略列表
    fetchStrategies()
  } catch (error) {
    console.error('添加策略失败:', error)
  }
}

// 编辑策略
const editStrategy = (strategy) => {
  strategyForm.value = {
    name: strategy.name,
    type: strategy.type,
    code: strategy.code,
    parameters: strategy.parameters || '',
    status: strategy.status
  }
  editingStrategyId.value = strategy.id
  showEditStrategyDialog.value = true
}

// 更新策略
const updateStrategy = async () => {
  try {
    let parameters = {}
    if (strategyForm.value.parameters) {
      try {
        parameters = JSON.parse(strategyForm.value.parameters)
      } catch (e) {
        console.error('参数格式错误:', e)
        return
      }
    }
    await api.put(`/strategy/${editingStrategyId.value}`, {
      name: strategyForm.value.name,
      type: strategyForm.value.type,
      code: strategyForm.value.code,
      parameters: parameters,
      status: strategyForm.value.status
    })
    showEditStrategyDialog.value = false
    // 刷新策略列表
    fetchStrategies()
  } catch (error) {
    console.error('更新策略失败:', error)
  }
}

// 保存策略
const saveStrategy = async () => {
  if (editingStrategyId.value) {
    await updateStrategy()
  } else {
    await addStrategy()
  }
}

// 删除策略
const deleteStrategy = async (id) => {
  try {
    await api.delete(`/strategy/${id}`)
    // 刷新策略列表
    fetchStrategies()
  } catch (error) {
    console.error('删除策略失败:', error)
  }
}

// 执行策略
const executeStrategy = async (id) => {
  try {
    const response = await api.post(`/strategy/${id}/execute`)
    executionResult.value = response.data
  } catch (error) {
    console.error('执行策略失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  strategyForm.value = {
    name: '',
    type: '',
    code: '',
    parameters: '',
    status: 'inactive'
  }
  editingStrategyId.value = null
}

onMounted(() => {
  fetchStrategies()
  // 设置默认策略代码
  strategyForm.value.code = `# 示例策略：移动平均线交叉策略
import pandas as pd
import numpy as np

# 策略参数
symbol = params.get('symbol', 'AAPL')
short_window = params.get('short_window', 5)
long_window = params.get('long_window', 20)

# 模拟数据获取
dates = pd.date_range('2026-01-01', '2026-03-31')
prices = np.random.randn(len(dates)) * 2 + 100
prices = np.cumsum(prices) + 1000
df = pd.DataFrame({'date': dates, 'close': prices})

# 计算移动平均线
df['short_ma'] = df['close'].rolling(window=short_window).mean()
df['long_ma'] = df['close'].rolling(window=long_window).mean()

# 生成交易信号
df['signal'] = 0
df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1

# 生成交易信号列表
for i in range(1, len(df)):
    if df['signal'].iloc[i] != df['signal'].iloc[i-1]:
        signal = 'buy' if df['signal'].iloc[i] == 1 else 'sell'
        signals.append({
            'symbol': symbol,
            'signal': signal,
            'price': df['close'].iloc[i],
            'quantity': 100,
            'timestamp': df['date'].iloc[i].strftime('%Y-%m-%d %H:%M:%S')
        })
`
  // 设置默认策略参数
  strategyForm.value.parameters = `{
  "symbol": "AAPL",
  "short_window": 5,
  "long_window": 20
}`
})
</script>

<style scoped>
.strategy-view {
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

.execution-result {
  margin-top: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>