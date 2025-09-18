<template>
  <el-container style="height: 100vh;">
    <el-aside :width="isSidebarCollapsed ? '0px' : '200px'" class="sidebar-container">
      <div class="system-message-box" v-if="!isSidebarCollapsed && systemMessages">
        <h4>{{ systemMessages.title }}</h4>
        <p>{{ systemMessages.content }}</p>
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
          <el-menu-item :index="dashboardPath">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu v-for="group in filteredMenuData" :key="group.name" :index="group.name">
            <template #title>
              <el-icon><Grid /></el-icon>
              <span>{{ group.name }}</span>
            </template>
            <el-menu-item 
              v-for="table in group.tables" 
              :key="table.id" 
              :index="`/project/${currentProjectId}/data-entry/${table.id}`" 
              :class="getStatusClass(table.id)"
            >
              {{ `${table.id} ${table.name.replace(/^\d+\s*/, '')}` }}
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
          <span v-if="authStore.user"><b>{{ authStore.user.username }}</b>, 欢迎使用</span>
          <span v-else>欢迎使用</span>
        </div>
        <div class="header-right">
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view v-if="isProjectLoaded"></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router'; // 引入 useRoute
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';
import { HomeFilled, Grid } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute(); // 使用 useRoute
const projectStore = useProjectStore();
const authStore = useAuthStore();

const buildUserHeaders = () => {
  const username = authStore.user?.username;
  return username ? { 'X-User-Name': username } : {};
};

const { menuData, isProjectLoaded, systemMessages } = storeToRefs(projectStore);
const { accessibleUnits } = storeToRefs(authStore);

// 从路由参数中获取当前项目ID
const currentProjectId = computed(() => route.params.projectId);

// 为模板动态生成首页链接
const dashboardPath = computed(() => `/project/${currentProjectId.value}/dashboard`);

const reportStatuses = ref({});
const isSidebarCollapsed = ref(false);

// 根据当前用户的权限过滤菜单
const filteredMenuData = computed(() => {
  if (!menuData.value) return [];
  const allowedUnits = new Set(accessibleUnits.value);
  return menuData.value.filter(group => allowedUnits.has(group.name));
});

const fetchReportStatuses = async () => {
  if (!menuData.value || menuData.value.length === 0) return;

  const tableIds = menuData.value.flatMap(group => group.tables.map(table => table.id));
  if (tableIds.length === 0) return;

  try {
    const response = await fetch(`/api/project/${currentProjectId.value}/table_statuses`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildUserHeaders()
      },
      body: JSON.stringify(tableIds)
    });
    if (response.ok) {
      const statuses = await response.json();
      reportStatuses.value = statuses;
    } else {
      console.error('Failed to fetch report statuses.');
    }
  } catch (error) {
    console.error('Error fetching report statuses:', error);
  }
};

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

onMounted(() => {
  fetchReportStatuses();
});

watch(menuData, () => {
  fetchReportStatuses();
}, { deep: true });

const getStatusClass = (reportId) => {
  const statusInfo = reportStatuses.value[reportId];
  if (!statusInfo) return 'status-new';
  
  const status = statusInfo.status;
  if (status === 'saved') return 'status-saved';
  if (status === 'submitted') return 'status-submitted';
  return 'status-new';
};

const handleLogout = () => {
  authStore.logout();
  projectStore.clearProject();
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
.system-message-box p { margin: 0; font-size: 12px; line-height: 1.5; white-space: pre-wrap; }

.el-scrollbar { flex-grow: 1; }

.el-menu {
  border-right: none;
}

.status-saved { color: #e6a23c !important; }
.status-submitted { color: #67c23a !important; }
.status-new { color: #f56c6c !important; }

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