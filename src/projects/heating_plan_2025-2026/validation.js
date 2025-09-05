const defaultBasicValidation = {
  hard: [
    { rule: 'isNumber', message: '必须为数字格式' },
    { rule: 'notEmpty', message: '此项为必填项，不能为空' }
  ],
  soft: [
    {
      rule: 'comparison',
      fieldA: 'totals.plan',
      operator: '<=',
      fieldB: 'totals.samePeriod',
      message: '本期计划不应超过同期完成'
    }
  ]
};

const defaultCalculatedValidation = {
  hard: [], // Calculated fields have no direct input to validate
  soft: [
    {
      rule: 'comparison',
      fieldA: 'totals.plan',
      operator: '<=',
      fieldB: 'totals.samePeriod',
      message: '本期计划不应超过同期完成'
    }
  ]
};

export const getDefaultValidation = (indicatorType) => {
  return indicatorType === 'basic' ? defaultBasicValidation : defaultCalculatedValidation;
};
