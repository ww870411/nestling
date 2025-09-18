<template>
  <div class="data-entry-container">
    <div class="title-container">
      <h2 class="page-title">{{ pageTitle }}</h2>
      <template v-if="route.params.tableId !== '0' && route.params.tableId !== '1'">
        <span v-if="lastSubmittedAt" class="submission-time submitted">
          上次提交时间: {{ formatDateTime(lastSubmittedAt) }}
        </span>
        <span v-else class="submission-time not-submitted">
          无提交记录
        </span>
      </template>
    </div>

    <div class="content-wrapper">
      <div class="main-content">
        <div v-if="projectStore.isLoading || isLoading" class="loading-indicator">
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
                    <div v-if="getCellState(row, childField, currentTableConfig, childToParentsMap.value, forcedParentMap.value) === 'WRITABLE'" class="cell-content">
                      <FormattedInput 
                        v-model="row.values[childField.id]"
                        :format-options="getFormatOptions(row, childField)"
                        @blur="handleInputBlur(row, childField.id)" 
                        @keyup.enter="handleInputBlur(row, childField.id)" />
                    </div>
                    <div v-else class="cell-content">
                      <span :style="getCellStyle(row, childField)">{{ getFormattedValue(row, childField) }}</span>
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
                  <div v-if="getCellState(row, field, currentTableConfig, childToParentsMap.value, forcedParentMap.value) === 'WRITABLE'" class="cell-content">
                    <FormattedInput 
                      v-model="row.values[field.id]"
                      :format-options="getFormatOptions(row, field)"
                      @blur="handleInputBlur(row, field.id)" 
                      @keyup.enter="handleInputBlur(row, field.id)" />
                  </div>
                  <div v-else class="cell-content">
                    <span :style="getCellStyle(row, field)">{{ getFormattedValue(row, field) }}</span>
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
        <el-button @click="handleShowExplanations">解释说明</el-button>
      </div>
      <div class="table-controls">
        <label style="margin-right: 10px; font-size: 14px; color: #606266;">表格缩放:</label>
        <el-radio-group v-model="zoomLevel" size="small">
          <el-radio-button :label="60">60%</el-radio-button>
          <el-radio-button :label="75">75%</el-radio-button>
          <el-radio-button :label="100">100%</el-radio-button>
        </el-radio-group>
      </div>
      <div>
        <el-button v-if="currentTableActions.save" @click="handleSave">{{ hasLocalDraft ? '更新暂存' : '暂存' }}</el-button>
        <el-button v-if="currentTableActions.save" @click="handleLoadDraft">取回暂存数据</el-button>
        <el-button @click="handleLoadFromServer" :icon="Download">加载已提交数据</el-button>
        <el-button v-if="currentTableActions.submit" type="primary" :disabled="hasHardErrors" @click="handleSubmit">提交</el-button>
      </div>
    </div>
  </div>

  <!-- 解释说明展示对话框 -->
  <el-dialog v-model="isExplanationsDialogVisible" title="编辑解释说明" width="60%">
    <el-table :data="submittedExplanations" border style="width: 100%">
      <el-table-column prop="label" label="指标位置" width="220"></el-table-column>
      <el-table-column prop="message" label="错误原因" width="200"></el-table-column>
      <el-table-column label="说明内容">
        <template #default="{ row }">
          <el-input v-model="row.content" type="textarea" :rows="2" :disabled="isExplanationsReadOnly" />
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="isExplanationsDialogVisible = false">取消</el-button>
        <el-button v-if="!isExplanationsReadOnly" type="primary" @click="handleUpdateExplanations">修改并提交</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { Close, Loading, Download } from '@element-plus/icons-vue'; // Import Download icon
import * as XLSX from 'xlsx';
import { validationSchemes, getCellState } from '@/projects/heating_plan_2025-2026/tableRules.js';
import { validationRules } from '@/utils/validator.js'; // Import the whole rules object
import { formatValue, formatDateTime, getBeijingISODateString } from '@/utils/formatter.js';
import FormattedInput from '@/components/FormattedInput.vue';

import { useAuthStore } from '@/stores/authStore';

// --- Store and Routing ---
const route = useRoute();
const projectStore = useProjectStore();
const authStore = useAuthStore(); // Get auth store

const buildUserHeaders = () => {
  const username = authStore.user?.username;
  return username ? { 'X-User-Name': username } : {};
};

const { menuData } = storeToRefs(projectStore);

const isGodUser = computed(() => authStore.user?.globalRole === 'god');

// --- Component State ---
const tableData = ref([]);
const errors = ref({});
const explanations = ref({});
const isErrorPanelVisible = ref(false);
const panelWidth = ref(300);
const zoomLevel = ref(100);
const isLoading = ref(false);
const hasLocalDraft = ref(false);
const lastSubmittedAt = ref(null);

const localDraftKey = computed(() => `data-draft-${route.params.tableId}`);

const checkLocalDraft = () => {
  const draft = localStorage.getItem(localDraftKey.value);
  hasLocalDraft.value = !!draft;
};

// --- Explanations Feature State ---
const isExplanationsDialogVisible = ref(false);
const submittedExplanations = ref([]);
const isExplanationsReadOnly = ref(false);

// --- Dynamically load table configuration ---
const currentTableConfig = computed(() => {
  const tableId = route.params.tableId;
  if (!menuData.value || !tableId) return null;
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return table; // Return the whole table object
  }
  return null;
});

const reportTemplate = computed(() => currentTableConfig.value?.template?.reportTemplate || []);
const fieldConfig = computed(() => currentTableConfig.value?.template?.fieldConfig || []);

const currentTableProperties = computed(() => {
  return currentTableConfig.value?.properties || {};
});

