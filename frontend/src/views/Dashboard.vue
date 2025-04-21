<template>
  <div class="dashboard-container">
    <!-- 核心监管指标 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="dashboard-header">
          <h2>医保智能监管看板</h2>
          <div class="time-selector">
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="quarter">本季度</el-radio-button>
              <el-radio-button label="year">本年度</el-radio-button>
            </el-radio-group>
            <span class="last-update">最后更新: {{ currentTime }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="12" :md="6" :lg="6" v-for="(stat, index) in statCards" :key="index">
        <el-card shadow="hover" :body-style="{ padding: '0px' }" class="stat-card">
          <div class="stat-card-body" :class="stat.colorClass">
            <el-icon class="stat-icon"><component :is="stat.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 异常检测指标 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>医保费用异常监测</span>
              <el-tooltip content="各医疗机构异常指数排名及趋势">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="filter-bar">
            <el-select v-model="selectedRegion" placeholder="选择区域" size="small">
              <el-option v-for="item in regions" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
            <el-select v-model="selectedType" placeholder="机构类型" size="small">
              <el-option v-for="item in orgTypes" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
            <el-radio-group v-model="anomalyMode" size="small">
              <el-radio-button label="cost">费用异常</el-radio-button>
              <el-radio-button label="behavior">行为异常</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="anomalyChart" style="height: 380px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>诈骗风险预警</span>
              <el-tag type="danger" size="small">{{ warningCount }}个预警</el-tag>
            </div>
          </template>
          <div ref="riskRadarChart" style="height: 220px;"></div>
          <el-divider></el-divider>
          <div class="warning-list">
            <div v-for="(warning, idx) in warnings" :key="idx" class="warning-item">
              <el-icon :class="warning.level"><component :is="warning.icon" /></el-icon>
              <span class="warning-text">{{ warning.text }}</span>
              <el-button type="primary" link size="small">详情</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 诊疗模式与区域分布 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>欺诈行为类型分布</span>
            </div>
          </template>
          <div ref="fraudTypeChart" style="height: 340px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>涉案医保金额统计</span>
            </div>
          </template>
          <div ref="amountBarChart" style="height: 340px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>案件地区分布热图</span>
              <el-switch v-model="heatmapMode" 
                active-text="金额" 
                inactive-text="数量" 
                inline-prompt 
                size="small">
              </el-switch>
            </div>
          </template>
          <div ref="mapChart" style="height: 340px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 智能分析面板 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>智能关联网络分析</span>
              <el-tooltip content="高风险医患药关系网络">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div ref="networkChart" style="height: 380px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>医保基金实时监控</span>
              <el-tag size="small" type="success">在线</el-tag>
            </div>
          </template>
          <div ref="fundFlowChart" style="height: 380px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 异常案例列表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近期高风险案例</span>
              <el-button type="primary" size="small" plain>查看全部</el-button>
            </div>
          </template>
          <el-table :data="anomalyCases" stripe style="width: 100%">
            <el-table-column prop="caseId" label="案件编号" width="120"></el-table-column>
            <el-table-column prop="orgName" label="医疗机构" width="180"></el-table-column>
            <el-table-column prop="type" label="欺诈类型" width="120">
              <template #default="scope">
                <el-tag :type="getFraudTypeColor(scope.row.type)">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="涉案金额" width="120"></el-table-column>
            <el-table-column prop="score" label="风险评分" width="120">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.score" 
                  :color="getRiskColor(scope.row.score)" 
                  :format="format => `${format}分`">
                </el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="发现时间" width="150"></el-table-column>
            <el-table-column prop="status" label="处理状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="primary" link size="small" @click="viewCase(scope.row)">详情</el-button>
                <el-button type="warning" link size="small" @click="handleCase(scope.row)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  Money, Warning, Stopwatch, User, Cpu, Grid, 
  WarningFilled, QuestionFilled, ArrowUp, ArrowDown 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart, BarChart, PieChart, RadarChart, MapChart, GraphChart, HeatmapChart } from 'echarts/charts'
import { 
  TitleComponent, TooltipComponent, LegendComponent, 
  GridComponent, DataZoomComponent, VisualMapComponent,
  GeoComponent, ToolboxComponent 
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElMessage } from 'element-plus'
import chinaJson from '../assets/china.js' // 改为导入 JS 模块而不是 JSON

// 注册ECharts组件
echarts.use([
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, 
  DataZoomComponent, LineChart, BarChart, PieChart, RadarChart,
  CanvasRenderer, GeoComponent, VisualMapComponent, MapChart,
  ToolboxComponent, GraphChart, HeatmapChart
])

// 注册地图
echarts.registerMap('china', chinaJson)

