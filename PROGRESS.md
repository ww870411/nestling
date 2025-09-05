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
