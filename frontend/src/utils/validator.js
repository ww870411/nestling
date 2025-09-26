/**
 * 通用校验规则模块（仅保留基础与软校验；已移除 C 类计算校验）
 */

export const validationRules = {
  /**
   * 是否为有效数字（为空不报错，required 用 notEmpty）
   */
  isNumber: (value) => {
    if (value === null || String(value).trim() === '') return true;
    return !isNaN(parseFloat(value)) && isFinite(value);
  },

  /**
   * 非空判断
   */
  notEmpty: (value) => {
    return value !== null && value !== undefined && String(value).trim() !== '';
  },

  /**
   * 比较运算，支持因子与偏移
   */
  comparison: (valueA, operator, valueB, factor, offset) => {
    if (typeof valueA !== 'number' || typeof valueB !== 'number') {
      return true; // 非数字不比较
    }

    let comparisonValue = valueB;
    if (factor !== undefined && typeof factor === 'number') comparisonValue *= factor;
    if (offset !== undefined && typeof offset === 'number') comparisonValue += offset;

    switch (operator) {
      case '<=': return valueA <= comparisonValue;
      case '>=': return valueA >= comparisonValue;
      case '<':  return valueA <  comparisonValue;
      case '>':  return valueA >  comparisonValue;
      case '==': return valueA == comparisonValue;
      default:   return true;
    }
  },

  // 已弃用：C 类（计算）校验彻底移除，占位保持兼容（始终为 true）
  calculation: () => true,
};

