import { defineStore } from 'pinia';
import { users } from '@/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: null, // 存放完整的用户对象
  }),

  getters: {
    // 根据角色和单位，计算出该用户有权访问的单位列表
    accessibleUnits() {
      if (!this.user) return [];

      if (this.user.globalRole === 'super_admin') {
        // 超级管理员可以访问所有单位
        return users.map(u => u.unit);
      }

      if (this.user.globalRole === 'regional_admin') {
        // 主城区管理员可以访问特定单位
        return ['主城区', '北海热电厂', '香海热电厂', '供热公司'];
      }

      // 普通用户只能访问自己的单位
      return [this.user.unit];
    },
  },

  actions: {
    login(username, password) {
      const foundUser = users.find(u => u.username === username && u.password === password);

      if (foundUser) {
        this.isAuthenticated = true;
        this.user = foundUser;
        // 将用户信息存入localStorage，用于持久化登录
        localStorage.setItem('user', JSON.stringify(foundUser));
        return true;
      } else {
        this.logout();
        return false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.user = null;
      localStorage.removeItem('user');
    },

    // 应用启动时，尝试从localStorage恢复登录状态
    tryAutoLogin() {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        this.isAuthenticated = true;
        this.user = JSON.parse(storedUser);
      }
    },
  },
});
