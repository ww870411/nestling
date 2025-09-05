<template>
  <div class="dashboard-container">
    <h2 class="dashboard-title">{{ config.title }}</h2>
    <div class="table-container">
      <el-table :data="allReports" stripe style="width: 100%">
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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { dashboardConfig } from '@/projects/heating_plan_2025-2026/dashboardData.js';

const router = useRouter();
const projectStore = useProjectStore();
const { menuData } = storeToRefs(projectStore);

const config = ref(dashboardConfig);
const reportInfo = ref({});

// 将菜单数据和状态数据结合
const allReports = computed(() => {
  return menuData.value.flatMap(group => 
    group.tables.map(table => ({
      ...table,
      groupName: group.name,
      status: reportInfo.value[table.id]?.status || 'new',
      submittedAt: reportInfo.value[table.id]?.submittedAt || null
    }))
  );
});

// 从 localStorage 更新状态
const updateReportInfo = () => {
  const info = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.startsWith('status-')) {
      const reportId = key.replace('status-', '');
      if (!info[reportId]) info[reportId] = {};
      info[reportId].status = localStorage.getItem(key);
    } else if (key.startsWith('submittedAt-')) {
      const reportId = key.replace('submittedAt-', '');
      if (!info[reportId]) info[reportId] = {};
      info[reportId].submittedAt = localStorage.getItem(key);
    }
  }
  reportInfo.value = info;
};

onMounted(() => {
  updateReportInfo();
  window.addEventListener('storage', updateReportInfo);
});

onUnmounted(() => {
  window.removeEventListener('storage', updateReportInfo);
});

// 根据状态获取显示信息
const getStatusInfo = (status) => {
  return config.value.statusMap[status] || config.value.statusMap.new;
};

// 格式化时间
const formatDateTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const goToReport = (reportId) => {
  router.push(`/data-entry/${reportId}`);
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