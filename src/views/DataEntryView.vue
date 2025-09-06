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
            <template v-for="field in processedFieldConfig" :key="field.id">
              <!-- If it's a group with children -->
              <el-table-column v-if="field.children && field.children.length > 0"
                :label="field.label">
                <el-table-column v-for="childField in field.children" :key="childField.id"
                  :prop="childField.name"
                  :label="childField.label"
                  :width="childField.width * zoomLevel / 100"
                  :fixed="childField.fixed">
                  <template #default="{ row }">
                    <div v-if="getCellState(row, childField, currentTableProperties) === 'WRITABLE'" class="cell-content">
                      <el-input 
                        v-model.number="row.values[childField.id]"
                        @blur="handleInputBlur(row, childField.id)" 
                        @keyup.enter="handleInputBlur(row, childField.id)" />
                    </div>
                    <div v-else class="cell-content">
                      <span :style="getCellStyle(row, childField)">{{ row.values[childField.id] }}</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table-column>

              <!-- If it's a regular, top-level column -->
              <el-table-column v-else
                :prop="field.name" 
                :label="field.label"
                :width="field.width * zoomLevel / 100" 
                :fixed="field.fixed">
                <template #default="{ row }">
                  <div v-if="getCellState(row, field, currentTableProperties) === 'WRITABLE'" class="cell-content">
                    <el-input 
                      v-model.number="row.values[field.id]"
                      @blur="handleInputBlur(row, field.id)" 
                      @keyup.enter="handleInputBlur(row, field.id)" />
                  </div>
                  <div v-else class="cell-content">
                    <span :style="getCellStyle(row, field)">{{ row.values[field.id] }}</span>
                  </div>
                </template>
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
import { getDefaultValidation } from '@/projects/heating_plan_2025-2026/tableRules.js';
import { validationRules } from '@/utils/validator.js';
import { getCellState } from '@/projects/heating_plan_2025-2026/tableRules.js';

// --- Store and Routing ---
const route = useRoute();
const projectStore = useProjectStore();
const { menuData } = storeToRefs(projectStore);

// --- Component State ---
const tableData = ref([]);
const errors = ref({});
const explanations = ref({});
const isErrorPanelVisible = ref(false);
const panelWidth = ref(300);
const zoomLevel = ref(100);

// --- Dynamically load table configuration ---
const currentTableConfig = computed(() => {
  const tableId = route.params.tableId;
  if (!menuData.value || !tableId) return null;
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return table.template;
  }
  return null;
});

const reportTemplate = computed(() => currentTableConfig.value?.reportTemplate || []);
const fieldConfig = computed(() => currentTableConfig.value?.fieldConfig || []);

const currentTableProperties = computed(() => {
  const tableId = route.params.tableId;
  if (!menuData.value || !tableId) return {};
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return table.properties || {};
  }
  return {};
});

const processedFieldConfig = computed(() => {
  if (!fieldConfig.value) return [];

  const result = [];
  const groups = new Map();

  fieldConfig.value.forEach(field => {
    if (field.label.includes('-')) {
      const [groupName, ...childLabelParts] = field.label.split('-');
      const childLabel = childLabelParts.join('-');

      if (!groups.has(groupName)) {
        const newGroup = {
          label: groupName,
          children: [],
          // A group doesn't have a single ID, so we can generate one for the key
          id: `group-${groupName}`, 
        };
        groups.set(groupName, newGroup);
        result.push(newGroup);
      }

      groups.get(groupName).children.push({
        ...field,
        label: childLabel, // Use the child part of the label
      });

    } else {
      result.push(field);
    }
  });

  return result;
});


