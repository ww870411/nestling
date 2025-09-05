<template>
  <div class="dashboard-container">
    <h2 class="dashboard-title">报表中心</h2>
    <div class="table-container">
      <el-table :data="allReports" stripe style="width: 100%">
        <el-table-column prop="groupName" label="所属单位" width="180" />
        <el-table-column prop="name" label="报表名称" />
        <el-table-column label="填报状态" width="120">
          <template #default="{ row }">
            <span :class="getStatusClass(row.id)" class="status-text">
              ● {{ getStatusText(row.id) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToReport(row.id)">
              进入
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { menuData } from '../services/menuData.js';

const router = useRouter();
const reportStatuses = ref({});

// Flatten menuData for the table
const allReports = computed(() => {
  return menuData.value.flatMap(group => 
    group.tables.map(table => ({
      ...table,
      groupName: group.name
    }))
  );
});

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

const getStatusText = (reportId) => {
  const status = reportStatuses.value[reportId];
  if (status === 'saved') return '已暂存';
  if (status === 'submitted') return '已提交';
  return '未填写';
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
