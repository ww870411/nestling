import { defineStore } from 'pinia';
import { projects, loadProjectConfig } from '@/projects';

export const useProjectStore = defineStore('project', {
  state: () => ({
    availableProjects: projects,
    currentProjectId: null,
    menuData: [],
    reportTemplate: [],
    fieldConfig: [],
    systemMessages: null,
    isLoading: false,
  }),

  getters: {
    isProjectLoaded: (state) => !!state.currentProjectId,
    currentProjectName: (state) => {
      const project = state.availableProjects.find(p => p.id === state.currentProjectId);
      return project ? project.name : '';
    }
  },

  actions: {
    async loadProject(projectId, force = false) {
      if (this.currentProjectId === projectId && !force) {
        return true;
      }

      this.isLoading = true;

      try {
        const config = await loadProjectConfig(projectId);
        if (config) {
          this.currentProjectId = projectId;
          this.menuData = Array.isArray(config.menuData)
            ? config.menuData
            : (config.menuData && Array.isArray(config.menuData.value) ? config.menuData.value : []);
          this.reportTemplate = Array.isArray(config.reportTemplate)
            ? config.reportTemplate
            : (config.reportTemplate && Array.isArray(config.reportTemplate.value) ? config.reportTemplate.value : []);
          this.fieldConfig = Array.isArray(config.fieldConfig)
            ? config.fieldConfig
            : (config.fieldConfig && Array.isArray(config.fieldConfig.value) ? config.fieldConfig.value : []);
          this.systemMessages = config.systemMessages || null;
          localStorage.setItem('currentProjectId', projectId);
          return true;
        } else {
          this.clearProject();
          return false;
        }
      } finally {
        this.isLoading = false;
      }
    },

    async loadPersistedProject() {
      const persistedId = localStorage.getItem('currentProjectId');
      if (persistedId && this.availableProjects.some(p => p.id === persistedId)) {
        return await this.loadProject(persistedId);
      }
      return false;
    },

    clearProject() {
      this.currentProjectId = null;
      this.menuData = [];
      this.reportTemplate = [];
      this.fieldConfig = [];
      this.systemMessages = null;
      localStorage.removeItem('currentProjectId');
    }
  },
});