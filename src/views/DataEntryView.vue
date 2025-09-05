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
                    :cell-style="{ textAlign: 'center' }" height="100%">
            <template v-for="field in fieldConfig" :key="field.id">
              <!-- Handle simple, fixed columns -->
              <el-table-column v-if="field.component === 'label'" :prop="field.id" :label="field.label"
                               :width="field.width * zoomLevel / 100" :fixed="field.fixed">
                <template #default="{ row }">
                  <div class="cell-content">
                    <span :style="row.style">{{ getValueByPath(row, field.id) }}</span>
                  </div>
                </template>
              </el-table-column>

              <!-- Handle display columns -->
              <el-table-column v-else-if="field.component === 'display'" :label="field.label"
                               :width="field.width * zoomLevel / 100">
                <template #default="{ row }">
                  <div class="cell-content">
                    <span :class="getDifferenceRateClass(row, field.id)">{{ getDisplayValue(row, field) }}</span>
                  </div>
                </template>
              </el-table-column>

              <!-- Handle grouped columns (monthly data) -->
              <el-table-column v-else-if="field.component === 'group'" :label="field.label">
                <el-table-column v-for="month in field.months" :key="month.key" :label="month.label">
                  <el-table-column v-for="subCol in field.subColumns" :key="subCol.id" :label="subCol.label"
                                   :prop="`${field.id}.${month.key}.${subCol.id}`"
                                   :width="subCol.width * zoomLevel / 100">
                    <template #default="{ row }">
                      <el-tooltip :content="errors[`${row.id}-${month.key}-${subCol.id}`]?.message"
                                  :disabled="!errors[`${row.id}-${month.key}-${subCol.id}`]"
                                  placement="top" effect="dark">
                        <div v-if="subCol.component === 'input' && row.type === 'basic'"
                             @click="startEdit(row, month.key)" class="cell-content">
                          <el-input v-if="isEditing(row.id, month.key)"
                                    v-model.number="row.monthlyData[month.key][subCol.id]"
                                    @blur="finishEdit()" @keyup.enter="finishEdit()" />
                          <span v-else>{{ row.monthlyData[month.key][subCol.id] }}</span>
                        </div>
                        <div v-else class="cell-content">
                          {{ getValueByPath(row, `${field.id}.${month.key}.${subCol.id}`) }}
                        </div>
                      </el-tooltip>
                    </template>
                  </el-table-column>
                </el-table-column>
              </el-table-column>
            </template>
          </el-table>
        </div>

        <div v-if="isErrorPanelVisible && softErrorsForDisplay.length > 0" class="error-panel" :style="{ width: `${panelWidth}px` }">
          <div class="resizer" @mousedown="startResize"></div>
          <div class="error-panel-header">
            <h4>软性错误与警告</h4>
            <el-icon @click="isErrorPanelVisible = false" class="close-icon"><Close /></el-icon>
          </div>
          <el-scrollbar class="error-list">
            <div v-for="([key, error]) in softErrorsForDisplay" :key="key" class="error-item error-item-soft">
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
        <el-button @click="handleExport">导出至本地</el-button>
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
import { getDefaultValidation } from '@/projects/heating_plan_2025-2026/validation.js';

// --- Utilities ---
const getValueByPath = (obj, path) => {
  if (!path) return null;
  return path.split('.').reduce((acc, part) => acc && acc[part], obj);
};

// --- Store and Routing ---
const route = useRoute();
const projectStore = useProjectStore();
const { menuData, reportTemplate, fieldConfig } = storeToRefs(projectStore);

// --- Component State ---
const tableData = ref([]);
const errors = ref({});
const explanations = ref({});
const isErrorPanelVisible = ref(false);
const panelWidth = ref(300);
const editingCell = ref(null);
const zoomLevel = ref(100);

// --- Computed Properties ---
const pageTitle = computed(() => {
  const tableId = route.params.id;
  if (!menuData.value) return '数据填报';
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return table.name;
  }
  return '数据填报';
});

const zoomStyle = computed(() => {
  const scale = zoomLevel.value / 100;
  const fontScale = (1 + scale) / 2;
  return {
    '--table-font-size': `${12 * fontScale}px`,
    '--table-cell-vertical-padding': `${5 * scale}px`,
  };
});

const getRowById = (id) => tableData.value.find(r => r.id === id);

const hasHardErrors = computed(() => Object.values(errors.value).some(e => e && e.type === 'A'));
const softErrorsForDisplay = computed(() => Object.entries(errors.value).filter(([, error]) => error.type === 'B'));

// --- Core Logic: Initialization, Calculation, Validation ---

