import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
      meta: { title: '监管看板' }
    },
    {
      path: '/fee-query',
      name: 'FeeQuery',
      component: () => import('../views/FeeQuery.vue'),
      meta: { title: '费用查询' }
    },
    {
      path: '/audit',
      name: 'Audit',
      redirect: '/audit/outpatient',
      meta: { title: '智能审核' }
    },
    {
      path: '/audit/outpatient',
      name: 'OutpatientAudit',
      component: () => import('../views/OutpatientAudit.vue'),
      meta: { title: '门诊审核' }
    },
    {
      path: '/audit/inpatient',
      name: 'InpatientAudit',
      component: () => import('../views/InpatientAudit.vue'),
      meta: { title: '住院审核' }
    }
  ]
}) 