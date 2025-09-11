/**
 * 通用校验规则实现模块
 */

export const validationRules = {
  /**
   * 检查值是否为有效数字
   * @param {*} value 
   * @returns {boolean}
   */
  isNumber: (value) => {
    if (value === null || String(value).trim() === '') return true; // Allow empty values, use notEmpty for required fields
    return !isNaN(parseFloat(value)) && isFinite(value);
  },

  /**
   * 检查值是否不为空
   * @param {*} value 
   * @returns {boolean}
   */
  notEmpty: (value) => {
    return value !== null && value !== undefined && String(value).trim() !== '';
  },

  /**
   * 比较两个值，支持乘以系数和增加偏移量
   * @param {*} valueA 
   * @param {string} operator 
   * @param {*} valueB 
   * @param {number} [factor] - 可选的乘法系数
   * @param {number} [offset] - 可选的加减偏移量
   * @returns {boolean}
   */
  comparison: (valueA, operator, valueB, factor, offset) => {
    if (typeof valueA !== 'number' || typeof valueB !== 'number') {
      return true; // Cannot compare non-numbers
    }
    
    let comparisonValue = valueB;
    // Apply factor first (multiplication)
    if (factor !== undefined && typeof factor === 'number') {
      comparisonValue *= factor;
    }
    // Then apply offset (addition/subtraction)
    if (offset !== undefined && typeof offset === 'number') {
      comparisonValue += offset;
    }

    switch (operator) {
      case '<=': return valueA <= comparisonValue;
      case '>=': return valueA >= comparisonValue;
      case '<': return valueA < comparisonValue;
      case '>': return valueA > comparisonValue;
      case '==': return valueA == comparisonValue;
      default: return true;
    }
  },

  /**
   * 校验一个计算结果是否在容差范围内
   * @param {number} actualValue - 单元格中的实际值
   * @param {number} expectedValue - 根据公式计算出的期望值
   * @param {number} [tolerance=0.01] - 容差，默认为 1%
   * @returns {boolean}
   */
  calculation: (actualValue, expectedValue, tolerance = 0.01) => {
    if (typeof actualValue !== 'number' || typeof expectedValue !== 'number') {
      return true; // 无法比较非数字
    }

    // 处理期望值为0的特殊情况
    if (expectedValue === 0) {
      return actualValue === 0;
    }

    const difference = Math.abs(actualValue - expectedValue);
    const differenceRate = difference / Math.abs(expectedValue);

    return differenceRate <= tolerance;
  }
};