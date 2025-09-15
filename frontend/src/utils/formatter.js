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
  if (value === null || value === undefined) {
    return value;
  }

  const numberValue = Number(value);
  if (isNaN(numberValue)) {
    return value; // Return original non-numeric value
  }

  if (!format || !format.type) {
    return value; // Return original value if no format is specified
  }

  // Handle percentage separately to exactly match existing output (e.g., '55.00%')
  if (format.type === 'percentage') {
    const percentagePlaces = format.places !== undefined ? format.places : 2;
    return `${(numberValue * 100).toFixed(percentagePlaces)}%`;
  }

  // Use Intl.NumberFormat for integer and decimal types
  const options = {
    useGrouping: format.thousandSeparator || false, // This enables the comma separator
  };

  if (format.type === 'integer') {
    options.minimumFractionDigits = 0;
    options.maximumFractionDigits = 0;
  } else if (format.type === 'decimal') {
    options.minimumFractionDigits = format.places !== undefined ? format.places : 2;
    options.maximumFractionDigits = format.places !== undefined ? format.places : 2;
  } else {
    return value; // Return original for unknown types
  }

  return new Intl.NumberFormat('en-US', options).format(numberValue);
}

/**
 * 将 ISO 格式的日期时间字符串或 Date 对象格式化为本地时间。
 * @param {string | Date} isoString - ISO 8601 格式的日期时间字符串或 Date 对象。
 * @param {string} format - 'full' (e.g., "2023-09-08 14:30:05") or 'date' (e.g., "2023-09-08")。
 * @returns {string} 格式化后的本地时间字符串, 如果输入无效则返回空字符串。
 */
export function formatDateTime(isoString, format = 'full') {
  if (!isoString) return '';

  const date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return ''; // Invalid date
  }

  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // Use 24-hour format
  };

  // For some reason, toLocaleString with options doesn't always produce the desired YYYY-MM-DD format.
  // A manual approach is more reliable.
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  
  if (format === 'date') {
    return `${year}-${month}-${day}`;
  }

  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
