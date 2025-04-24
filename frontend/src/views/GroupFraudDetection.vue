<template>
  <div class="container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">团体欺诈识别</span>
          <el-tag type="danger">高级分析</el-tag>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="医疗机构">
          <el-select v-model="queryParams.hospital" placeholder="请选择" clearable>
            <el-option v-for="item in hospitalOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="欺诈类型">
          <el-select v-model="queryParams.fraudType" placeholder="请选择" clearable>
            <el-option v-for="item in fraudTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="queryParams.riskLevel" placeholder="请选择" clearable>
            <el-option v-for="item in riskLevelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="事件周期">
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

      <!-- 发现的欺诈团体 -->
      <el-row :gutter="20" class="group-cards">
        <el-col :span="8" v-for="group in fraudGroups" :key="group.id">
          <el-card 
            shadow="hover" 
            class="group-card"
            :class="{ 'high-risk': group.riskLevel === '高风险' }"
          >
            <template #header>
              <div class="group-header">
                <span class="group-title">{{ group.groupName }}</span>
                <el-tag 
                  :type="group.riskLevel === '高风险' ? 'danger' : group.riskLevel === '中风险' ? 'warning' : 'success'"
                >
                  {{ group.riskLevel }}
                </el-tag>
              </div>
            </template>
            <div class="group-content">
              <div class="group-info">
                <div class="info-item">
                  <div class="info-label">成员数量</div>
                  <div class="info-value">{{ group.memberCount }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">事件次数</div>
                  <div class="info-value">{{ group.eventCount }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">累计金额</div>
                  <div class="info-value">{{ formatCurrency(group.totalAmount) }}元</div>
                </div>
              </div>
              <div class="group-description">
                <div class="description-title">欺诈特征:</div>
                <div class="description-content">{{ group.description }}</div>
              </div>
              <div class="group-actions">
                <el-button type="primary" size="small" @click="viewGroupDetails(group)">查看详情</el-button>
                <el-button type="warning" size="small" @click="startInvestigation(group)">立案调查</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页器 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[9, 18, 27]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        class="pagination"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="团体欺诈详情"
      width="80%"
      destroy-on-close
    >
      <div v-if="selectedGroupDetails" class="group-details">
        <div class="details-header">
          <h2>{{ selectedGroupDetails.groupName }}</h2>
          <div>
            <el-tag :type="selectedGroupDetails.riskLevel === '高风险' ? 'danger' : 'warning'">
              {{ selectedGroupDetails.riskLevel }}
            </el-tag>
            <el-tag type="info" style="margin-left: 10px;">
              成员数: {{ selectedGroupDetails.memberCount }}
            </el-tag>
          </div>
        </div>
        
        <el-divider content-position="center">欺诈团体成员</el-divider>
        
        <el-table :data="selectedGroupDetails.members" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="成员" width="120" />
          <el-table-column prop="role" label="角色" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.role === '主要涉案人' ? 'danger' : scope.row.role === '协助者' ? 'warning' : 'info'">
                {{ scope.row.role }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="hospital" label="医疗机构" width="180" show-overflow-tooltip />
          <el-table-column prop="department" label="科室" width="120" />
          <el-table-column prop="eventCount" label="事件数" width="100" align="right" />
          <el-table-column prop="totalAmount" label="涉及金额" width="150" align="right">
            <template #default="scope">
              {{ formatCurrency(scope.row.totalAmount) }}元
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        </el-table>
        
        <el-divider content-position="center">欺诈事件记录</el-divider>
        
        <el-table :data="selectedGroupDetails.events" border stripe>
          <el-table-column prop="id" label="事件ID" width="80" />
          <el-table-column prop="title" label="事件标题" width="180" show-overflow-tooltip />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="scope">
              <el-tag :type="getEventTagType(scope.row.type)">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="发生时间" width="150" />
          <el-table-column prop="amount" label="涉及金额" width="150" align="right">
            <template #default="scope">
              {{ formatCurrency(scope.row.amount) }}元
            </template>
          </el-table-column>
          <el-table-column prop="description" label="事件描述" min-width="250" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已确认' ? 'danger' : 'warning'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 状态数据
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)
const fraudGroups = ref([])
const dateRange = ref([])
const detailsVisible = ref(false)
const selectedGroupDetails = ref(null)

// 查询参数
const queryParams = reactive({
  hospital: '',
  fraudType: '',
  riskLevel: '',
  startDate: '',
  endDate: ''
})

// 选项数据
const hospitalOptions = [
  { value: 'H001', label: '第一人民医院' },
  { value: 'H002', label: '中心医院' },
  { value: 'H003', label: '妇幼保健院' },
  { value: 'H004', label: '协和医院' }
]

const fraudTypeOptions = [
  { value: '虚假住院', label: '虚假住院' },
  { value: '药品回扣', label: '药品回扣' },
  { value: '过度医疗', label: '过度医疗' },
  { value: '分解住院', label: '分解住院' }
]

const riskLevelOptions = [
  { value: '高风险', label: '高风险' },
  { value: '中风险', label: '中风险' },
  { value: '低风险', label: '低风险' }
]

// 初始化
onMounted(() => {
  fetchFraudGroups()
})

// 获取欺诈团体数据
const fetchFraudGroups = async () => {
  loading.value = true
  try {
    // 模拟API调用
    setTimeout(() => {
      fraudGroups.value = generateMockFraudGroups()
      total.value = 28
      loading.value = false
    }, 800)
  } catch (error) {
    ElMessage.error('获取数据失败')
    loading.value = false
  }
}

// 生成模拟数据
const generateMockFraudGroups = () => {
  const mockData = []
  const fraudTypes = fraudTypeOptions.map(option => option.value)
  const riskLevels = ['高风险', '中风险', '低风险']
  const hospitals = hospitalOptions.map(option => option.label)
  
  const groupNamePrefixes = [
    '联合', '串通', '医药', '医护', '医患', '医共体', '医诊所'
  ]
  
  for (let i = 1; i <= 9; i++) {
    const fraudType = fraudTypes[Math.floor(Math.random() * fraudTypes.length)]
    const riskLevel = i <= 3 ? '高风险' : i <= 6 ? '中风险' : '低风险'
    const hospital = hospitals[Math.floor(Math.random() * hospitals.length)]
    const memberCount = Math.floor(Math.random() * 10) + 3
    const eventCount = Math.floor(Math.random() * 20) + 5
    const totalAmount = Math.random() * 500000 + 50000
    
    const groupNamePrefix = groupNamePrefixes[Math.floor(Math.random() * groupNamePrefixes.length)]
    const groupName = `${groupNamePrefix}${fraudType}欺诈团体 #${i}`
    
    mockData.push({
      id: 'G' + String(i).padStart(3, '0'),
      groupName: groupName,
      fraudType: fraudType,
      riskLevel: riskLevel,
      hospital: hospital,
      memberCount: memberCount,
      eventCount: eventCount,
      totalAmount: totalAmount,
      description: generateDescription(fraudType, hospital)
    })
  }
  return mockData
}

// 生成欺诈描述
const generateDescription = (fraudType, hospital) => {
  const descriptions = {
    '虚假住院': `在${hospital}内存在大量虚假住院记录，患者实际未住院但申报住院费用`,
    '药品回扣': `医生开具特定厂商药品获取回扣，药品使用量明显高于同级医院`,
    '过度医疗': `患者接受多项不必要的检查和治疗，医疗费用显著高于同类疾病平均水平`,
    '分解住院': `将应当一次住院的诊疗分解为多次住院，骗取医保基金`
  }
  
  return descriptions[fraudType] || `${hospital}内发现团体欺诈行为，涉及多人参与`
}

// 查看团体详情
const viewGroupDetails = (group) => {
  selectedGroupDetails.value = {
    ...group,
    members: generateMockMembers(group.memberCount),
    events: generateMockEvents(group.eventCount, group.fraudType)
  }
  detailsVisible.value = true
}

// 开始调查
const startInvestigation = (group) => {
  ElMessage.success(`已启动对"${group.groupName}"的调查程序`)
}

// 生成模拟成员数据
const generateMockMembers = (count) => {
  const members = []
  const roles = ['主要涉案人', '协助者', '参与者']
  
  for (let i = 1; i <= count; i++) {
    const roleIndex = i === 1 ? 0 : (i <= 3 ? 1 : 2)
    members.push({
      id: 'M' + i,
      name: '成员 #' + i,
      role: roles[roleIndex],
      hospital: hospitalOptions[Math.floor(Math.random() * hospitalOptions.length)].label,
      department: ['内科', '外科', '妇科', '儿科', '骨科'][Math.floor(Math.random() * 5)],
      eventCount: Math.floor(Math.random() * 20) + 2,
      totalAmount: Math.random() * 200000 + 5000,
      description: '该成员' + (roleIndex === 0 ? '组织并参与多起欺诈活动' : roleIndex === 1 ? '协助实施欺诈行为' : '参与部分欺诈活动')
    })
  }
  
  return members
}

// 生成模拟事件数据
const generateMockEvents = (count, fraudType) => {
  const events = []
  const eventTypes = ['虚假住院', '药品回扣', '过度医疗', '资料造假', '分解住院']
  const statuses = ['已确认', '调查中']
  
  for (let i = 1; i <= Math.min(count, 10); i++) {
    const useMainType = Math.random() > 0.3
    const typeIndex = useMainType ? eventTypes.indexOf(fraudType) : Math.floor(Math.random() * eventTypes.length)
    const type = eventTypes[typeIndex >= 0 ? typeIndex : 0]
    const date = new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1)
    const amount = Math.random() * 50000 + 1000
    
    events.push({
      id: 'E' + i,
      title: '疑似' + type + '事件',
      type: type,
      date: formatDate(date),
      amount: amount,
      description: '在' + formatDate(date) + '发现的' + type + '行为，' + 
        ['涉及多名患者的虚假住院记录', '医生频繁开具特定厂商药品获取回扣', 
         '大量不必要的检查和治疗', '伪造病历和医疗文档', '人为分解住院周期'][typeIndex],
      status: i <= 5 ? '已确认' : '调查中'
    })
  }
  
  return events
}

// 查询处理
const handleSearch = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    queryParams.startDate = dateRange.value[0]
    queryParams.endDate = dateRange.value[1]
  }
  
  currentPage.value = 1
  fetchFraudGroups()
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchFraudGroups()
}

// 分页处理
const handlePageChange = (val) => {
  currentPage.value = val
  fetchFraudGroups()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchFraudGroups()
}

// 辅助函数
const formatDate = (date) => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatCurrency = (value) => {
  return parseFloat(value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}

const getEventTagType = (type) => {
  if (type === '虚假住院' || type === '资料造假') return 'danger'
  if (type === '药品回扣') return 'warning'
  if (type === '过度医疗') return 'success'
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

.group-cards {
  margin-bottom: 20px;
}

.group-card {
  margin-bottom: 20px;
  border: 1px solid #EBEEF5;
  height: 100%;
}

.high-risk {
  border: 1px solid #F56C6C;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-title {
  font-weight: bold;
  font-size: 16px;
}

.group-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.group-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
  flex: 1;
}

.info-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.group-description {
  margin-bottom: 15px;
  flex: 1;
}

.description-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #606266;
}

.description-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.group-actions {
  display: flex;
  justify-content: space-between;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.details-header h2 {
  margin: 0;
  color: #303133;
}
</style> 