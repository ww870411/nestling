<template>
  <div class="group-overview-container">
    <div class="header">
      <h2>集团公司 · 数据概览</h2>
      <div class="tips">展示“已提交/已批准”的汇总数据；未提交视为无数据。</div>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="主要指标对比图" name="charts">
        <div v-if="isLoading" class="loading">
          <el-icon class="is-loading" :size="26"><Loading /></el-icon>
          <span>正在加载概览数据...</span>
        </div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="charts-grid">
          <el-row :gutter="12">
            <el-col v-for="metric in metricsToShow" :key="metric" :xs="24" :sm="12" :md="8" :lg="8" :xl="6">
              <el-card shadow="always" class="chart-card">
                <div class="chart-title">{{ getMetricName(metric) }}</div>
                <div class="chart" :ref="setChartRef(metric)"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
      <el-tab-pane label="逻辑检查(BETA)" name="logic">
        <div class="report-container">
          <div class="report-toolbar">
            <div class="toolbar-item">
              <span>阈值：</span>
              <el-select v-model="thresholdPct" size="small" style="width: 120px">
                <el-option v-for="opt in thresholdOptions" :key="opt" :label="`${opt}%`" :value="opt" />
              </el-select>
            </div>
          </div>
          <div class="report-meta">
            <div>生成时间：{{ new Date().toLocaleString() }}</div>
            <div>范围：仅对“已提交/已批准（有数据）”的单位生成报告</div>
            <div>阈值：统一按 {{ thresholdPct }}% 严格判定（方向必须一致）</div>
          </div>
          <div class="report-grid">
            <div v-for="u in eligibleUnits" :key="u" class="report-card">
              <div class="report-card__header">
                <div class="report-unit">单位：{{ getUnitLabel(u) }}</div>
                <div class="report-status">状态：{{ getUnitStatusLabel(u) }}</div>
              </div>
              <div class="report-card__body">
                <template v-if="unitReports[u] && unitReports[u].length">
                  <div v-for="(item, idx) in unitReports[u]" :key="idx" class="report-item" :class="`level-${item.level}`">
                    <div class="report-item__title">{{ item.title }}</div>
                    <div class="report-item__desc">{{ item.desc }}</div>
                    <div class="report-item__evidence">{{ item.evidence }}</div>
                  </div>
                </template>
                <template v-else>
                  <div class="report-item ok">未发现问题</div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
// 数据概览（集团分单位对比）：基于表0（集团分单位汇总表）“已提交/已批准”数据
// 仅前端渲染，不修改任何既有接口。

import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';
import * as groupTemplate from '@/projects/heating_plan_2025-2026/templates/groupTemplate.js';
import * as subTemplate from '@/projects/heating_plan_2025-2026/templates/subsidiaryTemplate.js';
import * as projectMenu from '@/projects/heating_plan_2025-2026/menu.js';

const route = useRoute();
const projectStore = useProjectStore();

const projectId = computed(() => route.params.projectId);

// 约定单位顺序与显示名
const unitOrder = ['group','downtown','beihai','xianghai','heating_company','jinzhou','beifang','jinpu','zhuanghe','research'];
const unitDisplay = {
  group: '集团',
  downtown: '主城区',
  gufenbenbu: '股份本部',
  xianghai: '香海',
  heating_company: '供热公司',
  jinzhou: '金州',
  beifang: '北方',
  jinpu: '金普',
  zhuanghe: '庄河',
  research: '研究院',
};

// 主要指标（metricId）列表（顺序可调整）
// 移除 77（全厂热效率）
const metricsToShow = ref([6,13,7,14,24,18,25,28,40,68,113,114]);

// 页签
const activeTab = ref('charts');

const isLoading = ref(false);
const error = ref('');
const tableData = ref([]); // 表0数据（采纳“已提交/已批准”的汇总 tableData）
const unitStatus = ref({}); // 每个单位的表状态（submitted/approved）
const tablePropsMap = computed(() => {
  const map = {};
  (projectMenu.menuData || []).forEach(group => {
    (group.tables || []).forEach(t => {
      if (t && t.id) map[String(t.id)] = t.properties || {};
    });
  });
  return map;
});

