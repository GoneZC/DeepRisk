import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import FeeQuery from '../views/FeeQuery.vue'
import OutpatientMonitor from '../views/OutpatientMonitor.vue'
import InpatientMonitor from '../views/InpatientMonitor.vue'
import GroupFraudDetection from '../views/GroupFraudDetection.vue'


const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/fee-query',
    name: 'FeeQuery',
    component: FeeQuery
      },
  {
    path: '/analysis/outpatient',
    name: 'OutpatientMonitor',
    component: OutpatientMonitor
  },
  {
    path: '/analysis/inpatient',
    name: 'InpatientMonitor',
    component: InpatientMonitor
  },
  {
    path: '/analysis/group-fraud',
    name: 'GroupFraudDetection',
    component: GroupFraudDetection
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 