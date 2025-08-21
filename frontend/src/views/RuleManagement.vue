<template>
  <div class="rule-management">
    <h2>规则管理</h2>
    
    <!-- 规则列表 -->
    <el-card class="rule-list-card">
      <template #header>
        <div class="card-header">
          <span>规则列表</span>
          <el-button type="primary" size="small" @click="showAddRuleDialog">添加规则</el-button>
        </div>
      </template>
      
      <el-table :data="rules" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="120" />
        <el-table-column prop="name" label="规则名称" width="180" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="fieldName" label="字段名" width="150" />
        <el-table-column prop="operator" label="操作符" width="100">
          <template #default="scope">
            <el-tag>{{ getOperatorText(scope.row.operator) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="120" />
        <el-table-column prop="priority" label="优先级" width="80" />
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="scope">
            <el-switch 
              v-model="scope.row.enabled" 
              @change="toggleRuleStatus(scope.row)"
              active-color="#13ce66"
              inactive-color="#ff4949">
            </el-switch>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" type="primary" @click="editRule(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑规则对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible"
      width="50%">
      <el-form :model="ruleForm" :rules="formRules" ref="ruleFormRef" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="ruleForm.description"></el-input>
        </el-form-item>
        <el-form-item label="字段名" prop="fieldName">
          <el-select v-model="ruleForm.fieldName" placeholder="选择字段">
            <el-option 
              v-for="field in availableFields" 
              :key="field.value" 
              :label="field.label" 
              :value="field.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作符" prop="operator">
          <el-select v-model="ruleForm.operator" placeholder="选择操作符">
            <el-option 
              v-for="op in availableOperators" 
              :key="op.value" 
              :label="op.label" 
              :value="op.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="阈值" prop="threshold">
          <el-input v-model="ruleForm.threshold"></el-input>
        </el-form-item>
        <el-form-item label="提示消息" prop="message">
          <el-input v-model="ruleForm.message"></el-input>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="ruleForm.priority" :min="1" :max="100"></el-input-number>
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="ruleForm.enabled"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RuleManagement',
  data() {
    return {
      rules: [],
      loading: false,
      dialogVisible: false,
      dialogTitle: '添加规则',
      isEditing: false,
      ruleForm: {
        id: '',
        name: '',
        description: '',
        fieldName: '',
        operator: '',
        threshold: '',
        message: '',
        priority: 50,
        enabled: true
      },
      formRules: {
        name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入规则描述', trigger: 'blur' }],
        fieldName: [{ required: true, message: '请选择字段名', trigger: 'change' }],
        operator: [{ required: true, message: '请选择操作符', trigger: 'change' }],
        threshold: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
        message: [{ required: true, message: '请输入提示消息', trigger: 'blur' }]
      },
      availableFields: [
        { label: '费用总额(DET_ITEM_FEE_SUMAMT)', value: 'DET_ITEM_FEE_SUMAMT' },
        { label: '单价(PRIC)', value: 'PRIC' },
        { label: '定价上限(PRIC_UPLMT_AMT)', value: 'PRIC_UPLMT_AMT' },
        { label: '自付比例(SELFPAY_PROP)', value: 'SELFPAY_PROP' },
        { label: '数量(CNT)', value: 'CNT' },
        { label: '医保目录编码(HILIST_CODE)', value: 'HILIST_CODE' },
        { label: '医保目录名称(HILIST_NAME)', value: 'HILIST_NAME' }
      ],
      availableOperators: [
        { label: '大于(>)', value: 'GT' },
        { label: '大于等于(>=)', value: 'GTE' },
        { label: '小于(<)', value: 'LT' },
        { label: '小于等于(<=)', value: 'LTE' },
        { label: '等于(=)', value: 'EQ' },
        { label: '包含', value: 'CONTAINS' },
        { label: '以...开始', value: 'STARTS_WITH' },
        { label: '以...结束', value: 'ENDS_WITH' },
        { label: '匹配正则表达式', value: 'MATCHES' }
      ]
    };
  },
  created() {
    this.fetchRules();
  },
  methods: {
    // 获取规则列表
    fetchRules() {
      this.loading = true;
      axios.get('/api/rules/management')
        .then(response => {
          this.rules = response.data;
        })
        .catch(error => {
          console.error('获取规则列表失败:', error);
          this.$message.error('获取规则列表失败');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    // 获取操作符描述文本
    getOperatorText(operator) {
      const op = this.availableOperators.find(o => o.value === operator);
      return op ? op.label : operator;
    },
    
    // 显示添加规则对话框
    showAddRuleDialog() {
      this.isEditing = false;
      this.dialogTitle = '添加规则';
      this.ruleForm = {
        id: '',
        name: '',
        description: '',
        fieldName: '',
        operator: '',
        threshold: '',
        message: '',
        priority: 50,
        enabled: true
      };
      this.dialogVisible = true;
    },
    
    // 编辑规则
    editRule(rule) {
      this.isEditing = true;
      this.dialogTitle = '编辑规则';
      this.ruleForm = { ...rule };
      this.dialogVisible = true;
    },
    
    // 保存规则
    saveRule() {
      // 添加或修改规则
      const method = this.isEditing ? 'put' : 'post';
      const url = this.isEditing 
                ? `/api/rules/management/${this.ruleForm.id}` 
                : '/api/rules/management';
      
      axios[method](url, this.ruleForm)
        .then(response => {
          this.$message.success(`${this.isEditing ? '更新' : '添加'}规则成功`);
          this.dialogVisible = false;
          this.fetchRules();
        })
        .catch(error => {
          console.error(`${this.isEditing ? '更新' : '添加'}规则失败:`, error);
          this.$message.error(`${this.isEditing ? '更新' : '添加'}规则失败`);
        });
    },
    
    // 切换规则启用状态
    toggleRuleStatus(rule) {
      axios.patch(`/api/rules/management/${rule.id}/toggle`)
        .then(response => {
          this.$message.success(`规则已${rule.enabled ? '启用' : '禁用'}`);
        })
        .catch(error => {
          console.error('切换规则状态失败:', error);
          this.$message.error('切换规则状态失败');
          // 恢复状态
          rule.enabled = !rule.enabled;
        });
    },
    
    // 删除规则
    deleteRule(rule) {
      this.$confirm('确定要删除这条规则吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete(`/api/rules/management/${rule.id}`)
          .then(() => {
            this.$message.success('删除规则成功');
            this.fetchRules();
          })
          .catch(error => {
            console.error('删除规则失败:', error);
            this.$message.error('删除规则失败');
          });
      }).catch(() => {
        // 取消删除
      });
    }
  }
};
</script>

<style scoped>
.rule-management {
  padding: 20px;
}

.rule-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 