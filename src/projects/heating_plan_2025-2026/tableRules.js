/**
 * 表格相关的业务规则
 */

// ====================================================================
//                      单元格可写性规则
// ====================================================================

/**
 * 定义特定指标的可写规则。
 * 键是指标ID (metricId)，值是一个函数，该函数接收表格的 properties 对象并返回布尔值。
 * @type {Object.<number, function(TableProperties): boolean>}
 */
const writabilityRules = {
  // 示例: 指标6 (发电量) 仅在生产方式为 '热电联产' 的表中可写
  // 6: (props) => props.productionMethod.includes('thermoelectric'),
  
  // 在这里添加您需要的规则...
};


/**
 * 判断一个单元格是否可写。
 * @param {object} row - 当前行的数据对象 (包含 metricId, type, samePeriodEditable)
 * @param {object} field - 当前列的配置对象 (包含 component, name)
 * @param {object} tableProperties - 当前表格的属性对象 (来自 menu.js)
 * @returns {boolean}
 */
export const isCellWritable = (row, field, tableProperties) => {
  if (!row || !field) {
    return false;
  }

  // 优先规则 1: display类型的列永远不可写
  if (field.component === 'display') {
    return false;
  }

  // 优先规则 2: 检查是否存在基于业务属性的特殊规则
  const specificRule = writabilityRules[row.metricId];
  if (specificRule) {
    // 如果有特殊规则，则根据规则和表格属性来判断
    return specificRule(tableProperties || {});
  }

  // 默认规则 3: 常规输入单元格 (基础行 & input列)
  if (row.type === 'basic' && field.component === 'input') {
    return true;
  }

  // 默认规则 4: 特殊情况 - 同期值可编辑
  if (row.samePeriodEditable && field.name && field.name.endsWith('.samePeriod')) {
    return true;
  }

  return false;
};


// --- 校验规则 ---

/**
 * =====================================================
 *                  校验规则语法文档
 * =====================================================
 * 
 * 校验配置是一个包含 `hard` 和 `soft` 两个数组的对象。
 * - `hard`: 硬性校验，不通过则无法提交。
 * - `soft`: 软性校验，不通过会弹出提示，但允许填写说明后提交。
 * 
 * --- 规则详情 ---
 * 
 * 每个校验规则本身是一个对象，包含一个或多个属性：
 * 
 * 1. `rule: 'isNumber'`
 *    - 作用: 检查值是否为有效数字。
 *    - 示例: `{ rule: 'isNumber', message: '必须为数字格式' }`
 * 
 * 2. `rule: 'notEmpty'`
 *    - 作用: 检查值是否不为空（null, undefined, 或只包含空格的字符串）。
 *    - 示例: `{ rule: 'notEmpty', message: '此项为必填项，不能为空' }`
 * 
 * 3. `rule: 'comparison'`
 *    - 作用: 比较一行中的两个字段值。
 *    - 需要以下额外属性:
 *      - `fieldA` (string | number): 第一个字段的标识，可以是数字ID (如 1003) 或字段名 (如 'totals.plan')。
 *      - `fieldB` (string | number): 第二个字段的标识。
 *      - `operator` (string): 比较操作符。当前程序支持以下值:
 *        - '<=' (小于等于)
 *        - '>=' (大于等于)
 *        - '<'  (小于)
 *        - '>'  (大于)
 *        - '==' (等于)
 *    - 示例:
 *      `{ rule: 'comparison', fieldA: 'totals.plan', operator: '<=', fieldB: 'totals.samePeriod', message: '本期计划不应超过同期完成' }`
 */

const defaultBasicValidation = {
  hard: [
    { rule: 'isNumber', message: '必须为数字格式' },
    { rule: 'notEmpty', message: '此项为必填项，不能为空' }
  ],
  soft: [
    {
      rule: 'comparison',
      fieldA: 'totals.plan', // 可使用名称 'totals.plan' 或 ID 1003
      operator: '<=',
      fieldB: 'totals.samePeriod', // 可使用名称 'totals.samePeriod' 或 ID 1004
      message: '本期计划不应超过同期完成'
    }
  ]
};

const defaultCalculatedValidation = {
  hard: [], // Calculated fields have no direct input to validate
  soft: [
    {
      rule: 'comparison',
      fieldA: 'totals.plan',
      operator: '<=',
      fieldB: 'totals.samePeriod',
      message: '本期计划不应超过同期完成'
    }
  ]
};

export const getDefaultValidation = (indicatorType) => {
  return indicatorType === 'basic' ? defaultBasicValidation : defaultCalculatedValidation;
};