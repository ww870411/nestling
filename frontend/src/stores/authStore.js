import { defineStore } from 'pinia';

// The `users` import is temporarily needed for the `regional_admin` role logic.
// This should be replaced by a backend mechanism for managing unit lists.
import { users } from '@/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: null, // This will now store the user object from the backend
    token: null,
  }),

  getters: {
    // This getter is now fully functional with the updated backend User model.
    accessibleUnits() {
      if (!this.user) return [];

      if (this.user.global_role === 'super_admin') {
        // Super admin can access all units. We get this list from the mock data for now.
        return users.map(u => u.unit);
      }

      if (this.user.global_role === 'regional_admin') {
        // Regional admin can access a specific set of units.
        return ['主城区', '北海热电厂', '香海热电厂', '供热公司'];
      }

      // Normal users can only access their own unit.
      return [this.user.unit];
    },
  },

  actions: {
    async login(username, password) {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      try {
        const response = await fetch('http://localhost:8000/api/v1/token', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          this.token = data.access_token;
          localStorage.setItem('accessToken', data.access_token);
          
          // After getting the token, fetch the user details
          return await this.fetchUser();
        } else {
          this.logout();
          return false;
        }
      } catch (error) {
        console.error('Login failed:', error);
        this.logout();
        return false;
      }
    },

    async fetchUser() {
      if (!this.token) {
        return false;
      }
      try {
        const response = await fetch('http://localhost:8000/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${this.token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          this.isAuthenticated = true;
          this.user = userData;
          // Also save user to localStorage for persistence across page reloads
          localStorage.setItem('user', JSON.stringify(userData));
          return true;
        } else {
          this.logout();
          return false;
        }
      } catch (error) {
        console.error('Fetching user failed:', error);
        this.logout();
        return false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.user = null;
      this.token = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
    },

    async tryAutoLogin() {
      const storedToken = localStorage.getItem('accessToken');
      if (storedToken) {
        this.token = storedToken;
        // If token exists, try to fetch user data
        await this.fetchUser();
      } else {
        // Fallback for older sessions, try to load user from localStorage directly
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          this.user = JSON.parse(storedUser);
          this.isAuthenticated = true;
        }
      }
    },
  },
});