// 时间和筛选项
const timeRange = ref('month')
const selectedRegion = ref('all')
const selectedType = ref('all')
const anomalyMode = ref('cost')
const heatmapMode = ref(true)
const warningCount = ref(4)
const currentTime = computed(() => {
  const now = new Date()
  return `${now.toLocaleDateString()} ${now.toLocaleTimeString()}`
})

// 图表容器引用
const anomalyChart = ref(null)
const riskRadarChart = ref(null)
const fraudTypeChart = ref(null)
const amountBarChart = ref(null)
const mapChart = ref(null)
const networkChart = ref(null)
const fundFlowChart = ref(null)

// 顶部统计卡片数据
const statCards = ref([
  {
    title: '本月欺诈案件',
    value: '328',
    icon: 'Warning',
    trend: 12.5,
    colorClass: 'orange'
  },
  {
    title: '涉案金额(万元)',
    value: '4,582.3',
    icon: 'Money',
    trend: 8.2,
    colorClass: 'blue'
  },
  {
    title: '智能识别率',
    value: '86.7%',
    icon: 'Cpu',
    trend: 4.5,
    colorClass: 'green'
  },
  {
    title: '已挽回金额(万元)',
    value: '1,937.5',
    icon: 'Grid',
    trend: -2.1,
    colorClass: 'purple'
  }
])

// 异常案例数据
const anomalyCases = ref([
  {
    caseId: 'AF2023001',
    orgName: '广州市第一人民医院',
    type: '重复收费',
    amount: '192,500',
    score: 95,
    time: '2023-11-15 08:30',
    status: '待处理'
  },
  {
    caseId: 'AF2023002',
    orgName: '深圳市中医院',
    type: '虚假诊断',
    amount: '85,300',
    score: 87,
    time: '2023-11-14 14:22',
    status: '已立案'
  },
  {
    caseId: 'AF2023003',
    orgName: '东莞市人民医院',
    type: '套用项目',
    amount: '67,850',
    score: 82,
    time: '2023-11-12 10:15',
    status: '调查中'
  },
  {
    caseId: 'AF2023004',
    orgName: '佛山市第二人民医院',
    type: '超限用药',
    amount: '45,200',
    score: 75,
    time: '2023-11-10 16:40',
    status: '已结案'
  },
  {
    caseId: 'AF2023005',
    orgName: '中山市人民医院',
    type: '分解住院',
    amount: '158,700',
    score: 92,
    time: '2023-11-08 09:25',
    status: '调查中'
  }
])

// 风险预警数据
const warnings = ref([
  {
    text: '广州市第一人民医院疑似重复收费异常',
    level: 'high-risk',
    icon: 'WarningFilled'
  },
  {
    text: '深圳市中医院药品使用频次异常',
    level: 'medium-risk',
    icon: 'WarningFilled'
  },
  {
    text: '东莞市人民医院检查项目异常聚集',
    level: 'high-risk',
    icon: 'WarningFilled'
  },
  {
    text: '佛山市第二人民医院住院天数异常',
    level: 'medium-risk',
    icon: 'WarningFilled'
  }
])

// 下拉选项
const regions = ref([
  { value: 'all', label: '全部区域' },
  { value: 'north', label: '北部区域' },
  { value: 'south', label: '南部区域' },
  { value: 'east', label: '东部区域' },
  { value: 'west', label: '西部区域' }
])

const orgTypes = ref([
  { value: 'all', label: '所有机构' },
  { value: '3a', label: '三甲医院' },
  { value: '3b', label: '三乙医院' },
  { value: '2', label: '二级医院' },
  { value: 'clinic', label: '诊所' }
])

// 工具函数
const getFraudTypeColor = (type) => {
  const colorMap = {
    '重复收费': 'danger',
    '虚假诊断': 'warning',
    '套用项目': 'warning',
    '超限用药': 'info',
    '分解住院': 'danger'
  }
  return colorMap[type] || 'info'
}

const getStatusType = (status) => {
  const statusMap = {
    '待处理': 'info',
    '已立案': 'warning',
    '调查中': 'primary',
    '已结案': 'success'
  }
  return statusMap[status] || 'info'
}

const getRiskColor = (score) => {
  if (score >= 90) return '#F56C6C'
  if (score >= 80) return '#E6A23C'
  if (score >= 70) return '#409EFF'
  return '#67C23A'
}

// 查看案例详情
const viewCase = (row) => {
  ElMessage.info(`查看案件: ${row.caseId}`)
}

// 处理案例
const handleCase = (row) => {
  ElMessage.success(`处理案件: ${row.caseId}`)
}

