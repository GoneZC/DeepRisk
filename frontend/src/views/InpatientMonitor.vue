<template>
  <div class="container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">住院监管</span>
          <el-tag type="primary">数据分析</el-tag>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="医院名称">
          <el-select v-model="queryParams.hospital" placeholder="请选择医院" clearable>
            <el-option v-for="item in hospitalOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="queryParams.department" placeholder="请选择科室" clearable>
            <el-option v-for="item in departmentOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="入院日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据概览卡片 -->
      <el-row :gutter="20" class="data-overview">
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="overview-data">
              <div class="overview-value">{{ overviewData.totalHospitals }}</div>
              <div class="overview-label">监管医院数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon" style="background-color: #67C23A;">
              <el-icon><User /></el-icon>
            </div>
            <div class="overview-data">
              <div class="overview-value">{{ overviewData.totalPatients }}</div>
              <div class="overview-label">住院患者数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon" style="background-color: #E6A23C;">
              <el-icon><Money /></el-icon>
            </div>
            <div class="overview-data">
              <div class="overview-value">{{ formatCurrency(overviewData.totalCost) }}元</div>
              <div class="overview-label">总住院费用</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <div class="overview-icon" style="background-color: #F56C6C;">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="overview-data">
              <div class="overview-value">{{ overviewData.anomalyCount }}</div>
              <div class="overview-label">异常住院数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 住院监管数据表格 -->
      <el-table
        v-loading="loading"
        :data="inpatientList"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="patientId" label="患者ID" width="120" />
        <el-table-column prop="hospitalName" label="医院名称" width="180" show-overflow-tooltip />
        <el-table-column prop="department" label="科室" width="120" />
        <el-table-column prop="diagnosis" label="诊断" width="180" show-overflow-tooltip />
        <el-table-column prop="admissionDate" label="入院日期" width="120" />
        <el-table-column prop="dischargeDate" label="出院日期" width="120" />
        <el-table-column prop="stayLength" label="住院天数" width="100" align="right" sortable />
        <el-table-column prop="totalCost" label="总费用(元)" width="120" align="right" sortable>
          <template #default="scope">
            <span>{{ formatCurrency(scope.row.totalCost) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="anomalyType" label="异常类型" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.anomalyType" :type="getAnomalyTagType(scope.row.anomalyType)">
              {{ scope.row.anomalyType }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="riskScore" label="风险评分" width="100" align="center" sortable>
          <template #default="scope">
            <el-tag :type="getRiskTagType(scope.row.riskScore)">
              {{ scope.row.riskScore }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="viewDetails(scope.row)">详情</el-button>
            <el-button type="warning" link @click="handleAudit(scope.row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页器 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, OfficeBuilding, User, Money, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 页面数据
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dateRange = ref([])
const inpatientList = ref([])

// 查询参数
const queryParams = reactive({
  hospital: '',
  department: '',
  startDate: '',
  endDate: ''
})

// 数据概览
const overviewData = reactive({
  totalHospitals: 35,
  totalPatients: 12658,
  totalCost: 156789435.75,
  anomalyCount: 284
})

// 选项数据
const hospitalOptions = [
  { value: 'H001', label: '第一人民医院' },
  { value: 'H002', label: '中心医院' },
  { value: 'H003', label: '妇幼保健院' },
  { value: 'H004', label: '协和医院' }
]

const departmentOptions = [
  { value: 'D001', label: '内科' },
  { value: 'D002', label: '外科' },
  { value: 'D003', label: '妇科' },
  { value: 'D004', label: '儿科' },
  { value: 'D005', label: '骨科' },
  { value: 'D006', label: '神经科' }
]

// 初始化
onMounted(() => {
  fetchInpatientData()
})

// 获取住院数据
const fetchInpatientData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    setTimeout(() => {
      inpatientList.value = generateMockInpatientData()
      total.value = 2348
      loading.value = false
    }, 800)
  } catch (error) {
    ElMessage.error('获取数据失败')
    loading.value = false
  }
}

// 生成模拟数据
const generateMockInpatientData = () => {
  const mockData = []
  const anomalyTypes = [null, '费用异常', '住院时长异常', '诊疗路径异常', '重复住院']
  
  for (let i = 1; i <= 10; i++) {
    const hasAnomaly = Math.random() > 0.7
    const anomalyIndex = hasAnomaly ? Math.floor(Math.random() * 4) + 1 : 0
    const hospitalIndex = Math.floor(Math.random() * 4)
    const departmentIndex = Math.floor(Math.random() * 6)
    const stayLength = Math.floor(Math.random() * 30) + 1
    const totalCost = Math.random() * 50000 + 3000
    
    const admissionDate = new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1)
    const dischargeDate = new Date(admissionDate)
    dischargeDate.setDate(admissionDate.getDate() + stayLength)
    
    mockData.push({
      patientId: 'P' + String(Math.floor(Math.random() * 100000)).padStart(6, '0'),
      hospitalName: hospitalOptions[hospitalIndex].label,
      department: departmentOptions[departmentIndex].label,
      diagnosis: ['高血压', '糖尿病', '肺炎', '骨折', '胃炎'][Math.floor(Math.random() * 5)],
      admissionDate: formatDate(admissionDate),
      dischargeDate: formatDate(dischargeDate),
      stayLength: stayLength,
      totalCost: totalCost,
      anomalyType: anomalyTypes[anomalyIndex],
      riskScore: hasAnomaly ? Math.floor(Math.random() * 30) + 70 : Math.floor(Math.random() * 30) + 20
    })
  }
  return mockData
}

// 查看详情
const viewDetails = (row) => {
  ElMessage.info(`查看患者 ${row.patientId} 的详细信息`)
}

// 审核处理
const handleAudit = (row) => {
  ElMessage.info(`准备对患者 ${row.patientId} 的住院记录进行审核`)
}

// 查询处理
const handleSearch = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    queryParams.startDate = dateRange.value[0]
    queryParams.endDate = dateRange.value[1]
  }
  
  currentPage.value = 1
  fetchInpatientData()
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchInpatientData()
}

// 分页处理
const handlePageChange = (val) => {
  currentPage.value = val
  fetchInpatientData()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchInpatientData()
}

// 辅助函数
const formatDate = (date) => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatCurrency = (value) => {
  return parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}

const getRiskTagType = (score) => {
  if (score >= 80) return 'danger'
  if (score >= 60) return 'warning'
  if (score >= 40) return 'success'
  return 'info'
}

const getAnomalyTagType = (type) => {
  if (type === '费用异常' || type === '重复住院') return 'danger'
  if (type === '住院时长异常') return 'warning'
  return 'info'
}
</script>

<style scoped>
.container {
  max-width: 2000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--el-color-primary);
}

.search-form {
  margin-bottom: 20px;
}

.data-overview {
  margin-bottom: 20px;
}

.overview-card {
  display: flex;
  height: 100px;
}

.overview-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  background-color: #409EFF;
  color: white;
  font-size: 24px;
}

.overview-data {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 10px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: #909399;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style> 