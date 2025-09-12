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
/**
 * @function getCellState
 * @description 决定单元格的最终状态（可写、只读、只读计算等）。
 * 包含了核心的业务逻辑，特别是针对“同期完成”字段的动态权限控制。
 *
 * “同期完成”单元格（field.name.endsWith('.samePeriod')）是否可写的判断逻辑如下：
 * 该权限由表级（menu.js中）和指标级（模板文件中）的 `samePeriodEditable` 属性共同决定。
 *
 * 解析顺序与规则:
 * 1. 检查表级 `samePeriodEditable` 的设置:
 *    - 若为 'all': 单元格强制为【可写】。
 *    - 若为 'none': 单元格强制为【只读】。
 *    - 若为数组 (e.g., [1, 2, 3]):
 *        - 如果当前指标ID在数组中, 单元格为【可写】。
 *        - 如果不在数组中, 则继续执行第2步。
 *    - 若为空或未设置: 表级无影响，继续执行第2步。
 *
 * 2. 检查指标级 `samePeriodEditable` 的设置:
 *    - 若为 true: 单元格为【可写】。
 *
 * 3. 默认状态:
 *    - 如果以上所有规则都未允许写入，单元格最终为【只读】。
 */
export const getCellState = (row, field, currentTableConfig) => {
  // 新增：检查指标的 requiredProperties 是否被当前表格的 properties 满足
  const required = row.requiredProperties;
  const provided = currentTableConfig?.properties || {};

  if (required) {
    let isRequirementMet = true;
    for (const key in required) {
      // 检查表格是否定义了该属性，以及定义的属性数组中是否至少包含一个指标需要的属性值
      if (!provided[key] || !required[key].some(val => provided[key].includes(val))) {
        isRequirementMet = false;
        break; // 只要有一个条件不满足，即判定为失败
      }
    }

    if (!isRequirementMet) {
      // 如果要求不满足，则该行的所有单元格都应为只读
      return 'READONLY_DISPLAY';
    }
  }

  const properties = currentTableConfig?.properties || {};
  const isAggregated = properties.isAggregated || false;
  const isGroupSummary = properties.isGroupSummary || false;

  // For group summary tables (Table 0), all data cells are readonly calculated
  if (isGroupSummary && field.component !== 'label') {
    return 'READONLY_CALCULATED';
  }

  // For aggregated tables (like Table 1), plan is readonly, others are calculated
  if (isAggregated && field.component !== 'label') {
    if (field.name.endsWith('.plan')) {
      return 'READONLY_AGGREGATED';
    }
    return 'READONLY_CALCULATED';
  }

  // For basic data entry tables
  // 仅允许“月度计划”可写：monthlyData.*.plan，避免误将 totals.plan 判为可写
  if (typeof field.name === 'string' && field.name.startsWith('monthlyData.') && field.name.endsWith('.plan')) {
    if (row.type === 'basic') {
      return 'WRITABLE';
    }
  }

  // 同期可写性仅作用于“月度同期”字段：monthlyData.*.samePeriod
  if (typeof field.name === 'string' && field.name.startsWith('monthlyData.') && field.name.endsWith('.samePeriod')) {
    // If the row itself is a calculated metric, its samePeriod value should also be calculated.
    if (row.type === 'calculated') {
      return 'READONLY_CALCULATED';
    }

    const tableSetting = currentTableConfig?.samePeriodEditable;
    const metricSetting = row.samePeriodEditable;
    const metricId = row.metricId;

    // Check for table-level overrides that stop further checks
    if (tableSetting === 'all') return 'WRITABLE';
    if (tableSetting === 'none') return 'READONLY';

    // Check for table-level array setting
    if (Array.isArray(tableSetting)) {
      if (tableSetting.includes(metricId)) {
        return 'WRITABLE';
      }
    }

    // Fall back to metric-level setting
    if (metricSetting === true) {
      return 'WRITABLE';
    }

    // Final Default（除菜单或指标显式开放外，默认只读）
    return 'READONLY';
  }

  if (field.component === 'label') {
    return 'READONLY';
  }

  // Default for other cells (like diffRate) is calculated
  return 'READONLY_CALCULATED';
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
/**
 * =================================================================================
 *                            新版校验引擎语法说明
 * =================================================================================
 *
 * 新版校验引擎使用标准的JavaScript表达式作为规则，提供了强大的灵活性。
 *
 * --- 规则基本结构 ---
 * 每个校验规则都是一个包含'rule'和'message'的对象：
 * { rule: '表达式字符串', message: '用户友好的提示信息' }
 *
 * --- 表达式语法 (rule) ---
 *
 * 1. 引用字段:
 *    - 直接使用字段在`fieldConfig`中定义的`name`属性来引用其值。
 *    - 示例: `totals.plan`, `monthlyData.october.samePeriod`
 *
 * 2. 支持的运算符:
 *    - 比较运算符: `>`  `>=`  `<`  `<=`  `==`  `!=`  `===`  `!==`
 *    - 算术运算符: `+`  `-`  `*`  `/`  `%` (遵循标准运算优先级)
 *    - 逻辑运算符: `&&` (逻辑与), `||` (逻辑或)
 *    - 分组运算符: `()` (用于控制运算顺序)
 *
 * --- 规则示例 ---
 *
 * // 示例1: 简单比较
 * { rule: 'totals.plan <= totals.samePeriod', message: '本期计划不应超过同期完成。' }
 *
 * // 示例2: 使用算术运算
 * { rule: 'monthlyData.october.plan * 1.1 >= monthlyData.november.plan', message: '11月计划不应比10月计划高出超过10%。' }
 *
 * // 示例3: 使用逻辑运算符 (&&)
 * {
 *   rule: 'totals.plan <= totals.samePeriod * 1.2 && totals.plan >= totals.samePeriod * 0.8',
 *   message: '本期计划与同期的差异率绝对值不应超过20%。'
 * }
 *
 * // 示例4: 复杂的混合运算
 * {
 *   rule: '(monthlyData.october.plan + monthlyData.november.plan) > totals.samePeriod / 2',
 *   message: '10月与11月计划之和，应大于同期总完成值的一半。'
 * }
 *
 */
const defaultScheme = {
  basic: {
    hard: [
      // {
      //   rule: 'isNumber', 
      //   message: '必须为数字格式'
      // },
    ],
    soft: [
      {
        rule: 'totals.plan <= totals.samePeriod',
        message: '本期计划不应超过同期完成'
      }
    ]
  },
  calculated: {
    hard: [], // Calculated fields have no direct input to validate
    soft: [
      {
        rule: 'totals.plan <= totals.samePeriod',
        message: '本期计划不应超过同期完成'
      }
    ],
    // C类校验：用于校验计算指标的准确性
    // 在指标的 validation 属性中设置 { calc: true } 来启用
    // 或设置 { calc: { tolerance: 0.02, message: '自定义消息' } } 来覆盖默认值
    calc: {
      enabled: true, // 对所有计算指标默认启用
      tolerance: 0.01, // 默认 1% 容差
      message: '计算结果与公式不符'
    }
  }
};

// 未来可在这里添加更多方案, 例如 'strict', 'relaxed' 等
export const validationSchemes = {
  'default': defaultScheme,
};
