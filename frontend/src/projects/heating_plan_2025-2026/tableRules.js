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
 * @param {object} tableConfig - 当前表格的完整配置对象 from menu.js
 * @returns {'WRITABLE' | 'READONLY_CALCULATED' | 'READONLY_DISPLAY' | 'READONLY_AGGREGATED'} - 返回单元格的状态
 */
export const getCellState = (row, field, tableConfig) => {
  if (!row || !field) {
    return 'READONLY_DISPLAY';
  }

  // 规则 1: 计算类型的行或列，永远是只读计算状态 (最高优先级)
  if (row.type === 'calculated' || field.type === 'calculated') {
    return 'READONLY_CALCULATED';
  }

  // 规则 2: 在汇总表中，非排除的指标行，其输入单元格是只读的汇总态
  if (tableConfig?.type === 'summary') {
    const isExcluded = tableConfig.aggregationExclusions?.includes(row.metricId);
    if (!isExcluded && field.component === 'input') {
      return 'READONLY_AGGREGATED';
    }
  }

  // 规则 3: display类型的列永远不可写
  if (field.component === 'display') {
    return 'READONLY_DISPLAY';
  }

  const required = row.requiredProperties;
  const tableProperties = tableConfig?.properties || {};

  // 规则 4: 检查行内定义的 requiredProperties (已废弃，但保留兼容)
  if (required && Object.keys(required).length > 0) {
    for (const key in required) {
      const requiredValues = required[key];
      const tableValues = tableProperties[key] || [];
      if (requiredValues.length > 0 && tableValues.length === 0) {
        return 'READONLY_CALCULATED';
      }
      const match = requiredValues.some(val => tableValues.includes(val));
      if (!match) {
        return 'READONLY_CALCULATED';
      }
    }
  }

  // 规则 5: 默认可写情况
  if (field.component === 'input') {
    return 'WRITABLE';
  }

  // 规则 6: 特殊情况 - 同期值可编辑
  if (row.samePeriodEditable && field.name && field.name.endsWith('.samePeriod')) {
    return 'WRITABLE';
  }

  return 'READONLY_DISPLAY';
};


// --- 校验规则 ---

/**
 * =====================================================
 *                  校验规则库
 * =====================================================
 * 
 * 本文件定义了所有可复用的校验方案(Scheme)。
 * 每个方案包含针对不同指标类型(`basic`, `calculated`)的规则。
 * 
 * --- 规则详情 ---
 * 
 * 1. `rule: 'isNumber'`
 *    - 作用: 检查值是否为有效数字。
 * 
 * 2. `rule: 'notEmpty'`
 *    - 作用: 检查值是否不为空。
 * 
 * 3. `rule: 'comparison'`
 *    - 作用: 比较一行中的两个字段值，支持对第二个值进行系数和偏移量调整。
 *    - 需要以下额外属性:
 *      - `fieldA` (string | number): 第一个字段的标识。
 *      - `fieldB` (string | number): 第二个字段的标识。
 *      - `operator` (string): 比较操作符 ('<=', '>=', '<', '>', '==')。
 *      - `factor` (number, 可选): 一个可选的乘法系数。
 *      - `offset` (number, 可选): 一个可选的加减偏移量。
 *    - 注意: 会先计算乘法(`factor`)，再计算加法(`offset`)。
 *    - 示例 1 (简单比较):
 *      `{ rule: 'comparison', fieldA: 'totals.plan', operator: '<=', fieldB: 'totals.samePeriod', message: '本期计划不应超过同期完成' }`
 *    - 示例 2 (系数比较):
 *      `{ rule: 'comparison', fieldA: 'totals.plan', operator: '>=', fieldB: 'totals.samePeriod', factor: 0.95, message: '本期计划较同期完成减少不应超过5%' }`
 *    - 示例 3 (偏移量比较):
 *      `{ rule: 'comparison', fieldA: 'totals.plan', operator: '<=', fieldB: 'totals.samePeriod', offset: 100, message: '本期计划不应超过同期完成值+100' }`
 */
const defaultScheme = {
  basic: {
    hard: [
      { rule: 'isNumber', message: '必须为数字格式' },
      { rule: 'notEmpty', message: '此项为必填项，不能为空' }
    ],
    soft: [
      {
        rule: 'comparison',
        fieldA: 'totals.plan',
        operator: '<=',
        fieldB: 'totals.samePeriod',
        message: '本期计划不应超过同期完成'
      }
    ]
  },
  calculated: {
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
  }
};

// 未来可在这里添加更多方案, 例如 'strict', 'relaxed' 等
export const validationSchemes = {
  'default': defaultScheme,
};