export const dashboardConfig = {
  title: '报表中心',
  columns: [
    { prop: 'groupName', label: '所属单位', width: 180 },
    { prop: 'name', label: '报表名称' },
    { prop: 'status', label: '填报状态', width: 120, type: 'status' },
    { prop: 'submittedAt', label: '提交时间', width: 180, type: 'datetime' },
    { prop: 'submittedBy', label: '提交人', width: 120, type: 'submitter' },
    { prop: 'history', label: '提交历史', width: 120, type: 'history' },
    { prop: 'actions', label: '操作', width: 120, type: 'actions' }
  ],
  statusMap: {
    new: { text: '未填写', className: 'status-new' },
    saved: { text: '已暂存', className: 'status-saved' },
    submitted: { text: '已提交', className: 'status-submitted' }
  }
};