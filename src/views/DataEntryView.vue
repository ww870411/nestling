<template>
  <div class="data-entry-container">
    <h2 class="page-title">{{ pageTitle }}</h2>

    <div class="content-wrapper">
      <div class="main-content">
        <div v-if="projectStore.isLoading" class="loading-indicator">
          <el-icon class="is-loading" :size="26"><Loading /></el-icon>
          <p>正在加载数据...</p>
        </div>
        <div v-else-if="tableData.length === 0" class="no-data-message">
          <p>暂无数据或项目未选择。</p>
        </div>
        <div v-else class="table-wrapper" :style="zoomStyle">
          <el-table :data="tableData" :cell-class-name="getCellClass" border row-key="id" style="width: 100%"
                    :header-cell-style="{ textAlign: 'center' }"
                    :cell-style="{ textAlign: 'center' }"
                    height="100%">
            <el-table-column prop="name" label="指标名称" :width="scaledColumnWidths.name" fixed>
              <template #default="{ row }">
                <div class="cell-content">
                  <span :class="{ 'calculated-indicator': row.type === 'calculated' }">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="计量单位" :width="scaledColumnWidths.unit" fixed>
              <template #default="{ row }">
                <div class="cell-content">{{ row.unit }}</div>
              </template>
            </el-table-column>

            <el-table-column label="本期计划" :width="scaledColumnWidths.totalPlan">
              <template #default="{ row }">
                <div class="cell-content">{{ row.totals.plan }}</div>
              </template>
            </el-table-column>
            <el-table-column label="同期完成" :width="scaledColumnWidths.totalSamePeriod">
              <template #default="{ row }">
                <div class="cell-content">{{ row.totals.samePeriod }}</div>
              </template>
            </el-table-column>
            <el-table-column label="差异率" :width="scaledColumnWidths.diffRate">
              <template #default="{ row }">
                <div class="cell-content">
                  <span :class="getDifferenceRateClass(row)">{{ calculateDifferenceRate(row) }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column v-for="month in months" :key="month.key" :label="month.label" header-align="center">
              <el-table-column label="计划" :prop="`monthlyData.${month.key}.plan`" :width="scaledColumnWidths.monthPlan">
                <template #default="{ row }">
                  <div @click="startEdit(row, month.key)" class="cell-content">
                    <el-input
                      v-if="isEditing(row.id, month.key)"
                      v-model.number="row.monthlyData[month.key].plan"
                      @blur="finishEdit(row, month.key)"
                      @keyup.enter="finishEdit(row, month.key)"
                    />
                    <span v-else>{{ row.monthlyData[month.key].plan }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="同期" :prop="`monthlyData.${month.key}.samePeriod`" :width="scaledColumnWidths.monthSamePeriod">
                <template #default="{ row }">
                  <div class="cell-content">{{ row.monthlyData[month.key].samePeriod }}</div>
                </template>
              </el-table-column>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="isErrorPanelVisible" class="error-panel" :style="{ width: `${panelWidth}px` }">
          <div class="resizer" @mousedown="startResize"></div>
          <div class="error-panel-header">
            <h4>软性错误说明</h4>
            <el-icon @click="closeErrorPanel" class="close-icon"><Close /></el-icon>
          </div>
          <el-scrollbar class="error-list">
            <div v-for="([key, error]) in softErrors" :key="key" class="error-item">
              <label>{{ getErrorLabel(key) }}</label>
              <p class="error-message">原因: {{ error.message }}</p>
              <el-input v-model="explanations[key]" type="textarea" :rows="2" placeholder="请输入说明..." />
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>

    <div class="footer-actions">
      <div>
        <el-button @click="handleExport">导出</el-button>
      </div>
      <div class="table-controls">
        <label style="margin-right: 10px; font-size: 14px; color: #606266;">表格缩放:</label>
        <el-radio-group v-model="zoomLevel" size="small">
          <el-radio-button :label="50">50%</el-radio-button>
          <el-radio-button :label="75">75%</el-radio-button>
          <el-radio-button :label="100">100%</el-radio-button>
        </el-radio-group>
      </div>
      <div>
        <el-button @click="handleSave">暂存</el-button>
        <el-button @click="handleLoadDraft">取回暂存</el-button>
        <el-button type="primary" :disabled="hasHardErrors" @click="handleSubmit">提交</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { Close, Loading } from '@element-plus/icons-vue';
import * as XLSX from 'xlsx';

const route = useRoute();
const projectStore = useProjectStore();
const { menuData, reportTemplate } = storeToRefs(projectStore);

const pageTitle = computed(() => {
  const tableId = route.params.id;
  if (!menuData.value) return '数据填报';
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return table.name;
  }
  return '数据填报';
});

const months = ref([
  { key: 'october', label: '10月' }, { key: 'november', label: '11月' }, { key: 'december', label: '12月' },
  { key: 'january', label: '1月' }, { key: 'february', label: '2月' }, { key: 'march', label: '3月' }, { key: 'april', label: '4月' }
]);

const tableData = ref([]);
const errors = ref({});
const explanations = ref({});
const isErrorPanelVisible = ref(false);
const panelWidth = ref(240);
const editingCell = ref(null);
const zoomLevel = ref(100);

const baseColumnWidths = { name: 250, unit: 100, totalPlan: 120, totalSamePeriod: 120, diffRate: 100, monthPlan: 110, monthSamePeriod: 110 };
const scaledColumnWidths = computed(() => { const scale = zoomLevel.value / 100; const out = {}; for (const k in baseColumnWidths) out[k] = baseColumnWidths[k] * scale; return out; });
const zoomStyle = computed(() => { const baseFontSize = 12, basePadding = 5, scale = zoomLevel.value / 100, fontScale = (1 + scale) / 1.8; return { '--table-font-size': `${baseFontSize * fontScale}px`, '--table-cell-vertical-padding': `${basePadding * scale}px` }; });

const getRowById = (id) => tableData.value.find(r => r.id === id);
const validateCell = (row, monthKey, field) => { const key = `${row.id}-${monthKey}-${field}`; const value = row.monthlyData[monthKey][field]; if (isNaN(Number(value)) || String(value).trim() === '') errors.value[key] = { type: 'A', message: '必须输入有效的数字值' }; else delete errors.value[key]; };

const updateAllCalculations = () => {
  if (tableData.value.length === 0) return;
  for (let i = 0; i < 5; i++) {
    tableData.value.forEach(row => {
      if (row.type === 'calculated' && row.formula) {
        months.value.forEach(month => {
          const planReplaced = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => getRowById(parseInt(p1))?.monthlyData[month.key].plan || 0);
          try { row.monthlyData[month.key].plan = parseFloat(new Function(`return ${planReplaced}`)().toFixed(2)); } catch {}
          const samePeriodReplaced = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => getRowById(parseInt(p1))?.monthlyData[month.key].samePeriod || 0);
          try { row.monthlyData[month.key].samePeriod = parseFloat(new Function(`return ${samePeriodReplaced}`)().toFixed(2)); } catch {}
        });
      }
    });
  }
  tableData.value.forEach(row => {
    row.totals.plan = months.value.reduce((acc, month) => acc + Number(row.monthlyData[month.key].plan || 0), 0);
    row.totals.samePeriod = months.value.reduce((acc, month) => acc + Number(row.monthlyData[month.key].samePeriod || 0), 0);
  });
};

