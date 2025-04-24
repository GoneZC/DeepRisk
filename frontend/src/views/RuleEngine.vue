<template>
  <div class="container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">规则引擎</span>
          <el-button type="primary" @click="createRule">创建规则</el-button>
        </div>
      </template>

      <!-- 规则筛选表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="规则名称">
          <el-input v-model="queryParams.ruleName" placeholder="请输入规则名称" clearable />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="queryParams.ruleType" placeholder="请选择" clearable>
            <el-option v-for="item in ruleTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择" clearable>
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 规则表格 -->
      <el-table
        v-loading="loading"
        :data="ruleList"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="ruleId" label="规则ID" width="100" />
        <el-table-column prop="ruleName" label="规则名称" width="180" show-overflow-tooltip />
        <el-table-column prop="ruleType" label="规则类型" width="120">
          <template #default="scope">
            <el-tag :type="getRuleTypeTagType(scope.row.ruleType)">
              {{ scope.row.ruleType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="规则描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="creator" label="创建人" width="120" />
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '启用' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hitCount" label="命中次数" width="100" align="right" sortable />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="editRule(scope.row)">编辑</el-button>
            <el-button type="success" link @click="toggleStatus(scope.row)" v-if="scope.row.status === '禁用'">启用</el-button>
            <el-button type="info" link @click="toggleStatus(scope.row)" v-else>禁用</el-button>
            <el-button type="danger" link @click="deleteRule(scope.row)">删除</el-button>
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

    <!-- 规则编辑对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="dialogTitle"
      width="65%"
      destroy-on-close
    >
      <el-form :model="ruleForm" label-width="100px" :rules="rules" ref="ruleFormRef">
        <el-form-item label="规则名称" prop="ruleName">
          <el-input v-model="ruleForm.ruleName" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则类型" prop="ruleType">
          <el-select v-model="ruleForm.ruleType" placeholder="请选择规则类型">
            <el-option v-for="item in ruleTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则描述" prop="description">
          <el-input v-model="ruleForm.description" type="textarea" rows="3" placeholder="请输入规则描述" />
        </el-form-item>
        
        <el-divider content-position="center">规则条件</el-divider>
        
        <div v-for="(condition, index) in ruleForm.conditions" :key="index" class="condition-item">
          <el-row :gutter="10">
            <el-col :span="1" class="condition-index">
              <div class="condition-number">{{ index + 1 }}</div>
            </el-col>
            <el-col :span="7">
              <el-form-item :prop="'conditions.' + index + '.field'" :rules="{ required: true, message: '请选择字段', trigger: 'change' }">
                <el-select v-model="condition.field" placeholder="选择字段">
                  <el-option v-for="field in fieldOptions" :key="field.value" :label="field.label" :value="field.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="5">
              <el-form-item :prop="'conditions.' + index + '.operator'" :rules="{ required: true, message: '请选择操作符', trigger: 'change' }">
                <el-select v-model="condition.operator" placeholder="选择操作符">
                  <el-option v-for="op in operatorOptions" :key="op.value" :label="op.label" :value="op.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="9">
              <el-form-item :prop="'conditions.' + index + '.value'" :rules="{ required: true, message: '请输入值', trigger: 'blur' }">
                <el-input v-model="condition.value" placeholder="输入值" />
              </el-form-item>
            </el-col>
            <el-col :span="2" class="condition-action">
              <el-button type="danger" :icon="Delete" circle @click="removeCondition(index)" />
            </el-col>
          </el-row>
          <el-row v-if="index < ruleForm.conditions.length - 1">
            <el-col :span="24" class="condition-logic">
              <el-radio-group v-model="condition.logic">
                <el-radio label="AND">并且(AND)</el-radio>
                <el-radio label="OR">或者(OR)</el-radio>
              </el-radio-group>
            </el-col>
          </el-row>
        </div>
        
        <div class="add-condition">
          <el-button type="primary" :icon="Plus" @click="addCondition">添加条件</el-button>
        </div>
        
        <el-divider content-position="center">规则动作</el-divider>
        
        <el-form-item label="风险等级" prop="riskLevel">
          <el-select v-model="ruleForm.riskLevel" placeholder="请选择风险等级">
            <el-option v-for="item in riskLevelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险描述" prop="riskDescription">
          <el-input v-model="ruleForm.riskDescription" type="textarea" rows="2" placeholder="请输入风险描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRule" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 页面数据
const loading = ref(false)
const submitLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const ruleList = ref([])
const ruleDialogVisible = ref(false)
const dialogTitle = ref('')
const ruleFormRef = ref(null)

// 查询参数
const queryParams = reactive({
  ruleName: '',
  ruleType: '',
  status: ''
})

// 表单数据
const ruleForm = reactive({
  ruleId: '',
  ruleName: '',
  ruleType: '',
  description: '',
  conditions: [],
  riskLevel: '',
  riskDescription: ''
})

// 表单验证规则
const rules = {
  ruleName: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  ruleType: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入规则描述', trigger: 'blur' }
  ],
  riskLevel: [
    { required: true, message: '请选择风险等级', trigger: 'change' }
  ]
}

// 选项数据
const ruleTypeOptions = [
  { value: '费用异常', label: '费用异常' },
  { value: '就诊行为异常', label: '就诊行为异常' },
  { value: '用药异常', label: '用药异常' },
  { value: '医生行为异常', label: '医生行为异常' },
  { value: '重复住院', label: '重复住院' }
]

const statusOptions = [
  { value: '启用', label: '启用' },
  { value: '禁用', label: '禁用' }
]

const fieldOptions = [
  { value: 'totalAmount', label: '总费用' },
  { value: 'drugCost', label: '药品费用' },
  { value: 'examCost', label: '检查费用' },
  { value: 'stayLength', label: '住院天数' },
  { value: 'diagnosisCount', label: '诊断数量' },
  { value: 'drugCount', label: '药品数量' },
  { value: 'visitCount', label: '就诊次数' },
  { value: 'daysBetweenVisits', label: '就诊间隔' }
]

const operatorOptions = [
  { value: '>', label: '大于' },
  { value: '>=', label: '大于等于' },
  { value: '<', label: '小于' },
  { value: '<=', label: '小于等于' },
  { value: '==', label: '等于' },
  { value: '!=', label: '不等于' },
  { value: 'contains', label: '包含' },
  { value: 'in', label: '在列表中' }
]

const riskLevelOptions = [
  { value: 'high', label: '高风险' },
  { value: 'medium', label: '中风险' },
  { value: 'low', label: '低风险' }
]

// 初始化
onMounted(() => {
  fetchRuleData()
})

// 获取规则数据
const fetchRuleData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    setTimeout(() => {
      ruleList.value = generateMockRuleData()
      total.value = 43
      loading.value = false
    }, 800)
  } catch (error) {
    ElMessage.error('获取数据失败')
    loading.value = false
  }
}

