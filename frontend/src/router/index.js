import { createRouter, createWebHistory } from 'vue-router';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';

import LoginView from '../views/LoginView.vue';
import MainLayout from '../layouts/MainLayout.vue';
import DashboardView from '../views/DashboardView.vue';
import DataEntryView from '../views/DataEntryView.vue';
import ProjectSelectionView from '../views/ProjectSelectionView.vue';
import GroupOverviewView from '../views/GroupOverviewView.vue';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/projects',
    name: 'projects',
    component: ProjectSelectionView,
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:projectId',
    component: MainLayout,
    meta: { requiresAuth: true, requiresProject: true },
    redirect: to => ({ name: 'dashboard', params: { projectId: to.params.projectId } }),
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView
      },
      {
        path: 'group-overview',
        name: 'group-overview',
        component: GroupOverviewView
      },
      {
        path: 'data-entry/:tableId',
        name: 'data-entry',
        component: DataEntryView
      }
    ]
  },
  // 将根路径重定向到项目选择页
  {
    path: '/',
    redirect: '/projects'
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach(async (to, from, next) => {
  const projectStore = useProjectStore();
  const authStore = useAuthStore();

  // 1. 恢复登录状态
  if (!authStore.isAuthenticated) {
    authStore.tryAutoLogin();
  }
  const isAuthenticated = authStore.isAuthenticated;

  // 2. 检查需要认证的路由
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // 3. 已登录用户访问登录页，重定向到项目选择页
  if (to.name === 'login' && isAuthenticated) {
    return next({ name: 'projects' });
  }

  // 4. 核心逻辑：处理需要项目上下文的路由
  if (to.meta.requiresProject) {
    const projectId = to.params.projectId;
    if (!projectId) {
      // 如果URL中没有项目ID，则重定向到项目选择页
      return next({ name: 'projects' });
    }

    // 如果请求的项目ID与当前加载的项目不一致，则加载新项目
    if (projectStore.currentProjectId !== projectId) {
      const success = await projectStore.loadProject(projectId);
      if (!success) {
        // 如果项目加载失败（例如，项目ID无效），重定向到项目选择页
        return next({ name: 'projects' });
      }
    }
  }
  
  // 5. 报表权限校验
  if (to.name === 'data-entry') {
    const tableId = to.params.tableId;
    const menuData = projectStore.menuData;
    const accessibleUnits = new Set(authStore.accessibleUnits);

    let targetUnit = null;
    for (const group of menuData) {
      const foundTable = group.tables.find(t => t.id === tableId);
      if (foundTable) {
        targetUnit = group.name;
        break;
      }
    }

    if (!targetUnit || !accessibleUnits.has(targetUnit)) {
      console.warn(`权限拒绝: 用户尝试访问ID为 ${tableId} 的报表, 但无权访问 ${targetUnit} 单位。`);
      // 重定向到当前项目的 dashboard
      return next({ name: 'dashboard', params: { projectId: to.params.projectId } });
    }
  }

  // 所有检查通过
  next();
});

export default router;
