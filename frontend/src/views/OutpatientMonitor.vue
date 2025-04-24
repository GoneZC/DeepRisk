<template>
  <div class="container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">门诊监管</span>
          <el-tag type="success">实时监控</el-tag>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="医生编号">
          <el-input v-model="queryParams.doctorId" placeholder="请输入医生编号" clearable />
        </el-form-item>
        <el-form-item label="医疗机构">
          <el-select v-model="queryParams.hospital" placeholder="请选择" clearable>
            <el-option v-for="item in hospitalOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属社区">
          <el-select v-model="queryParams.community" placeholder="请选择" clearable>
            <el-option v-for="item in communityOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="doctorList"
        border
        stripe
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column prop="doctorId" label="医生编号" width="150" />
        <el-table-column prop="hospitalCode" label="医疗机构编号" width="150" />
        <el-table-column prop="community" label="所属社区" width="200" show-overflow-tooltip>
          <template #default="scope">
            <span class="clickable-text" @click="showCommunityDrugs(scope.row)">
              {{ scope.row.community }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="科室" width="150" show-overflow-tooltip />
        <el-table-column prop="prescriptionCount" label="处方数量" width="120" align="right" sortable />
        <el-table-column prop="totalCost" label="总花费(元)" width="150" align="right" sortable>
          <template #default="scope">
            <span>{{ formatCurrency(scope.row.totalCost) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="prescriptionDate" label="处方日期" width="120">
          <template #default="scope">
            {{ scope.row.prescriptionDate || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="风险类型" width="180">
          <template #default="scope">
            <div class="risk-tags">
              <el-tag v-if="scope.row.feeRiskLevel === '高风险'" type="danger">费用异常</el-tag>
              <el-tag v-if="scope.row.feeRiskLevel === '中风险'" type="warning">费用风险</el-tag>
              
              <el-tag v-if="scope.row.drugRiskLevel === '高风险'" type="danger">用药异常</el-tag>
              <el-tag v-if="scope.row.drugRiskLevel === '中风险'" type="warning">用药风险</el-tag>
              
              <el-tag v-if="scope.row.diagRiskLevel === '高风险'" type="danger">诊断异常</el-tag>
              <el-tag v-if="scope.row.diagRiskLevel === '中风险'" type="warning">诊断风险</el-tag>
              
              <el-tag v-if="isNormalRisk(scope.row)" type="success">正常</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleRiskAssessment(scope.row)">风险评估</el-button>
            <el-button type="success" link @click="viewDetails(scope.row)">查看详情</el-button>
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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsDialogVisible"
      title="门诊详情"
      width="70%"
      destroy-on-close
    >
      <div v-if="selectedDoctor" class="doctor-details">
        <div class="details-header">
          <h3>基本信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="医生编号">{{ selectedDoctor.doctorId }}</el-descriptions-item>
            <el-descriptions-item label="医疗机构编号">{{ selectedDoctor.hospitalCode }}</el-descriptions-item>
            <el-descriptions-item label="所属社区">{{ selectedDoctor.community }}</el-descriptions-item>
            <el-descriptions-item label="处方数量">{{ selectedDoctor.prescriptionCount }}</el-descriptions-item>
            <el-descriptions-item label="总花费">{{ formatCurrency(selectedDoctor.totalCost) }}元</el-descriptions-item>
            <el-descriptions-item label="日期">{{ selectedDoctor.prescriptionDate }}</el-descriptions-item>
            <el-descriptions-item label="风险评估" :span="3">
              <div class="risk-assessment-text">
                <span class="risk-item">
                  费用评估: 
                  <el-tag :type="getRiskTagType(selectedDoctor.feeRiskLevel)">{{ selectedDoctor.feeRiskLevel || '未评估' }}</el-tag>
                </span>
                <span class="risk-item">
                  药品评估: 
                  <el-tag :type="getRiskTagType(selectedDoctor.drugRiskLevel)">{{ selectedDoctor.drugRiskLevel || '未评估' }}</el-tag>
                </span>
                <span class="risk-item">
                  诊断评估: 
                  <el-tag :type="getRiskTagType(selectedDoctor.diagRiskLevel)">{{ selectedDoctor.diagRiskLevel || '未评估' }}</el-tag>
                </span>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <el-divider />
        
        <div class="prescription-list">
          <h3>处方列表</h3>
          <el-table :data="prescriptionList" border stripe>
            <el-table-column prop="prescriptionId" label="处方编号" width="150" />
            <el-table-column prop="patientId" label="患者ID" width="120" />
            <el-table-column prop="prescriptionDate" label="处方日期" width="120" />
            <el-table-column prop="totalFee" label="金额(元)" width="120" align="right">
              <template #default="scope">
                {{ formatCurrency(scope.row.totalFee) }}
              </template>
            </el-table-column>
            <el-table-column prop="drugCount" label="药品数量" width="100" align="center" />
            <el-table-column prop="diagnosis" label="诊断" min-width="200" show-overflow-tooltip />
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 社区药品对话框 -->
    <el-dialog :title="`${selectedCommunity}包含药品`" v-model="drugDialogVisible" width="50%">
      <div class="drug-list">
        {{ selectedDrugList }}
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 数据加载状态
const loading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 查询参数
const queryParams = reactive({
  doctorId: '',
  hospital: '',
  community: ''
})
const dateRange = ref([])

// 医生列表数据
const doctorList = ref([])

// 风险评估相关
const riskDialogVisible = ref(false)
const selectedDoctor = ref(null)
const riskScore = ref(0)

// 详情对话框相关
const detailsDialogVisible = ref(false)
const prescriptionList = ref([])

// 社区药品相关
const drugDialogVisible = ref(false)
const selectedCommunity = ref('')
const selectedDrugList = ref('')

// 社区选项
const communityOptions = ref([
  { value: '糖心共管社区', label: '糖心共管社区' },
  { value: '心肾同治社区', label: '心肾同治社区' },
  { value: '呼吸与代谢管理社区', label: '呼吸与代谢管理社区' },
  { value: '中西医结合慢病社区', label: '中西医结合慢病社区' },
  { value: '老年病综合管理社区', label: '老年病综合管理社区' },
  { value: '基础病强化治疗社区', label: '基础病强化治疗社区' }
])

// 初始化
onMounted(() => {
  fetchDoctorData()
})

// 获取医生数据
const fetchDoctorData = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      doctorId: queryParams.doctorId || null,
      hospitalCode: queryParams.hospital || null,
      community: queryParams.community || null,
      department: null,
      page: currentPage.value - 1,
      size: pageSize.value
    }
    
    // 添加日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = formatDate(dateRange.value[0])
      params.endDate = formatDate(dateRange.value[1])
    }
    
    console.log('查询参数:', params)
    
    // 调用后端API
    const response = await axios.post('/api/outpatient-monitor/search', params)
    
    doctorList.value = response.data.content
    total.value = response.data.totalElements
  } catch (error) {
    ElMessage.error('获取数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 风险评估处理
const handleRiskAssessment = async (row) => {
  // 不再显示弹窗
  // riskDialogVisible.value = true 
  selectedDoctor.value = row
  loading.value = true
  
  try {
    // 通过网关访问Python服务，而不是直接访问
    const response = await axios.post('/api/risk-assessment', {
      doctorId: row.doctorId,
      date: row.prescriptionDate
    })
    
    // 更新风险信息
    const result = response.data
    
    // 保存风险等级信息到医生对象
    row.feeRiskLevel = result.feeRiskLevel || '正常'
    row.drugRiskLevel = result.drugRiskLevel || '正常'
    row.diagRiskLevel = result.diagRiskLevel || '正常'
    row.fraudRisk = result.riskLevel || getHighestRiskLevel(row)
    
    loading.value = false
  } catch (error) {
    console.error('风险评估失败:', error)
    ElMessage.error('风险评估失败')
    loading.value = false
  }
}

// 确认风险评估结果
const confirmRiskAssessment = () => {
  const riskLevel = getRiskLevel(riskScore.value)
  
  // 更新本地数据
  if (selectedDoctor.value) {
    // 找到当前医生并更新风险等级
    const index = doctorList.value.findIndex(item => item.doctorId === selectedDoctor.value.doctorId)
    if (index !== -1) {
      doctorList.value[index].fraudRisk = riskLevel
    }
  }
  
  ElMessage.success('风险评估完成')
  riskDialogVisible.value = false
}

// 查询处理
const handleSearch = () => {
  currentPage.value = 1
  fetchDoctorData()
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchDoctorData()
}

// 分页处理
const handlePageChange = (val) => {
  currentPage.value = val
  fetchDoctorData()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchDoctorData()
}

// 辅助函数
const formatDate = (date) => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatCurrency = (value) => {
  return parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}

const getRiskLevel = (score) => {
  if (score >= 75) return '高风险'
  if (score >= 50) return '中风险'
  if (score >= 25) return '低风险'
  return '正常'
}

const getRiskTagType = (level) => {
  if (level === '高风险') return 'danger'
  if (level === '中风险') return 'warning'
  if (level === '低风险') return 'success'
  return 'info'
}

const getProgressColor = (score) => {
  if (score >= 75) return '#F56C6C'
  if (score >= 50) return '#E6A23C'
  if (score >= 25) return '#67C23A'
  return '#909399'
}

// 显示社区药品
const showCommunityDrugs = (row) => {
  console.log('点击的社区信息:', row)
  console.log('社区药品数据:', row.comDrug)
  selectedCommunity.value = row.community
  selectedDrugList.value = row.comDrug || '该社区暂无药品信息'
  drugDialogVisible.value = true
}

// 添加详细评分变量
const detailedScores = ref({
  feeScore: 0,
  drugScore: 0,
  diagScore: 0
})

// 判断是否全部正常
const isNormalRisk = (doctor) => {
  return (doctor.feeRiskLevel === '正常' || doctor.feeRiskLevel === '低风险') && 
         (doctor.drugRiskLevel === '正常' || doctor.drugRiskLevel === '低风险') && 
         (doctor.diagRiskLevel === '正常' || doctor.diagRiskLevel === '低风险');
}

// 表格行样式
const tableRowClassName = ({row}) => {
  if (row.feeRiskLevel === '高风险' || row.drugRiskLevel === '高风险' || row.diagRiskLevel === '高风险') {
    return 'high-risk-row';
  } else if (row.feeRiskLevel === '中风险' || row.drugRiskLevel === '中风险' || row.diagRiskLevel === '中风险') {
    return 'medium-risk-row';
  }
  return '';
}

const viewDetails = (doctor) => {
  selectedDoctor.value = { ...doctor }
  detailsDialogVisible.value = true
  
  // 确保风险评估结果在详情中可用
  selectedDoctor.value.feeRiskLevel = doctor.feeRiskLevel || '未评估'
  selectedDoctor.value.drugRiskLevel = doctor.drugRiskLevel || '未评估'
  selectedDoctor.value.diagRiskLevel = doctor.diagRiskLevel || '未评估'
}

// 添加此函数 - 获取最高风险等级
const getHighestRiskLevel = (doctor) => {
  const levels = { '正常': 0, '低风险': 1, '中风险': 2, '高风险': 3 }
  const maxLevel = Math.max(
    levels[doctor.feeRiskLevel || '正常'], 
    levels[doctor.drugRiskLevel || '正常'], 
    levels[doctor.diagRiskLevel || '正常']
  )
  return ['正常', '低风险', '中风险', '高风险'][maxLevel]
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

.unassessed {
  color: #909399;
  font-style: italic;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.risk-assessment {
  padding: 10px;
}

.doctor-info {
  margin-bottom: 20px;
}

.doctor-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.doctor-info p {
  margin: 5px 0;
  color: #606266;
}

.risk-score-container {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.risk-score-label {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.risk-score-value {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.risk-level {
  margin-top: 10px;
  font-size: 16px;
  color: #606266;
}

.doctor-details h3 {
  margin: 0 0 20px 0;
  color: #303133;
}

.prescription-list {
  margin-top: 20px;
}

.clickable-text {
  color: #409EFF;
  cursor: pointer;
}

.drug-list {
  white-space: pre-wrap;
  line-height: 1.5;
}

/* 风险标签样式 */
.risk-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.high-risk-row {
  background-color: rgba(245, 108, 108, 0.1);
}

.medium-risk-row {
  background-color: rgba(230, 162, 60, 0.1);
}

.risk-assessment-text {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.risk-item {
  font-weight: bold;
}
</style>