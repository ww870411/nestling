<template>
  <div class="dashboard-container">
    <el-dialog
      v-model="instructionDialogVisible"
      class="guide-dialog"
      width="860px"
      top="6vh"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <template #header>
        <div class="guide-dialog__header">
          <el-icon class="guide-dialog__header-icon" :size="28">
            <Notebook />
          </el-icon>
          <div>
            <div class="guide-dialog__title">系统使用简要说明</div>
            <div class="guide-dialog__subtitle">请仔细阅读以下指引后开始填报工作</div>
          </div>
        </div>
      </template>
      <div class="guide-dialog__content">
        <ol class="guide-dialog__list">
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">1</span>
            <p>欢迎您使用本系统！本系统由大连洁净能源集团有限公司-经济运行部自主开发并维护，以期为您提供便捷的生产数据计划与统计服务。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">2</span>
            <p>在左侧栏目中，您可以看到 <span style="color:red;">【需要您负责填报的】</span>单位及表格，表格名称显示为红色的表示未填报、黄色表示已暂存、绿色表示已提交。在右侧的主要区域中，您可以看到表格提交的时间、提交人等信息，也可以点击查看提交历史，同时提供了方便的表格入口。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">3</span>
            <p>进入填表页面后，仅需您填写可编辑的指标，当前表格<span style="color:red;">不适用</span>的统计指标均 <span style="color:red;">【不能修改】</span>，效率等计算指标、供暖期累计指标及区域汇总表也<span style="color:red;">【不需您填写】</span>，由系统自动计算。同期值已尽可能填好，但可能仍不完全，未填的还请您补充，但不要修改已填同期数据，如有特殊情况请联系管理员。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">4</span>
            <p>您可以随时使用 <span style="color:red;">【暂存】</span>功能，将当前页面中的表格数据暂存在浏览器缓存中，并可随时取回，暂存功能不进行数据校验。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">5</span>
            <p>您可以随时使用填表页面上提供的 <span style="color:red;">【导出至本地】</span>功能，可方便地将目前页面中的表格数据以EXCEL表格的形式导出，导出的表格内含计算公式，方便您使用。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">6</span>
            <p>当数据填好并经您所在单位领导审核后，便可以点击 <span style="color:red;">【提交】</span>按钮，将数据提交至服务器上，您所在区域的管理员便可看到相应的数据（如集团、主城区管理员）。在提交时，会进行数据有效性校验，请确保填写的数字合法，且与同期值之间的关系符合本工作的通知要求，若有特殊情况，必须撰写情况<span style="color:red;">【解释说明】</span>并提交审核。</p>
          </li>
          <li class="guide-dialog__item">
            <span class="guide-dialog__index">7</span>
            <p>本系统仍处于试用阶段，可能存在不足和bug，目前正在积极完善中，欢迎您在使用中随时提出宝贵的意见和建议！</p>
          </li>
        </ol>
      </div>
      <template #footer>
        <div class="guide-dialog__footer">
          <el-button type="primary" size="large" @click="markInstructionRead">已阅读</el-button>
        </div>
      </template>
    </el-dialog>
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

              <!-- 名称列：增加需要汇总更新标记 -->
              <div v-else-if="column.prop === 'name'">
                <span>{{ row.name }}</span>
                <span
                  v-if="needsAttention.has(row.id)"
                  class="attention-mark"
                  title="该表的提交时间晚于上级汇总表"
                >
                  !
                </span>
              </div>

              <!-- 提交历史 -->
              <div v-else-if="column.type === 'history'">
                <el-button type="primary" link @click="openHistoryDialog(row)">查看</el-button>
              </div>

              <!-- 操作列 -->
              <div v-else-if="column.type === 'actions'">
                <el-button type="primary" link @click="goToReport(row.id)">进入</el-button>
                <template v-if="authStore.user && (authStore.user.globalRole === 'unit_admin' || authStore.user.globalRole === 'regional_admin' || authStore.user.globalRole === 'super_admin' || authStore.user.globalRole === 'god')">
                  <el-button v-if="row.status === 'submitted'" type="success" link @click="approveRow(row)">批准</el-button>
                  <el-button v-if="row.status === 'approved'" type="warning" link @click="unapproveRow(row)">撤销批准</el-button>
                </template>
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
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';
import { dashboardConfig } from '@/projects/heating_plan_2025-2026/dashboardData.js';
import { formatDateTime } from '@/utils/formatter.js';
import { ElMessage } from 'element-plus';
import { Notebook } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const projectStore = useProjectStore();
const authStore = useAuthStore();

const { menuData } = storeToRefs(projectStore);
const { accessibleUnits } = storeToRefs(authStore);

const buildUserHeaders = () => {
  const username = authStore.user?.username;
  return username ? { 'X-User-Name': username } : {};
};

const config = ref(dashboardConfig);
// 扩展状态映射：增加已批准(approved)
if (!config.value.statusMap.approved) {
  config.value.statusMap.approved = { text: '已批准', className: 'status-approved' };
}
const reportInfo = ref({});
const isLoading = ref(false);

