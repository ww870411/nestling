<template>
  <div class="login-page">
    <div class="visual-panel">
      <div class="visual-shapes">
        <span class="shape shape-circle"></span>
        <span class="shape shape-square"></span>
        <span class="shape shape-triangle"></span>
        <span class="shape shape-ring"></span>
      </div>
      <div class="visual-overlay">
        <h1 class="visual-title">大连洁净能源集团有限公司</h1>
        <p class="visual-subtitle" style="text-align: center" >生产数据在线填报系统</p>

      </div>
    </div>
    <div class="form-panel">
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        label-position="left"
      >
        <div class="form-header">
          <h3 class="form-title" style="text-align: center">用户登录</h3>
          <p class="form-subtitle" style="text-align: center">请填写用户信息</p>
        </div>

        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            name="username"
            type="text"
            tabindex="1"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            show-password
            placeholder="密码"
            name="password"
            tabindex="2"
          />
        </el-form-item>

        <el-form-item prop="captcha">
          <div class="captcha-wrapper">
            <el-input
              v-model="loginForm.captcha"
              placeholder="验证码"
              name="captcha"
              tabindex="3"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-image" @click="generateCaptcha" title="点击刷新">
              <p>{{ captchaCode }}</p>
            </div>
          </div>
        </el-form-item>

        <el-button :loading="loading" type="primary" class="login-button" @click.prevent="handleLogin">
          登 录
        </el-button>
      </el-form>
      <div class="form-footer">© 大连洁净能源集团有限公司 经济运行部</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { ElMessage } from 'element-plus';

const router = useRouter();
const authStore = useAuthStore();

const loginForm = ref({
  username: '',
  password: '',
  captcha: ''
});

const captchaCode = ref('');

const loginRules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
});

const loading = ref(false);
const loginFormRef = ref(null);

const generateCaptcha = () => {
  let result = '';
  for (let i = 0; i < 4; i++) {
    result += Math.floor(Math.random() * 10).toString();
  }
  captchaCode.value = result;
};

onMounted(() => {
  generateCaptcha();
});

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      if (loginForm.value.captcha !== captchaCode.value) {
        ElMessage.error('验证码不正确');
        generateCaptcha();
        return;
      }

      loading.value = true;
      try {
        const loginSuccess = await authStore.login(loginForm.value.username, loginForm.value.password);
        if (loginSuccess) {
          ElMessage.success('登录成功');
          router.push({ name: 'projects' });
        } else {
          ElMessage.error('用户名或密码错误');
          generateCaptcha();
        }
      } catch (error) {
        ElMessage.error('登录请求失败，请稍后重试。');
        generateCaptcha();
      } finally {
        loading.value = false;
      }
    } else {
      return false;
    }
  });
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #3c7ade 0%, #66a7ff 45%, #9ed6ff 100%);
  color: #fff;
}

.visual-panel {
  flex: 1.3;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  overflow: hidden;
}

.visual-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  display: block;
  opacity: 0.4;
  filter: drop-shadow(0 18px 28px rgba(0, 0, 0, 0.25));
}

.shape-circle {
  width: 220px;
  height: 220px;
  top: 15%;
  left: 10%;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0));
  animation: float-slow 12s ease-in-out infinite;
}

.shape-square {
  width: 120px;
  height: 120px;
  bottom: 18%;
  left: 22%;
  transform: rotate(18deg);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0));
  border: 1px solid rgba(255, 255, 255, 0.35);
  animation: float-medium 9s ease-in-out infinite;
}

.shape-triangle {
  width: 0;
  height: 0;
  top: 18%;
  right: 20%;
  border-left: 60px solid transparent;
  border-right: 60px solid transparent;
  border-bottom: 110px solid rgba(255, 255, 255, 0.2);
  filter: drop-shadow(0 12px 18px rgba(0, 0, 0, 0.2));
  animation: float-fast 7s ease-in-out infinite;
}

.shape-ring {
  width: 260px;
  height: 260px;
  bottom: -60px;
  right: -40px;
  border-radius: 50%;
  border: 24px solid rgba(255, 255, 255, 0.12);
  border-top-color: rgba(255, 255, 255, 0.32);
  animation: slow-rotate 24s linear infinite;
}

.visual-overlay {
  position: relative;
  max-width: 420px;
  z-index: 1;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 44px 38px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.visual-title {
  font-size: 32px;
  margin-bottom: 18px;
  font-weight: 700;
}

.visual-subtitle {
  font-size: 20px;
  margin-bottom: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.visual-description {
  font-size: 15px;
  line-height: 1.7;
  margin: 0;
  opacity: 0.85;
}

.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 60px;
  background: rgba(255, 255, 255, 0.9);
  position: relative;
}

.login-form {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 20px;
  padding: 42px 38px 46px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(15, 23, 42, 0.06);
}

.form-header {
  text-align: left;
  margin-bottom: 32px;
}

.form-title {
  margin: 0 0 6px;
  font-size: 22px;
  color: #1f2d3d;
  font-weight: 600;
}

.form-subtitle {
  margin: 0;
  font-size: 14px;
  color: #8692a6;
}

.captcha-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.captcha-image {
  width: 110px;
  height: 44px;
  background: linear-gradient(135deg, #5ed6fb 0%, #d3e3f7 80%);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  border-radius: 6px;
  box-shadow: 0 12px 20px rgba(103, 197, 240, 0.3);
}

.captcha-image p {
  margin: 0;
  font-size: 22px;
  letter-spacing: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  color: #1f2d3d;
}

.login-button {
  width: 100%;
  margin-top: 18px;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
}

.form-footer {
  position: absolute;
  right: 40px;
  bottom: 24px;
  font-size: 12px;
  color: #5a6c82;
  letter-spacing: 0.5px;
}

@keyframes float-slow {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(12px, -18px, 0); }
}

@keyframes float-medium {
  0%, 100% { transform: translate3d(0, 0, 0) rotate(18deg); }
  50% { transform: translate3d(-16px, 12px, 0) rotate(24deg); }
}

@keyframes float-fast {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(-12px, 16px, 0); }
}

@keyframes slow-rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .login-page {
    flex-direction: column;
    background: linear-gradient(135deg, #3c7ade 0%, #7ab9ff 100%);
  }

  .visual-panel {
    flex: none;
    width: 100%;
    padding: 48px 24px;
    min-height: 40vh;
  }

  .form-panel {
    width: 100%;
    padding: 40px 24px 60px;
  }

  .visual-overlay {
    max-width: 520px;
  }
}

@media (max-width: 640px) {
  .login-form {
    padding: 32px 26px 36px;
  }

  .form-panel {
    padding: 32px 20px 48px;
  }

  .visual-overlay {
    padding: 32px 28px;
  }

  .visual-title {
    font-size: 26px;
  }

  .visual-subtitle {
    font-size: 18px;
  }
}
</style>
