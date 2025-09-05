import { createRouter, createWebHistory } from 'vue-router';
import { useProjectStore } from '@/stores/projectStore';

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
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';

  // Attempt to load project from local storage if it hasn't been loaded yet
  if (isAuthenticated && !projectStore.isProjectLoaded && localStorage.getItem('currentProjectId')) {
    await projectStore.loadPersistedProject();
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !isAuthenticated) {
    // Needs auth, but is not authenticated
    next({ name: 'login' });
  } else if (to.name === 'login' && isAuthenticated) {
    // Already authenticated, trying to access login page
    next({ name: 'projects' });
  } else if (to.meta.requiresProject && !projectStore.isProjectLoaded) {
    // Needs a project, but none is loaded
    // Exception: if we are already trying to go to the project selection page
    if (to.name !== 'projects') {
      next({ name: 'projects' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
