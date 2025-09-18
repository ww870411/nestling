<template>
  <el-input
    :model-value="displayValue"
    @update:model-value="handleInput"
    @focus="handleFocus"
    @blur="handleBlur"
  />
</template>

<script setup>
import { ref, computed } from 'vue';
import { formatValue } from '@/utils/formatter.js';

const props = defineProps({
  modelValue: [String, Number],
  formatOptions: {
    type: Object,
    default: () => ({ type: 'decimal', places: 2 }) // Default format
  }
});

const emit = defineEmits(['update:modelValue', 'blur']);

const normalizeValue = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'number') return String(value);
  return String(value);
};

const isZeroValue = (value) => {
  const normalized = normalizeValue(value).replace(/,/g, '').trim();
  if (normalized === '') return false;
  const parsed = Number(normalized);
  return !Number.isNaN(parsed) && parsed === 0;
};


const isFocused = ref(false);

const displayValue = computed(() => {
  // If the input is focused, show the raw, unformatted value for easy editing.
  if (isFocused.value) {
    return props.modelValue;
  }

  // When not focused, show the formatted value.
  if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
    return '';
  }

  const optionsWithSeparator = {
    ...props.formatOptions,
    thousandSeparator: true
  };
  
  return formatValue(props.modelValue, optionsWithSeparator);
});

const handleInput = (value) => {
  // When user types, remove commas to maintain a clean underlying value.
  const rawValue = String(value).replace(/,/g, '');
  emit('update:modelValue', rawValue);
};

const handleFocus = () => {
  isFocused.value = true;
  if (isZeroValue(props.modelValue)) {
    emit('update:modelValue', '');
  }
};

const handleBlur = (event) => {
  isFocused.value = false;
  const normalized = normalizeValue(props.modelValue).trim();
  if (normalized === '') {
    emit('update:modelValue', '0');
  }
  // Pass the blur event up to the parent component to trigger calculations.
  emit('blur', event);
};
</script>