const initialValidation = () => { tableData.value.forEach(row => { if (row.type === 'basic') months.value.forEach(month => validateCell(row, month.key, 'plan')); }); };

const initializeTableData = () => {
  errors.value = {};
  explanations.value = {};
  isErrorPanelVisible.value = false;
  tableData.value = (reportTemplate.value || []).map(item => {
    const monthlyData = {};
    months.value.forEach(month => { monthlyData[month.key] = { plan: 0, samePeriod: 0 }; });
    return { ...item, monthlyData, totals: { plan: 0, samePeriod: 0 } };
  });
  updateAllCalculations();
  initialValidation();
};

watch(reportTemplate, (newTemplate) => { if (newTemplate && newTemplate.length > 0) initializeTableData(); else tableData.value = []; }, { deep: true, immediate: true });

const isEditing = (rowId, monthKey) => editingCell.value === `${rowId}-${monthKey}`;
const startEdit = (row, monthKey) => { if (row.type !== 'calculated') editingCell.value = `${row.id}-${monthKey}`; };
const finishEdit = (row, monthKey) => { editingCell.value = null; validateCell(row, monthKey, 'plan'); updateAllCalculations(); };

const closeErrorPanel = () => { isErrorPanelVisible.value = false; };
const startResize = (event) => {
  event.preventDefault();
  const startX = event.clientX, startWidth = panelWidth.value;
  const doDrag = (e) => { const newWidth = startWidth - (e.clientX - startX); if (newWidth > 200 && newWidth < 600) panelWidth.value = newWidth; };
  const stopDrag = () => { document.documentElement.removeEventListener('mousemove', doDrag, false); document.documentElement.removeEventListener('mouseup', stopDrag, false); };
  document.documentElement.addEventListener('mousemove', doDrag, false);
  document.documentElement.addEventListener('mouseup', stopDrag, false);
};
const getCellClass = ({ row, column }) => {
  const prop = column.property;
  const isMonthlyPlan = prop?.includes('monthlyData') && prop?.includes('.plan');
  const isMonthlySamePeriod = prop?.includes('.samePeriod');
  const isTotalColumn = ['本期计划', '同期完成', '差异率'].includes(column.label);
  if ((row.type === 'calculated' && isMonthlyPlan) || isMonthlySamePeriod || isTotalColumn) return 'is-calculated';
  if (prop) {
    const monthKey = months.value.find(m => prop.startsWith(`monthlyData.${m.key}`))?.key;
    if (monthKey) {
      const key = `${row.id}-${monthKey}-plan`;
      const error = errors.value[key];
      if (error) { if (error.type === 'A') return 'is-error'; if (error.type === 'B') return 'is-warning'; }
    }
  }
  return '';
};
const calculateDifferenceRate = (row) => { if (row.totals.samePeriod === 0) return 'N/A'; const rate = ((row.totals.plan - row.totals.samePeriod) / row.totals.samePeriod) * 100; return `${rate.toFixed(2)}%`; };
const getDifferenceRateClass = (row) => row.totals.plan < row.totals.samePeriod ? 'text-danger' : 'text-success';
const hasHardErrors = computed(() => Object.values(errors.value).some(e => e && e.type === 'A'));
const softErrors = computed(() => Object.entries(errors.value).filter(([, value]) => value && value.type === 'B'));
const getErrorLabel = (key) => { const [rowId, monthKey] = key.split('-'); const row = getRowById(parseInt(rowId)); const month = months.value.find(m => m.key === monthKey); return `${row?.name} - ${month?.label}`; };
const setStatus = (status) => { const key = `status-${route.params.id}`; localStorage.setItem(key, status); window.dispatchEvent(new Event('storage')); };

