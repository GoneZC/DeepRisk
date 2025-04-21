<template>
  <div class="audit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>智能审核</span>
        </div>
      </template>
      <div class="content">
        审核功能开发中...
        <el-button @click="triggerRecovery" type="danger">紧急数据恢复</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AuditView',
  methods: {
    triggerRecovery() {
      const start = new Date();
      start.setHours(start.getHours() - 2); // 默认查前2小时
      const end = new Date();
      
      this.$axios.post('/api/db-recovery', {
        logFile: 'binlog.000219',
        startTime: start.toISOString().slice(0, 19).replace('T', ' '),
        endTime: end.toISOString().slice(0, 19).replace('T', ' ')
      }).then(response => {
        this.$message.success(response.data);
      });
    }
  }
}
</script>

<style scoped>
.content {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style> 