// 从表0模板中抽取：各单位的 plan/samePeriod 对应的 fieldId
const planFieldIdByUnit = computed(() => {
  const map = {};
  const fields = groupTemplate.fieldConfig || [];
  for (const f of fields) {
    if (!f || typeof f.name !== 'string') continue;
    if (f.name.endsWith('.plan')) {
      const key = f.name.split('.')[0];
      if (unitOrder.includes(key)) map[key] = f.id;
    }
  }
  return map;
});

const samePeriodFieldIdByUnit = computed(() => {
  const map = {};
  const fields = groupTemplate.fieldConfig || [];
  for (const f of fields) {
    if (!f || typeof f.name !== 'string') continue;
    if (f.name.endsWith('.samePeriod')) {
      const key = f.name.split('.')[0];
      if (unitOrder.includes(key)) map[key] = f.id;
    }
  }
  return map;
});

// 指标名称：优先使用行上的 name，其次回退
const getMetricName = (metricId) => {
  const row = tableData.value.find(r => r.metricId === metricId);
  return row?.name || `指标 ${metricId}`;
};

// 拉取表0数据（采纳“已提交/已批准”的汇总数据）
const fetchTable0Overview = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const resp = await fetch(`/api/project/${projectId.value}/data/table/0`);
    if (!resp.ok) throw new Error('加载表0数据失败');
    const payload = await resp.json();
    // 表0接口返回 submit（通常聚合“已提交/已批准”的子表），本页采纳其中的 tableData
    const submitTableData = payload?.submit?.tableData;
    if (!Array.isArray(submitTableData)) {
      tableData.value = [];
      return;
    }
    tableData.value = submitTableData;
  } catch (e) {
    console.error(e);
    error.value = '概览数据加载失败，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
};

// 拉取各单位（子表）的状态信息，用于报告头部展示
// 业务约定映射：单位 -> 表ID数组（有的单位对应多张表）
const unitToTables = {
  group: ['1'],
  downtown: ['2','3'], // 主城区：表2、表3
  beihai: ['4'],
  xianghai: ['8'],
  heating_company: ['9','10'],
  jinzhou: ['11'],
  beifang: ['12'],
  jinpu: ['13'],
  zhuanghe: ['14'],
  research: ['15'],
};

