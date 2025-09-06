import { createRouter, createWebHistory } from 'vue-router';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';

import LoginView from '../views/LoginView.vue';
import MainLayout from '../layouts/MainLayout.vue';
import DashboardView from '../views/DashboardView.vue';
import DataEntryView from '../views/DataEntryView.vue';
import ProjectSelectionView from '../views/ProjectSelectionView.vue';

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
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true, requiresProject: true },
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView
      },
      {
        path: 'data-entry/:id',
        name: 'data-entry',
        component: DataEntryView
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach(async (to, from, next) => {
  const projectStore = useProjectStore();
  const authStore = useAuthStore();

  // 尝试从localStorage恢复登录状态
  if (!authStore.isAuthenticated) {
    authStore.tryAutoLogin();
  }

  const isAuthenticated = authStore.isAuthenticated;

  // 尝试从localStorage加载项目配置
  if (isAuthenticated && !projectStore.isProjectLoaded && localStorage.getItem('currentProjectId')) {
    await projectStore.loadPersistedProject();
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  // 1. 检查是否需要认证
  if (requiresAuth && !isAuthenticated) {
    return next({ name: 'login' });
  }

  // 2. 检查是否已登录就不要去登录页
  if (to.name === 'login' && isAuthenticated) {
    return next({ name: 'projects' });
  }

  // 3. 检查是否需要项目但未加载
  if (to.meta.requiresProject && !projectStore.isProjectLoaded) {
    return next({ name: 'projects' });
  }

  // 4. 核心权限校验：检查用户是否有权访问此报表
  if (to.name === 'data-entry') {
    const tableId = to.params.id;
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
      // 如果找不到报表，或者报表所属的单位不在用户的可访问列表内
      console.warn(`权限拒绝: 用户尝试访问ID为 ${tableId} 的报表, 但无权访问 ${targetUnit} 单位。`);
      return next({ name: 'dashboard' }); // 重定向到首页
    }
  }

  // 所有检查通过
  next();
});

export default router;
