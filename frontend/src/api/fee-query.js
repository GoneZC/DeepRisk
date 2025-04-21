import axios from 'axios';

// 创建API实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL, // 从环境变量获取API地址
  timeout: 10000
});

// API方法
export default {
  // 获取结算信息列表
  getSettlements(params) {
    return api.get('/api/fee/settlements', { params });
  },
  
  // 获取费用明细
  getFeeDetails(settlementId) {
    return api.get(`/api/fee/details/${settlementId}`);
  },
  
  // 获取诊断信息
  getDiagnosis(settlementId) {
    return api.get(`/api/fee/diagnosis/${settlementId}`);
  }
}; 