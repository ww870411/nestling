/**
 * @file 菜单及报表配置文件
 * 
 * 本文件定义了项目的菜单结构、报表属性以及特殊的行为配置。
 * 
 * === 报表特殊配置说明 ===
 * 
 * 1. `properties`: 
 *    - 类型: Object
 *    - 作用: 定义报表的业务属性，用于 `tableRules.js` 中的 `getCellState` 函数判断单元格是否可写。
 * 
 * 2. `validationScheme`: 
 *    - 类型: string (可选)
 *    - 作用: 指定该报表使用的基础校验方案。方案名对应 `tableRules.js` 中 `validationSchemes` 导出的key。
 *    - **默认行为**: 如果此属性被省略，系统将自动使用名为 `'default'` 的校验方案。
 *    - 示例: `validationScheme: 'strict'` (假如未来在rules中定义了名为'strict'的方案)
 * 
 * 3. `validationOverrides`:
 *    - 类型: Object (可选)
 *    - 作用: 在基础校验方案之上，提供针对单个指标的、更精细的规则覆盖或禁用。
 *    - 结构: key为指标的ID(字符串格式)，value为新的规则对象或`null`。
 *    - `value`为`null`: 表示禁用该指标的所有默认校验。
 *    - `value`为规则对象: 表示用新规则完全覆盖该指标的默认校验。
 *    - 示例: `validationOverrides: { '5': null, '115': { hard: [...] } }`
 * 
 * 4. `validation`: 
 *    - 类型: null (可选)
 *    - 作用: 一个“总开关”，如果设置为 `null`，则该报表将禁用所有校验，忽略 `validationScheme` 和 `validationOverrides`。
 *    - 示例: `validation: null`
 */
import * as groupTemplate from './templates/groupTemplate.js';
import * as subsidiaryTemplate from './templates/subsidiaryTemplate.js';

/**
 * @typedef {Object} TableProperties
 * @property ['thermoelectric','heating_company','boiler_room'] productionMethod - 生产方式
 * @property ['coal','natural_gas','purchased_heat','electric'] fuelType - 燃料种类
 * @property ['independent','non_independent'] businessModel - 经营模式
 */

export const menuData = [
  {
    name: '集团公司',
    tables: [
      { id: '0', name: '0 集团分单位汇总表', template: groupTemplate, templateName: 'groupTemplate',actions: { submit: false, save: false } },
      { 
        id: '1', 
        name: '1 集团汇总表', 
        actions: { submit: false, save: false },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas','purchased_heat'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null, // 禁用1-5号指标的校验
          '115': { // 为115号指标“毛利”设置特殊规则
            hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }]
          }
        }
      },
    ]
  },
  {
    name: '主城区',
    tables: [
      { 
        id: '2', 
        name: '2 主城区汇总表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        actions: { submit: true, save: true },
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
    ]
  },
  {
    name: '北海热电厂',
    tables: [
      { 
        id: '3', 
        name: '3 北海汇总表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        actions: { submit: true, save: true },
        properties: { productionMethod: ['thermoelectric','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
      { 
        id: '4', 
        name: '4 北海热电厂(热电联产)表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        actions: { submit: true, save: true },
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal'], businessModel: ['non_independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
      { 
        id: '5', 
        name: '5 北海热电厂(水炉)表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['boiler_room'], fuelType: ['coal'], businessModel: ['non_independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
      { 
        id: '6', 
        name: '6 北海热电厂(天然气炉)表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        actions: { submit: true, save: true },
        properties: { productionMethod: ['boiler_room'], fuelType: ['natural_gas'], businessModel: ['non_independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
    ]
  },
  {
    name: '香海热电厂',
    tables: [ 
      { 
        id: '7', 
        name: '7 香海热电厂表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  },
  {
    name: '供热公司',
    tables: [
      { 
        id: '8', 
        name: '8 供热公司表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['heating_company'], fuelType: [], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
      { 
        id: '9', 
        name: '9 主城区电锅炉表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['boiler_room'], fuelType: ['electric'], businessModel: ['non_independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      },
    ]
  },
  {
    name: '金州热电',
    tables: [ 
      { 
        id: '10', 
        name: '10 金州热电表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  },
  {
    name: '北方热电',
    tables: [ 
      { 
        id: '11', 
        name: '11 北方热电表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  },
  {
    name: '金普热电',
    tables: [ 
      { 
        id: '12', 
        name: '12 金普热电表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  },
  {
    name: '庄河热电',
    tables: [ 
      { 
        id: '13', 
        name: '13 庄河环海表', 
        actions: { submit: true, save: true },
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal','purchased_heat'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  },
  {
    name: '研究院',
    tables: [ 
      { 
        id: '14', 
        name: '14 研究院表', 
        template: subsidiaryTemplate, templateName: 'subsidiaryTemplate', 
        actions: { submit: true, save: true },
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['electric'], businessModel: ['independent'] },
        validationOverrides: {
          '1': null, '2': null, '3': null, '4': null, '5': null,
          '115': { hard: [{ rule: 'comparison', fieldA: 1003, operator: '>=', fieldB: 1004, message: '毛利必须大于等于同期完成值' }] }
        }
      } 
    ]
  }
];