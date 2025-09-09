<template>
  <div class="dashboard-container">
    <h2 class="dashboard-title">{{ config.title }}</h2>
    <div class="table-container">
      <el-table :data="allReports" stripe style="width: 100%" v-loading="isLoading">
        <template v-for="column in config.columns" :key="column.prop">
          <el-table-column :prop="column.prop" :label="column.label" :width="column.width">
            
            <template #default="{ row }">
              <!-- 状态列 -->
              <div v-if="column.type === 'status'">
                <span :class="getStatusInfo(row.status).className" class="status-text">
                  ● {{ getStatusInfo(row.status).text }}
                </span>
              </div>

              <!-- 时间列 -->
              <div v-else-if="column.type === 'datetime'">
                <span v-if="row.status === 'submitted'">{{ formatDateTime(row.submittedAt) }}</span>
                <span v-else></span>
              </div>

              <!-- 提交人列 -->
              <div v-else-if="column.type === 'submitter'">
                <span v-if="row.status === 'submitted'">{{ row.submittedBy?.username }}</span>
                <span v-else></span>
              </div>

              <!-- 操作列 -->
              <div v-else-if="column.type === 'actions'">
                <el-button type="primary" link @click="goToReport(row.id)">
                  进入
                </el-button>
              </div>

              <!-- 默认列 -->
              <div v-else>
                {{ row[column.prop] }}
              </div>
            </template>

          </el-table-column>
        </template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';
import { dashboardConfig } from '@/projects/heating_plan_2025-2026/dashboardData.js';
import { formatDateTime } from '@/utils/formatter.js';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const projectStore = useProjectStore();
const authStore = useAuthStore();

const { menuData } = storeToRefs(projectStore);
const { accessibleUnits } = storeToRefs(authStore);

const config = ref(dashboardConfig);
const reportInfo = ref({});
const isLoading = ref(false);

// 将菜单数据和状态数据结合，并根据权限过滤
const allReports = computed(() => {
  const allowedUnits = new Set(accessibleUnits.value);
  return menuData.value
    .filter(group => allowedUnits.has(group.name)) // 应用权限过滤
    .flatMap(group => 
      group.tables.map(table => ({
        ...table,
        groupName: group.name,
        // The key in reportInfo is the table's name
        status: reportInfo.value[table.name]?.status || 'new',
        submittedAt: reportInfo.value[table.name]?.submittedAt || null,
        submittedBy: reportInfo.value[table.name]?.submittedBy || null
      }))
    );
});

// 从后端获取状态
const fetchReportStatuses = async () => {
  isLoading.value = true;
  const projectId = route.params.projectId;
  if (!projectId) {
    isLoading.value = false;
    return;
  }

  // 从菜单数据中收集所有表格的名称
  const tableNames = menuData.value.flatMap(group => group.tables.map(t => t.name));

  if (tableNames.length === 0) {
    isLoading.value = false;
    return;
  }

  try {
    const response = await fetch(`/api/project/${projectId}/table_statuses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tableNames)
    });

    if (!response.ok) {
      throw new Error('Failed to fetch report statuses from server.');
    }

    const statuses = await response.json();
    reportInfo.value = statuses;

  } catch (error) {
    console.error("Error fetching report statuses:", error);
    ElMessage.error('无法从服务器加载报表状态。');
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // Ensure menuData is loaded before fetching statuses
  if (menuData.value.length > 0) {
    fetchReportStatuses();
  } else {
    // If menuData is not ready, watch it. This is a fallback.
    const unwatch = projectStore.$subscribe((mutation, state) => {
      if (state.menuData.length > 0) {
        fetchReportStatuses();
        unwatch(); // Stop watching once data is loaded
      }
    });
  }
});

// 根据状态获取显示信息
const getStatusInfo = (status) => {
  return config.value.statusMap[status] || config.value.statusMap.new;
};

const goToReport = (reportId) => {
  const projectId = route.params.projectId;
  router.push({ name: 'data-entry', params: { projectId, tableId: reportId } });
};
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #fff;
  height: 100%;
}

.dashboard-title {
  text-align: center;
  margin-bottom: 20px;
}

.table-container {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.status-text {
  font-weight: bold;
}

.status-new {
  color: #f56c6c;
}

.status-saved {
  color: #e6a23c;
}

.status-submitted {
  color: #67c23a;
}
</style>
