/**
 * @file 菜单及报表配置文件
 * 
 * 本文件定义了项目的菜单结构、报表属性以及特殊的行为配置。
 */
import * as groupTemplate from './templates/groupTemplate.js';
import * as subsidiaryTemplate from './templates/subsidiaryTemplate.js';

export const menuData = [
  {
    name: '集团公司',
    tables: [
      { 
        id: '0', 
        name: '0 集团分单位汇总表', 
        template: groupTemplate, 
        templateName: 'groupTemplate', 
        type: 'summary', 
        // 使用对象来定义列与数据源的映射关系
        subsidiaries: {
          'group': '1',
          'downtown': '2',
          'beihai': '3',
          'xianghai': '7',
          'jinzhou': '10',
          'beifang': '11',
          'jinpu': '12',
          'zhuanghe': '13',
          'research': '14'
        },
        aggregationExclusions: [], 
        actions: { submit: false, save: false } 
      },
      { 
        id: '1', 
        name: '1 集团汇总表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['2', '9', '10', '11', '12', '13', '14'],
        aggregationExclusions: [],
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas','purchased_heat'], businessModel: ['independent'] },
        actions: { submit: true, save: false },
      },
    ]
  },
  {
    name: '主城区',
    tables: [
      { 
        id: '2', 
        name: '2 主城区汇总表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['3', '7', '8'],
        aggregationExclusions: [],
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
      },
    ]
  },
  {
    name: '北海热电厂',
    tables: [
      { 
        id: '3', 
        name: '3 北海汇总表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['4', '5', '6'],
        aggregationExclusions: [97,105,107,109,111,113,114],
        properties: { productionMethod: ['thermoelectric','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
      },
      { 
        id: '4', 
        name: '4 北海热电厂(热电联产)表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal'], businessModel: ['non_independent'] },
      },
      { 
        id: '5', 
        name: '5 北海热电厂(水炉)表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['boiler_room'], fuelType: ['coal'], businessModel: ['non_independent'] },
      },
      { 
        id: '6', 
        name: '6 北海热电厂(天然气炉)表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['boiler_room'], fuelType: ['natural_gas'], businessModel: ['non_independent'] },
      },
    ]
  },
  {
    name: '香海热电厂',
    tables: [ 
      { 
        id: '7', 
        name: '7 香海热电厂表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
      } 
    ]
  },
  {
    name: '供热公司',
    tables: [
      { 
        id: '8', 
        name: '8 供热公司表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company'], fuelType: [], businessModel: ['independent'] },
      },
      { 
        id: '9', 
        name: '9 主城区电锅炉表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['boiler_room'], fuelType: ['electric'], businessModel: ['non_independent'] },
      },
    ]
  },
  {
    name: '金州热电',
    tables: [ 
      { 
        id: '10', 
        name: '10 金州热电表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] },
      } 
    ]
  },
  {
    name: '北方热电',
    tables: [ 
      { 
        id: '11', 
        name: '11 北方热电表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] },
      } 
    ]
  },
  {
    name: '金普热电',
    tables: [ 
      { 
        id: '12', 
        name: '12 金普热电表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal'], businessModel: ['independent'] },
      } 
    ]
  },
  {
    name: '庄河热电',
    tables: [ 
      { 
        id: '13', 
        name: '13 庄河环海表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal','purchased_heat'], businessModel: ['independent'] },
      } 
    ]
  },
  {
    name: '研究院',
    tables: [ 
      { 
        id: '14', 
        name: '14 研究院表', 
        samePeriodEditable: 'all',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['electric'], businessModel: ['independent'] },
      } 
    ]
  }
];