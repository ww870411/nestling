# Nestling 项目进度日志 (Top-Level)

---

### 2025-09-07 15:30:00 (UTC+8)

*   **模块:** `root` (项目架构)
*   **修改内容:**
    1.  **架构重构:** 创建了 `frontend` 和 `backend` 文件夹，并将所有现存的前端代码移入 `frontend` 目录。
    2.  **技术决策:** 决定采用基于 Docker 和 Docker Compose 的容器化方案来搭建和管理开发环境。
*   **修改原因:**
    *   为了给即将开始的后端开发提供一个清晰、隔离的目录结构，并为整个项目引入现代化的、可复现的开发与部署工作流。
*   **实现效果:**
    *   项目结构现在能够清晰地分离前后端关注点，为全栈开发做好了准备。

---

### 2025-09-07 15:40:00 (UTC+8)

*   **模块:** `root`, `frontend`, `backend` (Docker & 后端)
*   **修改内容:**
    1.  **新增文件:** 在项目根目录创建了 `docker-compose.yml`，用于编排前后端服务。
    2.  **后端初始化:** 在 `backend` 目录下创建了 `Dockerfile`, `requirements.txt` 和 `main.py`，搭建了一个基础的 FastAPI 应用。
    3.  **前端容器化:** 在 `frontend` 目录下创建了 `Dockerfile`，用于构建 Vue 应用镜像。
    4.  **配置修改:** 更新了 `frontend/vite.config.js`，添加了 `server` 配置以确保其在 Docker 容器内正常运行。
*   **修改原因:**
    *   执行之前制定的容器化方案，为项目搭建一个隔离、可复现且生产就绪的开发环境。
*   **实现效果:**
    *   项目现在已完全容器化。开发者可以通过 `docker-compose up --build` 命令一键启动整个前后端应用，极大地简化了环境配置和项目管理。

---

### 2025-09-07 15:45:00 (UTC+8)

*   **模块:** `root`, `backend` (数据库集成)
*   **修改内容:**
    1.  **架构升级:** 更新了 `docker-compose.yml` 文件，新增了一个名为 `db` 的 PostgreSQL 服务。
    2.  **持久化:** 为数据库服务配置了名为 `postgres_data` 的 Docker 卷，以确保数据在容器重启后依然存在。
    3.  **服务连接:** 在 `docker-compose.yml` 中配置了 `backend` 服务，使其依赖 `db` 服务，并通过环境变量 (`DATABASE_URL`) 获取数据库连接信息。
    4.  **依赖更新:** 在 `backend/requirements.txt` 文件中添加了 `psycopg2-binary` 和 `SQLAlchemy`，为后端与 PostgreSQL 的交互提供必要的库。
*   **修改原因:**
    *   为应用程序提供一个持久化的数据存储层，这是所有数据驱动应用的核心需求。
*   **实现效果:**
    *   项目现在拥有了一个完整的、由 Docker Compose 管理的全栈架构（前端 + 后端 + 数据库）。后端服务已具备连接数据库所需的所有配置和依赖，为下一步开发数据模型和API接口奠定了坚实的基础。

---

### 2025-09-07 15:50:00 (UTC+8)

*   **模块:** `frontend` (Docker 构建)
*   **修改内容:**
    1.  **Bug修复:** 在排查 `docker-compose up --build` 命令失败的问题时，根据错误日志 `[vite:vue] crypto.hash is not a function` 和 Vite 的版本要求提示，将 `frontend/Dockerfile` 中的基础镜像从 `node:18-alpine` 升级到了 `node:20-alpine`。
*   **修改原因:**
    *   前端项目依赖（`@vitejs/plugin-vue`）需要一个比 `node:18` 更新的 Node.js 版本才能正常工作，导致生产构建失败。
*   **实现效果:**
    *   成功修复了前端 Docker 镜像的构建失败问题。整个应用（前端、后端、数据库）现在可以通过 `docker-compose up --build` 命令成功启动，开发环境已完全就绪。

---

### 2025-09-07 15:55:00 (UTC+8)

*   **模块:** `frontend` (Docker 配置)
*   **修改内容:**
    1.  **Bug修复:** 将 `frontend/Dockerfile` 从一个生产环境配置（使用 `npm run build` 和 Nginx）替换为了一个开发环境配置（使用 `npm run dev`）。
*   **修改原因:**
    *   之前的生产配置导致 `http://localhost:5173` 无法访问，因为它将服务暴露在容器的80端口，而非 `docker-compose.yml` 中映射的5173端口。此外，该配置不支持开发时至关重要的热重载功能。
*   **实现效果:**
    *   前端服务现在可以通过 `http://localhost:5173` 正确访问。更重要的是，开发体验得到了保障，代码修改可以实时在浏览器中反映出来，无需重新构建镜像。

