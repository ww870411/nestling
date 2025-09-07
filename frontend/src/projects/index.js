// This file dynamically discovers and exports all project configurations.

const projectModules = import.meta.glob('./*/config.js', { eager: true });

export const projects = Object.values(projectModules).map(module => module.projectConfig);

export const loadProjectConfig = async (projectId) => {
  try {
    const configModule = await import(`./${projectId}/config.js`);
    const menuModule = await import(`./${projectId}/menu.js`);
    // const templateModule = await import(`./${projectId}/template.js`); // DEPRECATED: Template is now part of menu.js
    return {
      menuData: menuModule.menuData,
      // reportTemplate: templateModule.reportTemplate, // DEPRECATED
      // fieldConfig: templateModule.fieldConfig, // DEPRECATED
      systemMessages: configModule.systemMessages,
    };
  } catch (error) {
    console.error(`Failed to load project config for: ${projectId}`, error);
    return null;
  }
};