onMounted(() => {
  // 定时更新当前时间
  setInterval(() => {
    currentTime.value = new Date().toLocaleString()
  }, 60000)
  
  // 初始化所有图表
  initAnomalyChart()
  initRiskRadarChart()
  initFraudTypeChart()
  initAmountBarChart()
  initMapChart()
  initNetworkChart()
  initFundFlowChart()
  
  // 窗口大小变化时重新调整图表
  window.addEventListener('resize', () => {
    const charts = [
      anomalyChart.value, riskRadarChart.value, 
      fraudTypeChart.value, amountBarChart.value,
      mapChart.value, networkChart.value, 
      fundFlowChart.value
    ]
    
    charts.forEach(chart => {
      if (chart) {
        echarts.getInstanceByDom(chart)?.resize()
      }
    })
  })
})

// 初始化各个图表
function initAnomalyChart() {
  const chart = echarts.init(anomalyChart.value)
  
  const option = {
    title: {
      text: '医疗机构异常指数排名'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '异常指数',
      max: 100
    },
    yAxis: {
      type: 'category',
      data: ['广州市第一人民医院', '深圳市中医院', '东莞市人民医院', '佛山市第二人民医院', '中山市人民医院', '惠州市中心医院', '珠海市人民医院', '江门市中心医院', '肇庆市第一人民医院', '清远市人民医院'],
      axisLabel: {
        width: 150,
        overflow: 'truncate'
      }
    },
    series: [
      {
        name: '异常指数',
        type: 'bar',
        data: [95, 87, 82, 75, 72, 68, 65, 60, 58, 52],
        itemStyle: {
          color: function(params) {
            // 根据数值设置不同的颜色
            const value = params.value
            if (value >= 85) {
              return '#F56C6C'
            } else if (value >= 70) {
              return '#E6A23C'
            } else if (value >= 60) {
              return '#409EFF'
            } else {
              return '#67C23A'
            }
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}分'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

function initRiskRadarChart() {
  const chart = echarts.init(riskRadarChart.value)
  
  const option = {
    radar: {
      indicator: [
        { name: '重复收费', max: 100 },
        { name: '异常用药', max: 100 },
        { name: '虚假诊断', max: 100 },
        { name: '过度治疗', max: 100 },
        { name: '分解住院', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [85, 65, 78, 60, 92],
          name: '风险指数',
          areaStyle: {
            color: 'rgba(255, 73, 73, 0.6)'
          },
          lineStyle: {
            color: '#F56C6C'
          }
        }
      ]
    }]
  }
  
  chart.setOption(option)
}

function initFraudTypeChart() {
  const chart = echarts.init(fraudTypeChart.value)
  
  const option = {
    title: {
      text: '欺诈行为类型占比',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ['重复收费', '虚假诊断', '套用项目', '超限用药', '分解住院', '其他']
    },
    series: [
      {
        name: '欺诈类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 35, name: '重复收费' },
          { value: 20, name: '虚假诊断' },
          { value: 15, name: '套用项目' },
          { value: 12, name: '超限用药' },
          { value: 10, name: '分解住院' },
          { value: 8, name: '其他' }
        ]
      }
    ]
  }
  
  chart.setOption(option)
}

function initAmountBarChart() {
  const chart = echarts.init(amountBarChart.value)
  
  const option = {
    title: {
      text: '各类欺诈涉案金额(万元)'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br>{a}: {c}万元'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['重复收费', '虚假诊断', '套用项目', '超限用药', '分解住院', '其他']
    },
    yAxis: {
      type: 'value',
      name: '金额(万元)'
    },
    series: [
      {
        name: '涉案金额',
        type: 'bar',
        data: [1850, 1200, 750, 480, 220, 82],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

function initMapChart() {
  const chart = echarts.init(mapChart.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br>案件数: {c}'
    },
    visualMap: {
      min: 0,
      max: 200,
      text: ['高', '低'],
      realtime: false,
      calculable: true,
      inRange: {
        color: ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c']
      }
    },
    series: [
      {
        name: '案件分布',
        type: 'map',
        map: 'china',
        emphasis: {
          label: {
            show: true
          }
        },
        data: [
          { name: '广东', value: 185 },
          { name: '北京', value: 120 },
          { name: '上海', value: 145 },
          { name: '江苏', value: 98 },
          { name: '浙江', value: 87 },
          { name: '四川', value: 65 },
          { name: '湖北', value: 52 },
          { name: '湖南', value: 48 },
          { name: '河南', value: 45 },
          { name: '福建', value: 38 }
        ]
      }
    ]
  }
  
  chart.setOption(option)
}

function initNetworkChart() {
  const chart = echarts.init(networkChart.value)
  
  const option = {
    title: {
      text: '医-患-药关联网络',
      subtext: '高风险关系自动标红',
      left: 'center'
    },
    tooltip: {},
    legend: {
      data: ['医生', '患者', '药品', '医院'],
      orient: 'vertical',
      right: 10,
      top: 20
    },
    series: [
      {
        name: '关联网络',
        type: 'graph',
        layout: 'force',
        data: [
          { name: '李医生', value: 10, category: 0, symbolSize: 30 },
          { name: '张医生', value: 8, category: 0, symbolSize: 25 },
          { name: '王医生', value: 8, category: 0, symbolSize: 25 },
          { name: '患者A', value: 5, category: 1, symbolSize: 20 },
          { name: '患者B', value: 6, category: 1, symbolSize: 22 },
          { name: '患者C', value: 7, category: 1, symbolSize: 24 },
          { name: '药品X', value: 9, category: 2, symbolSize: 28 },
          { name: '药品Y', value: 7, category: 2, symbolSize: 24 },
          { name: '第一医院', value: 10, category: 3, symbolSize: 35 }
        ],
        links: [
          { source: '李医生', target: '患者A', value: 8, lineStyle: {color: '#F56C6C', width: 4} },
          { source: '李医生', target: '患者B', value: 6 },
          { source: '张医生', target: '患者B', value: 5 },
          { source: '王医生', target: '患者C', value: 7 },
          { source: '患者A', target: '药品X', value: 9, lineStyle: {color: '#F56C6C', width: 4} },
          { source: '患者B', target: '药品Y', value: 5 },
          { source: '患者C', target: '药品X', value: 3 },
          { source: '李医生', target: '第一医院', value: 8 },
          { source: '张医生', target: '第一医院', value: 8 },
          { source: '王医生', target: '第一医院', value: 8 }
        ],
        categories: [
          { name: '医生' },
          { name: '患者' },
          { name: '药品' },
          { name: '医院' }
        ],
        roam: true,
        label: {
          show: true,
          position: 'right'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 5
          }
        },
        force: {
          repulsion: 100,
          edgeLength: 80
        }
      }
    ]
  }
  
  chart.setOption(option)
}

function initFundFlowChart() {
  const chart = echarts.init(fundFlowChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['住院报销', '门诊报销', '慢病报销', '门特报销', '资金余额']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '报销金额(万)',
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '资金余额(亿)',
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '住院报销',
        type: 'line',
        stack: '总量',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: [120, 132, 101, 134, 90, 230, 210]
      },
      {
        name: '门诊报销',
        type: 'line',
        stack: '总量',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: [220, 182, 191, 234, 290, 330, 310]
      },
      {
        name: '慢病报销',
        type: 'line',
        stack: '总量',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: [150, 232, 201, 154, 190, 330, 410]
      },
      {
        name: '门特报销',
        type: 'line',
        stack: '总量',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: [320, 332, 301, 334, 390, 330, 320]
      },
      {
        name: '资金余额',
        type: 'line',
        yAxisIndex: 1,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#F56C6C'
        },
        itemStyle: {
          color: '#F56C6C',
          borderColor: '#fff',
          borderWidth: 2
        },
        data: [8.21, 8.16, 8.10, 8.07, 8.03, 7.96, 7.92]
      }
    ]
  }
  
  chart.setOption(option)
}
</script>

<style scoped>
.dashboard-container {
  padding: 15px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.dashboard-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.time-selector {
  display: flex;
  align-items: center;
  gap: 15px;
}

.last-update {
  font-size: 13px;
  color: #909399;
  margin-left: 15px;
}

.stat-row {
  margin-bottom: 20px;
}

.chart-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.stat-card-body {
  padding: 20px;
  display: flex;
  border-radius: 4px;
}

.stat-card-body.blue {
  background: linear-gradient(135deg, #409EFF, #64b6ff);
  color: white;
}

.stat-card-body.orange {
  background: linear-gradient(135deg, #E6A23C, #f0b95d);
  color: white;
}

.stat-card-body.green {
  background: linear-gradient(135deg, #67C23A, #88d15f);
  color: white;
}

.stat-card-body.purple {
  background: linear-gradient(135deg, #9254de, #a97ae0);
  color: white;
}

.stat-icon {
  font-size: 48px;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-trend.up {
  color: #e6f7ff;
}

.stat-trend.down {
  color: #e6f7ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  margin-bottom: 15px;
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.warning-list {
  max-height: 150px;
  overflow-y: auto;
}

.warning-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.warning-item:last-child {
  border-bottom: none;
}

.warning-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.warning-item .high-risk {
  color: #F56C6C;
}

.warning-item .medium-risk {
  color: #E6A23C;
}

.warning-item .low-risk {
  color: #409EFF;
}

.warning-text {
  flex: 1;
  font-size: 13px;
  margin-right: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>