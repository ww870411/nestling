<template>
  <div class="group-overview-container">
    <div class="header">
      <h2>集团公司 · 数据概览</h2>
      <div class="tips">仅展示已批准（approved）数据；未批准视为无数据。</div>
    </div>

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
  </div>
</template>

<script setup>
// 数据概览（集团分单位对比）：基于表0（集团分单位汇总表）已批准数据
// 仅前端渲染，不修改任何既有接口。

import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';
import * as groupTemplate from '@/projects/heating_plan_2025-2026/templates/groupTemplate.js';

const route = useRoute();
const projectStore = useProjectStore();

const projectId = computed(() => route.params.projectId);

// 约定单位顺序与显示名
const unitOrder = ['group','downtown','gufenbenbu','xianghai','jinzhou','beifang','jinpu','zhuanghe','research'];
const unitDisplay = {
  group: '集团',
  downtown: '主城区',
  gufenbenbu: '股份本部',
  xianghai: '香海',
  jinzhou: '金州',
  beifang: '北方',
  jinpu: '金普',
  zhuanghe: '庄河',
  research: '研究院',
};

// 主要指标（metricId）列表（顺序可调整）
// 移除 77（全厂热效率）
const metricsToShow = ref([6,13,7,14,24,18,25,28,40,68,113,114]);

const isLoading = ref(false);
const error = ref('');
const tableData = ref([]); // 已批准的表0数据（tableData 数组）

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

// 拉取表0数据（仅取 approved）
const fetchTable0Approved = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    const resp = await fetch(`/api/project/${projectId.value}/data/table/0`);
    if (!resp.ok) throw new Error('加载表0数据失败');
    const payload = await resp.json();
    // 表0接口返回 submit 聚合自子表 approved，本页仅采纳其中的 tableData
    const approvedTableData = payload?.submit?.tableData;
    if (!Array.isArray(approvedTableData)) {
      tableData.value = [];
      return;
    }
    tableData.value = approvedTableData;
  } catch (e) {
    console.error(e);
    error.value = '概览数据加载失败，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
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
  const xCats = unitOrder.map(u => unitDisplay[u]);
  const planData = buildSeriesData(row, planFieldIdByUnit.value);
  const sameData = buildSeriesData(row, samePeriodFieldIdByUnit.value);
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => (typeof v === 'number' ? v : '--'),
    },
    grid: { left: 8, right: 8, top: 20, bottom: 8, containLabel: true },
    legend: { data: ['本期计划', '同期完成'] },
    xAxis: { type: 'category', data: xCats, axisLabel: { interval: 0 } },
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
  await fetchTable0Approved();
  await renderAll();
  window.addEventListener('resize', handleResize);
});

watch([tableData, metricsToShow], async () => {
  await renderAll();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});
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
</style>
