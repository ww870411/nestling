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
      { id: '0', name: '0 集团分单位汇总表', template: groupTemplate },
      { id: '1', name: '1 集团汇总表', template: subsidiaryTemplate ,properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas','purchased_heat'], businessModel: ['independent'] }},
    ]
  },
  {
    name: '主城区',
    tables: [
      { id: '2', name: '2 主城区汇总表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric','heating_company','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] } },
    ]
  },
  {
    name: '北海热电厂',
    tables: [
      { id: '3', name: '3 北海汇总表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric','boiler_room'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] } },
      { id: '4', name: '4 北海热电厂(热电联产)表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric'], fuelType: ['coal'], businessModel: ['non_independent'] } },
      { id: '5', name: '5 北海热电厂(水炉)表', template: subsidiaryTemplate, properties: { productionMethod: ['boiler_room'], fuelType: ['coal'], businessModel: ['non_independent'] } },
      { id: '6', name: '6 北海热电厂(天然气炉)表', template: subsidiaryTemplate, properties: { productionMethod: ['boiler_room'], fuelType: ['natural_gas'], businessModel: ['non_independent'] } },
    ]
  },
  {
    name: '香海热电厂',
    tables: [ { id: '7', name: '7 香海热电厂表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric'], fuelType: ['coal','natural_gas'], businessModel: ['independent'] } } ]
  },
  {
    name: '供热公司',
    tables: [
      { id: '8', name: '8 供热公司表', template: subsidiaryTemplate, properties: { productionMethod: ['heating_company'], fuelType: [], businessModel: ['independent'] } },
      { id: '9', name: '9 主城区电锅炉表', template: subsidiaryTemplate, properties: { productionMethod: ['boiler_room'], fuelType: ['electric'], businessModel: ['non_independent'] } },
    ]
  },
  {
    name: '金州热电',
    tables: [ { id: '10', name: '10 金州热电表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] } } ]
  },
  {
    name: '北方热电',
    tables: [ { id: '11', name: '11 北方热电表', template: subsidiaryTemplate, properties: { productionMethod: ['thermoelectric','heating_company'], fuelType: ['coal'], businessModel: ['independent'] } } ]
  },
  {
    name: '金普热电',
    tables: [ { id: '12', name: '12 金普热电表', template: subsidiaryTemplate, properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal'], businessModel: ['independent'] } } ]
  },
  {
    name: '庄河热电',
    tables: [ { id: '13', name: '13 庄河环海表', template: subsidiaryTemplate, properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['coal','purchased_heat'], businessModel: ['independent'] } } ]
  },
  {
    name: '研究院',
    tables: [ { id: '14', name: '14 研究院表', template: subsidiaryTemplate, properties: { productionMethod: ['heating_company','boiler_room'], fuelType: ['electric'], businessModel: ['independent'] } } ]
  }
];