const initializeTableData = () => {
  if (!reportTemplate.value || !fieldConfig.value) return;

  const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
  const months = monthlyGroup ? monthlyGroup.months : [];

  tableData.value = (reportTemplate.value || []).map(item => {
    const monthlyData = {};
    months.forEach(month => {
      monthlyData[month.key] = { plan: 0, samePeriod: 0 };
    });
    const plainItem = JSON.parse(JSON.stringify(item));
    return { ...plainItem, monthlyData, totals: { plan: 0, samePeriod: 0, diffRate: 0 } };
  });

  updateAllCalculations();
};

const updateAllCalculations = () => {
  if (tableData.value.length === 0) return;

  const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
  const months = monthlyGroup ? monthlyGroup.months : [];

  for (let i = 0; i < 5; i++) {
    tableData.value.forEach(row => {
      if (row.type === 'calculated' && row.formula) {
        months.forEach(month => {
          const formulaEvaluator = (field) => {
            return row.formula.replace(/VAL\((\d+)\)/g, (match, p1) => {
              return getRowById(parseInt(p1))?.monthlyData[month.key]?.[field] || 0;
            });
          };
          try {
            row.monthlyData[month.key].plan = parseFloat(new Function(`return ${formulaEvaluator('plan')}`)().toFixed(2));
            row.monthlyData[month.key].samePeriod = parseFloat(new Function(`return ${formulaEvaluator('samePeriod')}`)().toFixed(2));
          } catch (e) {
            console.error(`Error calculating formula for row ${row.id}, month ${month.key}:`, e);
          }
        });
      }
    });
  }

  tableData.value.forEach(row => {
    row.totals.plan = months.reduce((acc, month) => acc + Number(row.monthlyData[month.key].plan || 0), 0);
    row.totals.samePeriod = months.reduce((acc, month) => acc + Number(row.monthlyData[month.key].samePeriod || 0), 0);
  });

  runHardValidation();
};

const runHardValidation = () => {
  const newErrors = { ...errors.value };
  // Clear existing hard errors
  Object.keys(newErrors).forEach(key => {
    if (newErrors[key].type === 'A') {
      delete newErrors[key];
    }
  });

  const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
  const months = monthlyGroup ? monthlyGroup.months : [];

  tableData.value.forEach(row => {
    const metricValidation = row.validation || {};
    const defaultValidation = getDefaultValidation(row.type);
    const finalValidation = {
        hard: metricValidation.hard !== undefined ? metricValidation.hard : defaultValidation.hard,
        soft: metricValidation.soft !== undefined ? metricValidation.soft : defaultValidation.soft,
    };

    if (row.type === 'basic' && finalValidation.hard) {
      months.forEach(month => {
        const value = row.monthlyData[month.key].plan;
        const key = `${row.id}-${month.key}-plan`;
        for (const rule of finalValidation.hard) {
          let isValid = true;
          if (rule.rule === 'isNumber') {
            isValid = value === null || (String(value).trim() !== '' && !isNaN(Number(value)));
          }
          if (rule.rule === 'notEmpty') {
            isValid = value !== null && String(value).trim() !== '';
          }
          if (!isValid) {
            newErrors[key] = { type: 'A', message: rule.message };
            break;
          }
        }
      });
    }
  });
  errors.value = newErrors;
};

const runSoftValidation = () => {
    const newErrors = { ...errors.value };
    // Clear existing soft errors
    Object.keys(newErrors).forEach(key => {
        if (newErrors[key].type === 'B') {
            delete newErrors[key];
        }
    });

    tableData.value.forEach(row => {
        const metricValidation = row.validation || {};
        const defaultValidation = getDefaultValidation(row.type);
        const finalValidation = {
            hard: metricValidation.hard !== undefined ? metricValidation.hard : defaultValidation.hard,
            soft: metricValidation.soft !== undefined ? metricValidation.soft : defaultValidation.soft,
        };

        if (finalValidation.soft) {
            finalValidation.soft.forEach((rule, index) => {
                if (rule.rule === 'comparison') {
                    const valA = getValueByPath(row, rule.fieldA);
                    const valB = getValueByPath(row, rule.fieldB);
                    let isSoftValid = true;
                    if (typeof valA === 'number' && typeof valB === 'number') {
                        switch (rule.operator) {
                            case '<=': isSoftValid = valA <= valB; break;
                            case '>=': isSoftValid = valA >= valB; break;
                            case '<': isSoftValid = valA < valB; break;
                            case '>': isSoftValid = valA > valB; break;
                            case '==': isSoftValid = valA == valB; break;
                        }
                    }
                    const key = `${row.id}-soft-${index}`;
                    if (!isSoftValid) {
                        newErrors[key] = { type: 'B', message: rule.message };
                    }
                }
            });
        }
    });
    errors.value = newErrors;
    if (softErrorsForDisplay.value.length > 0) {
        isErrorPanelVisible.value = true;
    }
};

