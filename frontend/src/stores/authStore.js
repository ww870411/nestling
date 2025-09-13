import { defineStore } from 'pinia';

// The full list of units is temporarily hardcoded here for the 'super_admin' role.
// In a real-world scenario, this list should be fetched from a dedicated API endpoint.
const ALL_UNITS = [
  '集团公司', '主城区', '北海热电厂', '香海热电厂', '供热公司', 
  '金州热电', '北方热电', '金普热电', '庄河环海', '研究院'
];

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: null, // Stores the complete user object from the backend
  }),

  getters: {
    // Calculates the list of units accessible to the user based on their role and unit.
    accessibleUnits(state) {
      if (!state.user) return [];

      switch (state.user.globalRole) {
        case 'super_admin':
        case 'god':
          // Super admin can access all units.
          return ALL_UNITS;
        case 'regional_admin':
          // Downtown admin can access a specific set of units.
          return ['主城区', '北海热电厂', '香海热电厂', '供热公司'];
        default:
          // Regular users can only access their own unit.
          return [state.user.unit];
      }
    },
  },

  actions: {
    async login(username, password) {
      try {
        const response = await fetch(`/api/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
          const data = await response.json();
          this.isAuthenticated = true;
          this.user = data.user;
          // Persist user information in localStorage for auto-login
          localStorage.setItem('user', JSON.stringify(data.user));
          return true;
        } else {
          this.logout();
          return false;
        }
      } catch (error) {
        console.error('Login request failed:', error);
        this.logout();
        return false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.user = null;
      localStorage.removeItem('user');
    },

    // Tries to restore login state from localStorage when the app starts
    tryAutoLogin() {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        this.isAuthenticated = true;
        this.user = JSON.parse(storedUser);
      }
    },
  },
});