const fetchUnitStatuses = async () => {
  try {
    const ids = Array.from(new Set(Object.values(unitToTables).flat()));
    if (!ids || ids.length === 0) return;
    const resp = await fetch(`/api/project/${projectId.value}/table_statuses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ids)
    });
    if (!resp.ok) return;
    const data = await resp.json();
    const map = {};
    Object.entries(unitToTables).forEach(([unitKey, tableIds]) => {
      const sts = (tableIds || []).map(tid => data?.[tid]?.status || 'new');
      map[unitKey] = sts; // 多表：保存数组
    });
    unitStatus.value = map;
  } catch (_) {}
};

// —— ECharts 渲染 ——
let echartsModule = null;
const chartRefs = new Map();
const setChartRef = (metricId) => (el) => {
  if (el) chartRefs.set(metricId, el);
};

// 等待元素具备非 0 尺寸后再初始化图表（最多重试 ~600ms）
const waitForSize = (el, tries = 20) => new Promise((resolve) => {
  const tick = () => {
    if (el && el.clientWidth > 0 && el.clientHeight > 0) return resolve(true);
    if (tries <= 0) return resolve(false);
    tries -= 1;
    requestAnimationFrame(() => setTimeout(tick, 30));
  };
  tick();
});

const getRowByMetric = (metricId) => tableData.value.find(r => r.metricId === metricId);

const buildSeriesData = (row, fieldIdMap) => {
  // 返回按 unitOrder 顺序的数值数组
  return unitOrder.map(u => {
    const fid = fieldIdMap[u];
    if (!fid) return 0;
    // row.values 是数组：[{ fieldId, value }]
    const cell = Array.isArray(row?.values) ? row.values.find(c => c.fieldId === fid) : null;
    const val = cell && typeof cell.value === 'number' ? cell.value : 0;
    return val;
  });
};

const makeOption = (metricId) => {
  const row = getRowByMetric(metricId) || {};
  const xCats = unitOrder.map(u => getUnitLabel(u));
  const statusTags = unitOrder.map(u => {
    const sts = unitStatus.value?.[u];
    let overall = 'new';
    if (Array.isArray(sts)) {
      overall = (sts.includes('approved') ? 'approved' : (sts.includes('submitted') ? 'submitted' : (sts.includes('saved') ? 'saved' : 'new')));
    } else if (typeof sts === 'string') {
      overall = sts;
    }
    if (overall === 'submitted') return 'submitted';
    if (overall === 'approved') return 'approved';
    if (overall === 'saved') return 'saved';
    return 'new';
  });
  const planData = buildSeriesData(row, planFieldIdByUnit.value);
  const sameData = buildSeriesData(row, samePeriodFieldIdByUnit.value);
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => (typeof v === 'number' ? v : '--'),
    },
    grid: { left: 8, right: 8, top: 20, bottom: 36, containLabel: true },
    legend: { data: ['本期计划', '同期完成'] },
    xAxis: {
      type: 'category',
      data: xCats,
      axisLabel: {
        interval: 0,
        hideOverlap: true,
        rotate: 28,
        formatter: (value, idx) => {
          const s = String(value || '');
          const maxLine = 6;
          const display = s.length > maxLine ? s.slice(0, maxLine) + '\n' + s.slice(maxLine) : s;
          const tag = statusTags[idx] || 'new';
          return `{${tag}|${display}}`;
        },
        rich: {
          approved: { color: '#303133' },
          submitted: { color: '#F56C6C' },
          saved: { color: '#909399' },
          new: { color: '#B4B4B4' }
        }
      }
    },
    yAxis: { type: 'value' },
    series: [
      { name: '本期计划', type: 'bar', data: planData, itemStyle: { color: '#5470C6' } },
      { name: '同期完成', type: 'bar', data: sameData, itemStyle: { color: '#91CC75' } },
    ],
  };
};

const renderAll = async () => {
  if (!echartsModule) {
    echartsModule = await import('echarts');
  }
  await nextTick();
  for (const mid of metricsToShow.value) {
    const el = chartRefs.get(mid);
    if (!el) continue;
    const ready = await waitForSize(el, 20);
    if (!ready) continue;
    let inst = echartsModule.getInstanceByDom(el);
    if (!inst) {
      inst = echartsModule.init(el);
    }
    inst.setOption(makeOption(mid), true);
    inst.resize();
  }
};

const handleResize = () => {
  if (!echartsModule) return;
  metricsToShow.value.forEach((mid) => {
    const el = chartRefs.get(mid);
    if (!el) return;
    const inst = echartsModule.getInstanceByDom(el);
    if (inst) inst.resize();
  });
};

onMounted(async () => {
  // 权限层面：菜单入口仅对“集团公司”可见，这里不再重复校验
  await fetchTable0Overview();
  await fetchUnitStatuses();
  await renderAll();
  window.addEventListener('resize', handleResize);
});

watch([tableData, metricsToShow], async () => {
  await renderAll();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

// —— 逻辑检查(BETA)：基于表0各单位 plan/samePeriod ——
const tracked = {
  // 产量
  gen: 6,
  heat: 7,
  // 能耗/消耗
  coal: 28,
  water: 40,
  pel: 68, // 外购电量
  oil: 36,
  ammonia: 54,
  limestoneFine: 53,
  // 比率
  eff: 77,
  heatWaterRate: 91,
  heatElecRate: 92,
};

const EPS = 1e-6;
// 阈值（百分比 3-15），默认 5
const thresholdOptions = Array.from({ length: 13 }, (_, i) => i + 3);
const thresholdPct = ref(Number(localStorage.getItem('logicCheckThresholdPct') || 5));
watch(thresholdPct, (v) => { localStorage.setItem('logicCheckThresholdPct', String(v)); });
const WIN = computed(() => (thresholdPct.value / 100));

const getRowById = (id) => tableData.value.find(r => r.metricId === id);
const getVal = (row, unitKey, map) => {
  const fid = map[unitKey];
  if (!row || !fid) return 0;
  const cell = Array.isArray(row.values) ? row.values.find(c => c.fieldId === fid) : null;
  const v = cell && typeof cell.value === 'number' ? cell.value : 0;
  return v;
};

const eligibleUnits = computed(() => {
  const genRow = getRowById(tracked.gen);
  const heatRow = getRowById(tracked.heat);
  return unitOrder.filter(u => {
    if (u === 'group') return false; // 跳过集团汇总本身
    const sts = unitStatus.value?.[u];
    // 仅对“已提交/已批准”的单位生成报告（多表单位：任一达标即可生成）
    const hasEligible = Array.isArray(sts) ? sts.some(s => s === 'submitted' || s === 'approved') : (sts === 'submitted' || sts === 'approved');
    if (!hasEligible) return false;
    // 另外确保至少有一项产量数据有数值
    const gPlan = getVal(genRow, u, planFieldIdByUnit.value);
    const gSame = getVal(genRow, u, samePeriodFieldIdByUnit.value);
    const hPlan = getVal(heatRow, u, planFieldIdByUnit.value);
    const hSame = getVal(heatRow, u, samePeriodFieldIdByUnit.value);
    return (Math.abs(gPlan) + Math.abs(gSame) + Math.abs(hPlan) + Math.abs(hSame)) > 0;
  });
});

const unitReports = computed(() => {
  const reports = {};
  const rows = Object.fromEntries(Object.entries(tracked).map(([k, id]) => [k, getRowById(id)]));
  const r = (plan, same) => {
    const base = Math.max(Math.abs(same), EPS);
    return (plan - same) / base;
  };
  const dirSame = (a, b) => a * b >= 0;
  const fmtPct = (x) => {
    if (typeof x !== 'number' || !isFinite(x)) return '--';
    const v = x * 100;
    const sign = v > 0 ? '+' : '';
    return `${sign}${v.toFixed(2)}%`;
  };
  const fmtNum = (n) => {
    if (typeof n !== 'number' || !isFinite(n)) return String(n ?? '');
    const abs = Math.abs(n);
    if (abs >= 1000) return n.toLocaleString('en-US', { maximumFractionDigits: 2 });
    return Number(n.toFixed(2)).toString();
  };

  eligibleUnits.value.forEach(u => {
    const items = [];
    const val = (row, kind) => kind === 'plan' ? getVal(row, u, planFieldIdByUnit.value) : getVal(row, u, samePeriodFieldIdByUnit.value);

    // 软校验降噪：取消“本期计划为0（可写指标）”的逻辑检查

    // 产量与能耗/消耗：方向一致 + 5%紧窗
    const pairs = [
      { a: rows.gen, b: rows.coal, name: '发电量 vs 耗标煤总量' },
      { a: rows.heat, b: rows.water, name: '供热量 vs 耗水量' },
      { a: rows.heat, b: rows.pel, name: '供热量 vs 外购电量' },
      { a: rows.gen, b: rows.oil, name: '发电量 vs 耗油量' },
      { a: rows.gen, b: rows.ammonia, name: '发电量 vs 耗氨水量' },
      { a: rows.gen, b: rows.limestoneFine, name: '发电量 vs 耗石灰石量（细）' },
    ];
    pairs.forEach(({ a, b, name }) => {
      if (!a || !b) return;
      const aS = val(a, 'same'); const aP = val(a, 'plan');
      const bS = val(b, 'same'); const bP = val(b, 'plan');
      if (Math.abs(aS) < EPS || Math.abs(bS) < EPS) return; // 小基数跳过
      const ra = r(aP, aS), rb = r(bP, bS);
      const aName = a.name || '指标A';
      const bName = b.name || '指标B';
      if (!dirSame(ra, rb)) {
        const small = (Math.abs(ra) <= 0.01 && Math.abs(rb) <= 0.01) ? '（幅度较小）' : '';
        items.push({
          level: 'p1',
          title: '方向不一致',
          desc: `${aName}与${bName}变动方向不一致${small}`,
          evidence: `${aName}：同期=${fmtNum(aS)}，本期=${fmtNum(aP)}（${fmtPct(ra)}）；${bName}：同期=${fmtNum(bS)}，本期=${fmtNum(bP)}（${fmtPct(rb)}）`
        });
      } else if (Math.abs(ra - rb) > WIN.value) {
        items.push({
          level: 'p2',
          title: `幅度差异超${thresholdPct.value}%`,
          desc: `${aName}与${bName}变动幅度差异超过${thresholdPct.value}%`,
          evidence: `${aName}：${fmtPct(ra)}；${bName}：${fmtPct(rb)}（差异=${fmtPct(ra - rb)}）`
        });
      }
    });

    // 比率类（5%紧阈值）
    const ratios = [
      { row: rows.eff, label: '全厂热效率' },
      { row: rows.heatWaterRate, label: '供暖水耗率' },
      { row: rows.heatElecRate, label: '供暖电耗率' },
    ];
    ratios.forEach(({ row, label }) => {
      if (!row) return;
      const sp = val(row, 'same'); const pl = val(row, 'plan');
      if (Math.abs(sp) < EPS) return;
      const rr = r(pl, sp);
      if (Math.abs(rr) > WIN.value) {
        items.push({ level: 'p2', title: `比率波动超${thresholdPct.value}%`, desc: `${label} 变化超过${thresholdPct.value}%`, evidence: `${label}：同期=${fmtNum(sp)}，本期=${fmtNum(pl)}（${fmtPct(rr)}）` });
      }
    });
    
    reports[u] = items;
  });
  return reports;
});

const getUnitLabel = (u) => (u === 'beihai' ? '北海' : (unitDisplay[u] || u));

const getUnitStatusLabel = (unitKey) => {
  const sts = unitStatus.value?.[unitKey];
  const toText = (s) => s === 'approved' ? '已批准' : s === 'submitted' ? '已提交（未批准）' : s === 'saved' ? '已暂存（未提交）' : '未提交';
  const tables = unitToTables[unitKey] || [];
  if (Array.isArray(sts)) {
    // 多表单位：逐表展示，例如 “表2：已提交（未批准）；表3：已批准”
    return tables.map((tid, idx) => `表${tid}：${toText(sts[idx] || 'new')}`).join('；');
  }
  // 单表单位
  const tid = tables[0];
  return `表${tid}：${toText(sts || 'new')}`;
};
</script>

<style scoped>
.group-overview-container { padding: 16px; }
.header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; }
.header .tips { color: #909399; font-size: 13px; }
.loading, .error { padding: 24px; color: #606266; display: flex; align-items: center; gap: 8px; }
.charts-grid { width: 100%; }
.chart-card { height: 260px; display: flex; flex-direction: column; }
.chart-title { font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #303133; }
.chart { height: 220px; width: 100%; }

/* 逻辑检查(BETA) 样式 */
.report-container { padding: 8px; }
.report-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.toolbar-item { display: flex; align-items: center; gap: 6px; color: #606266; font-size: 13px; }
.report-meta { color: #606266; font-size: 13px; margin-bottom: 8px; display: flex; gap: 16px; flex-wrap: wrap; }
.report-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; }
.report-card { border: 1px solid #dcdfe6; border-radius: 6px; background: #fff; overflow: hidden; }
.report-card__header { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: #f5f7fa; border-bottom: 1px solid #ebeef5; }
.report-unit { font-weight: 600; color: #303133; }
.report-status { font-size: 12px; color: #909399; }
.report-card__body { padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.report-item { border-left: 3px solid transparent; padding-left: 8px; }
.report-item.ok { color: #67C23A; }
.report-item.level-p1 { border-color: #F56C6C; }
.report-item.level-p2 { border-color: #E6A23C; }
.report-item.level-p3 { border-color: #409EFF; }
.report-item__title { font-weight: 600; color: #303133; margin-bottom: 2px; }
.report-item__desc { color: #606266; font-size: 13px; }
.report-item__evidence { color: #909399; font-size: 12px; }
</style>
