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

              <!-- 提交历史 -->
              <div v-else-if="column.type === 'history'">
                <el-button type="primary" link @click="openHistoryDialog(row)">查看</el-button>
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
    <el-dialog v-model="historyDialogVisible" :title="historyDialogTitle" width="560px">
      <div v-if="historyLoading" class="history-dialog__loading">正在加载历史记录...</div>
      <div v-else>
        <div v-if="historyError" class="history-dialog__error">{{ historyError }}</div>
        <div v-else-if="historyRecords.length === 0" class="history-dialog__empty">暂无历史记录</div>
        <el-table v-else :data="historyRecords" border style="width: 100%;">
          <el-table-column prop="action" label="操作类型" width="120">
            <template #default="{ row }">{{ historyActionLabel(row.action) }}</template>
          </el-table-column>
          <el-table-column prop="timestamp" label="操作时间" width="200">
            <template #default="{ row }">{{ formatDateTime(row.timestamp) }}</template>
          </el-table-column>
          <el-table-column prop="submittedBy" label="操作人">
            <template #default="{ row }">
              <div>{{ row.submittedBy?.username || '-' }}</div>
              <div v-if="row.submittedBy?.unit" class="history-dialog__unit">{{ row.submittedBy.unit }}</div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

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

const historyDialogVisible = ref(false);
const historyRecords = ref([]);
const historyLoading = ref(false);
const historyError = ref('');
const historyTableName = ref('');
const historyDialogTitle = computed(() => historyTableName.value ? `${historyTableName.value} 提交历史` : '提交历史');

// 将菜单数据和状态数据结合，并根据权限过滤
const allReports = computed(() => {
  const allowedUnits = new Set(accessibleUnits.value);
  return menuData.value
    .filter(group => allowedUnits.has(group.name)) // 应用权限过滤
    .flatMap(group => 
      group.tables.map(table => ({
        ...table,
        name: `${table.id} ${table.name.replace(/^\d+\s*/, '')}`,
        groupName: group.name,
        // The key in reportInfo is the table's id
        status: reportInfo.value[table.id]?.status || 'new',
        submittedAt: reportInfo.value[table.id]?.submittedAt || null,
        submittedBy: reportInfo.value[table.id]?.submittedBy || null
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

  // 从菜单数据中收集所有表格的ID
  const tableIds = menuData.value.flatMap(group => group.tables.map(t => t.id));

  if (tableIds.length === 0) {
    isLoading.value = false;
    return;
  }

  try {
    const response = await fetch(`/api/project/${projectId}/table_statuses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tableIds)
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

const historyActionLabel = (action) => {
  if (action === 'submit') return '提交';
  if (action === 'save_draft') return '暂存';
  return action || '';
};

const openHistoryDialog = async (table) => {
  historyDialogVisible.value = true;
  historyTableName.value = table.name || '';
  historyRecords.value = [];
  historyError.value = '';
  historyLoading.value = true;

  const projectId = route.params.projectId;
  if (!projectId) {
    historyLoading.value = false;
    historyError.value = '缺少项目 ID，无法获取历史记录。';
    return;
  }

  try {
    const response = await fetch(`/api/project/${projectId}/table/${table.id}/history`);
    if (!response.ok) {
      throw new Error('failed to fetch history');
    }
    const data = await response.json();
    historyRecords.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Error fetching history records:', error);
    historyError.value = '获取历史记录失败，请稍后重试。';
  } finally {
    historyLoading.value = false;
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

.history-dialog__loading,
.history-dialog__empty {
  text-align: center;
  padding: 20px 0;
  color: #606266;
}

.history-dialog__error {
  text-align: center;
  padding: 20px 0;
  color: #f56c6c;
}

.history-dialog__unit {
  font-size: 12px;
  color: #909399;
}
</style>
