import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useProjectStore } from './stores/projectStore';
import 'element-plus/dist/index.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

// Must instantiate store after pinia is used by the app
const projectStore = useProjectStore();

// Load persisted project before mounting the app
projectStore.loadPersistedProject().then(() => {
  app.use(router);
  app.mount('#app');
});