const instructionDialogVisible = ref(false);
const instructionStorageKey = 'dashboardGuideAcknowledged';

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

// 基于菜单构建 子->父(汇总表) 映射
const parentMap = computed(() => {
  const map = new Map();
  if (!menuData.value) return map;
  for (const group of menuData.value) {
    for (const table of group.tables || []) {
      if (table && table.type === 'summary' && Array.isArray(table.subsidiaries)) {
        for (const childId of table.subsidiaries) {
          if (!map.has(childId)) map.set(childId, []);
          map.get(childId).push(table.id);
        }
      }
    }
  }
  return map;
});

// 需要提示的表集合（仅对子表显示标记）
// 条件：
// 1) 子未提交 且 任一祖先汇总已提交；或
// 2) 子已提交 且 任一祖先未提交 或 祖先时间早于子时间。
const needsAttention = computed(() => new Set());

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
      headers: {
        'Content-Type': 'application/json',
        ...buildUserHeaders()
      },
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

const markInstructionRead = () => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(instructionStorageKey, 'true');
  }
  instructionDialogVisible.value = false;
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
    const response = await fetch(`/api/project/${projectId}/table/${table.id}/history`, {
      headers: buildUserHeaders()
    });
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
  const forceGuideFromQuery = route.query.showGuide === '1' || route.query.showGuide === true;

  if (forceGuideFromQuery) {
    instructionDialogVisible.value = true;
    if (typeof window !== 'undefined') {
      localStorage.setItem(instructionStorageKey, 'true');
    }

    nextTick(() => {
      const cleanedQuery = { ...route.query };
      delete cleanedQuery.showGuide;
      const cleanedParams = { ...route.params };
      router.replace({ name: route.name || 'dashboard', params: cleanedParams, query: cleanedQuery });
    });
  } else if (typeof window !== 'undefined') {
    const hasAcknowledged = localStorage.getItem(instructionStorageKey);
    if (!hasAcknowledged) {
      instructionDialogVisible.value = true;
    }
  }

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

const approveRow = async (row) => {
  try {
    const projectId = route.params.projectId;
    const resp = await fetch(`/api/project/${projectId}/table/${row.id}/approve`, { method: 'POST', headers: buildUserHeaders() });
    if (!resp.ok) throw new Error('approve failed');
    ElMessage.success('已批准。');
    fetchReportStatuses();
  } catch (e) {
    ElMessage.error('批准失败');
  }
};

const unapproveRow = async (row) => {
  try {
    const projectId = route.params.projectId;
    const resp = await fetch(`/api/project/${projectId}/table/${row.id}/unapprove`, { method: 'POST', headers: buildUserHeaders() });
    if (!resp.ok) throw new Error('unapprove failed');
    ElMessage.success('已撤销批准。');
    fetchReportStatuses();
  } catch (e) {
    ElMessage.error('撤销批准失败');
  }
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

.status-text { font-weight: bold; }
.status-new { color: inherit; }
.status-saved { color: #e6a23c; }
.status-submitted { color: #409eff; }
.status-approved { color: #67c23a; }

/* 需要汇总更新的提示标记（名称列旁） */
.attention-mark {
  color: #f56c6c;
  margin-left: 6px;
  font-weight: bold;
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
.guide-dialog :deep(.el-dialog) {
  border-radius: 18px;
  overflow: hidden;
  max-height: min(88vh, 700px);
}

.guide-dialog :deep(.el-dialog__header) {
  margin: 0;
  padding: 0;
}

.guide-dialog :deep(.el-dialog__body) {
  padding: 0;
  background: #fff;
  max-height: calc(min(88vh, 700px) - 110px);
}

.guide-dialog :deep(.el-dialog__footer) {
  padding: 0;
}

.guide-dialog__header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 32px 18px;
  background: linear-gradient(135deg, #f3f6ff 0%, #ffffff 90%);
  border-bottom: 1px solid #ebeef5;
}

.guide-dialog__header-icon {
  color: #3a70ff;
}

.guide-dialog__title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2d3d;
}

.guide-dialog__subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: #909399;
}

.guide-dialog__content {
  max-height: calc(min(88vh, 700px) - 180px);
  overflow-y: auto;
  padding: 26px 36px;
  background-color: #fff;
}

.guide-dialog__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 18px;
}

.guide-dialog__item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 22px;
  align-items: flex-start;
  padding: 16px 22px;
  background: #f7f9fc;
  border: 1px solid #eef2fb;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(63, 99, 188, 0.1);
}

.guide-dialog__index {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3a70ff 0%, #60a5fa 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}

.guide-dialog__item p {
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: #4a5568;
}

.guide-dialog__footer {
  display: flex;
  justify-content: center;
  padding: 22px 0 30px;
  background: #fff;
  border-top: 1px solid #f0f2f5;
}

.guide-dialog__footer :deep(.el-button) {
  min-width: 200px;
  font-size: 18px;
  letter-spacing: 1px;
}

</style>
