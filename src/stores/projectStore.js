import { defineStore } from 'pinia';
import { projects, loadProjectConfig } from '@/projects';

export const useProjectStore = defineStore('project', {
  state: () => ({
    availableProjects: projects,
    currentProjectId: null,
    menuData: [],
    reportTemplate: [],
    isLoading: false, // Add loading state
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

      this.isLoading = true; // Set loading to true

      try {
        const config = await loadProjectConfig(projectId);
        if (config) {
          this.currentProjectId = projectId;
          // Normalize to plain arrays in state
          this.menuData = Array.isArray(config.menuData)
            ? config.menuData
            : (config.menuData && Array.isArray(config.menuData.value) ? config.menuData.value : []);
          this.reportTemplate = Array.isArray(config.reportTemplate)
            ? config.reportTemplate
            : (config.reportTemplate && Array.isArray(config.reportTemplate.value) ? config.reportTemplate.value : []);
          localStorage.setItem('currentProjectId', projectId);
          return true;
        } else {
          this.currentProjectId = null;
          this.menuData = [];
          this.reportTemplate = [];
          localStorage.removeItem('currentProjectId');
          return false;
        }
      } finally {
        this.isLoading = false; // Set loading to false regardless of success or failure
      }
    },

    // Action to load the last selected project on app startup
    async loadPersistedProject() { // Make it async
      const persistedId = localStorage.getItem('currentProjectId');
      if (persistedId && this.availableProjects.some(p => p.id === persistedId)) {
        this.isLoading = true; // Set loading to true
        try {
          return await this.loadProject(persistedId); // Await the loadProject call
        } finally {
          this.isLoading = false; // Set loading to false
        }
      }
      return false; // Return false if no persisted project
    },

    clearProject() {
      this.currentProjectId = null;
      this.menuData = [];
      this.reportTemplate = [];
      localStorage.removeItem('currentProjectId');
    }
  },
});
