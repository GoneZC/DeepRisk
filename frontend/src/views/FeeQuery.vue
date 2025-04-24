<template>
  <div class="container">
    <!-- 诊断详情对话框 -->
    <el-dialog
      v-model="diagDetailVisible"
      title="诊断详情"
      width="70%"
      destroy-on-close
    >
      <el-table
        :data="diagDetails"
        border
        stripe
        v-loading="diagLoading"
        style="width: 100%"
      >
        <el-table-column prop="inoutDiagType" label="出入院诊断类别" width="120">
          <template #default="scope">
            {{ formatDiagType(scope.row.inoutDiagType) }}
          </template>
        </el-table-column>
        <el-table-column prop="diagType" label="诊断类别" width="120">
          <template #default="scope">
            {{ formatDiagCategory(scope.row.diagType) }}
          </template>
        </el-table-column>
        <el-table-column prop="maindiagFlag" label="主诊断标志" width="120">
          <template #default="scope">
            {{ formatMainDiagFlag(scope.row.diagType) }}
          </template>
        </el-table-column>
        <el-table-column prop="diagSrtNo" label="诊断排序号" width="120" />
        <el-table-column prop="diagName" label="诊断名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="admCond" label="入院病情" width="120" />
        <el-table-column prop="diagDept" label="诊断科室" width="150" />
        <el-table-column prop="diagTime" label="诊断时间" width="180" :formatter="formatDateTime" />
      </el-table>
    </el-dialog>
    <!-- 治疗详情对话框 -->
    <el-dialog
      v-model="feeDetailVisible"
      title="费用明细"
      width="80%"
      destroy-on-close
    >
      <el-table
        :data="feeDetails"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
        :default-sort="{ prop: 'feeOcurTime', order: 'ascending' }"
      >
        <el-table-column prop="hilistName" label="医保目录名称" width="180" show-overflow-tooltip />
        <el-table-column prop="listType" label="目录类别" width="120" />
        <el-table-column prop="chrgitmLv" label="收费项目等级" width="120" />
        <el-table-column prop="prodname" label="药品名称" width="180" show-overflow-tooltip />
        <el-table-column prop="dosformName" label="剂型名称" width="120" />
        <el-table-column prop="bilgDeptName" label="开单科室" width="150" />
        <el-table-column prop="prcuDrugFlag" label="处方药标志" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.prcuDrugFlag === '1' ? 'warning' : ''">
              {{ formatType(scope.row.prcuDrugFlag, { '1': '非处方药', '0': '处方药' }) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cnt" label="数量" align="right" width="100" />
        <el-table-column prop="pric" label="单价(元)" align="right" width="100" />
        <el-table-column prop="detItemFeeSumamt" label="金额(元)" align="right" width="120" />
        <el-table-column prop="feeOcurTime" label="发生时间" :formatter="formatDateTime" width="180" sortable />
      </el-table>
    </el-dialog>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">医疗费用查询</span>
          <el-tag type="info">v3.0</el-tag>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item label="就诊ID">
          <el-input
            v-model="mdtrtId"
            placeholder="请输入就诊编号"
            clearable
            @keyup.enter="search"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="患者编号">
          <el-input
            v-model="psnNo"
            placeholder="请输入患者编号"
            clearable
            @keyup.enter="search"
          />
        </el-form-item>
        <el-form-item label="医疗类别">
          <el-select 
            v-model="queryParams.medTypes" 
            multiple
            clearable
            collapse-tags
            placeholder="请选择"
            style="width: 300px;"
          >
            <el-option
              v-for="item in medTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="search"
          >
            立即查询
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 结算信息表 -->
      <el-table
        :data="settlementList"
        stripe
        border
        v-loading="loading"
        empty-text="暂无结算记录"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="mdtrtId" label="就诊编号" width="180" />
        <el-table-column prop="psnNo" label="患者编号" width="180" />
        <el-table-column prop="gend" label="性别" width="80">
          <template #default="scope">
            {{ scope.row.gend === '1' ? '男' : scope.row.gend === '2' ? '女' : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="diseName" label="疾病名称" width="100" show-overflow-tooltip />
        <el-table-column prop="fixmedinsCode" label="定点医疗机构编号" width="120" show-overflow-tooltip />
        <el-table-column prop="medType" label="医疗类别" width="120">
          <template #default="scope">
            {{ formatMedType(scope.row.medType) }}
          </template>
        </el-table-column>
        <el-table-column prop="begndate" label="开始日期" width="150" :formatter="formatDate" />
        <el-table-column prop="enddate" label="结束日期" width="150" :formatter="formatDate" />
        <el-table-column prop="medfeeSumamt" label="总费用(元)" width="120" align="right" />
        <el-table-column prop="fulamtOwnpayAmt" label="自费金额(元)" width="120" align="right" />
        <el-table-column prop="hifpPay" label="医保支付(元)" width="120" align="right" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="viewDiagDetails(scope.row.mdtrtId)">诊断详情</el-button>
            <el-button type="success" link @click="viewFeeDetails(scope.row.mdtrtId)">治疗详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Search } from '@element-plus/icons-vue'

const mdtrtId = ref('')
const psnNo = ref('')
const feeDetails = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 结算表数据
const settlementList = ref([])

// 诊断详情相关
const diagDetailVisible = ref(false)
const diagDetails = ref([])
const diagLoading = ref(false)

// 费用详情对话框
const feeDetailVisible = ref(false)

// 初始化查询参数
const queryParams = reactive({
  medTypes: [],
  startDate: null,
  endDate: null
});

// 新增查询参数存储
const searchParams = ref({});

// 添加医疗类别选项
const medTypeOptions = [
  { value: '11', label: '普通门诊' },
  { value: '13', label: '急诊' },
  { value: '21', label: '普通住院' },
  { value: '14', label: '门诊慢特病' },
  { value: '41', label: '定点药店购药' },
  { value: '51', label: '生育门诊' },
  { value: '52', label: '生育住院' },
  { value: '53', label: '计划生育手术费' },
  { value: '54', label: '基本医疗生育门诊' },
  { value: '55', label: '基本医疗生育住院' },
  { value: '56', label: '基本医疗计划生育手术' },
  { value: '5301', label: '计划生育门诊' },
  { value: '5302', label: '计划生育住院' },
  { value: '2101', label: '日间手术' },
  { value: '22', label: '外伤住院' },
  { value: '23', label: '转外诊治住院' },
  { value: '24', label: '急诊转住院' }
];

// 初始化
onMounted(() => {
  login()
  loadInitialData()
})

const loadInitialData = () => {
  search(1);
}

const login = async () => {
  try {
    console.log('开始登录请求...');
    const response = await axios.post('/api/auth/login', {
      // username: 'admin',
      username: 'hospital2',
      password: '123'
    });
    
    console.log('登录响应:', response.data);
    localStorage.setItem('token', response.data.token);
    console.log('登录成功，令牌已保存');
  } catch (error) {
    console.error('登录失败', error.message);
    if (error.response) {
      console.error('错误状态:', error.response.status);
      console.error('错误数据:', error.response.data);
    } else if (error.request) {
      console.error('请求发送但没有响应');
    }
  }
}


const search = async (pageNum = 1) => {
  try {
    loading.value = true
    currentPage.value = pageNum
    
    searchParams.value = {
      mdtrtId: mdtrtId.value,
      psnNo: psnNo.value,
      medTypes: queryParams.medTypes
    }
    
    const requestParams = {
      ...searchParams.value,
      page: currentPage.value - 1,
      size: pageSize.value
    }
    
    // 确保从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token');
    const headers = {
      'Authorization': token ? `Bearer ${token}` : ''
    };
    
    console.log('发送请求参数:', requestParams);
    console.log('认证头:', headers.Authorization);
    
    const response = await axios.post('/api/settlements/search', requestParams, { headers })
    // const response = await axios.post('http://localhost:8082/api/settlements/search', requestParams, { headers })

    
    console.log('收到响应:', response.data)
    
    settlementList.value = response.data.data
    total.value = response.data.totalElements
    
    ElMessage.success(`查询到${total.value}条记录`)
  } catch (error) {
    console.error('完整错误信息:', error)
    console.error('请求失败，请检查API网关服务是否运行')
    ElMessage.error('查询失败: 无法连接到服务器')
  } finally {
    loading.value = false
  }
}

// 查看诊断详情
const viewDiagDetails = async (treatmentId) => {
  try {
    diagLoading.value = true
    diagDetailVisible.value = true
    
    const response = await axios.get(`/api/diagnosis-details/${treatmentId}`)
    diagDetails.value = response.data
  } catch (error) {
    ElMessage.error('获取诊断详情失败')
    console.error(error)
  } finally {
    diagLoading.value = false
  }
}

// 查看费用明细
const viewFeeDetails = async (treatmentId) => {
  try {
    loading.value = true
    feeDetailVisible.value = true
    
    const response = await axios.get(`/api/fee-details/${treatmentId}`)
    feeDetails.value = response.data
  } catch (error) {
    ElMessage.error('获取费用明细失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  mdtrtId.value = ''
  psnNo.value = ''
  queryParams.medTypes = []
  searchParams.value = {}
  settlementList.value = []
  total.value = 0
}

// 格式化函数
const formatDate = (row, column, cellValue) => {
  if (!cellValue) return '--'
  const date = new Date(cellValue)
  return date.toLocaleDateString()
}

const formatDateTime = (row, column, cellValue) => {
  if (!cellValue) return '--'
  const date = new Date(cellValue)
  return date.toLocaleString()
}

const formatPercent = (row, column, cellValue) => {
  if (cellValue === null || cellValue === undefined) return '--'
  return cellValue + '%'
}

// 通用格式化函数
const formatType = (type, typeMap) => {
  return typeMap[type] || type; // 如果没有匹配，返回原始类型
}

// 格式化诊断类别
const formatDiagType = (type) => {
  const diagTypeMap = {
    '1': '入院诊断',
    '2': '出院诊断'
  };
  return formatType(type, diagTypeMap);
}

// 格式化诊断分类
const formatDiagCategory = (type) => {
  const diagCategoryMap = {
    '1': '西医诊断',
    '2': '中医主病诊断',
    '3': '中医主证诊断'
  };
  return formatType(type, diagCategoryMap);
}

// 格式化主诊断标志
const formatMainDiagFlag = (flag) => {
  return flag === '1' ? '主诊断' : '次要诊断';
}

// 格式化医疗类别
const formatMedType = (type) => {
    const medTypeMap = {
        '11': '普通门诊',
        '12': '门诊挂号',
        '13': '急诊',
        '14': '门诊慢特病',
        '21': '普通住院',
        '22': '外伤住院',
        '23': '转外诊治住院',
        '24': '急诊转住院',
        '41': '定点药店购药',
        '51': '生育门诊',
        '52': '生育住院',
        '53': '计划生育手术费',
        '54': '基本医疗生育门诊',
        '55': '基本医疗生育住院',
        '56': '基本医疗计划生育手术',
        '5301': '计划生育门诊',
        '5302': '计划生育住院',
        '2101': '日间手术'
    };
    return medTypeMap[type] || '未知类型';
};
    

const handlePageChange = (val) => {
  currentPage.value = val
  search(val) // 始终使用保存的查询条件
}

const handleSizeChange = (val) => {
  pageSize.value = val
  search(1) // 重置到第一页
}
</script>

<style scoped>
.container {
  max-width: 2000px;
  margin: 20px auto;
  padding: 0 20px;
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

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>