<template>
  <div class="data-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>数据源管理</span>
          <el-button type="primary" @click="showAddDataSourceDialog = true">添加数据源</el-button>
        </div>
      </template>
      <el-table :data="dataSources" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="url" label="URL" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">{{ scope.row.is_active ? '激活' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="editDataSource(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDataSource(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>市场数据</span>
        </div>
      </template>
      <el-form :model="marketDataForm" label-width="80px">
        <el-form-item label=" symbol">
          <el-input v-model="marketDataForm.symbol" placeholder="请输入股票代码" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="marketDataForm.startDate" type="date" placeholder="选择开始日期" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="marketDataForm.endDate" type="date" placeholder="选择结束日期" />
        </el-form-item>
        <el-form-item label="时间间隔">
          <el-select v-model="marketDataForm.interval" placeholder="选择时间间隔">
            <el-option label="1分钟" value="1m" />
            <el-option label="5分钟" value="5m" />
            <el-option label="15分钟" value="15m" />
            <el-option label="30分钟" value="30m" />
            <el-option label="1小时" value="1h" />
            <el-option label="1天" value="1d" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="marketDataForm.source" placeholder="选择数据源">
            <el-option label="Tushare" value="tushare" />
            <el-option label="Binance" value="binance" />
            <el-option label="模拟数据" value="mock" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getMarketData">获取数据</el-button>
          <el-button @click="processData" v-if="marketDataResult">处理数据</el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="marketDataResult" class="market-data-result">
        <h3>市场数据结果</h3>
        <el-table :data="marketDataResult.data" style="width: 100%">
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="open" label="开盘价" />
          <el-table-column prop="high" label="最高价" />
          <el-table-column prop="low" label="最低价" />
          <el-table-column prop="close" label="收盘价" />
          <el-table-column prop="volume" label="成交量" />
        </el-table>
      </div>
      
      <div v-if="processedDataResult" class="processed-data-result">
        <h3>处理后数据</h3>
        <el-table :data="processedDataResult.processed_data" style="width: 100%">
          <el-table-column prop="date" label="日期" />
          <el-table-column prop="close" label="收盘价" />
          <el-table-column prop="ma5" label="MA5" />
          <el-table-column prop="ma10" label="MA10" />
          <el-table-column prop="return" label="收益率" />
          <el-table-column prop="volatility" label="波动率" />
        </el-table>
        <div class="data-summary" v-if="processedDataResult.summary">
          <h4>数据摘要</h4>
          <el-descriptions :column="3">
            <el-descriptions-item label="平均收盘价">{{ processedDataResult.summary.mean_close }}</el-descriptions-item>
            <el-descriptions-item label="收盘价标准差">{{ processedDataResult.summary.std_close }}</el-descriptions-item>
            <el-descriptions-item label="最高收盘价">{{ processedDataResult.summary.max_close }}</el-descriptions-item>
            <el-descriptions-item label="最低收盘价">{{ processedDataResult.summary.min_close }}</el-descriptions-item>
            <el-descriptions-item label="平均成交量">{{ processedDataResult.summary.mean_volume }}</el-descriptions-item>
            <el-descriptions-item label="总收益率">{{ processedDataResult.summary.total_return }}%</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

    <!-- 添加数据源对话框 -->
    <el-dialog v-model="showAddDataSourceDialog" title="添加数据源">
      <el-form :model="dataSourceForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="dataSourceForm.type" placeholder="请输入数据源类型" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="dataSourceForm.url" placeholder="请输入数据源URL" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="dataSourceForm.api_key" placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="dataSourceForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDataSourceDialog = false">取消</el-button>
          <el-button type="primary" @click="addDataSource">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑数据源对话框 -->
    <el-dialog v-model="showEditDataSourceDialog" title="编辑数据源">
      <el-form :model="dataSourceForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dataSourceForm.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="dataSourceForm.type" placeholder="请输入数据源类型" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="dataSourceForm.url" placeholder="请输入数据源URL" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="dataSourceForm.api_key" placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="dataSourceForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDataSourceDialog = false">取消</el-button>
          <el-button type="primary" @click="updateDataSource">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

// 数据源管理
const dataSources = ref([])
const showAddDataSourceDialog = ref(false)
const showEditDataSourceDialog = ref(false)
const dataSourceForm = ref({
  name: '',
  type: '',
  url: '',
  api_key: '',
  is_active: true
})
const editingDataSourceId = ref(null)

// 市场数据
const marketDataForm = ref({
  symbol: '000001',
  startDate: '',
  endDate: '',
  interval: '1d',
  source: 'mock'
})
const marketDataResult = ref(null)
const processedDataResult = ref(null)

// 获取数据源列表
const fetchDataSources = async () => {
  try {
    const response = await api.get('/data/sources')
    dataSources.value = response.data
  } catch (error) {
    console.error('获取数据源失败:', error)
  }
}

// 添加数据源
const addDataSource = async () => {
  try {
    await api.post('/data/sources', {
      name: dataSourceForm.value.name,
      type: dataSourceForm.value.type,
      url: dataSourceForm.value.url,
      api_key: dataSourceForm.value.api_key
    })
    showAddDataSourceDialog.value = false
    // 重置表单
    dataSourceForm.value = {
      name: '',
      type: '',
      url: '',
      api_key: '',
      is_active: true
    }
    // 刷新数据源列表
    fetchDataSources()
  } catch (error) {
    console.error('添加数据源失败:', error)
  }
}

// 编辑数据源
const editDataSource = (dataSource) => {
  dataSourceForm.value = {
    name: dataSource.name,
    type: dataSource.type,
    url: dataSource.url,
    api_key: dataSource.api_key,
    is_active: dataSource.is_active
  }
  editingDataSourceId.value = dataSource.id
  showEditDataSourceDialog.value = true
}

// 更新数据源
const updateDataSource = async () => {
  try {
    await api.put(`/data/sources/${editingDataSourceId.value}`, {
      name: dataSourceForm.value.name,
      type: dataSourceForm.value.type,
      url: dataSourceForm.value.url,
      api_key: dataSourceForm.value.api_key,
      is_active: dataSourceForm.value.is_active
    })
    showEditDataSourceDialog.value = false
    // 刷新数据源列表
    fetchDataSources()
  } catch (error) {
    console.error('更新数据源失败:', error)
  }
}

// 删除数据源
const deleteDataSource = async (id) => {
  try {
    await api.delete(`/data/sources/${id}`)
    // 刷新数据源列表
    fetchDataSources()
  } catch (error) {
    console.error('删除数据源失败:', error)
  }
}

// 获取市场数据
const getMarketData = async () => {
  try {
    const response = await api.get('/data/market', {
      params: {
        symbol: marketDataForm.value.symbol,
        start_date: marketDataForm.value.startDate,
        end_date: marketDataForm.value.endDate,
        interval: marketDataForm.value.interval
      }
    })
    marketDataResult.value = response.data
    processedDataResult.value = null
  } catch (error) {
    console.error('获取市场数据失败:', error)
  }
}

// 处理数据
const processData = async () => {
  try {
    const response = await api.post('/data/process', marketDataResult.value)
    processedDataResult.value = response.data
  } catch (error) {
    console.error('处理数据失败:', error)
  }
}

onMounted(() => {
  fetchDataSources()
  // 设置默认日期
  const today = new Date()
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(today.getMonth() - 1)
  marketDataForm.value.startDate = oneMonthAgo
  marketDataForm.value.endDate = today
})
</script>

<style scoped>
.data-view {
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

.market-data-result,
.processed-data-result {
  margin-top: 20px;
}

.data-summary {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>
