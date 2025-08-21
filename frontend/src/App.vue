<template>
  <el-container class="app-container">
    <!-- 侧边导航栏 -->
    <el-aside width="275px">
      <el-menu
        :router="true"
        :default-active="activeIndex"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <div class="logo-container">
          <el-icon class="logo-icon"><Monitor /></el-icon>
          <span class="logo-text">数智驱动的医保反欺诈系统</span>
        </div>
        
        <!-- 监管看板 -->
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <span>监管看板</span>
        </el-menu-item>
        
        <!-- 数据查询 -->
        <el-menu-item index="/fee-query">
          <el-icon><Search /></el-icon>
          <span>数据查询</span>
        </el-menu-item>
        
        <!-- 智能审核 -->
        <el-sub-menu index="/analysis">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>智能审核</span>
          </template>
          
          <el-menu-item index="/analysis/outpatient">
            <el-icon><FirstAidKit /></el-icon>
            <span>门诊监管</span>
          </el-menu-item>
          
          <el-menu-item index="/analysis/inpatient">
            <el-icon><OfficeBuilding /></el-icon>
            <span>住院监管</span>
          </el-menu-item>
          
          <el-menu-item index="/analysis/group-fraud">
            <el-icon><User /></el-icon>
            <span>团体欺诈识别</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <el-header height="60px">
        <div class="header-right">
          <el-dropdown>
            <span class="user-dropdown">
              管理员 <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, Search, Cpu, FirstAidKit, OfficeBuilding, ArrowDown, Monitor, SetUp, User } from '@element-plus/icons-vue'

const route = useRoute()
const activeIndex = ref('/')

// 保持当前路由高亮
watch(() => route.path, (newPath) => {
  // 主路径和子路径的一致性处理
  if (newPath.startsWith('/analysis/')) {
    activeIndex.value = '/analysis'
  } else {
    activeIndex.value = newPath
  }
}, { immediate: true })
</script>

<style>
.app-container {
  height: 100vh;
  min-height: 600px;
}

.el-aside {
  background-color: #304156;
  color: #bfcbd9;
  overflow: hidden;
}

.el-menu {
  border-right: none;
}

.logo-container {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 16px;
  color: #fff;
  background-color: #263445;
}

.logo-icon {
  font-size: 24px;
  margin-right: 10px;
}

.logo-text {
  font-size: 16px;
  font-weight: 500;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #333;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style> 