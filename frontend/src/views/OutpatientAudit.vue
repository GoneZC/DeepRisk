<template>
  <div class="container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">门诊智能审核</span>
          <el-tag type="success">AI辅助</el-tag>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="就诊编号">
          <el-input v-model="searchForm.mdtrtId" placeholder="请输入就诊编号" />
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="searchForm.status" placeholder="请选择">
            <el-option label="全部" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="异常" value="abnormal" />
            <el-option label="已通过" value="passed" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="auditList" border stripe style="width: 100%">
        <el-table-column prop="mdtrtId" label="就诊编号" width="180" />
        <el-table-column prop="patientName" label="患者姓名" width="120" />
        <el-table-column prop="visitDate" label="就诊日期" width="120" />
        <el-table-column prop="deptName" label="科室" width="120" />
        <el-table-column prop="diagnosisName" label="诊断" />
        <el-table-column prop="totalFee" label="总费用" width="120" align="right" />
        <el-table-column prop="abnormalItems" label="异常项数" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.abnormalItems > 0" type="danger">{{ scope.row.abnormalItems }}</el-tag>
            <span v-else>0</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="审核状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="viewDetail(scope.row)">查看</el-button>
            <el-button link type="primary" @click="auditRecord(scope.row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 搜索表单
const searchForm = reactive({
  mdtrtId: '',
  status: '',
  dateRange: []
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 模拟数据
const auditList = ref([
  {
    mdtrtId: 'OP20240101001',
    patientName: '张三',
    visitDate: '2024-01-01',
    deptName: '内科',
    diagnosisName: '上呼吸道感染',
    totalFee: 280.50,
    abnormalItems: 2,
    status: 'abnormal'
  },
  {
    mdtrtId: 'OP20240102002',
    patientName: '李四',
    visitDate: '2024-01-02',
    deptName: '外科',
    diagnosisName: '腕关节扭伤',
    totalFee: 320.00,
    abnormalItems: 0,
    status: 'passed'
  },
  // 更多模拟数据...
])

// 状态转换
const getStatusType = (status) => {
  switch (status) {
    case 'pending': return 'info'
    case 'abnormal': return 'danger'
    case 'passed': return 'success'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '待审核'
    case 'abnormal': return '异常'
    case 'passed': return '已通过'
    default: return '未知'
  }
}

// 搜索功能
const handleSearch = () => {
  ElMessage.success('触发搜索')
  // 实际应用中这里会调用API
}

const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    if (key === 'dateRange') {
      searchForm[key] = []
    } else {
      searchForm[key] = ''
    }
  })
}

// 分页功能
const handleSizeChange = (val) => {
  pageSize.value = val
  // 实际应用中这里会刷新数据
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // 实际应用中这里会刷新数据
}

// 操作功能
const viewDetail = (row) => {
  ElMessage.info(`查看就诊记录: ${row.mdtrtId}`)
  // 实际应用中这里会跳转到详情页
}

const auditRecord = (row) => {
  ElMessage.info(`审核就诊记录: ${row.mdtrtId}`)
  // 实际应用中这里会打开审核对话框
}
</script>

<style scoped>
.container {
  max-width: 100%;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 