// 生成模拟数据
const generateMockRuleData = () => {
  const mockData = []
  const ruleTypes = ruleTypeOptions.map(option => option.value)
  const statuses = statusOptions.map(option => option.value)
  
  for (let i = 1; i <= 10; i++) {
    const ruleType = ruleTypes[Math.floor(Math.random() * ruleTypes.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const createTime = new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1)
    
    mockData.push({
      ruleId: 'R' + String(i).padStart(5, '0'),
      ruleName: ruleType + '规则-' + i,
      ruleType: ruleType,
      description: '检测' + ruleType + '的规则，用于医保智能监管',
      creator: ['张三', '李四', '王五'][Math.floor(Math.random() * 3)],
      createTime: formatDate(createTime),
      status: status,
      hitCount: Math.floor(Math.random() * 1000)
    })
  }
  return mockData
}

// 创建规则
const createRule = () => {
  dialogTitle.value = '创建规则'
  ruleForm.ruleId = ''
  ruleForm.ruleName = ''
  ruleForm.ruleType = ''
  ruleForm.description = ''
  ruleForm.conditions = [createEmptyCondition()]
  ruleForm.riskLevel = ''
  ruleForm.riskDescription = ''
  ruleDialogVisible.value = true
}

// 编辑规则
const editRule = (row) => {
  dialogTitle.value = '编辑规则'
  
  // 复制规则数据到表单
  ruleForm.ruleId = row.ruleId
  ruleForm.ruleName = row.ruleName
  ruleForm.ruleType = row.ruleType
  ruleForm.description = row.description
  
  // 生成一些模拟的条件数据
  ruleForm.conditions = generateMockConditions()
  
  ruleForm.riskLevel = ['high', 'medium', 'low'][Math.floor(Math.random() * 3)]
  ruleForm.riskDescription = '当' + row.ruleType + '达到异常值时，判定为风险事件'
  
  ruleDialogVisible.value = true
}

// 删除规则
const deleteRule = (row) => {
  ElMessageBox.confirm(
    `确定要删除规则 "${row.ruleName}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用删除API
    ElMessage({
      type: 'success',
      message: '删除成功'
    })
    fetchRuleData()
  }).catch(() => {})
}

// 切换规则状态
const toggleStatus = (row) => {
  const newStatus = row.status === '启用' ? '禁用' : '启用'
  const actionText = newStatus === '启用' ? '启用' : '禁用'
  
  ElMessageBox.confirm(
    `确定要${actionText}规则 "${row.ruleName}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用API更新状态
    row.status = newStatus
    ElMessage({
      type: 'success',
      message: `${actionText}成功`
    })
  }).catch(() => {})
}

