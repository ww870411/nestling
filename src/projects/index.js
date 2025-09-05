// This file dynamically discovers and exports all project configurations.

const projectModules = import.meta.glob('./*/config.js', { eager: true });

export const projects = Object.values(projectModules).map(module => module.projectConfig);

export const loadProjectConfig = async (projectId) => {
  try {
    const menuModule = await import(`./${projectId}/menu.js`);
    const templateModule = await import(`./${projectId}/template.js`);
    return {
      menuData: menuModule.menuData,
      reportTemplate: templateModule.reportTemplate,
    };
  } catch (error) {
    console.error(`Failed to load project config for: ${projectId}`, error);
    return null;
  }
};
