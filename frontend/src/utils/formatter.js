/**
 * @file 格式化工具函数
 */

/**
 * 根据提供的格式化选项格式化一个数值。
 * @param {*} value - 要格式化的原始值。
 * @param {object} format - 格式化选项对象, e.g., { type: 'integer' }, { type: 'decimal', places: 2 }, { type: 'percentage', places: 2 }。
 * @returns {string} 格式化后的字符串。
 */
export function formatValue(value, format) {
  if (value === null || value === undefined || isNaN(value)) {
    return value; // Return original value if it's not a valid number
  }

  if (!format || !format.type) {
    return value; // Return original value if no format is specified
  }

  const numberValue = Number(value);

  switch (format.type) {
    case 'integer':
      return Math.round(numberValue).toString();
    
    case 'decimal':
      const decimalPlaces = format.places !== undefined ? format.places : 2;
      return numberValue.toFixed(decimalPlaces);

    case 'percentage':
      const percentagePlaces = format.places !== undefined ? format.places : 2;
      return `${(numberValue * 100).toFixed(percentagePlaces)}%`;

    default:
      return value; // Return original value for unknown format types
  }
}
