<template>
  <div class="project-selection-container">
    <el-card class="selection-card">
      <template #header>
        <div class="card-header">
          <span>请在下方选择填报项目</span>
        </div>
      </template>
      <div v-for="project in projects" :key="project.id" class="project-item">
        <el-button class="project-button" @click="selectProject(project.id)">
          {{ project.name }}
        </el-button>
      </div>
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="26"><Loading /></el-icon>
        <p>加载项目中...</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useProjectStore } from '@/stores/projectStore';
import { ElMessage } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';

const router = useRouter();
const projectStore = useProjectStore();
const { availableProjects: projects } = storeToRefs(projectStore);

const loading = ref(false);

const selectProject = async (projectId) => {
  loading.value = true;
  const success = await projectStore.loadProject(projectId, true);
  loading.value = false;

  if (success) {
    router.push({ name: 'dashboard', params: { projectId } });
  } else {
    ElMessage.error('项目加载失败，请检查配置或联系管理员。');
  }
};
</script>

<style scoped>
.project-selection-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.selection-card {
  width: 400px;
  position: relative;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}

.project-item {
  margin-bottom: 15px;
}

.project-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-overlay p {
  margin-top: 10px;
}
</style>