// --- Watchers ---
watch(reportTemplate, initializeTableData, { deep: true, immediate: true });

// --- UI Event Handlers ---
const isEditing = (rowId, monthKey) => editingCell.value === `${rowId}-${monthKey}`;
const startEdit = (row, monthKey) => {
  if (row.type !== 'calculated') {
    editingCell.value = `${row.id}-${monthKey}`;
  }
};
const finishEdit = () => {
  editingCell.value = null;
  updateAllCalculations();
};

const startResize = (event) => {
  event.preventDefault();
  const startX = event.clientX, startWidth = panelWidth.value;
  const doDrag = (e) => { const newWidth = startWidth - (e.clientX - startX); if (newWidth > 200 && newWidth < 600) panelWidth.value = newWidth; };
  const stopDrag = () => { document.documentElement.removeEventListener('mousemove', doDrag, false); document.documentElement.removeEventListener('mouseup', stopDrag, false); };
  document.documentElement.addEventListener('mousemove', doDrag, false);
  document.documentElement.addEventListener('mouseup', stopDrag, false);
};

// --- Display & Class Logic ---
const getDisplayValue = (row, field) => {
  if (field.id === 'totals.diffRate') {
    if (row.totals.samePeriod === 0) return 'N/A';
    const rate = ((row.totals.plan - row.totals.samePeriod) / row.totals.samePeriod) * 100;
    return `${rate.toFixed(2)}%`;
  }
  return getValueByPath(row, field.id);
};

const getDifferenceRateClass = (row, fieldId) => {
  if (fieldId === 'totals.diffRate') {
    return row.totals.plan < row.totals.samePeriod ? 'text-danger' : 'text-success';
  }
  return '';
};

const getCellClass = ({ row, column }) => {
  const prop = column.property;
  if (!prop) return;

  const parts = prop.split('.');
  if (parts[0] === 'monthlyData') {
    const key = `${row.id}-${parts[1]}-${parts[2]}`;
    if (errors.value[key]?.type === 'A') {
      return 'is-error';
    }
  }

  if (row.type === 'calculated') {
    return 'is-calculated';
  }
  return '';
};

const getErrorLabel = (key) => {
    const parts = key.split('-');
    const rowId = parseInt(parts[0]);
    const row = getRowById(rowId);
    if (!row) return '未知错误';

    if (parts[1] === 'soft') {
        return `${row.name} (汇总)`;
    }

    const monthKey = parts[1];
    const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
    const month = monthlyGroup ? monthlyGroup.months.find(m => m.key === monthKey) : null;
    return `${row.name} - ${month?.label || ''}`;
};

// --- Actions (Save, Load, Submit, Export) ---
const handleSave = () => {
  const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
  const months = monthlyGroup ? monthlyGroup.months : [];
  const draftData = {};
  tableData.value.forEach(row => {
    if (row.type === 'basic') {
      draftData[row.id] = {};
      months.forEach(month => {
        draftData[row.id][month.key] = row.monthlyData[month.key].plan;
      });
    }
  });
  localStorage.setItem(`data-draft-${route.params.id}`, JSON.stringify(draftData));
  ElMessage.success('草稿已暂存');
};

const handleLoadDraft = () => {
  const savedData = localStorage.getItem(`data-draft-${route.params.id}`);
  if (!savedData) {
    ElMessage.warning('没有找到可用的暂存数据');
    return;
  }
  const draftData = JSON.parse(savedData);
  tableData.value.forEach(row => {
    if (draftData[row.id]) {
      const monthlyGroup = fieldConfig.value.find(f => f.component === 'group');
      const months = monthlyGroup ? monthlyGroup.months : [];
      months.forEach(month => {
        if (draftData[row.id][month.key] !== undefined) {
          row.monthlyData[month.key].plan = draftData[row.id][month.key];
        }
      });
    }
  });
  updateAllCalculations();
  ElMessage.success('暂存数据已成功拉取');
};

const handleSubmit = () => {
  runHardValidation();
  if (hasHardErrors.value) {
    ElMessage.error('提交失败，请修正所有红色错误后再试。');
    return;
  }
  
  runSoftValidation();
  if (softErrorsForDisplay.value.length > 0) {
    isErrorPanelVisible.value = true;
    const allExplained = softErrorsForDisplay.value.every(([key]) => explanations.value[key]?.trim());
    if (!allExplained) {
        ElMessage.warning('检测到软性错误/警告，请填写所有说明后再提交。');
        return;
    }
  }

  ElMessage.success('提交成功！');
  isErrorPanelVisible.value = false;
};

