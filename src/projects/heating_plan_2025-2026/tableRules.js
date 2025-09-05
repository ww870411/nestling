/**
 * 表格相关的业务规则
 */

/**
 * 判断一个单元格是否可写
 * @param {object} row - 当前行的数据对象 (包含 type, values等)
 * @param {object} field - 当前列的配置对象 (包含 component 等)
 * @returns {boolean}
 */
export const isCellWritable = (row, field) => {
  if (!row || !field) {
    return false;
  }
  // 必须同时满足：行是基础行，且列是输入列
  return row.type === 'basic' && field.component === 'input';
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