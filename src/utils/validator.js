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
   * 比较两个值
   * @param {*} valueA 
   * @param {string} operator 
   * @param {*} valueB 
   * @returns {boolean}
   */
  comparison: (valueA, operator, valueB) => {
    if (typeof valueA !== 'number' || typeof valueB !== 'number') {
      return true; // Cannot compare non-numbers
    }
    switch (operator) {
      case '<=': return valueA <= valueB;
      case '>=': return valueA >= valueB;
      case '<': return valueA < valueB;
      case '>': return valueA > valueB;
      case '==': return valueA == valueB;
      default: return true;
    }
  }
};