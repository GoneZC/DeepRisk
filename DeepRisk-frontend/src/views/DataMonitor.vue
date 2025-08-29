<template>
  <div class="data-collection-monitor">
    <h2>数据采集实时监控</h2>
    <div class="status-cards">
      <div class="status-card">
        <div class="card-title">已处理数据</div>
        <div class="card-value">{{ processedCount }}</div>
      </div>
      <div class="status-card">
        <div class="card-title">触发规则数据</div>
        <div class="card-value">{{ ruleTriggeredCount }}</div>
      </div>
    </div>
    
    <div class="button-group">
      <el-button type="primary" @click="triggerCollection" :loading="loading">
        模拟数据采集
      </el-button>
    </div>
  </div>
</template>

<script>
import SockJS from 'sockjs-client';
import Stomp from 'webstomp-client';
import axios from 'axios';

// 配置后端服务URL
axios.defaults.baseURL = 'http://localhost:8082';

export default {
  name: 'DataMonitor',
  data() {
    return {
      processedCount: 0,
      ruleTriggeredCount: 0,
      stompClient: null,
      connected: false,
      loading: false
    }
  },
  mounted() {
    this.connectWebSocket();
    this.getStatus();
  },
  methods: {
    connectWebSocket() {
      const socket = new SockJS('http://localhost:8083/ws-data-collection');
      this.stompClient = Stomp.over(socket);
      
      this.stompClient.connect({}, () => {
        this.connected = true;
        
        // 订阅状态更新
        this.stompClient.subscribe('/topic/collection-status', response => {
          const statusUpdate = JSON.parse(response.body);
          this.processedCount = statusUpdate.processedCount;
          this.ruleTriggeredCount = statusUpdate.ruleTriggeredCount;
        });
      }, error => {
        console.error('WebSocket连接错误:', error);
        this.connected = false;
        
        // 5秒后自动重连
        setTimeout(() => {
          this.connectWebSocket();
        }, 5000);
      });
    },
    
    triggerCollection() {
      this.loading = true;
      axios.post('/api/data-collection/collect')
        .then(() => {
          console.log('数据采集触发成功');
        })
        .catch(error => {
          console.error('数据采集触发失败:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    getStatus() {
      axios.get('/api/data-collection/status')
        .then(response => {
          this.processedCount = response.data.processedCount;
          this.ruleTriggeredCount = response.data.ruleTriggeredCount;
        })
        .catch(error => {
          console.error('获取状态失败:', error);
        });
    }
  },
  beforeUnmount() {
    if (this.stompClient && this.stompClient.connected) {
      this.stompClient.disconnect();
    }
  }
}
</script>

<style scoped>
.data-collection-monitor {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.status-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.status-card {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
  background-color: #f5f7fa;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: center;
}
.card-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}
.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}
.button-group {
  margin-top: 20px;
}
</style> 