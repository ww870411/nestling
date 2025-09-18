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
        name: '集团分单位汇总表', 
        template: groupTemplate, 
        templateName: 'groupTemplate', 
        type: 'summary', 
        // 使用对象来定义列与数据源的映射关系
        subsidiaries: {
          'group': '1',
          'downtown': '2',
          'gufenbenbu':'3',
          'beihai': '4',
          'xianghai': '8',
          'jinzhou': '11',
          'beifang': '12',
          'jinpu': '13',
          'zhuanghe': '14',
          'research': '15'
        },
        aggregationExclusions: [], 
        actions: { submit: false, save: false } 
      },
      { 
        id: '1', 
        name: '集团汇总表', 
        samePeriodEditable: '',  //‘all’或'none'或[1,2,7]
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['2', '11', '12', '13', '14', '15'],
        aggregationExclusions: [1,2,191],
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
        name: '主城区汇总表', 
        samePeriodEditable: '',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['4', '8', '9','10'],
        aggregationExclusions: [1,2,15,16,191],
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] ,special:['related-rarty transaction','steam','hotwater','low vacuum']},
      },
      { 
        id: '3', 
        name: '股份本部汇总表', 
        samePeriodEditable: '',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['4','9'],
        aggregationExclusions: [1,2,14,17,18,19,20,23,24,95,99,101,191],
        properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] ,special:['related-rarty transaction','steam','hotwater','low vacuum']},
      },
    ]
  },
  {
    name: '北海热电厂',
    tables: [
      { 
        id: '4', 
        name: '北海汇总表', 
        samePeriodEditable: 'same as plan',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'summary',
        subsidiaries: ['5', '6', '7'],
        aggregationExclusions: [1,2,97,105,107,109,111,113,114,191],  //在表5,6,7中不必填写，因此默认为零，防止其将汇总表中填写的数据覆盖，并且在读取时引用本表自身的json数据。
        properties: { productionMethod: ['thermoelectric','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] },
      },
      { 
        id: '5', 
        name: '北海热电厂(热电联产)表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal'], businessModel: ['non_independent'],special:['steel ball','recycle_water',"steam"],position:['downtown'] },
      },
      { 
        id: '6', 
        name: '北海热电厂(水炉)表', 
        samePeriodEditable: 'same as plan',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        beAggregatedExclusions: [67],
        properties: { productionMethod: ['elec_boiler_room'], fuelType: ['coal'], businessModel: ['non_independent'] ,special:['recycle_water']},
      },
      { 
        id: '7', 
        name: '北海热电厂(天然气炉)表', 
        samePeriodEditable: 'same as plan',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['gas_boiler_room'], fuelType: ['natural_gas'], businessModel: ['non_independent'] ,special:['recycle_water']},
      },
    ]
  },
  {
    name: '香海热电厂',
    tables: [ 
      { 
        id: '8', 
        name: '香海热电厂表', 
        samePeriodEditable: 'same as plan',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric'], fuelType: ['coal'], businessModel: ['independent'],special:['low vacuum','steam'],position:['downtown'] },
      } 
    ]
  },
  {
    name: '供热公司',
    tables: [
      { 
        id: '9', 
        name: '供热公司表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company'], fuelType: [], businessModel: ['independent'],special:['hotwater','steam','low vacuum','not_only_boiler'] },
      },
      { 
        id: '10', 
        name: '主城区电锅炉表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['boiler_room'], fuelType: ['electric'], businessModel: ['semi_independent'] },
      },
    ]
  },
  {
    name: '金州热电',
    tables: [ 
      { 
        id: '11', 
        name: '金州热电表', 
        samePeriodEditable: 'same as plan',
        validation: true,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] ,special:['hotwater','low vacuum','not_only_boiler'],position:['north']},
      } 
    ]
  },
  {
    name: '北方热电',
    tables: [ 
      { 
        id: '12', 
        name: '北方热电表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] ,special:['hotwater','coarse powder','steel ball','recycle_water','not_only_boiler'],position:['north']},
      } 
    ]
  },
  {
    name: '金普热电',
    tables: [ 
      { 
        id: '13', 
        name: '金普热电表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal'], businessModel: ['independent'] ,special:['hotwater','recycle_water']},
      } 
    ]
  },
  {
    name: '庄河环海',
    tables: [ 
      { 
        id: '14', 
        name: '庄河环海表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal','purchased_heat'], businessModel: ['independent','recycle_water'] },
      } 
    ]
  },
  {
    name: '研究院',
    tables: [ 
      { 
        id: '15', 
        name: '研究院表', 
        samePeriodEditable: 'same as plan',
        validation: false,
        template: subsidiaryTemplate, 
        templateName: 'subsidiaryTemplate', 
        type: 'subsidiary',
        properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['electric'], businessModel: ['independent'] },
      } 
    ]
  }
];