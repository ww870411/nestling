<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <h3>校验错误</h3>
      <div class="error-list">
        <ul>
          <li v-for="(error, index) in errors" :key="index">
            行 {{ error.rowIndex + 1 }}, 列 "{{ error.colName }}": {{ error.message }}
          </li>
        </ul>
      </div>
      <button @click="close" class="close-button">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  errors: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 80%;
  max-width: 600px;
}

.error-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.close-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  float: right;
}

.close-button:hover {
  background-color: #0056b3;
}
</style>
