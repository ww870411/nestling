<template>
  <div class="login-container">
    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      class="login-form"
      label-position="left"
    >
      <div class="title-container">
        <h3 class="title">大连洁净能源集团有限公司<br>
          数据在线填报平台</h3>
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
          <div class="captcha-image">
            <p>1234</p>
          </div>
        </div>
      </el-form-item>

      <el-button :loading="loading" type="primary" style="width:100%;margin-bottom:30px;" @click.prevent="handleLogin">
        登 录
      </el-button>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { ElMessage } from 'element-plus';

const router = useRouter();
const authStore = useAuthStore();

const loginForm = ref({
  username: '',
  password: '',
  captcha: '' // 验证码逻辑暂时保留UI，但不参与实际验证
});

const loginRules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
});

const loading = ref(false);
const loginFormRef = ref(null);

const handleLogin = () => {
  loginFormRef.value.validate(valid => {
    if (valid) {
      loading.value = true;
      // 使用 authStore 进行登录
      const loginSuccess = authStore.login(loginForm.value.username, loginForm.value.password);

      setTimeout(() => {
        if (loginSuccess) {
          ElMessage.success('登录成功');
          router.push({ path: '/' });
        } else {
          ElMessage.error('用户名或密码错误');
        }
        loading.value = false;
      }, 500);
    } else {
      return false;
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  background-color: #2d3a4b;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-form {
  position: relative;
  width: 520px;
  max-width: 100%;
  padding: 35px;
  margin: 0 auto;
  overflow: hidden;
  background: #fff;
  border-radius: 5px;
}

.title-container {
  position: relative;
}

.title {
  font-size: 22px; /* Adjusted for longer title */
  color: #333;
  margin: 0px auto 40px auto;
  text-align: center;
  font-weight: bold;
}

.captcha-wrapper {
  display: flex;
  align-items: center;
}

.captcha-image {
  width: 100px;
  height: 40px;
  margin-left: 10px;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  border-radius: 4px;
}

.captcha-image p {
  margin: 0;
  font-size: 20px;
  letter-spacing: 5px;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  color: #666;
}
</style>