const currentTableActions = computed(() => {
  const defaults = { submit: true, save: true };
  const configActions = currentTableConfig.value?.actions;
  return { ...defaults, ...configActions };
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

const globalDisplayFormat = computed(() => currentTableConfig.value?.template?.globalDisplayFormat || null);

const getFormatOptions = (row, field) => {
  const fieldFormat = field.displayFormat;
  const metric = reportTemplate.value.find(m => m.id === row.metricId);
  const metricFormat = metric?.displayFormat;
  const globalFormat = globalDisplayFormat.value;
  // Return the most specific format found, or a default for numeric inputs.
  return fieldFormat || metricFormat || globalFormat || { type: 'decimal', places: 2 };
};

const getFormattedValue = (row, field) => {
  const value = row.values[field.id];
  if (field.component === 'label') {
      return value;
  }
  
  const formatToApply = getFormatOptions(row, field);

  // Automatically enable thousand separators for numeric display formats.
  if (formatToApply && (formatToApply.type === 'integer' || formatToApply.type === 'decimal')) {
    const optionsWithSeparator = { ...formatToApply, thousandSeparator: true };
    return formatValue(value, optionsWithSeparator);
  }

  return formatValue(value, formatToApply);
};


// --- Computed Properties ---
const pageTitle = computed(() => {
  const tableId = route.params.tableId;
  if (!menuData.value) return '数据填报';
  for (const group of menuData.value) {
    const table = group.tables.find(t => t.id === tableId);
    if (table) return `${table.id} ${table.name.replace(/^\d+\s*/, '')}`;
  }
  return '数据填报';
});

const zoomStyle = computed(() => {
  const scale = zoomLevel.value / 100;
  const baseFontSize = 14; // Element Plus 默认字号
  const baseCellPadding = 12;
  const baseInputHeight = 32;
  const baseInputPaddingX = 4;

  const fontSize = baseFontSize * scale;
  const inputHeight = baseInputHeight * scale;
  const inputPaddingX = baseInputPaddingX * scale;
  return {
    '--table-font-size': `${fontSize}px`,
    '--table-cell-vertical-padding': `${baseCellPadding * scale}px`,
    '--table-input-height': `${inputHeight}px`,
    '--table-input-horizontal-padding': `${inputPaddingX}px`,
    '--el-font-size-base': `${fontSize}px`,
    '--el-input-height': `${inputHeight}px`,
    '--el-input-font-size': `${fontSize}px`,
    '--el-input-padding-horizontal': `${inputPaddingX}px`,
    fontSize: `${fontSize}px`,
    lineHeight: `${inputHeight}px`,
  };
});

const childToParentsMap = computed(() => {
  const map = new Map();
  if (!reportTemplate.value) return map;

  const calculatedMetrics = reportTemplate.value.filter(m => m.type === 'calculated' && m.formula);

  calculatedMetrics.forEach(parentMetric => {
    const childIds = Array.from(parentMetric.formula.matchAll(/VAL\((\d+)\)/g)).map(m => Number(m[1]));
    childIds.forEach(childId => {
      if (!map.has(childId)) {
        map.set(childId, []);
      }
      map.get(childId).push(parentMetric.id);
    });
  });

  return map;
});

const forcedParentMap = computed(() => {
  const set = new Set();
  tableData.value.filter(r => r.isForced && r.type === 'calculated').forEach(r => set.add(r.metricId));
  return set;
});

const hasHardErrors = computed(() => Object.values(errors.value).some(e => e && (e.type === 'A' || e.type === 'C')));
const softErrorsForDisplay = computed(() => Object.entries(errors.value).filter(([, error]) => error.type === 'B'));

// --- Core Logic: Initialization & Formula Engine ---

const initializeTableData = async () => {
  if (!reportTemplate.value || !fieldConfig.value) return;

  const data = reportTemplate.value.filter(metric => metric.visible !== false).map((metric, index) => {
    const rowData = {
      metricId: metric.id,
      style: metric.style,
      type: metric.type, // Pass metric type to row
      formula: metric.formula, // Pass formula to row for calc validation
      isForced: false, // Flag to prevent calculation override
      validation: metric.validation, // Pass personalized validation to row
      samePeriodEditable: metric.samePeriodEditable, // Pass editable flag to row
      requiredProperties: metric.requiredProperties, // Pass required properties to row
      columnFormulaOverrides: metric.columnFormulaOverrides, // Pass overrides
      aggregationExclusions: currentTableConfig.value?.aggregationExclusions, // Pass aggregation exclusions
      values: {},
      cellIssues: {},
    };

    fieldConfig.value.forEach(field => {
      if (field.id === 1000) { // NEW: Handle metric ID column
        rowData.values[field.id] = index + 1;
      } else if (field.name === 'name') {
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

  const dataLoaded = await _fetchDataFromServer(true);
  if (!dataLoaded) {
    // If no data was loaded from the server, we still need to calculate the blank form.
    calculateAll();
  }
};

/**
 * Core logic to fetch data from the server for the current table.
 * The backend handles aggregation for summary tables.
 * @param {boolean} silent - If true, no success/info messages will be shown.
 */
const _fetchDataFromServer = async (silent = false) => {
  const { projectId, tableId } = route.params;
  if (!tableId || !projectId) {
    if (!silent) ElMessage.error('无法获取当前项目或表格ID。');
    return false;
  }

  isLoading.value = true;
  lastSubmittedAt.value = null; // Reset before fetching
  try {
    const response = await fetch(`/api/project/${projectId}/data/table/${tableId}`, {
      headers: buildUserHeaders()
    });
    if (!response.ok) {
      if (response.status !== 404) {
        throw new Error('Failed to load data from server');
      }
      return false;
    }

    const data = await response.json();
    const payloadToApply = data.submit || data.temp;

    // --- NEW CORE FIX ---
    // Reset and pre-populate the central explanations state from the loaded data.
    // This ensures that subsequent checks in handleSubmit will find the existing explanations.
    explanations.value = {};
    if (payloadToApply && payloadToApply.tableData) {
      payloadToApply.tableData.forEach(row => {
        row.values.forEach(cell => {
          if (cell.explanation && cell.explanation.ruleKey) {
            explanations.value[cell.explanation.ruleKey] = cell.explanation.content;
          }
        });
      });
    }
    // --- END NEW CORE FIX ---

    // Logic for submission time display
    if (data.submit) {
        const submittedBy = data.submit.submittedBy;
        // Per backend logic, 'ww870411' is the god user whose submissions are "invisible"
        const isGodSubmission = submittedBy && submittedBy.username === 'ww870411';

        if (isGodSubmission) {
            lastSubmittedAt.value = null; // Hide time for god user
        } else {
            lastSubmittedAt.value = data.submit.submittedAt; // Show time for normal users
        }
    } else {
        lastSubmittedAt.value = null; // No submission, no time
    }

    if (payloadToApply) {
      _applyPayloadToTable(payloadToApply);
      return true;
    } else {
      if (!silent) ElMessage.info('服务器上没有找到该表格的已提交数据。');
      return false;
    }

  } catch (error) {
    console.error('Error loading data from server:', error);
    if (!silent) ElMessage.error(`从服务器加载数据失败: ${error.message}`);
    return false;
  } finally {
    isLoading.value = false;
  }
};

// --- Load submitted data from server ---
const handleLoadFromServer = async () => {
  _fetchDataFromServer(false);
};

const calculateAll = () => {
  if (tableData.value.length === 0) return;

  const getRowByMetricId = (metricId) => tableData.value.find(r => r.metricId === metricId);

  // --- 列内计算 (Column-level formulas) ---
  const colCalculatedFields = fieldConfig.value.filter(f => ['calculated', 'totals'].includes(f.type) && f.formula);
  tableData.value.forEach(row => {
    const metricDef = reportTemplate.value.find(m => m.id === row.metricId);

    colCalculatedFields.forEach(field => {
      const valResolver = (columnId) => parseFloat(row.values[columnId]) || 0;
      
      let formulaToUse = field.formula;
      if (metricDef?.columnFormulaOverrides?.[field.name]) {
        formulaToUse = metricDef.columnFormulaOverrides[field.name];
      }

      try {
        let result;
        
        if (formulaToUse.startsWith('AVG(')) {
          const ids = formulaToUse.match(/\d+/g).map(Number);
          const values = ids.map(id => valResolver(id));
          if (values.length > 0) {
            const sum = values.reduce((a, b) => a + b, 0);
            result = sum / values.length;
          } else {
            result = 0;
          }
        } else if (formulaToUse.startsWith('LAST_VAL(')) {
          const ids = formulaToUse.match(/\d+/g).map(Number);
          const lastId = ids.length > 0 ? ids[ids.length - 1] : null;
          result = lastId ? valResolver(lastId) : 0;
        } else {
          const funcBody = formulaToUse.replace(/VAL\((\d+)\)/g, (match, id) => `(valResolver(${id}))`);
          result = new Function('valResolver', `return ${funcBody}`)(valResolver);
        }
        row.values[field.id] = parseFloat(result.toFixed(10));
      } catch (e) {
        console.error(`Error calculating column formula for field ${field.id} in row ${row.metricId}:`, e);
      }
    });
  });

  // --- 行内计算 (Row-level formulas) ---
  const rowCalculatedFields = reportTemplate.value.filter(f => f.type === 'calculated' && f.formula);

  const valueColumns = fieldConfig.value.filter(fc => (fc.component === 'input' || fc.component === 'display') && fc.type !== 'diffs');

  const MAX_ITERATIONS = 10; // Safety break for circular dependencies
  let iteration = 0;
  let changedInPass;

  do {
    changedInPass = false;
    iteration++;

    rowCalculatedFields.forEach(metricToCalculate => {
      const targetRow = getRowByMetricId(metricToCalculate.id);
      if (!targetRow) return;

      valueColumns.forEach(col => {
        if (getCellState(targetRow, col, currentTableConfig.value, childToParentsMap.value, forcedParentMap.value) !== 'READONLY_CALCULATED') return;
        // 若该行被标记为强制，仅屏蔽“同期值”列的自动计算，允许“计划值”等继续计算
        if (targetRow.isForced && typeof col.name === 'string' && col.name.endsWith('.samePeriod')) return;

        const valResolver = (sourceMetricId) => {
          const sourceRow = getRowByMetricId(sourceMetricId);
          return sourceRow ? (parseFloat(sourceRow.values[col.id]) || 0) : 0;
        };

        try {
          const funcBody = metricToCalculate.formula.replace(/VAL\((\d+)\)/g, (match, id) => `(valResolver(${id}))`);
          const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
          const newValue = parseFloat(result.toFixed(10));
          
          // Check if the value has changed, also handling NaN cases to prevent infinite loops
          if (targetRow.values[col.id] !== newValue && !(isNaN(targetRow.values[col.id]) && isNaN(newValue))) {
            targetRow.values[col.id] = newValue;
            changedInPass = true;
          }
        } catch (e) {
          if (!isNaN(targetRow.values[col.id])) {
             targetRow.values[col.id] = NaN;
             changedInPass = true;
          }
        }
      });
    });

  } while (changedInPass && iteration < MAX_ITERATIONS);

  // 行级计算完成后，刷新差异类列，确保引用更新后的 totals
  const diffColumns = fieldConfig.value.filter(fc => fc.type === 'diffs' && fc.formula);
  tableData.value.forEach(row => {
    diffColumns.forEach(field => {
      const valResolver = (columnId) => parseFloat(row.values[columnId]) || 0;
      try {
        const funcBody = field.formula.replace(/VAL\((\d+)\)/g, (match, id) => `(valResolver(${id}))`);
        const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
        row.values[field.id] = parseFloat(result.toFixed(10));
      } catch (e) {
        console.error(`Error calculating diff formula for field ${field.id} in row ${row.metricId}:`, e);
      }
    });
  });

  if (iteration >= MAX_ITERATIONS) {
      console.warn("Calculation reached max iterations. Check for circular dependencies in formulas.");
  }

  // Run validation only if it's not explicitly disabled for the table
  if (currentTableConfig.value?.validation !== false) {
    runValidation({ level: 'hard' });
  }
};

// --- NEW Validation Logic ---
const evaluateValidationRule = (rule, rowData, findFieldByIdentifier) => {
    const valResolver = (identifier) => {
        const field = findFieldByIdentifier(identifier);
        if (!field) {
            console.warn(`Validation rule error: Field '${identifier}' not found.`);
            return 0;
        }
        const value = rowData.values[field.id];
        if (value === undefined || value === null) return 0;
        const parsed = parseFloat(value);
        // Replace NaN, Infinity, and -Infinity with 0 for stable validation
        return isFinite(parsed) ? parsed : 0;
    };

    const identifiers = Array.from(new Set(rule.match(/[a-zA-Z_][a-zA-Z0-9_.]*/g) || []));
    identifiers.sort((a, b) => b.length - a.length);

    let evaluatableString = rule;
    identifiers.forEach(id => {
        const escapedId = id.replace(/\./g, '\\.');
        const regex = new RegExp(escapedId, 'g');
        evaluatableString = evaluatableString.replace(regex, `valResolver('${id}')`);
    });

    try {
        // The expression is now expected to use standard JS operators like && and || directly.
        return Boolean(new Function('valResolver', `return ${evaluatableString}`)(valResolver));
    } catch (e) {
        console.error(`Error evaluating validation rule "${rule}":`, e);
        return false;
    }
};

const runValidation = ({ level = 'hard' } = {}) => {
  const newErrors = {};

  const schemeName = currentTableConfig.value?.validationScheme || 'default';
  const baseScheme = validationSchemes[schemeName] || validationSchemes['default'];
  const overrides = currentTableConfig.value?.validationOverrides || {};

  if (currentTableConfig.value?.validation === false) {
    errors.value = {};
    return;
  }

  const findFieldByIdentifier = (identifier) => {
    if (typeof identifier === 'number') return fieldConfig.value.find(f => f.id === identifier);
    return fieldConfig.value.find(f => f.name === identifier);
  };

  const oldErrors = { ...errors.value };
  if (level === 'hard') {
    Object.entries(oldErrors).forEach(([key, err]) => {
      if (err.type === 'B') newErrors[key] = err;
    });
  }

  tableData.value.forEach((row, rowIndex) => {
    const metricId = row.metricId;
    
    const menuOverride = overrides[metricId];
    const templateOverride = row.validation;

    if (menuOverride === null || templateOverride === null) {
      return;
    }

    const baseRules = baseScheme[row.type] || {};
    const finalValidation = { ...baseRules, ...menuOverride, ...templateOverride };

    const processRules = (rules, errorType) => {
      if (!rules) return;
      
      rules.forEach((ruleDef, index) => {
        const key = `${metricId}-${errorType}-${index}`;
        
        if (!evaluateValidationRule(ruleDef.rule, row, findFieldByIdentifier)) {
          const firstFieldInRule = (ruleDef.rule.match(/[a-zA-Z_][a-zA-Z0-9_.]*/g) || [])[0];
          const fieldForError = findFieldByIdentifier(firstFieldInRule);

          newErrors[key] = { 
            type: errorType, 
            message: ruleDef.message,
            metricId: metricId,
            fieldId: fieldForError ? fieldForError.id : null 
          };
        }
      });
    };

    const processCalcRules = (calcConfig) => {
      const config = typeof calcConfig === 'object' ? { ...baseScheme.calculated.calc, ...calcConfig } : baseScheme.calculated.calc;

      if (!config.enabled || row.type !== 'calculated' || !row.formula) return;

      const getRowByMetricId = (mId) => tableData.value.find(r => r.metricId === mId);
      const sanitize = (v) => {
        const p = parseFloat(v);
        return isFinite(p) ? p : 0;
      };

      // Per user request, C-type validation only applies to these two columns.
      const columnsToValidate = fieldConfig.value.filter(
        c => c.name === 'totals.plan' || c.name === 'totals.samePeriod'
      );

      // 按列进行校验：若行被强制，仅对“同期”列执行反向校验；其他列执行正常校验
      const childMetricIds = Array.from(row.formula.matchAll(/VAL\((\d+)\)/g)).map(m => Number(m[1]));
      columnsToValidate.forEach((col) => {
        if (getCellState(row, col, currentTableConfig.value) !== 'READONLY_CALCULATED') return;
        const isSamePeriodCol = typeof col.name === 'string' && col.name.endsWith('.samePeriod');

        const valResolver = (sourceMetricId) => {
          const sourceRow = getRowByMetricId(sourceMetricId);
          return sourceRow ? sanitize(sourceRow.values[col.id]) : 0;
        };

        if (row.isForced && isSamePeriodCol) {
          // 反向校验：强制行的“同期”列以子项合计校验
          if (childMetricIds.length === 0) return;
          let childrenSum = 0;
          try {
            const funcBody = row.formula.replace(/VAL\((\d+)\)/g, (match, id) => `(valResolver(${id}))`);
            const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
            childrenSum = sanitize(result);
          } catch (e) {
            console.error(`Error evaluating reverse-calc formula for metric ${metricId} in column ${col.id}:`, e);
          }
          const forcedValue = sanitize(row.values[col.id]);
          if (!validationRules.calculation(forcedValue, childrenSum, config.tolerance)) {
            childMetricIds.forEach(childId => {
              const key = `${childId}-C-reverse-${row.metricId}-${col.id}`;
              newErrors[key] = {
                type: 'C',
                message: `该值导致上级计算指标 '${row.values[1001]}' 的合计值不等于其强制设定的值 (${forcedValue})`,
                metricId: childId,
                fieldId: col.id,
              };
            });
          }
        } else {
          // 正常校验：计算值与期望值比较
          const actualValue = sanitize(row.values[col.id]);
          let expectedValue = 0;
          try {
            const funcBody = row.formula.replace(/VAL\((\d+)\)/g, (match, id) => `(valResolver(${id}))`);
            const result = new Function('valResolver', `return ${funcBody}`)(valResolver);
            expectedValue = sanitize(result);
          } catch (e) {
            console.error(`Error evaluating calc formula for metric ${metricId} in column ${col.id}:`, e);
          }
          if (!validationRules.calculation(actualValue, expectedValue, config.tolerance)) {
            const key = `${metricId}-C-${col.id}`;
            newErrors[key] = {
              type: 'C',
              message: config.message,
              metricId: metricId,
              fieldId: col.id,
            };
          }
        }
      });
    };

    if (finalValidation.hard) processRules(finalValidation.hard, 'A');
    if (level === 'all' && finalValidation.soft) processRules(finalValidation.soft, 'B');
    if (finalValidation.calc) processCalcRules(finalValidation.calc);
  });

  errors.value = newErrors;
};






// --- Watchers ---
watch(currentTableConfig, async () => {
  await initializeTableData();
  checkLocalDraft();
}, { deep: true, immediate: true });


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
  const state = getCellState(row, field, currentTableConfig.value);

  // 仅在数值列应用加粗样式
  const isValueColumn = field.component !== 'label';

  if (isValueColumn && (state === 'READONLY_CALCULATED' || row.type === 'calculated')) {
    return { ...row.style, fontWeight: 'bold' };
  }

  return row.style;
};

const getCellClass = ({ row, column }) => {
  const field = fieldConfig.value.find(f => f.name === column.property);
  if (!field) return '';

  const classes = [];

  // Find if there is any hard error ('A' or 'C') associated with this specific cell
  const hasCellError = Object.values(errors.value).some(error =>
    error.metricId === row.metricId &&
    error.fieldId === field.id &&
    (error.type === 'A' || error.type === 'C')
  );

  if (hasCellError) {
    classes.push('is-error');
  }

  const aggregatedIssues = row.cellIssues?.[field.id];
  if (Array.isArray(aggregatedIssues) && aggregatedIssues.some(issue => issue && (issue.type === 'B' || issue.type === 'C'))) {
    classes.push('has-soft-issue');
  }

  const cellState = getCellState(row, field, currentTableConfig.value, childToParentsMap.value, forcedParentMap.value);
  if (cellState === 'READONLY_AGGREGATED') {
    classes.push('is-readonly-aggregated');
  } else if (cellState !== 'WRITABLE') {
    classes.push('is-readonly-shadow');
  }

  return classes.join(' ');
};

const getErrorLabel = (key) => {
    const parts = key.split('-');
    if (parts.length < 2) return '未知错误';

    const metricId = parseInt(parts[0]);
    const errorType = parts[1]; // 'A', 'B', or legacy field ID

    const row = tableData.value.find(r => r.metricId === metricId);
    if (!row) return `未知指标 (ID: ${metricId})`;

    const metricName = row.values[1001] || `指标ID ${metricId}`;

    // Handle new row-based errors ('A' for hard, 'B' for soft)
    if (errorType === 'A' || errorType === 'B') {
        const error = errors.value[key];
        // If the error is associated with a specific field, mention it.
        if (error && error.fieldId) {
            const field = fieldConfig.value.find(f => f.id === error.fieldId);
            if (field) return `${metricName} - ${field.label}`;
        }
        return `${metricName} (行校验)`; // Fallback for row-level errors
    }

    // Legacy support for old cell-based errors
    const fieldId = parseInt(parts[1]);
    if (!isNaN(fieldId)) {
        const field = fieldConfig.value.find(f => f.id === fieldId);
        if (field) {
            return `${metricName} - ${field.label}`;
        }
    }

    return '未知错误';
};



const handleShowExplanations = async () => {
  const { projectId, tableId } = route.params;
  if (!tableId || !projectId) return;

  isExplanationsReadOnly.value = false;

  try {
    const response = await fetch(`/api/project/${projectId}/data/table/${tableId}`, {
      headers: buildUserHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch data for explanations.');

    const data = await response.json();
    const explanationsList = [];
    const summaryItems = Array.isArray(data?.explanationSummary)
      ? data.explanationSummary
      : Array.isArray(data?.submit?.explanationSummary)
        ? data.submit.explanationSummary
        : [];

    if (summaryItems.length > 0) {
      isExplanationsReadOnly.value = true;
      summaryItems.forEach(item => {
        const parts = [];
        if (item?.type) parts.push(`[${item.type}]`);
        if (item?.sourceTableName || item?.sourceTableId) {
          parts.push(item.sourceTableName || `表 ${item.sourceTableId}`);
        }
        if (item?.metricName) parts.push(item.metricName);
        if (item?.fieldLabel) {
          parts.push(item.fieldLabel);
        } else if (item?.fieldId) {
          parts.push(`字段 ${item.fieldId}`);
        }
        explanationsList.push({
          label: parts.join(' / ') || '未知指标',
          message: item?.message || '',
          content: item?.content || '',
          ruleKey: item?.ruleKey,
        });
      });
    } else if (data?.submit?.tableData) {
      isExplanationsReadOnly.value = false;
      data.submit.tableData.forEach(row => {
        row.values.forEach(cell => {
          if (cell.explanation) {
            explanationsList.push({
              label: getErrorLabel(cell.explanation.ruleKey),
              message: cell.explanation.message,
              content: cell.explanation.content,
              ruleKey: cell.explanation.ruleKey, // Store the key for mapping back
            });
          }
        });
      });
    }

    if (explanationsList.length === 0) {
      ElMessage.info('当前表格没有可用的解释说明。');
      return;
    }

    submittedExplanations.value = explanationsList;
    isExplanationsDialogVisible.value = true;
  } catch (error) {
    console.error('Error loading explanations:', error);
    ElMessage.error('加载解释说明失败。');
  }
};


// --- Actions (Save, Load, Submit, Export) ---

/**
 * Helper function to create the data payload for submission or saving.
 */
const _createPayload = () => {
  // --- 组织要发送到后端的数据 ---
  const processedData = tableData.value.map(row => {
    const metricInfo = reportTemplate.value.find(m => m.id === row.metricId);

    // 1. 转换 values 对象为数组，并加入字段的上下文信息
    const processedValues = Object.entries(row.values).map(([fieldId, value]) => {
      const fieldInfo = fieldConfig.value.find(f => f.id === parseInt(fieldId));
      
      let finalValue = value;
      // 仅对数值类型的字段进行转换 (component 不是 'label')
      if (fieldInfo && fieldInfo.component !== 'label') {
        if (typeof value === 'string') {
          const trimmedValue = value.trim();
          if (trimmedValue === '') {
            finalValue = 0; // 空字符串转为 0
          } else {
            const numericValue = Number(trimmedValue);
            // 只有在转换后是有效数字时才赋值，否则保留原始字符串(例如，用户可能输入了无效字符)
            if (!isNaN(numericValue)) {
              finalValue = numericValue;
            }
          }
        }
      }

      return {
        fieldId: parseInt(fieldId),
        fieldName: fieldInfo ? fieldInfo.name : 'unknown',
        fieldLabel: fieldInfo ? fieldInfo.label : 'unknown',
        value: finalValue,
      };
    });

    // 2. 查找软性错误，并将解释说明附加到对应的单元格上
    softErrorsForDisplay.value.forEach(([key, error]) => {
      const metricId = parseInt(key.split('-')[0]);
      // Check if the error belongs to the current row and has an explanation
      if (metricId === row.metricId && explanations.value[key]) {
        // Find the target cell in processedValues using the fieldId from the error object
        const targetCell = processedValues.find(cell => cell.fieldId === error.fieldId);
        if (targetCell) {
          // Attach the explanation to the specific cell
          targetCell.explanation = {
            ruleKey: key,
            message: error.message,
            content: explanations.value[key]
          };
        }
      }
    });

    const newRow = {
      metricId: row.metricId,
      metricName: metricInfo ? metricInfo.name : 'unknown',
      type: row.type,
      ...(row.isForced && { force: true }), // Conditionally add force flag
      values: processedValues,
    };

    return newRow;
  });

  return {
    submittedAt: getBeijingISODateString(),
    table: {
      id: currentTableConfig.value?.id,
      name: currentTableConfig.value?.name,
      template: currentTableConfig.value?.templateName,
    },
    submittedBy: authStore.user, // 添加提交者信息
    tableData: processedData,
  };
};

/**
 * Helper function to apply a given payload (from temp or submit) to the table.
 */
const _applyPayloadToTable = (payload) => {
  if (!payload || !payload.tableData) {
    ElMessage.info('没有可用于加载的数据。');
    return;
  }

  const loadedDataMap = new Map(payload.tableData.map(m => [m.metricId, m]));

  tableData.value.forEach(localRow => {
    const loadedMetric = loadedDataMap.get(localRow.metricId);

    // Reset force flag before applying new data
    localRow.isForced = false;
    localRow.cellIssues = {};

    if (loadedMetric) {
      // Apply the force flag from the payload
      if (loadedMetric.force) {
        localRow.isForced = true;
      }

      // 仅对 basic 行直接应用所有加载数据；
      // 若是被强制的 calculated 行，仅应用“各月的同期值”（monthlyData.*.samePeriod），不覆盖计划值和其他计算列。
      const loadedValuesMap = new Map();
      const loadedIssuesMap = new Map();

      if (Array.isArray(loadedMetric.values)) {
        loadedMetric.values.forEach(cell => {
          if (!cell || cell.fieldId == null) return;
          loadedValuesMap.set(cell.fieldId, cell.value);
          if (Array.isArray(cell.issues) && cell.issues.length > 0) {
            loadedIssuesMap.set(cell.fieldId, cell.issues);
          }
        });
      }


      const isTable0 = currentTableConfig.value?.id === '0';

      if (isTable0) {
        // 表0（集团分单位汇总表）：无论行类型如何，均应应用后端聚合给出的值，
        // 以便显示各单位的 totals.plan/samePeriod 等列（保留 1000 序号列）。
        fieldConfig.value.forEach(fc => {
          const fid = fc.id;
          if (fid === 1000) return;
          if (loadedValuesMap.has(fid)) {
            localRow.values[fid] = loadedValuesMap.get(fid);
          }
        });
      } else if (localRow.type === 'basic') {
        Object.keys(localRow.values).forEach(fieldId => {
          const numericFieldId = parseInt(fieldId);
          if (Number.isNaN(numericFieldId)) return;
          // Do not overwrite the sequential number column (ID 1000)
          if (numericFieldId === 1000) return;

          if (loadedValuesMap.has(numericFieldId)) {
            localRow.values[numericFieldId] = loadedValuesMap.get(numericFieldId);
          }
        });
      } else if (localRow.isForced) {
        Object.keys(localRow.values).forEach(fieldId => {
          const numericFieldId = parseInt(fieldId);
          if (Number.isNaN(numericFieldId)) return;
          const fieldDef = fieldConfig.value.find(f => f.id === numericFieldId);
          if (!fieldDef || typeof fieldDef.name !== 'string') return;
          const isMonthlySamePeriod = fieldDef.name.startsWith('monthlyData.') && fieldDef.name.endsWith('.samePeriod');
          if (isMonthlySamePeriod && loadedValuesMap.has(numericFieldId)) {
            localRow.values[numericFieldId] = loadedValuesMap.get(numericFieldId);
          }
        });
      }

      if (loadedIssuesMap.size > 0) {
        loadedIssuesMap.forEach((issues, fieldId) => {
          localRow.cellIssues[fieldId] = issues;
        });
      }
    }
  });

  calculateAll(); // Recalculate formulas and validations
  ElMessage.success('数据已成功加载！');

  // New logic to show validation errors
  const hardErrors = Object.entries(errors.value).filter(([, error]) => error.type === 'A' || error.type === 'C');
  if (hardErrors.length > 0) {
    const errorDetails = hardErrors.map(([key, error]) => {
      const label = getErrorLabel(key);
      const [metricName, fieldName] = label.split(' - ');
      return {
        metric: metricName || 'N/A',
        field: fieldName || 'N/A',
        message: error.message
      };
    });

    const tableHeader = `
      <thead style="text-align: left;">
        <tr>
          <th style="padding: 4px 8px;">指标</th>
          <th style="padding: 4px 8px;">字段</th>
          <th style="padding: 4px 8px;">错误信息</th>
        </tr>
      </thead>
    `;

    const tableBody = errorDetails.map(e => `
      <tr>
        <td style="padding: 4px 8px;">${e.metric}</td>
        <td style="padding: 4px 8px;">${e.field}</td>
        <td style="padding: 4px 8px;">${e.message}</td>
      </tr>
    `).join('');

    const tableHtml = `<table style="width: 100%; border-collapse: collapse;">${tableHeader}<tbody>${tableBody}</tbody></table>`;

    ElMessageBox.alert(tableHtml, '校验错误详情', {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定',
      width: '60%',
    });
  }
};

const handleSave = async () => {
  // 1. Save to localStorage for quick access
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
  localStorage.setItem(localDraftKey.value, JSON.stringify(draftData));
  hasLocalDraft.value = true; // Update the state
  
  // 2. Set status for immediate UI feedback on dashboard
  localStorage.setItem(`status-${route.params.tableId}`, 'saved');
  ElMessage.success('草稿已暂存至本地浏览器。');

  // 3. Silently back up to server
  const payload = _createPayload();
  try {
    const projectId = route.params.projectId;
    const tableId = route.params.tableId;
    // Fire and forget
    fetch(`/api/project/${projectId}/table/${tableId}/save_draft`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildUserHeaders()
      },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    // Log silent backup error, but don't bother the user
    console.error('Silent draft backup to server failed:', error);
  }
};

const handleLoadDraft = async () => {
  const savedData = localStorage.getItem(localDraftKey.value);
  if (savedData) {
    const draftData = JSON.parse(savedData);
    tableData.value.forEach(row => {
      if (draftData[row.metricId]) {
        Object.keys(draftData[row.metricId]).forEach(fieldId => {
          row.values[fieldId] = draftData[row.metricId][fieldId];
        });
      }
    });
    calculateAll();
    ElMessage.success('本地暂存数据已成功取回');
    return;
  }

  const projectId = route.params.projectId;
  const tableId = route.params.tableId;
  if (!projectId || !tableId) {
    ElMessage.warning('未找到本地暂存数据');
    return;
  }

  try {
    isLoading.value = true;
    const response = await fetch(`/api/project/${projectId}/data/table/${tableId}`, {
      headers: buildUserHeaders()
    });
    if (response.status === 404) {
      ElMessage.warning('未找到本地暂存数据');
      return;
    }
    if (!response.ok) {
      throw new Error(`Unexpected status ${response.status}`);
    }

    const data = await response.json();
    const tempPayload = data?.temp;
    if (!tempPayload || !Array.isArray(tempPayload.tableData)) {
      ElMessage.warning('未找到本地暂存数据');
      return;
    }

    try {
      await ElMessageBox.confirm(
        '缓存中未找到暂存数据，但服务器上存在备份，是否确定取回？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info',
        }
      );
    } catch (err) {
      ElMessage.warning('取回暂存数据失败');
      return;
    }

    _applyPayloadToTable(tempPayload);
    checkLocalDraft();
  } catch (error) {
    console.error('Load draft from server failed:', error);
    ElMessage.error('尝试从服务器加载暂存备份失败，请稍后重试。');
  } finally {
    isLoading.value = false;
  }
};

const handleSubmit = async () => {
  const skipValidation = isGodUser.value;

  if (!skipValidation) {
    // Step 1: Run validation to find all errors.
    runValidation({ level: 'all' });

    // Step 2: Check for hard errors.
    if (hasHardErrors.value) {
      ElMessage.error('提交失败：请先修复所有红色错误项。');
      return;
    }

    // Step 3: Handle soft errors.
    if (softErrorsForDisplay.value.length > 0) {
      // Check if all found soft errors have explanations.
      const allExplained = softErrorsForDisplay.value.every(([key]) =>
        explanations.value[key] && explanations.value[key].trim().length >= 10
      );

      // If not all are explained, open the panel and stop.
      if (!allExplained) {
        isErrorPanelVisible.value = true; // Open panel only when needed.
        ElMessage.warning('检测到软性问题/警告，请为相关项填写至少10字说明后再提交。');
        return;
      }
    }
  } else {
    // God users submit without validation barriers.
    errors.value = {};
    isErrorPanelVisible.value = false;
  }

  // Step 4: Proceed to create payload and submit.
  const payload = _createPayload();

  // --- 提交数据到后端 ---
  try {
    const projectId = route.params.projectId;
    const tableId = route.params.tableId;

    const response = await fetch(`/api/project/${projectId}/table/${tableId}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...buildUserHeaders()
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Backend submission failed');
    }

    // For immediate UI feedback
    localStorage.setItem(`status-${route.params.tableId}`, 'submitted');
    localStorage.setItem(`submittedAt-${route.params.tableId}`, payload.submittedAt);

    ElMessage.success('数据已成功提交至服务器');
    isErrorPanelVisible.value = false;

  } catch (error) {
    console.error('Submission error:', error);
    ElMessage.error(`数据提交到服务器失败: ${error.message}`);
  }
};
const handleUpdateExplanations = async () => {
  if (isExplanationsReadOnly.value) {
    isExplanationsDialogVisible.value = false;
    return;
  }
  // 1. Validate all explanations have at least 10 characters
  const allValid = submittedExplanations.value.every(exp => exp.content && exp.content.trim().length >= 10);
  if (!allValid) {
    ElMessage.warning('请确保所有解释说明都不少于10个字。');
    return;
  }

  // 2. Update the component's main 'explanations' state object
  submittedExplanations.value.forEach(exp => {
    if (exp.ruleKey) {
      explanations.value[exp.ruleKey] = exp.content;
    }
  });

  // 3. Close the dialog
  isExplanationsDialogVisible.value = false;

  // 4. Call handleSubmit, telling it to skip the interactive explanation check.
  setTimeout(() => {
    handleSubmit({ skipExplanationCheck: true });
  }, 100);
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
        const cellState = getCellState(row, field, currentTableConfig.value, childToParentsMap.value, forcedParentMap.value);

        // Only add formulas to cells that are meant to be calculated,
        // and respect the 'isForced' flag for samePeriod columns.
        if (cellState === 'READONLY_CALCULATED' && !(row.isForced && typeof field.name === 'string' && field.name.endsWith('.samePeriod'))) {
          const c = colIndex;
          const excelFormula = metricDef.formula.replace(/VAL\((\d+)\)/g, (match, id) => {
            const sourceRowIndex = metricIdToRowIndex.get(parseInt(id));
            return XLSX.utils.encode_cell({ r: sourceRowIndex, c });
          });
          worksheet[XLSX.utils.encode_cell({ r, c })] = { t: 'n', f: excelFormula };
        }
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
:deep(.el-input) {
  font-size: var(--table-font-size, 14px) !important;
  height: var(--table-input-height, 32px) !important;
  line-height: var(--table-input-height, 32px) !important;
}
:deep(.el-input__wrapper) {
  padding: 0;
  box-shadow: none !important;
  min-height: var(--table-input-height, 32px);
  height: var(--table-input-height, 32px) !important;
  line-height: var(--table-input-height, 32px) !important;
  font-size: var(--table-font-size, 14px) !important;
  border-radius: 0;
  width: 100%;
}
:deep(.el-input__wrapper input),
:deep(.el-input__wrapper .el-input__inner) {
  font-size: var(--table-font-size, 14px) !important;
  height: var(--table-input-height, 32px);
  line-height: var(--table-input-height, 32px);
  padding: 0 var(--table-input-horizontal-padding, 4px);
  text-align: center;
}
.el-table th.el-table__cell, .el-table td.el-table__cell { border-right: 1px solid #ebeef5; border-bottom: 1px solid #ebeef5; font-size: var(--table-font-size, 14px); padding: var(--table-cell-vertical-padding, 12px) 0; }
.el-table th.el-table__cell { background-color: #fafafa; }
.is-error .cell-content { box-shadow: 0 0 0 1px #f56c6c inset !important; border-radius: 4px; }
.has-soft-issue .cell-content { box-shadow: 0 0 0 1px #409eff inset !important; border-radius: 4px; }
.is-warning .el-input__wrapper, .is-warning .cell-content { box-shadow: 0 0 0 1px #e6a23c inset !important; border-radius: 4px; }
.is-readonly-shadow { background-color: #fafafa; box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.05); }
.is-readonly-aggregated { background-color: #f0f9eb; }
.loading-indicator, .no-data-message { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; width: 100%; font-size: 16px; color: #606266; }
.loading-indicator .el-icon { margin-bottom: 10px; }
</style>

<style scoped>
.data-entry-container { display: flex; flex-direction: column; height: 100%; padding: 20px; box-sizing: border-box; }
.title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  margin: 5px 0;
}

.page-title {
  flex-shrink: 0;
  font-size: 18px;
  margin: 0;
}

.submission-time {
  font-size: 13px; /* Slightly larger font size */
  margin-left: 16px;
  position: absolute;
  right: 0;
  bottom: 0;
}

.submission-time.submitted {
  color: #f56c6c; /* Red color */
}

.submission-time.not-submitted {
  color: #909399; /* Grey color */
}
.content-wrapper { flex-grow: 1; display: flex; overflow: hidden; }
.main-content { flex-grow: 1; display: flex; flex-direction: row; overflow: hidden; }
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
.cell-content {
  cursor: pointer;
  min-height: var(--table-input-height, 32px);
  padding: 1px 0;
  font-size: var(--table-font-size, 14px) !important;
  line-height: var(--table-input-height, 32px);
  width: 100%;
}
.cell-content span { font-size: inherit; }
.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }
</style>
