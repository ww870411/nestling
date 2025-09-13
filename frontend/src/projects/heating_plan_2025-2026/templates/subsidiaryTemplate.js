// templates/subsidiaryTemplate.js

/**
 * 新版字段配置 (fieldConfig)
 * 
 * 结构变更说明:
 * 1.  ID系统: 所有字段ID已从字符串（如 'name'）更改为唯一的数字ID（从1001开始）。
 * 2.  扁平化结构: 原来的 'monthlyData' 分组已被移除。每个月份的'计划'和'同期'现在都是拥有独立ID的顶级字段。
 *    - 例如，'10月-计划' 的ID为 2001，'11月-计划' 的ID为 2003，以此类推。
 * 3.  计算字段: 增加了 'type' 和 'formula' 属性。
 *    - type: 'basic' (基础字段，用户可直接输入) 或 'calculated' (计算字段)。
 *    - formula: 使用 VAL(id) 格式定义计算逻辑。
 */
export const fieldConfig = [
  // --- 基础信息列 (ID: 1001-1002) ---
  {
    id: 1000,
    name: 'metricid', 
    label: '指标序号',
    type: 'basic',
    component: 'label',
    width: 74,
    fixed: true,
  },
  {
    id: 1001,
    name: 'name', // 保留原始name用于数据映射
    label: '指标名称',
    type: 'basic',
    component: 'label',
    width: 250,
    fixed: true,
  },
  {
    id: 1002,
    name: 'unit',
    label: '计量单位',
    type: 'basic',
    component: 'label',
    width: 100,
    fixed: true,
  },

  // --- 汇总计算列 (ID: 1003-1005) ---
  {
    id: 1003,
    name: 'totals.plan',
    label: '本期计划',
    type: 'calculated',
    component: 'display',
    width: 120,
    // 公式: 累加所有月份的“计划”值 (ID: 2001, 2003, 2005, ...)
    formula: 'VAL(2001)+VAL(2003)+VAL(2005)+VAL(2007)+VAL(2009)+VAL(2011)+VAL(2013)',
  },
  {
    id: 1004,
    name: 'totals.samePeriod',
    label: '同期完成',
    type: 'calculated',
    component: 'display',
    width: 120,
    // 公式: 累加所有月份的“同期”值 (ID: 2002, 2004, 2006, ...)
    formula: 'VAL(2002)+VAL(2004)+VAL(2006)+VAL(2008)+VAL(2010)+VAL(2012)+VAL(2014)',
  },
  {
    id: 1005,
    name: 'totals.diffRate',
    label: '差异率',
    type: 'calculated',
    component: 'display',
    width: 100,
    displayFormat: { type: 'percentage', places: 2 },
    // 公式: (本期计划 - 同期完成) / 同期完成
    formula: '(VAL(1003)-VAL(1004))/VAL(1004)',
  },

  // --- 月度数据列 (ID: 2001-2014) ---
  // 10月
  { id: 2001, name: 'monthlyData.october.plan', label: '10月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2002, name: 'monthlyData.october.samePeriod', label: '10月-同期', type: 'basic', component: 'display', width: 110 },
  // 11月
  { id: 2003, name: 'monthlyData.november.plan', label: '11月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2004, name: 'monthlyData.november.samePeriod', label: '11月-同期', type: 'basic', component: 'display', width: 110 },
  // 12月
  { id: 2005, name: 'monthlyData.december.plan', label: '12月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2006, name: 'monthlyData.december.samePeriod', label: '12月-同期', type: 'basic', component: 'display', width: 110 },
  // 1月
  { id: 2007, name: 'monthlyData.january.plan', label: '1月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2008, name: 'monthlyData.january.samePeriod', label: '1月-同期', type: 'basic', component: 'display', width: 110 },
  // 2月
  { id: 2009, name: 'monthlyData.february.plan', label: '2月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2010, name: 'monthlyData.february.samePeriod', label: '2月-同期', type: 'basic', component: 'display', width: 110 },
  // 3月
  { id: 2011, name: 'monthlyData.march.plan', label: '3月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2012, name: 'monthlyData.march.samePeriod', label: '3月-同期', type: 'basic', component: 'display', width: 110 },
  // 4月
  { id: 2013, name: 'monthlyData.april.plan', label: '4月-计划', type: 'basic', component: 'input', width: 110 },
  { id: 2014, name: 'monthlyData.april.samePeriod', label: '4月-同期', type: 'basic', component: 'display', width: 110 },
];

// reportTemplate 保持不变
export const reportTemplate = [
  { id: 1, category: '气温', name: '月平均高温', unit: '℃', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: true, requiredProperties: {businessModel: ['independent']}, columnFormulaOverrides: { 'totals.plan': 'AVG(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'AVG(2002, 2004, 2006, 2008, 2010, 2012, 2014)' } , validation: { soft: [] }},
  { id: 2, category: '气温', name: '月平均低温', unit: '℃', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: true, requiredProperties: {businessModel: ['independent']}, columnFormulaOverrides: { 'totals.plan': 'AVG(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'AVG(2002, 2004, 2006, 2008, 2010, 2012, 2014)' } , validation: { soft: [] } },
  { id: 3, category: '设备参数', name: '发电机组容量', unit: '万kW', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] }, columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] } },
  { id: 4, category: '设备参数', name: '燃煤锅炉装机容量', unit: 'MW', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','boiler_room','elec_boiler_room'] ,fuelType: ['coal'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 5, category: '设备参数', name: '电锅炉/热泵装机容量', unit: 'MW', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['electric'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 6, category: '产量', name: '发电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 7, category: '产量', name: '供热量', unit: 'GJ', type: 'calculated', formula: 'VAL(8)*2.951694+VAL(9)+VAL(10)+VAL(11)+VAL(12)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} , validation: { soft: [] }},
  { id: 8, category: '产量', name: '其中：1.供汽量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','gas_boiler_room'],special:['steam']} , validation: { soft: [] }},
  { id: 9, category: '产量', name: '2.高温水供热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','elec_boiler_room'] } , validation: { soft: [] }},
  { id: 10, category: '产量', name: '3.低真空供热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] ,special:['low vacuum']} , validation: { soft: [] }},
  { id: 11, category: '产量', name: '4.低温水供热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['boiler_room'],fuelType: ['coal']  } , validation: { soft: [] }},
  { id: 12, category: '产量', name: '5.电锅炉/热泵/供热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['electric'] } , validation: { soft: [] }},
  { id: 13, category: '销量', name: '售电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 14, category: '销量', name: '售汽量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],special:['steam'] } , validation: { soft: [] }},
  { id: 15, category: '销量', name: '关联交易汽量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],special:['related-rarty transaction'] } , validation: { soft: [] }},
  { id: 16, category: '销量', name: '关联交易高温水量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],special:['related-rarty transaction'] } , validation: { soft: [] }},
  { id: 17, category: '销量', name: '期末挂网面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] ,businessModel: ['independent','semi_independent']}, columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] } },
  { id: 18, category: '销量', name: '期末供暖收费面积', unit: '㎡', type: 'calculated', formula: 'VAL(19)+VAL(20)+VAL(21)+VAL(22)+VAL(23)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],businessModel: ['independent','semi_independent'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 19, category: '销量', name: '1.汽站面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],businessModel: ['independent','semi_independent'],special:['steam'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 20, category: '销量', name: '2.高温水站面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'],businessModel: ['independent','semi_independent'],special:['hotwater'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 21, category: '销量', name: '3.低真空站面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] ,businessModel: ['independent','semi_independent'],special:['low vacuum']}, columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' } , validation: { soft: [] }},
  { id: 22, category: '销量', name: '4.低温水供热面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['boiler_room'],fuelType: ['coal'] ,businessModel: ['independent','semi_independent'] } , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 23, category: '销量', name: '5.电锅炉/热泵面积', unit: '㎡', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['electric'] ,businessModel: ['independent','semi_independent']} , columnFormulaOverrides: { 'totals.plan': 'LAST_VAL(2001, 2003, 2005, 2007, 2009, 2011, 2013)', 'totals.samePeriod': 'LAST_VAL(2002, 2004, 2006, 2008, 2010, 2012, 2014)' }, validation: { soft: [] }},
  { id: 24, category: '销量', name: '高温水销售量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] ,special:['hotwater'] } , validation: { soft: [] }},
  { id: 25, category: '主要物料消耗量', name: '生产耗原煤量', unit: '吨', type: 'calculated', formula: 'VAL(26)+VAL(27)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 26, category: '主要物料消耗量', name: '其中：1.发电耗原煤量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric']} },
  { id: 27, category: '主要物料消耗量', name: '2.供热耗原煤量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 28, category: '主要物料消耗量', name: '耗标煤总量', unit: '吨', type: 'calculated', formula: 'VAL(29)+VAL(32)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 29, category: '主要物料消耗量', name: '其中：1.发电耗标煤量', unit: '吨', type: 'calculated', formula: 'VAL(30)+VAL(31)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric']} },
  { id: 30, category: '主要物料消耗量', name: '1.1煤折标煤耗量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric']} },
  { id: 31, category: '主要物料消耗量', name: '1.2油折标煤耗量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric']} },
  { id: 32, category: '主要物料消耗量', name: '2.供热耗标煤量', unit: '吨', type: 'calculated', formula: 'VAL(33)+VAL(34)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 33, category: '主要物料消耗量', name: '2.1煤折标煤耗量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 34, category: '主要物料消耗量', name: '2.2油折标煤耗量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','elec_boiler_room']} },
  { id: 35, category: '主要物料消耗量', name: '煤折标煤耗量', unit: '吨', type: 'calculated', formula: 'VAL(30)+VAL(33)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } },
  { id: 36, category: '主要物料消耗量', name: '耗油量', unit: '吨', type: 'calculated', formula: 'VAL(37)+VAL(38)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room'],fuelType: ['coal'] } },
  { id: 37, category: '主要物料消耗量', name: '其中：1.发电耗油量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] ,fuelType: ['coal']} },
  { id: 38, category: '主要物料消耗量', name: '2.供热耗油量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room'],fuelType: ['coal']} },
  { id: 39, category: '主要物料消耗量', name: '外购热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['purchased_heat'] } , validation: { soft: [] }},
  { id: 40, category: '主要物料消耗量', name: '耗水量', unit: '吨', type: 'calculated', formula: 'VAL(41)+VAL(42)+VAL(45)+VAL(46)+VAL(47)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 41, category: '主要物料消耗量', name: '其中：1.电厂耗水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','elec_boiler_room'] } },
  { id: 42, category: '主要物料消耗量', name: '2.电厂一次网补水量', unit: '吨', type: 'calculated', formula: 'VAL(43)+VAL(44)+VAL(192)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } },
  { id: 43, category: '主要物料消耗量', name: '2.1主城区高温水首站补水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] ,position:['downtown']} },
  { id: 44, category: '主要物料消耗量', name: '2.2主城区低真空补水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'],special:['low vacuum'] ,position:['downtown']} },
  { id: 192, category: '主要物料消耗量', name: '2.3北部单位热网补水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'],position:['north']} },
  { id: 45, category: '主要物料消耗量', name: '3.换热站补水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] ,special:['not_only_boiler']} },
  { id: 46, category: '主要物料消耗量', name: '4.燃煤锅炉房耗水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['boiler_room'] ,fuelType: ['coal'] } },
  { id: 47, category: '主要物料消耗量', name: '5.电锅炉/热泵耗水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['electric'] } },
  { id: 48, category: '主要物料消耗量', name: '耗自来水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 49, category: '主要物料消耗量', name: '耗再生水/井水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {special:['recycle_water']} },
  { id: 50, category: '主要物料消耗量', name: '耗酸量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 51, category: '主要物料消耗量', name: '耗碱量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 52, category: '主要物料消耗量', name: '耗石灰石量（粗）', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room'] ,special:['coarse powder']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 53, category: '主要物料消耗量', name: '耗石灰石粉量（细）', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 54, category: '主要物料消耗量', name: '耗氨水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 55, category: '主要物料消耗量', name: '耗氧化镁量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['boiler_room'],fuelType: ['coal'], businessModel: ['independent'] } , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 56, category: '主要物料消耗量', name: '耗脱硝剂量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['boiler_room'],fuelType: ['coal'], businessModel: ['independent'] } , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 57, category: '主要物料消耗量', name: '耗阻垢剂量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 58, category: '主要物料消耗量', name: '耗杀菌剂量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric']} , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.9', message: '本期计划不应超过同期的90%。' }] }},
  { id: 59, category: '主要物料消耗量', name: '耗钢球量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric'],special:['steel ball']} },
  { id: 60, category: '主要物料消耗量', name: '耗天然气量', unit: '万m3', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['natural_gas'] } , validation: { soft: [] }},
  { id: 61, category: '主要物料消耗量', name: '站内耗热量', unit: 'GJ', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] } },
  { id: 62, category: '主要物料消耗量', name: '耗电量', unit: '万kWh', type: 'calculated', formula: 'VAL(63)+VAL(68)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 63, category: '主要物料消耗量', name: '综合厂用电量', unit: '万kWh', type: 'calculated', formula: 'VAL(6)-VAL(13)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 64, category: '主要物料消耗量', name: '其中：1.非生产厂用电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 65, category: '主要物料消耗量', name: '2.生产厂用电量', unit: '万kWh', type: 'calculated', formula: 'VAL(66)+VAL(67)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 66, category: '主要物料消耗量', name: '2.1发电厂用电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 67, category: '主要物料消耗量', name: '2.2供热厂用电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','elec_boiler_room'] } , validation: { soft: [] }},
  { id: 68, category: '主要物料消耗量', name: '外购电量', unit: '万kWh', type: 'calculated', formula: 'VAL(69)+VAL(70)+VAL(71)+VAL(72)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 69, category: '主要物料消耗量', name: '其中：1.电厂外购电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric','elec_boiler_room'] } },
  { id: 70, category: '主要物料消耗量', name: '2.燃煤锅炉房外购电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['boiler_room'] ,fuelType: ['coal']} },
  { id: 71, category: '主要物料消耗量', name: '3.换热站外购电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] ,special:['not_only_boiler']} },
  { id: 72, category: '主要物料消耗量', name: '4.电锅炉/热泵外购电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['electric'] } },
  { id: 73, category: '主要物料消耗量', name: '脱硫脱销耗水量', unit: '吨', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room'] ,fuelType: ['coal']} },
  { id: 74, category: '主要物料消耗量', name: '脱硫脱硝耗电量', unit: '万kWh', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: {productionMethod: ['thermoelectric','elec_boiler_room'] ,fuelType: ['coal']} },
  { id: 75, category: '比率', name: '生产产出率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: '(VAL(7)+VAL(13)*36)/(29.308*VAL(28)+36*VAL(72)+VAL(39))', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} , validation: { soft: [{ rule: 'totals.plan >= totals.samePeriod ', message: '本期计划应不低于同期。' }] }},
  { id: 76, category: '比率', name: '综合产出率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: '(VAL(13)*36+VAL(14)*2.951694+VAL(24)+VAL(61))/(29.308*VAL(28)+36*VAL(72)+VAL(39))', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} , validation: { soft: [{ rule: 'totals.plan >= totals.samePeriod ', message: '本期计划应不低于同期。' }] }},
  { id: 77, category: '比率', name: '全厂热效率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: '(VAL(7)+VAL(13)*36)/(29.308*VAL(28)+36*VAL(72)+VAL(39))', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} , validation: { soft: [{ rule: 'totals.plan >= totals.samePeriod ', message: '本期计划应不低于同期。' }] }},
  { id: 78, category: '比率', name: '热电比', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: 'VAL(7)/(VAL(13)*36)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] }, validation: { soft: [] } },
  { id: 79, category: '比率', name: '热分摊比', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: 'VAL(32)/VAL(28)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 80, category: '比率', name: '发电设备利用率', unit: '%',displayFormat: { type: 'percentage', places: 2 }, type: 'calculated', formula: 'VAL(6)/VAL(3)/VAL(191)/24', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] }, validation: { soft: [{ rule: 'totals.plan >= totals.samePeriod ', message: '本期计划应不低于同期。' }] } },
  { id: 81, category: '比率', name: '供热设备利用率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: '(VAL(7)*1000-VAL(39))/(VAL(4)+VAL(5))/VAL(191)/24/3600', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} , validation: { soft: [] }},
  { id: 82, category: '单耗', name: '综合厂用电率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: 'VAL(63)/VAL(6)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] }, validation: { soft: [] } },
  { id: 83, category: '单耗', name: '发电厂用电率', unit: '%', displayFormat: { type: 'percentage', places: 2 },type: 'calculated', formula: 'VAL(66)/VAL(6)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } , validation: { soft: [] }},
  { id: 84, category: '单耗', name: '供热厂用电率', unit: 'kWh/GJ', type: 'calculated', formula: 'VAL(67)*10000/VAL(7)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] }, validation: { soft: [] } },
  { id: 85, category: '单耗', name: '发电标准煤耗率', unit: 'g/kWh', type: 'calculated', formula: 'VAL(29)*100/VAL(6)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } },
  { id: 86, category: '单耗', name: '供电标准煤耗率', unit: 'g/kWh', type: 'calculated', formula: 'VAL(29)*100/(VAL(6)-VAL(66))', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } },
  { id: 87, category: '单耗', name: '供热标准煤耗率', unit: 'kg/GJ', type: 'calculated', formula: 'VAL(32)*1000/VAL(7)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 88, category: '单耗', name: '发电水耗率', unit: '吨/万kWh', type: 'calculated', formula: '(VAL(41)-VAL(8))*(1-VAL(79))/VAL(6)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'] } },
  { id: 89, category: '单耗', name: '供热水耗率', unit: '吨/GJ', type: 'calculated', formula: '((VAL(41)-VAL(8))*VAL(79)+VAL(8))/VAL(7)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: {} },
  { id: 90, category: '单耗', name: '供暖热耗率', unit: 'GJ/㎡', type: 'calculated', formula: 'VAL(61)/VAL(18)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] } , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.95', message: '本期计划不应超过同期的95%。' }] }},
  { id: 91, category: '单耗', name: '供暖水耗率', unit: 'kg/㎡', type: 'calculated', formula: '(VAL(42)+VAL(45)+VAL(46)+VAL(47))*1000/VAL(18)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] }, validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.8', message: '本期计划不应超过同期的80%。' }] } },
  { id: 92, category: '单耗', name: '供暖电耗率', unit: 'kWh/㎡', type: 'calculated', formula: '(VAL(70)+VAL(71)+VAL(72))*10000/VAL(18)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'] } , validation: { soft: [{ rule: 'totals.plan <= totals.samePeriod * 0.95', message: '本期计划不应超过同期的95%。' }] }},
  { id: 93, category: '其它', name: '入炉煤低位发热量', unit: 'kJ/kg', type: 'calculated', formula: 'VAL(35)/VAL(25)*29308', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'] } , validation: { soft: [] }},
  { id: 94, category: '经济指标', name: '供热发电收入', unit: '万元', type: 'calculated', formula: 'VAL(95)+VAL(97)+VAL(99)+VAL(101)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 95, category: '经济指标', name: '暖收入', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] }, validation: { soft: [] } },
  { id: 96, category: '经济指标', name: '暖单价', unit: '元/㎡', type: 'calculated', formula: 'VAL(95)*10000/VAL(18)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 97, category: '经济指标', name: '电收入', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 98, category: '经济指标', name: '电单价', unit: '元/kWh', type: 'calculated', formula: 'VAL(97)/VAL(13)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['thermoelectric'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 99, category: '经济指标', name: '售汽收入', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] ,special:['steam'] }, validation: { soft: [] } },
  { id: 100, category: '经济指标', name: '汽平均单价', unit: '元/吨', type: 'calculated', formula: 'VAL(99)*10000/VAL(14)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 101, category: '经济指标', name: '售高温水收入', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 102, category: '经济指标', name: '高温水平均单价', unit: '元/GJ', type: 'calculated', formula: 'VAL(101)*10000/VAL(24)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { productionMethod: ['heating_company'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 103, category: '经济指标', name: '购热成本', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['purchased_heat'], businessModel: ['independent'] }, validation: { soft: [] } },
  { id: 104, category: '经济指标', name: '热单价', unit: '元/GJ', type: 'calculated', formula: 'VAL(103)*10000/VAL(39)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['purchased_heat'], businessModel: ['independent'] } , validation: { soft: [] }},
  { id: 105, category: '经济指标', name: '煤成本', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'], businessModel: ['independent'] } },
  { id: 106, category: '经济指标', name: '标煤单价', unit: '元/吨', type: 'calculated', formula: 'VAL(105)*10000/VAL(28)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['coal'], businessModel: ['independent'] } },
  { id: 107, category: '经济指标', name: '购电成本', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent','semi_independent'] } },
  { id: 108, category: '经济指标', name: '购电单价', unit: '元/kWh', type: 'calculated', formula: 'VAL(107)/VAL(68)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'] } },
  { id: 109, category: '经济指标', name: '水成本', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent','semi_independent'] } },
  { id: 110, category: '经济指标', name: '水单价', unit: '元/吨', type: 'calculated', formula: 'VAL(109)*10000/VAL(40)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'] } },
  { id: 111, category: '经济指标', name: '天然气成本', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'],fuelType: ['natural_gas'] } , validation: { soft: [] }},
  { id: 112, category: '经济指标', name: '购天然气单价', unit: '元/吨', type: 'calculated', formula: 'VAL(111)*10000/VAL(60)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { fuelType: ['natural_gas'] } , validation: { soft: [] }},
  { id: 113, category: '经济指标', name: '劳务费', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'] } },
  { id: 114, category: '经济指标', name: '抢修费', unit: '万元', type: 'basic', formula: null, style: { fontWeight: 'normal' }, samePeriodEditable: true, requiredProperties: { businessModel: ['independent'] } },
  { id: 115, category: '经济指标', name: '毛利', unit: '万元', type: 'calculated', formula: 'VAL(94)-VAL(103)-VAL(105)-VAL(107)-VAL(109)-VAL(111)-VAL(113)-VAL(114)', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { businessModel: ['independent'] }, validation: { soft: [{ rule: 'totals.plan >= totals.samePeriod', message: '本期计划应不低于同期。' }] } },
  { id: 191, category: '参考数据', name: '本月天数', unit: '天', type: 'basic', style: { fontWeight: 'bold' }, samePeriodEditable: false, requiredProperties: { special:['frozen'] },visible:true}
];

export const globalDisplayFormat =  { type: 'decimal', places: 2 };