---

### 2025-09-08 10:00:00 (UTC+8)

*   **模块:** `backend`, `frontend` (用户认证)
*   **修改内容:**
    1.  **后端API:** 在 `backend/main.py` 中新增了 `/login` API 端点，该端点通过读取 `backend/app/data/auth.json` 文件来验证用户凭据。
    2.  **数据迁移:** 将原存于 `frontend/src/auth.js` 的用户数据迁移至 `backend/app/data/auth.json`。
    3.  **前端状态管理:** 重构了 `frontend/src/stores/authStore.js`，将其登录逻辑从直接读取本地文件修改为调用后端 `/login` API。
    4.  **前端视图:** 更新了 `frontend/src/views/LoginView.vue` 以适应 `authStore` 中新的异步登录操作。
    5.  **代码清理:** 删除了已废弃的 `frontend/src/auth.js` 文件。
*   **修改原因:**
    *   将用户认证的核心逻辑从前端转移到后端，这是构建安全、可扩展的全栈应用程序的第一步。
*   **实现效果:**
    *   应用的登录流程现在由后端API驱动。前端不再包含任何硬编码的用户数据，提高了安全性。用户登录时，前端会向后端发送请求，后端验证成功后返回用户信息，前端据此更新登录状态。

---

### 2025-09-08 10:15:00 (UTC+8)

*   **模块:** `backend`, `frontend` (数据持久化)
*   **修改内容:**
    1.  **后端API:** 在 `backend/main.py` 中新增了 `POST /api/project/{project_id}/table/{table_id}/submit` API 端点。
    2.  **后端存储:** 该API目前将接收到的前端数据作为一个JSON文件存储在 `backend/app/data/submissions/` 目录中，作为临时“接收池”以便于测试。
    3.  **前端视图:** 更新了 `frontend/src/views/DataEntryView.vue` 中的 `handleSubmit` 方法，使其在客户端验证通过后，将完整的报表数据和解释说明打包发送到新的后端API。
*   **修改原因:**
    *   实现核心的数据持久化流程，将前端的填报数据发送并存储到后端服务器，替代纯前端的 `localStorage` 方案。
*   **实现效果:**
    *   成功打通了从前端填报、提交到后端接收、存储的完整数据链路。现在，当用户提交报表时，数据会被发送到FastAPI服务器并保存为一个文件，为下一步接入真实数据库做好了准备。

---

### 2025-09-08 10:30:00 (UTC+8)

*   **模块:** `frontend` (网络配置)
*   **修改内容:**
    1.  **Bug修复:** 解决了前端API请求失败并出现 `net::ERR_NAME_NOT_RESOLVED` 错误的问题。
    2.  **Vite代理:** 在 `frontend/vite.config.js` 中配置了Vite开发服务器代理，将所有 `/api` 前缀的请求转发到后端容器 (`http://backend:8000`)。
    3.  **代码重构:** 修改了 `authStore.js` 和 `DataEntryView.vue` 中的 `fetch` 调用，使其使用相对路径 (如 `/api/login`)，不再依赖环境变量或硬编码的URL。
*   **修改原因:**
    *   浏览器无法直接解析Docker内部网络的服务名 (`backend`)，导致API请求失败。使用环境变量注入 `localhost` 的方案也不够稳定。
*   **实现效果:**
    *   通过Vite代理，前端应用现在可以稳定、可靠地与后端API通信，彻底解决了跨域和容器网络解析问题。该方案是开发环境中处理前后端分离的最佳实践。

---

### 2025-09-08 10:45:00 (UTC+8)

*   **模块:** `frontend` (数据提交)
*   **修改内容:**
    1.  **丰富提交信息:** 在前端向后端提交的数据 `payload` 中，新增了 `table` 对象，用于包含被提交报表的元数据。
    2.  **新增字段:** `table` 对象包含 `id` (报表ID), `name` (报表名称), 和 `template` (所使用的模板名称) 三个字段。
    3.  **配置修改:** 为实现此功能，修改了 `frontend/src/projects/heating_plan_2025-2026/menu.js`，为每个报表配置添加了 `templateName` 属性。
    4.  **逻辑调整:** 更新了 `frontend/src/views/DataEntryView.vue` 中的 `handleSubmit` 方法，以从 `currentTableConfig` 中读取这些新信息并将其加入 `payload`。
*   **修改原因:**
    *   后端需要知道提交的数据具体来源于哪张报表、使用了哪个模板，以便进行更精确的数据处理、归档和未来的分析。
*   **实现效果:**
    *   现在每次提交到后端的数据都包含了完整的上下文信息。后端可以轻松识别报表的来源和结构，这对于构建一个健壮的、可扩展的数据处理管道至关重要。