// 提交规则
const submitRule = async () => {
  if (!ruleFormRef.value) return
  
  await ruleFormRef.value.validate((valid, fields) => {
    if (valid) {
      submitLoading.value = true
      
      // 模拟提交
      setTimeout(() => {
        ElMessage.success(ruleForm.ruleId ? '更新规则成功' : '创建规则成功')
        ruleDialogVisible.value = false
        submitLoading.value = false
        fetchRuleData()
      }, 1000)
    }
  })
}

// 条件操作
const createEmptyCondition = () => {
  return {
    field: '',
    operator: '',
    value: '',
    logic: 'AND'
  }
}

const addCondition = () => {
  ruleForm.conditions.push(createEmptyCondition())
}

const removeCondition = (index) => {
  ruleForm.conditions.splice(index, 1)
  if (ruleForm.conditions.length === 0) {
    addCondition()
  }
}

// 生成模拟条件
const generateMockConditions = () => {
  const count = Math.floor(Math.random() * 3) + 1
  const conditions = []
  
  for (let i = 0; i < count; i++) {
    const fieldIndex = Math.floor(Math.random() * fieldOptions.length)
    const field = fieldOptions[fieldIndex].value
    const operatorIndex = Math.floor(Math.random() * 4) // 只使用前4个操作符
    const operator = operatorOptions[operatorIndex].value
    
    let value
    if (field === 'totalAmount' || field === 'drugCost' || field === 'examCost') {
      value = (Math.random() * 10000 + 1000).toFixed(2)
    } else {
      value = Math.floor(Math.random() * 30 + 1).toString()
    }
    
    conditions.push({
      field,
      operator,
      value,
      logic: i < count - 1 ? (Math.random() > 0.5 ? 'AND' : 'OR') : 'AND'
    })
  }
  
  return conditions
}

// 查询处理
const handleSearch = () => {
  currentPage.value = 1
  fetchRuleData()
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = ''
  })
  currentPage.value = 1
  fetchRuleData()
}

// 分页处理
const handlePageChange = (val) => {
  currentPage.value = val
  fetchRuleData()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchRuleData()
}

// 辅助函数
const formatDate = (date) => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const getRuleTypeTagType = (type) => {
  switch(type) {
    case '费用异常':
      return 'danger'
    case '就诊行为异常':
      return 'warning'
    case '用药异常':
      return 'success'
    default:
      return 'info'
  }
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

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.condition-item {
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.condition-index {
  display: flex;
  align-items: center;
}

.condition-number {
  width: 22px;
  height: 22px;
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.condition-action {
  display: flex;
  align-items: center;
  justify-content: center;
}

.condition-logic {
  margin-top: 10px;
  margin-left: 30px;
}

.add-condition {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}
</style> 