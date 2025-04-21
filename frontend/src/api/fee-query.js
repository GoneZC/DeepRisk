import axios from 'axios';

// 创建API实例
const api = axios.create({
  baseURL: 'http://localhost:8082',
  timeout: 10000
});

// API方法
export default {
  // 获取结算信息列表
  getSettlements(params) {
    return api.post('/api/settlements/search', params);
  },
  
  // 获取费用明细
  getFeeDetails(settlementId) {
    return api.get(`/api/fee-details/${settlementId}`);
  },
  
  // 获取诊断信息
  getDiagnosis(settlementId) {
    return api.get(`/api/diagnosis-details/${settlementId}`);
  }
}; 