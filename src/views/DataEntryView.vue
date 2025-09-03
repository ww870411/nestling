<template>
  <div class="data-entry-container">
    <h2 class="page-title">{{ pageTitle }}</h2>
    
    <div class="content-wrapper">
      <div class="main-content">
        <div class="table-wrapper">
          <el-table :data="tableData" :cell-class-name="getCellClass" border style="width: 100%" row-key="id">
            <!-- All table columns -->
            <el-table-column prop="name" label="指标名称" width="250" fixed>
              <template #default="{ row }">
                <div class="cell-content">
                  <span :class="{ 'calculated-indicator': row.type === 'calculated' }">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="计量单位" width="100" fixed>
              <template #default="{ row }">
                <div class="cell-content">{{ row.unit }}</div>
              </template>
            </el-table-column>
            
            <el-table-column label="本期计划" width="120">
              <template #default="{ row }">
                <div class="cell-content">{{ row.totals.plan }}</div>
              </template>
            </el-table-column>
            <el-table-column label="同期完成" width="120">
              <template #default="{ row }">
                <div class="cell-content">{{ row.totals.samePeriod }}</div>
              </template>
            </el-table-column>
            <el-table-column label="差异率" width="100">
              <template #default="{ row }">
                <div class="cell-content">
                  <span :class="getDifferenceRateClass(row)">{{ calculateDifferenceRate(row) }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column v-for="month in months" :key="month.key" :label="month.label">
              <el-table-column label="计划" :prop="`monthlyData.${month.key}.plan`" width="110">
                <template #default="{ row, $index }">
                   <el-tooltip
                    :disabled="!errors[`${row.id}-${month.key}-plan`]?.message"
                    :content="errors[`${row.id}-${month.key}-plan`]?.message"
                    placement="top"
                    effect="dark"
                  >
                    <div @click="startEdit(row, month.key)" class="cell-content">
                      <el-input
                        v-if="isEditing(row.id, month.key)"
                        v-model.number="row.monthlyData[month.key].plan"
                        @blur="finishEdit(row, month.key)"
                        @keyup.enter="finishEdit(row, month.key)"
                      />
                      <span v-else>{{ row.monthlyData[month.key].plan }}</span>
                    </div>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column label="同期" :prop="`monthlyData.${month.key}.samePeriod`" width="110">
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
              <el-input
                v-model="explanations[key]"
                type="textarea"
                :rows="2"
                placeholder="请输入说明..."
              />
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>

    <div class="footer-actions">
      <div>
        <el-button @click="handleExport">导出</el-button>
      </div>
      <div>
        <el-button @click="handleSave">暂存</el-button>
        <el-button type="primary" :disabled="hasHardErrors" @click="handleSubmit">提交</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { reportTemplate } from '../services/reportTemplate.js';
import { menuData } from '../services/menuData.js';
import { Close } from '@element-plus/icons-vue';
import * as XLSX from 'xlsx';

const route = useRoute();

const pageTitle = computed(() => {
  const tableId = route.params.id;
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

// --- Calculation Engine (Simplified & Robust) ---
const getRowById = (id) => tableData.value.find(r => r.id === id);

// --- Editing & Validation ---
const validateCell = (row, monthKey, field) => {
  const key = `${row.id}-${monthKey}-${field}`;
  const value = row.monthlyData[monthKey][field];
  if (isNaN(Number(value)) || String(value).trim() === '') {
    errors.value[key] = { type: 'A', message: '必须输入有效的数字值' };
  } else {
    delete errors.value[key];
  }
};

const updateAllCalculations = () => {
  if (tableData.value.length === 0) return;

  tableData.value.forEach(row => {
    row.totals.plan = months.value.reduce((acc, month) => acc + Number(row.monthlyData[month.key].plan || 0), 0);
    row.totals.samePeriod = months.value.reduce((acc, month) => acc + Number(row.monthlyData[month.key].samePeriod || 0), 0);
  });

  tableData.value.forEach(row => {
    if (row.type === 'calculated' && row.formula) {
      const formula = row.formula;
      const replaced = formula.replace(/VAL\((\d+)\)/g, (match, p1) => {
        return getRowById(parseInt(p1))?.totals.plan || 0;
      });
      try {
        row.totals.plan = parseFloat(new Function(`return ${replaced}`)().toFixed(2));
      } catch (e) {
        console.error('Error evaluating formula:', formula, e);
      }
    }
  });
};

const initialValidation = () => {
  tableData.value.forEach(row => {
    if (row.type === 'basic') {
      months.value.forEach(month => validateCell(row, month.key, 'plan'));
    }
  });
};

const initializeTableData = () => {
  errors.value = {};
  explanations.value = {};
  isErrorPanelVisible.value = false;
  tableData.value = reportTemplate.map(item => {
    const monthlyData = {};
    months.value.forEach(month => {
      monthlyData[month.key] = { plan: 0, samePeriod: 0 };
    });
    return { ...item, monthlyData, totals: { plan: 0, samePeriod: 0 } };
  });
  updateAllCalculations();
  initialValidation();
};

// --- Data Initialization & Reactivity ---
watch(() => route.params.id, (newId) => {
  if (newId) initializeTableData();
}, { immediate: true });

const isEditing = (rowId, monthKey) => editingCell.value === `${rowId}-${monthKey}`;

const startEdit = (row, monthKey) => {
  if (row.type === 'calculated') return;
  editingCell.value = `${row.id}-${monthKey}`;
};

const finishEdit = (row, monthKey) => {
  editingCell.value = null;
  validateCell(row, monthKey, 'plan');
  // Explicitly trigger calculation after an edit is finished.
  updateAllCalculations();
};

// ... (The rest of the file is identical to the last fully-featured version) ...
const closeErrorPanel = () => { isErrorPanelVisible.value = false; };
const startResize = (event) => {
  event.preventDefault();
  const startX = event.clientX;
  const startWidth = panelWidth.value;
  const doDrag = (e) => {
    const newWidth = startWidth - (e.clientX - startX);
    if (newWidth > 200 && newWidth < 600) panelWidth.value = newWidth;
  };
  const stopDrag = () => {
    document.documentElement.removeEventListener('mousemove', doDrag, false);
    document.documentElement.removeEventListener('mouseup', stopDrag, false);
  };
  document.documentElement.addEventListener('mousemove', doDrag, false);
  document.documentElement.addEventListener('mouseup', stopDrag, false);
};
const getCellClass = ({ row, column }) => {
  const prop = column.property;

  // --- Style non-editable cells ---
  const isMonthlyPlan = prop?.includes('monthlyData') && prop?.includes('.plan');
  const isMonthlySamePeriod = prop?.includes('.samePeriod');
  const isTotalColumn = ['本期计划', '同期完成', '差异率'].includes(column.label);

  if ((row.type === 'calculated' && isMonthlyPlan) || isMonthlySamePeriod || isTotalColumn) {
    return 'is-calculated';
  }

  // --- Style error/warning cells ---
  if (prop) {
    const monthKey = months.value.find(m => prop.startsWith(`monthlyData.${m.key}`))?.key;
    if (monthKey) {
      const key = `${row.id}-${monthKey}-plan`;
      const error = errors.value[key];
      if (error) {
        if (error.type === 'A') return 'is-error';
        if (error.type === 'B') return 'is-warning';
      }
    }
  }

  return '';
};
const calculateDifferenceRate = (row) => {
  if (row.totals.samePeriod === 0) return 'N/A';
  const rate = ((row.totals.plan - row.totals.samePeriod) / row.totals.samePeriod) * 100;
  return `${rate.toFixed(2)}%`;
};
const getDifferenceRateClass = (row) => row.totals.plan < row.totals.samePeriod ? 'text-danger' : 'text-success';
const hasHardErrors = computed(() => Object.values(errors.value).some(e => e && e.type === 'A'));
const softErrors = computed(() => Object.entries(errors.value).filter(([, value]) => value && value.type === 'B'));
const getErrorLabel = (key) => {
  const [rowId, monthKey] = key.split('-');
  const row = getRowById(parseInt(rowId));
  const month = months.value.find(m => m.key === monthKey);
  return `${row?.name} - ${month?.label}`;
};
const setStatus = (status) => {
  const key = `status-${route.params.id}`;
  localStorage.setItem(key, status);
  window.dispatchEvent(new Event('storage'));
};
const handleSave = () => {
  setStatus('saved');
  ElMessage.success('草稿已暂存');
};
const handleSubmit = () => {
  if (hasHardErrors.value) {
    ElMessage.error('提交失败，请修正所有红色错误后再试。');
    return;
  }
  const softErrorEntries = softErrors.value;
  if (softErrorEntries.length > 0) {
    if (!isErrorPanelVisible.value) {
      isErrorPanelVisible.value = true;
      ElMessage.warning('检测到软性错误，请在右侧说明栏中填写原因后再次提交。');
      return;
    }
    const allExplained = softErrorEntries.every(([key]) => explanations.value[key]?.trim());
    if (!allExplained) {
      ElMessage.warning('您有未说明的软性错误，请填写所有说明后再提交。');
      return;
    }
  }
  console.log('Explanations:', explanations.value);
  setStatus('submitted');
  ElMessage.success('提交成功！');
  isErrorPanelVisible.value = false;
};
const handleExport = () => {
  const dataToExport = tableData.value.map(row => {
    const flatRow = {
      '指标名称': row.name,
      '计量单位': row.unit,
      '本期计划': row.totals.plan,
      '同期完成': row.totals.samePeriod,
      '差异率': calculateDifferenceRate(row),
    };
    months.value.forEach(month => {
      flatRow[`${month.label}-计划`] = row.monthlyData[month.key].plan;
      flatRow[`${month.label}-同期`] = row.monthlyData[month.key].samePeriod;
    });
    return flatRow;
  });
  const worksheet = XLSX.utils.json_to_sheet(dataToExport);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  XLSX.writeFile(workbook, `${pageTitle.value}.xlsx`);
  ElMessage.success('导出成功！');
};

</script>

<style>
/* General Table Style Enhancement */
.el-table {
  border-left: 1px solid #ebeef5;
  border-top: 1px solid #ebeef5;
}
.el-table th.el-table__cell, .el-table td.el-table__cell {
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}
.el-table th.el-table__cell {
  background-color: #fafafa;
}

/* Error and Warning Styles */
.is-error .el-input__wrapper, .is-error .cell-content { box-shadow: 0 0 0 1px #f56c6c inset !important; border-radius: 4px; }
.is-warning .el-input__wrapper, .is-warning .cell-content { box-shadow: 0 0 0 1px #e6a23c inset !important; border-radius: 4px; }

/* Style for non-editable/calculated cells */
.is-calculated .cell-content {
  background-color: #f0f2f5; /* A slightly darker grey */
  background-image: linear-gradient(
    45deg,
    #e9ecef 25%,
    transparent 25%,
    transparent 50%,
    #e9ecef 50%,
    #e9ecef 75%,
    transparent 75%,
    transparent
  );
  background-size: 12px 12px;
  color: #909399;
  cursor: not-allowed;
  font-style: italic; /* Italicize text to further indicate it's different */
}

.calculated-indicator { font-weight: bold; }
</style>

<style scoped>
.data-entry-container { display: flex; flex-direction: column; height: 100%; padding: 20px; box-sizing: border-box; }
.page-title { flex-shrink: 0; text-align: center; margin-bottom: 20px; }
.content-wrapper { flex-grow: 1; display: flex; overflow: hidden; }
.main-content { flex-grow: 1; display: flex; overflow: hidden; }
.table-wrapper { flex-grow: 1; overflow: auto; }
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
.cell-content { cursor: pointer; min-height: 24px; padding: 5px; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>