const handleSave = () => {
  setStatus('saved');
  const draftData = {};
  tableData.value.forEach(row => { if (row.type === 'basic') { draftData[row.id] = {}; months.value.forEach(month => { draftData[row.id][month.key] = row.monthlyData[month.key].plan; }); } });
  const dataKey = `data-draft-${route.params.id}`;
  localStorage.setItem(dataKey, JSON.stringify(draftData));
  ElMessage.success('草稿已暂存');
};

const handleLoadDraft = () => {
  const dataKey = `data-draft-${route.params.id}`;
  const savedData = localStorage.getItem(dataKey);
  if (!savedData) { ElMessage.warning('没有找到可用的暂存数据'); return; }
  const draftData = JSON.parse(savedData);
  tableData.value.forEach(row => { if (draftData[row.id]) { months.value.forEach(month => { if (draftData[row.id][month.key] !== undefined) { row.monthlyData[month.key].plan = draftData[row.id][month.key]; } }); } });
  updateAllCalculations();
  ElMessage.success('暂存数据已成功拉取');
};

const handleSubmit = () => {
  if (hasHardErrors.value) { ElMessage.error('提交失败，请修正所有红色错误后再试。'); return; }
  const softErrorEntries = softErrors.value;
  if (softErrorEntries.length > 0) {
    if (!isErrorPanelVisible.value) { isErrorPanelVisible.value = true; ElMessage.warning('检测到软性错误，请在右侧说明栏中填写原因后再次提交。'); return; }
    const allExplained = softErrorEntries.every(([key]) => explanations.value[key]?.trim());
    if (!allExplained) { ElMessage.warning('您有未说明的软性错误，请填写所有说明后再提交。'); return; }
  }
  setStatus('submitted');
  ElMessage.success('提交成功！');
  isErrorPanelVisible.value = false;
};