// --- Computed Properties ---
const pageTitle = computed(() => {
  const tableId = route.params.tableId;
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

const hasHardErrors = computed(() => Object.values(errors.value).some(e => e && e.type === 'A'));
const softErrorsForDisplay = computed(() => Object.entries(errors.value).filter(([, error]) => error.type === 'B'));

// --- Core Logic: Initialization & Formula Engine ---

const initializeTableData = () => {
  if (!reportTemplate.value || !fieldConfig.value) return;

  const data = reportTemplate.value.map(metric => {
    const rowData = {
      metricId: metric.id,
      style: metric.style,
      type: metric.type, // Pass metric type to row
      validation: metric.validation, // Pass personalized validation to row
      samePeriodEditable: metric.samePeriodEditable, // Pass editable flag to row
      requiredProperties: metric.requiredProperties, // Pass required properties to row
      values: {},
    };

    fieldConfig.value.forEach(field => {
      if (field.name === 'name') {
        rowData.values[field.id] = metric.name;
      } else if (field.name === 'unit') {
        rowData.values[field.id] = metric.unit;
      } else if (field.type === 'basic') {
        rowData.values[field.id] = 0; // Default value for inputs
      }
    });
    return rowData;
  });

  tableData.value = data;
  calculateAll();
};

const calculateAll = () => {
  if (tableData.value.length === 0) return;

  const getRowByMetricId = (metricId) => tableData.value.find(r => r.metricId === metricId);

  // --- 行内计算 (Row-level formulas) ---
  const rowCalculatedFields = reportTemplate.value.filter(f => f.type === 'calculated' && f.formula);
  rowCalculatedFields.forEach(field => {
    const targetRow = getRowByMetricId(field.id);
    if (!targetRow) return;

    const valResolver = (metricId) => {
      const sourceRow = getRowByMetricId(metricId);
      // For row-level formulas, we assume they depend on the main input columns.
      // This might need to be more robust if formulas can span across different column types.
      const firstInputCol = fieldConfig.value.find(fc => fc.component === 'input');
      return sourceRow && firstInputCol ? (sourceRow.values[firstInputCol.id] || 0) : 0;
    };

    try {
      const funcBody = field.formula.replace(/VAL\((\d+)\)/g, (match, id) => `valResolver(${id})`);
      const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
      
      // Apply the result to all writable columns in the calculated row
      fieldConfig.value.forEach(col => {
        if (getCellState(targetRow, col, currentTableProperties) === 'WRITABLE') {
            targetRow.values[col.id] = parseFloat(result.toFixed(2));
        }
      });

    } catch (e) {
      console.error(`Error calculating row formula for metric ${field.id}:`, e);
    }
  });

  // --- 列内计算 (Column-level formulas) ---
  const colCalculatedFields = fieldConfig.value.filter(f => f.type === 'calculated' && f.formula);
  tableData.value.forEach(row => {
    colCalculatedFields.forEach(field => {
      const valResolver = (columnId) => row.values[columnId] || 0;
      try {
        const funcBody = field.formula.replace(/VAL\((\d+)\)/g, (match, id) => `valResolver(${id})`);
        const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
        row.values[field.id] = parseFloat(result.toFixed(2));
      } catch (e) {
        console.error(`Error calculating column formula for field ${field.id} in row ${row.metricId}:`, e);
      }
    });
  });

  runValidation({ level: 'hard' });
};

// --- NEW Validation Logic ---
const runValidation = ({ level = 'hard' } = {}) => {
  const newErrors = {};

  const findFieldByIdentifier = (identifier) => {
    if (typeof identifier === 'number') {
      return fieldConfig.value.find(f => f.id === identifier);
    }
    return fieldConfig.value.find(f => f.name === identifier);
  };

  // Clear previous errors based on validation level
  if (level === 'all') {
    Object.assign(newErrors, errors.value);
  } else {
    Object.entries(errors.value).forEach(([key, err]) => {
      if (err.type !== 'A') newErrors[key] = err; // Keep soft errors
    });
  }

  tableData.value.forEach(row => {
    const defaultValidation = getDefaultValidation(row.type);
    const finalValidation = {
      hard: row.validation?.hard ?? defaultValidation.hard,
      soft: row.validation?.soft ?? defaultValidation.soft,
    };

    // Hard Validations
    if (finalValidation.hard) {
      fieldConfig.value.forEach(field => {
        if (field.type !== 'basic' || field.component !== 'input') return;
        
        const value = row.values[field.id];
        const key = `${row.metricId}-${field.id}`;
        let hasError = false;
        finalValidation.hard.forEach(ruleDef => {
          const ruleFunc = validationRules[ruleDef.rule];
          if (ruleFunc && !ruleFunc(value)) {
            newErrors[key] = { type: 'A', message: ruleDef.message };
            hasError = true;
          }
        });
        if (!hasError && newErrors[key]?.type === 'A') {
          delete newErrors[key];
        }
      });
    }

    // Soft Validations (only run on 'all' level)
    if (level === 'all' && finalValidation.soft) {
      finalValidation.soft.forEach((ruleDef, index) => {
        const key = `${row.metricId}-soft-${index}`;
        let hasError = false;
        if (ruleDef.rule === 'comparison') {
          const fieldA = findFieldByIdentifier(ruleDef.fieldA);
          const fieldB = findFieldByIdentifier(ruleDef.fieldB);
          if (!fieldA || !fieldB) return;

          const valueA = row.values[fieldA.id];
          const valueB = row.values[fieldB.id];

          const ruleFunc = validationRules[ruleDef.rule];
          if (ruleFunc && !ruleFunc(valueA, ruleDef.operator, valueB)) {
            newErrors[key] = { type: 'B', message: ruleDef.message };
            hasError = true;
          }
        }
        if (!hasError && newErrors[key]?.type === 'B') {
          delete newErrors[key];
        }
      });
    }
  });

  errors.value = newErrors;
  if (level === 'all' && softErrorsForDisplay.value.length > 0) {
    isErrorPanelVisible.value = true;
  }
};


// --- Watchers ---
watch(reportTemplate, initializeTableData, { deep: true, immediate: true });

watch(() => route.params.tableId, () => {
  initializeTableData();
}, { immediate: true });

const handleInputBlur = (row, fieldId) => {
  calculateAll();
};

// --- UI Event Handlers ---

const startResize = (event) => {
  event.preventDefault();
  const startX = event.clientX, startWidth = panelWidth.value;
  const doDrag = (e) => { const newWidth = startWidth - (e.clientX - startX); if (newWidth > 200 && newWidth < 600) panelWidth.value = newWidth; };
  const stopDrag = () => { document.documentElement.removeEventListener('mousemove', doDrag, false); document.documentElement.removeEventListener('mouseup', stopDrag, false); };
  document.documentElement.addEventListener('mousemove', doDrag, false);
  document.documentElement.addEventListener('mouseup', stopDrag, false);
};

// --- Display & Class Logic ---

const getCellStyle = (row, field) => {
  const state = getCellState(row, field, currentTableProperties);

  // 仅在数值列应用加粗样式
  const isValueColumn = field.component !== 'label'; 

  if (isValueColumn && (state === 'READONLY_CALCULATED' || row.type === 'calculated')) {
    return { ...row.style, fontWeight: 'bold' };
  }
  
  return row.style;
};

const getCellClass = ({ row, column }) => {
  // Search in the original flat config, as it's simpler and contains all fields.
  const field = fieldConfig.value.find(f => f.name === column.property);
  if (!field) return '';

  const key = `${row.metricId}-${field.id}`;
  if (errors.value[key]?.type === 'A') {
    return 'is-error';
  }

  if (getCellState(row, field, currentTableProperties) !== 'WRITABLE') {
    return 'is-readonly-shadow';
  }
  
  return '';
};

const getErrorLabel = (key) => {
    const parts = key.split('-');
    const metricId = parseInt(parts[0]);
    const fieldId = parseInt(parts[1]);

    const row = tableData.value.find(r => r.metricId === metricId);
    
    if (!row) return '未知错误';

    if (parts[1] === 'soft') {
        return `${row.values[1001]} (汇总)`; // 1001 is the ID for 'name'
    }

    const field = fieldConfig.value.find(f => f.id === fieldId);
    if (!field) return '未知错误';
    
    return `${row.values[1001]} - ${field.label}`;
};

// --- Actions (Save, Load, Submit, Export) ---
const handleSave = () => {
  const draftData = {};
  tableData.value.forEach(row => {
    if (row.type !== 'basic') return;
    draftData[row.metricId] = {};
    fieldConfig.value.forEach(field => {
      if (field.component === 'input') {
        draftData[row.metricId][field.id] = row.values[field.id];
      }
    });
  });
  localStorage.setItem(`data-draft-${route.params.tableId}`, JSON.stringify(draftData));
  
  // Set status for dashboard
  localStorage.setItem(`status-${route.params.tableId}`, 'saved');

  ElMessage.success('草稿已暂存');
};

const handleLoadDraft = () => {
  const savedData = localStorage.getItem(`data-draft-${route.params.tableId}`);
  if (!savedData) {
    ElMessage.warning('没有找到可用的暂存数据');
    return;
  }
  const draftData = JSON.parse(savedData);
  tableData.value.forEach(row => {
    if (draftData[row.metricId]) {
      Object.keys(draftData[row.metricId]).forEach(fieldId => {
        row.values[fieldId] = draftData[row.metricId][fieldId];
      });
    }
  });
  calculateAll();
  ElMessage.success('暂存数据已成功拉取');
};

const handleSubmit = () => {
  runValidation({ level: 'all' });
  if (hasHardErrors.value) {
    ElMessage.error('提交失败，请修正所有红色错误后再试。');
    return;
  }
  
  if (softErrorsForDisplay.value.length > 0) {
    isErrorPanelVisible.value = true;
    const allExplained = softErrorsForDisplay.value.every(([key]) => explanations.value[key]?.trim());
    if (!allExplained) {
        ElMessage.warning('检测到软性错误/警告，请填写所有说明后再提交。');
        return;
    }
  }

  // Set status and submission time for dashboard
  localStorage.setItem(`status-${route.params.tableId}`, 'submitted');
  localStorage.setItem(`submittedAt-${route.params.tableId}`, new Date().toISOString());

  ElMessage.success('提交成功！');
  isErrorPanelVisible.value = false;
};

const handleExport = () => {
  const header = fieldConfig.value.map(f => f.label);
  const data = [header];

  const metricIdToRowIndex = new Map();
  tableData.value.forEach((row, index) => {
    metricIdToRowIndex.set(row.metricId, index + 1); // 0-based index for worksheet
  });

  const fieldIdToColIndex = new Map();
  fieldConfig.value.forEach((field, index) => {
    fieldIdToColIndex.set(field.id, index);
  });

  tableData.value.forEach(row => {
    const rowData = fieldConfig.value.map(field => row.values[field.id] ?? '');
    data.push(rowData);
  });

  const worksheet = XLSX.utils.aoa_to_sheet(data);

  // Re-add formulas
  tableData.value.forEach((row, rowIndex) => {
    const r = rowIndex + 1; // 1-based for cell address
    const metricDef = reportTemplate.value.find(m => m.id === row.metricId);

    // Handle row-level formulas (e.g., VAL(8)+VAL(9))
    if (metricDef && metricDef.type === 'calculated' && metricDef.formula) {
      fieldConfig.value.forEach((field, colIndex) => {
        if (field.component !== 'input') return; // Apply formula only to data columns
        const c = colIndex;
        const excelFormula = metricDef.formula.replace(/VAL\((\d+)\)/g, (match, id) => {
          const sourceRowIndex = metricIdToRowIndex.get(parseInt(id));
          return XLSX.utils.encode_cell({ r: sourceRowIndex, c });
        });
        worksheet[XLSX.utils.encode_cell({ r, c })] = { t: 'n', f: excelFormula };
      });
    }

    // Handle column-level formulas (e.g., totals)
    fieldConfig.value.forEach((field, colIndex) => {
      if (field.type === 'calculated' && field.formula) {
        const c = colIndex;
        const excelFormula = field.formula.replace(/VAL\((\d+)\)/g, (match, id) => {
          const sourceColIndex = fieldIdToColIndex.get(parseInt(id));
          return XLSX.utils.encode_cell({ r, c: sourceColIndex });
        });
        worksheet[XLSX.utils.encode_cell({ r, c })] = { t: 'n', f: excelFormula };
        // Add number formatting for percentage
        if (field.name === 'totals.diffRate') {
          worksheet[XLSX.utils.encode_cell({ r, c })].z = '0.00%';
        }
      }
    });
  });

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, pageTitle.value || 'Sheet1');
  XLSX.writeFile(workbook, `${pageTitle.value}.xlsx`);
  ElMessage.success('导出成功！');
};

</script>

<style>
.el-table { border-left: 1px solid #ebeef5; border-top: 1px solid #ebeef5; }
.el-table .el-input__inner { text-align: center; }
:deep(.el-input__wrapper) { padding: 0; box-shadow: none !important; }
.el-table th.el-table__cell, .el-table td.el-table__cell { border-right: 1px solid #ebeef5; border-bottom: 1px solid #ebeef5; font-size: var(--table-font-size, 14px); padding: var(--table-cell-vertical-padding, 12px) 0; }
.el-table th.el-table__cell { background-color: #fafafa; }
.is-error .cell-content { box-shadow: 0 0 0 1px #f56c6c inset !important; border-radius: 4px; }
.is-warning .el-input__wrapper, .is-warning .cell-content { box-shadow: 0 0 0 1px #e6a23c inset !important; border-radius: 4px; }
.is-readonly-shadow { background-color: #fafafa; box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.05); }
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