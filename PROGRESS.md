# Nestling 项目进度日志

## 初始记录

*   **时间:** 2025-09-06 10:00:00 (UTC+8)
*   **操作:** 初始化项目进度日志 (`PROGRESS.md`)。

---

## 项目概述

### 1. 项目目的

`nestling` (雏鸟) 是一个可配置的前端应用程序框架，旨在快速构建数据驱动的业务应用。从项目结构和参考文件来看，其核心功能是为特定业务（如当前的 "2025-2026年度供热计划"）提供数据填报、展示、校验和管理的用户界面。它旨在标准化和简化类似数据收集与管理项目的开发流程。

### 2. 技术架构与实现

本项目是基于现代前端技术栈构建的单页面应用 (SPA)。

*   **核心框架:** [Vue.js](https://vuejs.org/) (v3)
*   **构建工具:** [Vite](https://vitejs.dev/)
*   **UI 组件库:** [Element Plus](https://element-plus.org/)
*   **路由管理:** [Vue Router](https://router.vuejs.org/)
*   **状态管理:** [Pinia](https://pinia.vuejs.org/)
*   **代码规范:** ESLint 和 Prettier 用于保证代码质量和风格统一。
*   **数据处理:** `xlsx` 库被用于处理 Excel 文件，这表明应用可能支持 Excel 数据的导入导出功能。

### 3. 目录结构简述

*   `src/`: 存放核心源代码。
*   `src/views/`: 存放应用的视图组件，如登录页 (`LoginView.vue`)、数据看板 (`DashboardView.vue`) 和数据录入页 (`DataEntryView.vue`)。
*   `src/router/`: 配置页面路由。
*   `src/stores/`: 通过 Pinia 管理全局应用状态。
*   `src/projects/`: 存放特定业务项目的配置文件、菜单、校验规则、数据模板等。这种设计使得 `nestling` 框架可以轻松适配不同的业务需求，具有良好的可扩展性。
*   `参考文件/`: 包含业务需求说明书、设计原型和模板数据，为开发提供了清晰的指引。

---

## 变更日志

### 2025-09-06 10:15:00 (UTC+8)

*   **模块:** `heating_plan_2025-2026` (项目配置)
*   **修改内容:**
    1.  在 `src/projects/heating_plan_2025-2026/` 目录下创建了 `templates` 文件夹。
    2.  将原有的 `template.js` 拆分为 `templates/groupTemplate.js` 和 `templates/subsidiaryTemplate.js`，以支持不同类型的报表模板。
    3.  更新 `menu.js`，为每个 `tables` 对象添加 `template` 属性，显式指定其所使用的模板。
    4.  删除了根目录下的旧 `template.js` 文件。
*   **修改原因:**
    *   原设计中所有报表共享同一个模板，无法满足集团公司报表 (ID '0') 与其他子公司报表具有不同结构的业务需求。
*   **实现效果:**
    *   实现了报表与模板的灵活对应关系，提高了项目配置的可扩展性和可维护性。现在可以为不同报表轻松指定不同的数据结构和列定义。

### 2025-09-06 10:20:00 (UTC+8)

*   **模块:** `projects`, `stores` (核心架构)
*   **修改内容:**
    1.  **Bug修复:** 修正了 `src/projects/index.js` 中的 `loadProjectConfig` 函数，移除了对已删除的 `template.js` 文件的动态导入。
    2.  **代码重构:** 更新了 `src/stores/projectStore.js` 中的 `loadProject` action，使其不再从项目配置的顶层加载 `reportTemplate` 和 `fieldConfig`。
*   **修改原因:**
    *   在将模板具体化到 `menu.js` 的每个条目后，旧的项目配置加载逻辑 (`loadProjectConfig`) 出错，因为它仍在尝试加载一个不存在的全局模板文件。
*   **实现效果:**
    *   修复了因模板重构导致的应用程序加载失败的 bug。
    *   使状态管理 (`projectStore`) 与新的项目配置结构保持一致。

### 2025-09-06 10:25:00 (UTC+8)

*   **模块:** `views` (UI/视图层)
*   **修改内容:**
    1.  **Bug修复:** 修改了 `src/views/DataEntryView.vue` 组件的逻辑。
    2.  **代码重构:** 组件不再从全局 `projectStore` 中直接获取 `reportTemplate` 和 `fieldConfig`。而是通过一个 `computed` 属性，根据当前路由参数 (`route.params.id`) 在 `menuData` 中查找对应的表格项，并动态获取其 `template` 配置。
    3.  **代码重构:** 更新了组件内的 `watch` 监听器，以响应动态获取的模板配置和路由变化。
*   **修改原因:**
    *   上一次重构将模板配置移入了 `menuData` 的具体表格项中，导致 `DataEntryView.vue` 无法从全局 store 中获取到配置，从而显示“暂无数据”。
*   **实现效果:**
    *   修复了点击具体报表链接后无法显示表格数据的 bug。
    *   `DataEntryView.vue` 现在可以正确地为不同的报表加载和渲染各自独立的模板和配置。