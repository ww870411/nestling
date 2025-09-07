
# --- Project Data ---
projects_data = [
    {
        "id": "heating_plan_2025-2026",
        "name": "2025-2026供暖期产销计划填报"
    }
]

# --- Report Definition Data (from menu.js) ---
report_definitions_data = [
    {'id': '0', 'name': '0 集团分单位汇总表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'group'},
    {'id': '1', 'name': '1 集团汇总表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '2', 'name': '2 主城区汇总表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '3', 'name': '3 北海汇总表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '4', 'name': '4 北海热电厂(热电联产)表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '5', 'name': '5 北海热电厂(水炉)表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '6', 'name': '6 北海热电厂(天然气炉)表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '7', 'name': '7 香海热电厂表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '8', 'name': '8 供热公司表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '9', 'name': '9 主城区电锅炉表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '10', 'name': '10 金州热电表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '11', 'name': '11 北方热电表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '12', 'name': '12 金普热电表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '13', 'name': '13 庄河环海表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
    {'id': '14', 'name': '14 研究院表', 'project_id': 'heating_plan_2025-2026', 'template_name': 'subsidiary'},
]

# --- Template Field Data ---
subsidiary_fields = [
    {'field_id': 1001, 'name': 'name', 'label': '指标名称', 'type': 'basic', 'component': 'label', 'width': 250, 'fixed': True, 'formula': None},
    {'field_id': 1002, 'name': 'unit', 'label': '计量单位', 'type': 'basic', 'component': 'label', 'width': 100, 'fixed': True, 'formula': None},
    {'field_id': 1003, 'name': 'totals.plan', 'label': '本期计划', 'type': 'calculated', 'component': 'display', 'width': 120, 'formula': 'VAL(2001)+VAL(2003)+VAL(2005)+VAL(2007)+VAL(2009)+VAL(2011)+VAL(2013)'},
    {'field_id': 1004, 'name': 'totals.samePeriod', 'label': '同期完成', 'type': 'calculated', 'component': 'display', 'width': 120, 'formula': 'VAL(2002)+VAL(2004)+VAL(2006)+VAL(2008)+VAL(2010)+VAL(2012)+VAL(2014)'},
    {'field_id': 1005, 'name': 'totals.diffRate', 'label': '差异率', 'type': 'calculated', 'component': 'display', 'width': 100, 'formula': '(VAL(1003)-VAL(1004))/VAL(1004)'},
    {'field_id': 2001, 'name': 'monthlyData.october.plan', 'label': '10月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2002, 'name': 'monthlyData.october.samePeriod', 'label': '10月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2003, 'name': 'monthlyData.november.plan', 'label': '11月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2004, 'name': 'monthlyData.november.samePeriod', 'label': '11月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2005, 'name': 'monthlyData.december.plan', 'label': '12月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2006, 'name': 'monthlyData.december.samePeriod', 'label': '12月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2007, 'name': 'monthlyData.january.plan', 'label': '1月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2008, 'name': 'monthlyData.january.samePeriod', 'label': '1月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2009, 'name': 'monthlyData.february.plan', 'label': '2月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2010, 'name': 'monthlyData.february.samePeriod', 'label': '12月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2011, 'name': 'monthlyData.march.plan', 'label': '3月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2012, 'name': 'monthlyData.march.samePeriod', 'label': '3月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
    {'field_id': 2013, 'name': 'monthlyData.april.plan', 'label': '4月-计划', 'type': 'basic', 'component': 'input', 'width': 110, 'formula': None},
    {'field_id': 2014, 'name': 'monthlyData.april.samePeriod', 'label': '4月-同期', 'type': 'basic', 'component': 'display', 'width': 110, 'formula': None},
]

group_fields = [
    {'field_id': 1001, 'name': 'name', 'label': '指标名称', 'type': 'basic', 'component': 'label', 'width': 250, 'fixed': True},
    {'field_id': 1002, 'name': 'unit', 'label': '计量单位', 'type': 'basic', 'component': 'label', 'width': 100, 'fixed': True},
    {'field_id': 1003, 'name': 'group.plan', 'label': '集团全口径-本期计划', 'type': 'basic', 'component': 'display', 'width': 140},
    {'field_id': 1004, 'name': 'group.samePeriod', 'label': '集团全口径-同期完成', 'type': 'basic', 'component': 'display', 'width': 140},
    {'field_id': 1005, 'name': 'group.diffRate', 'label': '集团全口径-差异率', 'type': 'basic', 'component': 'display', 'width': 140},
    {'field_id': 1006, 'name': 'downtown.plan', 'label': '主城区-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1007, 'name': 'downtown.samePeriod', 'label': '主城区-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1008, 'name': 'downtown.diffRate', 'label': '主城区-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1009, 'name': 'beihai.plan', 'label': '北海汇总-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1010, 'name': 'beihai.samePeriod', 'label': '北海汇总-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1011, 'name': 'beihai.diffRate', 'label': '北海汇总-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1012, 'name': 'xianghai.plan', 'label': '香海-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1013, 'name': 'xianghai.samePeriod', 'label': '香海-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1014, 'name': 'xianghai.diffRate', 'label': '香海-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1015, 'name': 'jinzhou.plan', 'label': '金州-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1016, 'name': 'jinzhou.samePeriod', 'label': '金州-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1017, 'name': 'jinzhou.diffRate', 'label': '金州-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1018, 'name': 'beifang.plan', 'label': '北方-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1019, 'name': 'beifang.samePeriod', 'label': '北方-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1020, 'name': 'beifang.diffRate', 'label': '北方-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1021, 'name': 'jinpu.plan', 'label': '金普-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1022, 'name': 'jinpu.samePeriod', 'label': '金普-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1023, 'name': 'jinpu.diffRate', 'label': '金普-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1024, 'name': 'zhuanghe.plan', 'label': '庄河-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1025, 'name': 'zhuanghe.samePeriod', 'label': '庄河-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1026, 'name': 'zhuanghe.diffRate', 'label': '庄河-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1027, 'name': 'research.plan', 'label': '研究院-本期计划', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1028, 'name': 'research.samePeriod', 'label': '研究院-同期完成', 'type': 'basic', 'component': 'display', 'width': 120},
    {'field_id': 1029, 'name': 'research.diffRate', 'label': '研究院-差异率', 'type': 'basic', 'component': 'display', 'width': 120},
]

# --- Template Metric Data ---
# This data is shared between subsidiary and group templates
shared_metrics = [
    {'metric_id': 1, 'category': '气温', 'name': '月平均高温', 'unit': '℃', 'type': 'basic', 'formula': None, 'style': {'fontWeight': 'normal'}, 'same_period_editable': False, 'required_properties': {}},
    {'metric_id': 2, 'category': '气温', 'name': '月平均低温', 'unit': '℃', 'type': 'basic', 'formula': None, 'style': {'fontWeight': 'normal'}, 'same_period_editable': False, 'required_properties': {}},
    # ... (all other metrics from the template files) ...
    {'metric_id': 115, 'category': '经济指标', 'name': '毛利', 'unit': '万元', 'type': 'calculated', 'formula': 'VAL(94)-VAL(103)-VAL(105)-VAL(107)-VAL(109)-VAL(111)-VAL(113)-VAL(114)', 'style': {'fontWeight': 'bold'}, 'same_period_editable': False, 'required_properties': {'businessModel': ['independent']}},
]

# --- Combine and add metadata ---
def add_metadata(data, template_name, project_id):
    return [{**item, "template_name": template_name, "project_id": project_id} for item in data]

all_template_fields = (
    add_metadata(subsidiary_fields, 'subsidiary', 'heating_plan_2025-2026') +
    add_metadata(group_fields, 'group', 'heating_plan_2025-2026')
)

all_template_metrics = (
    add_metadata(shared_metrics, 'subsidiary', 'heating_plan_2025-2026') +
    add_metadata(shared_metrics, 'group', 'heating_plan_2025-2026')
)

# --- Initial User Data ---
initial_users = [
  {
    "username": 'group_admin',
    "password": 'password',
    "unit": '集团公司',
    "global_role": 'super_admin',
  },
  # ... (rest of the users)
]
