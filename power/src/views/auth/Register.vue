<template>
  <div class="form-content">
    <h3 class="form-title">用户注册</h3>
    <form @submit.prevent="handleRegister">

      <div class="input-group">
        <label for="reg-username">用户名:</label>
        <input
          type="text"
          id="reg-username"
          v-model="registerForm.username"
          required
          placeholder="请输入用户名"
        />
      </div>

      <div class="input-group">
        <label for="reg-email">邮箱:</label>
        <input
          type="email"
          id="reg-email"
          v-model="registerForm.email"
          required
          placeholder="请输入邮箱"
        />
      </div>

      <div class="input-group">
        <label for="reg-password">密码:</label>
        <input
          type="password"
          id="reg-password"
          v-model="registerForm.password"
          required
          minlength="6"
          placeholder="请输入密码"
        />
      </div>

      <button type="submit" :disabled="isLoading" class="register-btn">
        {{ isLoading ? '注册中...' : '注 册' }}
      </button>
    </form>
  </div>
</template>

<script>

import request from '../../utils/request'; 

export default {
  props: {
    // 接收父组件（AuthLayout）传递的消息提示函数
    setGlobalMessage: {
      type: Function,
      required: true
    },
    // 接收父组件传递的切换到登录页的函数
    switchToLogin: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      isLoading: false,
      registerForm: {
        username: '',
        email: '',
        password: ''
      }
    };
  },
  methods: {
    /**
     * 处理注册逻辑，将数据添加到后端的 user 表
     */
    async handleRegister() {
      // 1. 清空旧消息
      this.setGlobalMessage('', '');

      // 2. 密码长度校验
      if (this.registerForm.password.length < 6) {
        this.setGlobalMessage('注册失败：密码长度不能少于6位。', 'error');
        return;
      }
      
      this.isLoading = true;

      try {
        // 3. 发送 POST 请求到后端注册接口
        const response = await request.post('/register', {
          username: this.registerForm.username,
          password: this.registerForm.password,
          email: this.registerForm.email,
          // role: 'user' // 默认注册为普通用户，写入 user 表
        });
        
        // 4. 注册成功
        const successMsg = response.data.message || '注册成功！请使用您的新账号登录。';
        this.setGlobalMessage(successMsg, 'success');
        
        // 5. 清空表单
        this.registerForm = { username: '', email: '', password: '' };

        // 6. 1.5秒后自动切换到登录页
        setTimeout(() => {
            this.switchToLogin(); // 调用 AuthLayout 的函数切换 Tab
        }, 1500);

      } catch (error) {
        // 7. 注册失败
        const errorMsg = error.response 
                          ? error.response.data.message 
                          : '网络连接错误或后端服务不可用。';

        this.setGlobalMessage(`注册失败：${errorMsg}`, 'error');
        console.error('Registration Error:', error);

      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* 继承 AuthLayout.vue 中定义的 CSS 变量 */

/* 标题 */
.form-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-color-dark);
  font-size: 24px;
}

/* 输入组 */
.input-group { 
  margin-bottom: 20px; 
}
.input-group label { 
  display: block; 
  margin-bottom: 8px; 
  font-weight: 500;
  color: var(--text-color-dark);
}

/* ⭐去除白色背景 → 使用半透明输入框 */
.input-group input { 
  width: 100%; 
  padding: 12px; 
  box-sizing: border-box; 
  background: rgba(255,255,255,0.18); /* 不再是白色 */
  color: #fff; /* 与深色背景兼容 */
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 6px;
  transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
}

/* 光效聚焦（不会变白） */
.input-group input:focus {
  background: rgba(255,255,255,0.1);
  border-color: var(--primary-color);
  box-shadow: 0 0 6px rgba(0, 123, 255, 0.45);
  outline: none;
}

/* 防止自动填充变白 */
.input-group input:-webkit-autofill,
.input-group input:-webkit-autofill:hover,
.input-group input:-webkit-autofill:focus {
  background: rgba(255,255,255,0.18) !important;
  -webkit-box-shadow: 0 0 0 1000px rgba(255,255,255,0.18) inset !important;
  color: #fff !important;
}

/* Placeholder 柔和处理 */
.input-group input::placeholder {
  color: rgba(255,255,255,0.6);
}

/* 按钮（绿色注册） */
.register-btn { 
  width: 100%; 
  padding: 12px; 
  margin-top: 10px;
  background-color: var(--success-color);
  color: white; 
  border: none; 
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer; 
  transition: background-color 0.3s;
  font-weight: bold;
}
.register-btn:hover:not(:disabled) {
  background-color: #1e7e34; 
}
.register-btn:disabled { 
  background-color: #90d79d; 
  cursor: not-allowed;
}
</style>
