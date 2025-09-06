import * as groupTemplate from './templates/groupTemplate.js';
import * as subsidiaryTemplate from './templates/subsidiaryTemplate.js';

export const menuData = [
  {
    name: '集团公司',
    tables: [
      { id: '0', name: '0 集团分单位汇总表', template: groupTemplate },
      { id: '1', name: '1 集团汇总表', template: subsidiaryTemplate },
    ]
  },
  {
    name: '主城区',
    tables: [
      { id: '2', name: '2 主城区汇总表', template: subsidiaryTemplate },
    ]
  },
  {
    name: '北海热电厂',
    tables: [
      { id: '3', name: '3 北海汇总表', template: subsidiaryTemplate },
      { id: '4', name: '4 北海热电厂(热电联产)表', template: subsidiaryTemplate },
      { id: '5', name: '5 北海热电厂(水炉)表', template: subsidiaryTemplate },
      { id: '6', name: '6 北海热电厂(天然气炉)表', template: subsidiaryTemplate },
    ]
  },
  {
    name: '香海热电厂',
    tables: [ { id: '7', name: '7 香海热电厂表', template: subsidiaryTemplate } ]
  },
  {
    name: '供热公司',
    tables: [
      { id: '8', name: '8 供热公司表', template: subsidiaryTemplate },
      { id: '9', name: '9 主城区电锅炉表', template: subsidiaryTemplate },
    ]
  },
  {
    name: '金州热电',
    tables: [ { id: '10', name: '10 金州热电表', template: subsidiaryTemplate } ]
  },
  {
    name: '北方热电',
    tables: [ { id: '11', name: '11 北方热电表', template: subsidiaryTemplate } ]
  },
  {
    name: '金普热电',
    tables: [ { id: '12', name: '12 金普热电表', template: subsidiaryTemplate } ]
  },
  {
    name: '庄河热电',
    tables: [ { id: '13', name: '13 庄河环海表', template: subsidiaryTemplate } ]
  },
  {
    name: '研究院',
    tables: [ { id: '14', name: '14 研究院表', template: subsidiaryTemplate } ]
  }
];