const handleExport = () => {
  const header = ['指标名称', '计量单位', '本期计划', '同期完成', '差异率', ...months.value.flatMap(m => [`${m.label}-计划`, `${m.label}-同期`])];
  const data = [header];
  const rowIdToRowIndex = new Map();
  tableData.value.forEach((row, index) => { rowIdToRowIndex.set(row.id, index + 2); });
  tableData.value.forEach((row, rowIndex) => {
    const r = rowIndex + 2;
    const rowData = [];
    rowData[0] = row.name;
    rowData[1] = row.unit;
    if (row.type === 'calculated' && row.formula) {
      const excelFormulaC = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => `C${rowIdToRowIndex.get(parseInt(p1))}`);
      rowData[2] = { t: 'n', f: excelFormulaC };
      const excelFormulaD = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => `D${rowIdToRowIndex.get(parseInt(p1))}`);
      rowData[3] = { t: 'n', f: excelFormulaD };
    } else {
      const monthPlanCells = months.value.map((m, i) => XLSX.utils.encode_cell({c: 5 + i * 2, r: r - 1})).join(',');
      rowData[2] = { t: 'n', f: `SUM(${monthPlanCells})` };
      const monthSamePeriodCells = months.value.map((m, i) => XLSX.utils.encode_cell({c: 6 + i * 2, r: r - 1})).join(',');
      rowData[3] = { t: 'n', f: `SUM(${monthSamePeriodCells})` };
    }
    rowData[4] = { t: 'n', f: `IF(D${r}=0, 0, (C${r}-D${r})/D${r})`, z: '0.00%' };
    months.value.forEach((month, monthIndex) => {
      const planCol = 5 + monthIndex * 2;
      const samePeriodCol = 6 + monthIndex * 2;
      if (row.type === 'calculated' && row.formula) {
        const planFormula = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => `${XLSX.utils.encode_col(planCol)}${rowIdToRowIndex.get(parseInt(p1))}`);
        rowData[planCol] = { t: 'n', f: planFormula };
        const samePeriodFormula = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => `${XLSX.utils.encode_col(samePeriodCol)}${rowIdToRowIndex.get(parseInt(p1))}`);
        rowData[samePeriodCol] = { t: 'n', f: samePeriodFormula };
      } else {
        rowData[planCol] = row.monthlyData[month.key].plan;
        rowData[samePeriodCol] = row.monthlyData[month.key].samePeriod;
      }
    });
    data.push(rowData);
  });
  const worksheet = XLSX.utils.aoa_to_sheet(data);
  data.forEach((rowData, r) => { rowData.forEach((cellData, c) => { if (typeof cellData === 'object' && cellData !== null && cellData.f) { const cellRef = XLSX.utils.encode_cell({r, c}); worksheet[cellRef] = cellData; } }); });
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  XLSX.writeFile(workbook, `${pageTitle.value}.xlsx`);
  ElMessage.success('导出成功！');
};
</script>

<style>
.el-table { border-left: 1px solid #ebeef5; border-top: 1px solid #ebeef5; }
:deep(.el-input__inner) { text-align: center; border: none; padding: 0 2px; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
:deep(.el-input__wrapper) { padding: 0; box-shadow: none !important; }
.el-table th.el-table__cell, .el-table td.el-table__cell { border-right: 1px solid #ebeef5; border-bottom: 1px solid #ebeef5; font-size: var(--table-font-size, 14px); padding: var(--table-cell-vertical-padding, 12px) 0; }
.el-table th.el-table__cell { background-color: #fafafa; }
.is-error .el-input__wrapper, .is-error .cell-content { box-shadow: 0 0 0 1px #f56c6c inset !important; border-radius: 4px; }
.is-warning .el-input__wrapper, .is-warning .cell-content { box-shadow: 0 0 0 1px #e6a23c inset !important; border-radius: 4px; }
.is-calculated .cell-content { background-color: #f0f2f5; background-image: linear-gradient(45deg,#e9ecef 25%,transparent 25%,transparent 50%,#e9ecef 50%,#e9ecef 75%,transparent 75%,transparent); background-size: 12px 12px; color: #909399; cursor: not-allowed; font-style: italic; }
.calculated-indicator { font-weight: bold; }
.loading-indicator, .no-data-message { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; font-size: 16px; color: #606266; }
.loading-indicator .el-icon { margin-bottom: 10px; }
</style>

<style scoped>
.data-entry-container { display: flex; flex-direction: column; height: 100%; padding: 20px; box-sizing: border-box; }
.page-title { flex-shrink: 0; text-align: center; margin: 5px 0; font-size: 18px; }
.content-wrapper { flex-grow: 1; display: flex; overflow: hidden; }
.main-content { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }
.table-controls { display: flex; align-items: center; }
.table-wrapper { flex-grow: 1; overflow: hidden; min-height: 0; }
.error-panel { position: relative; flex-shrink: 0; margin-left: 20px; border: 1px solid #ebeef5; border-radius: 4px; padding: 15px; display: flex; flex-direction: column; }
.resizer { position: absolute; left: -5px; top: 0; height: 100%; width: 10px; cursor: col-resize; z-index: 10; }
.error-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #ebeef5; }
.error-panel-header h4 { margin: 0; }
.close-icon { cursor: pointer; }
.error-list { flex-grow: 1; }
.error-item { margin-bottom: 15px; }
.error-item label { font-weight: bold; font-size: 14px; }
.error-item .error-message { font-size: 12px; color: #909399; margin: 5px 0; }
.footer-actions { flex-shrink: 0; display: flex; justify-content: space-between; align-items: center; padding-top: 20px; }
.cell-content { cursor: pointer; min-height: 20px; padding: 2px 5px; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>
