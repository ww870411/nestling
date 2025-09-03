<template>
  <el-container style="height: 100vh;">
    <el-aside :width="isSidebarCollapsed ? '0px' : '200px'" class="sidebar-container">
      <div class="system-message-box" v-if="!isSidebarCollapsed">
        <h4>系统消息</h4>
        <p>欢迎使用雏鸟计划数据填报平台！请各单位按时提交生产计划。</p>
      </div>
      <el-scrollbar>
        <el-menu
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :collapse="isSidebarCollapsed"
          :collapse-transition="false"
          router
        >
          <!-- Menu items are the same -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu v-for="group in menuData" :key="group.name" :index="group.name">
            <template #title>
              <el-icon><Grid /></el-icon>
              <span>{{ group.name }}</span>
            </template>
            <el-menu-item 
              v-for="table in group.tables" 
              :key="table.id" 
              :index="`/data-entry/${table.id}`" 
              :class="getStatusClass(table.id)"
            >
              {{ table.name }}
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <el-header class="main-header">
        <div class="header-left">
          <div @click="toggleSidebar" class="collapse-icon">
            {{ isSidebarCollapsed ? '>>' : '<<' }}
          </div>
          <span>欢迎使用</span>
        </div>
        <div class="header-right">
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
// Script is the same as before
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { HomeFilled, Grid } from '@element-plus/icons-vue';

const router = useRouter();
const reportStatuses = ref({});
const isSidebarCollapsed = ref(false);

import { menuData } from '../services/menuData.js';

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const updateStatuses = () => {
  const statuses = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.startsWith('status-')) {
      const reportId = key.replace('status-', '');
      statuses[reportId] = localStorage.getItem(key);
    }
  }
  reportStatuses.value = statuses;
};

onMounted(() => {
  updateStatuses();
  window.addEventListener('storage', updateStatuses);
});

onUnmounted(() => {
  window.removeEventListener('storage', updateStatuses);
});

const getStatusClass = (reportId) => {
  const status = reportStatuses.value[reportId];
  if (status === 'saved') return 'status-saved';
  if (status === 'submitted') return 'status-submitted';
  return 'status-new';
};

const handleLogout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<style scoped>
.sidebar-container {
  background-color: #304156;
  transition: width 0.28s;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Hide content when width is 0 */
}

.system-message-box {
  padding: 15px;
  background-color: #263445;
  color: #bfcbd9;
  border-bottom: 1px solid #4d5d70;
  flex-shrink: 0;
}
.system-message-box h4 { margin: 0 0 10px 0; font-size: 14px; }
.system-message-box p { margin: 0; font-size: 12px; line-height: 1.5; }

.el-scrollbar { flex-grow: 1; }

.el-menu {
  border-right: none;
}

.status-saved { color: #e6a23c !important; }
.status-submitted { color: #67c23a !important; }

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 15px;
}

.zoom-label {
  font-size: 14px;
  color: #606266;
}

.zoom-value {
  font-size: 14px;
  color: #303133;
  width: 40px;
  text-align: right;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  font-size: 18px;
  cursor: pointer;
  margin-right: 15px;
  font-family: monospace;
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
.collapse-icon:hover { background-color: #f0f2f5; }

.el-main {
  background-color: #f0f2f5;
  padding: 0; /* Remove padding to allow full control from child */
}
</style>