const handleExport = () => {
  const header = [];
  const columnMapping = [];
  fieldConfig.value.forEach(field => {
    if (field.component === 'group') {
      field.months.forEach(month => {
        field.subColumns.forEach(subCol => {
          header.push(`${month.label}-${subCol.label}`);
          columnMapping.push({ ...subCol, monthKey: month.key, groupId: field.id });
        });
      });
    } else {
      header.push(field.label);
      columnMapping.push(field);
    }
  });

  const data = [header];
  const rowIdToRowIndex = new Map();
  tableData.value.forEach((row, index) => { rowIdToRowIndex.set(row.id, index + 2); });

  tableData.value.forEach((row, rowIndex) => {
    const r = rowIndex + 2;
    const rowData = [];
    columnMapping.forEach((col, colIndex) => {
      if (col.groupId === 'monthlyData') {
        const path = `${col.groupId}.${col.monthKey}.${col.id}`;
        rowData[colIndex] = getValueByPath(row, path);
      } else {
        rowData[colIndex] = getValueByPath(row, col.id);
      }
    });
    data.push(rowData);
  });

  const worksheet = XLSX.utils.aoa_to_sheet(data);

  // Re-add formulas
  tableData.value.forEach((row, rowIndex) => {
      const r = rowIndex + 2;
      if (row.type === 'calculated' && row.formula) {
          columnMapping.forEach((col, colIndex) => {
              if (col.groupId === 'monthlyData') {
                  const excelFormula = row.formula.replace(/VAL\((\d+)\)/g, (m, p1) => {
                      const targetRowIndex = rowIdToRowIndex.get(parseInt(p1));
                      return `${XLSX.utils.encode_col(colIndex)}${targetRowIndex}`;
                  });
                  worksheet[XLSX.utils.encode_cell({r: r-1, c: colIndex})] = { t: 'n', f: excelFormula };
              }
          });
      }
      // Add total formulas
      const planTotalCol = columnMapping.findIndex(c => c.id === 'totals.plan');
      if (planTotalCol !== -1) {
          const monthPlanCells = columnMapping.map((c, i) => ({...c, index: i})).filter(c => c.groupId === 'monthlyData' && c.id === 'plan').map(c => `${XLSX.utils.encode_col(c.index)}${r}`).join(',');
          worksheet[XLSX.utils.encode_cell({r: r-1, c: planTotalCol})] = { t: 'n', f: `SUM(${monthPlanCells})` };
      }
      const samePeriodTotalCol = columnMapping.findIndex(c => c.id === 'totals.samePeriod');
      if (samePeriodTotalCol !== -1) {
          const monthSamePeriodCells = columnMapping.map((c, i) => ({...c, index: i})).filter(c => c.groupId === 'monthlyData' && c.id === 'samePeriod').map(c => `${XLSX.utils.encode_col(c.index)}${r}`).join(',');
          worksheet[XLSX.utils.encode_cell({r: r-1, c: samePeriodTotalCol})] = { t: 'n', f: `SUM(${monthSamePeriodCells})` };
      }
      const diffRateCol = columnMapping.findIndex(c => c.id === 'totals.diffRate');
       if (diffRateCol !== -1) {
          const planTotalRef = XLSX.utils.encode_cell({r: r-1, c: planTotalCol});
          const samePeriodTotalRef = XLSX.utils.encode_cell({r: r-1, c: samePeriodTotalCol});
          worksheet[XLSX.utils.encode_cell({r: r-1, c: diffRateCol})] = { t: 'n', f: `IF(${samePeriodTotalRef}=0, "N/A", (${planTotalRef}-${samePeriodTotalRef})/${samePeriodTotalRef})`, z: '0.00%' };
      }
  });

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
.is-error .cell-content { box-shadow: 0 0 0 1px #f56c6c inset !important; border-radius: 4px; }
.is-warning .el-input__wrapper, .is-warning .cell-content { box-shadow: 0 0 0 1px #e6a23c inset !important; border-radius: 4px; }
.is-calculated { background-color: #f0f2f5; color: #909399; cursor: not-allowed; }
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
.error-item-hard { border-left: 3px solid #f56c6c; padding-left: 10px; }
.error-item-soft { border-left: 3px solid #e6a23c; padding-left: 10px; }
.footer-actions { flex-shrink: 0; display: flex; justify-content: space-between; align-items: center; padding-top: 20px; }
.cell-content { cursor: pointer; min-height: 20px; padding: 2px 5px; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>