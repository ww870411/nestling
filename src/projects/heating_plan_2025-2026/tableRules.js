/**
 * 表格相关的业务规则
 */

// ====================================================================
//                      单元格可写性规则
// ====================================================================

/**
 * 判断一个单元格的可写状态
 * @param {object} row - 当前行的数据对象
 * @param {object} field - 当前列的配置对象
 * @param {object} tableProperties - 当前表格的属性对象
 * @returns {'WRITABLE' | 'READONLY_CALCULATED' | 'READONLY_DISPLAY'} - 返回单元格的状态
 */
export const getCellState = (row, field, tableProperties) => {
  if (!row || !field) {
    return 'READONLY_DISPLAY';
  }

  // 规则1: display类型的列永远不可写 (最高优先级)
  if (field.component === 'display') {
    return 'READONLY_DISPLAY';
  }

  // 规则2: 模板中预定义的计算行，永远是计算状态 (高优先级)
  if (row.type === 'calculated') {
    return 'READONLY_CALCULATED';
  }

  const required = row.requiredProperties;

  // 规则3: 检查行内定义的 requiredProperties
  if (required && Object.keys(required).length > 0) {
    const props = tableProperties || {};
    for (const key in required) {
      const requiredValues = required[key];
      const tableValues = props[key] || [];
      if (requiredValues.length > 0 && tableValues.length === 0) {
        return 'READONLY_CALCULATED'; // Should be calculated from other tables
      }
      const match = requiredValues.some(val => tableValues.includes(val));
      if (!match) {
        return 'READONLY_CALCULATED'; // Should be calculated from other tables
      }
    }
  }

  // 规则4: 默认可写情况
  if (field.component === 'input') {
    return 'WRITABLE';
  }

  // 规则5: 特殊情况 - 同期值可编辑
  if (row.samePeriodEditable && field.name && field.name.endsWith('.samePeriod')) {
    return 'WRITABLE';
  }

  return 'READONLY_DISPLAY';
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