<template>
  <div class="fee-query">
    <h1>费用查询</h1>
    
    <!-- 查询表单 -->
    <div class="search-form">
      <input v-model="searchParams.patientId" placeholder="患者ID" />
      <button @click="searchSettlements">查询</button>
    </div>
    
    <!-- 结算信息表格 -->
    <table v-if="settlements.length > 0">
      <thead>
        <tr>
          <th>就诊ID</th>
          <th>患者ID</th>
          <th>性别</th>
          <th>年龄</th>
          <th>疾病名称</th>
          <th>医疗类型</th>
          <th>开始日期</th>
          <th>结束日期</th>
          <th>总费用</th>
          <th>自付费用</th>
          <th>医保支付</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in settlements" :key="item.mdtrtId">
          <td>{{ item.mdtrtId }}</td>
          <td>{{ item.psnNo }}</td>
          <td>{{ item.gend }}</td>
          <td>{{ item.age }}</td>
          <td>{{ item.diseName }}</td>
          <td>{{ item.medType }}</td>
          <td>{{ item.begndate }}</td>
          <td>{{ item.enddate }}</td>
          <td>{{ item.medfeeSum }}</td>
          <td>{{ item.fulOwnpay }}</td>
          <td>{{ item.hifpPay }}</td>
          <td>
            <button @click="viewDetails(item.mdtrtId)">费用明细</button>
            <button @click="viewDiagnosis(item.mdtrtId)">诊断详情</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 费用明细对话框 -->
    <fee-details-dialog
      v-if="showDetails"
      :settlement-id="currentSettlementId"
      @close="showDetails = false"
    />
  </div>
</template>

<script>
import feeQueryApi from '@/api/fee-query';
import FeeDetailsDialog from '@/components/FeeDetailsDialog.vue';

export default {
  components: {
    FeeDetailsDialog
  },
  data() {
    return {
      searchParams: {
        patientId: ''
      },
      settlements: [],
      showDetails: false,
      currentSettlementId: null
    };
  },
  methods: {
    async searchSettlements() {
      try {
        const response = await feeQueryApi.getSettlements(this.searchParams);
        this.settlements = response.data;
      } catch (error) {
        console.error('获取结算信息失败', error);
        // 显示错误提示
      }
    },
    viewDetails(settlementId) {
      this.currentSettlementId = settlementId;
      this.showDetails = true;
    },
    viewDiagnosis(settlementId) {
      // 导航到诊断详情页
      this.$router.push(`/diagnosis/${settlementId}`);
    }
  }
};
</script> 