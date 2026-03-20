<template>
  <div class="form-content">
    <h3 class="form-title">用户登录</h3>
    <form @submit.prevent="handleLogin">
      
      <div class="input-group">
        <label for="role">用户身份:</label>
        <select id="role" v-model="loginForm.role" required>
          <option value="" disabled>请选择您的身份</option>
          <option value="users">普通用户</option>
          <option value="admin">管理员</option>
          <option value="sysadmin">系统管理员</option>
        </select>
      </div>

      <div class="input-group">
        <label for="login-username">用户名:</label>
        <input
          type="text"
          id="login-username"
          v-model="loginForm.username"
          required
          placeholder="请输入用户地址"
        />
      </div>

      <div class="input-group">
        <label for="login-password">密码:</label>
        <input
          type="password"
          id="login-password"
          v-model="loginForm.password"
          required
          placeholder="请输入密码"
        />
      </div>

      <button type="submit" :disabled="isLoading" class="primary-btn">
        {{ isLoading ? '登录中...' : '登 录' }}
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
    }
  },
  data() {
    return {
      isLoading: false,
      loginForm: {
        role: '', // 用于发送给后端，告诉它查询 admin 或 user 表
        username: '',
        password: ''
      }
    };
  },
  methods: {

    /**
     * 处理登录逻辑，与后端 127.0.0.1:5000 通信
     */
    async handleLogin() {
      this.setGlobalMessage('', '');
      
      // 前端简单验证
      if (!this.loginForm.role || !this.loginForm.username || !this.loginForm.password) {
        this.setGlobalMessage('请填写完整的登录信息并选择身份。', 'error');
        return;
      }
      
      if (this.loginForm.role === 'sysadmin') {
        // 如果是系统管理员，弹出特殊提醒，提示由于链上核验较慢需要等待
        this.setGlobalMessage('正在启动区块链核验引擎，获取链上实时身份地址，请稍候 (约5-10秒)...', 'info');
      }

      this.isLoading = true;

    
      try {
        // 1. 发送 POST 请求到 /login 接口
        const response = await request.post('/login', {
          username: this.loginForm.username,
          password: this.loginForm.password,
          role: this.loginForm.role // 告诉后端查询哪个用户表
        });
        
        if (response.data.status === "jump" || response.data.type === "JUMP") {
          
          setTimeout(() => {
            window.location.href = response.data.redirect_url;
          }, 1500);
          return; // 重要：直接返回，不执行后面的 localStorage 逻辑
        }
        else{
          const { username, user_id, email, balance, remark, address, permissions } = response.data;
          const role = this.loginForm.role;
    

          // ✅ 存储登录态
          localStorage.setItem('username', username);
          localStorage.setItem('user_id', user_id);
          localStorage.setItem('role', role);
          if (role === 'admin') {
            // 存储管理员特有的：钱包地址和权限对象
            localStorage.setItem('address', address);
            // 权限是对象，存储前需要转为 JSON 字符串
            localStorage.setItem('permissions', JSON.stringify(permissions));
            
            // 清理掉可能残留的用户字段（可选）
            localStorage.removeItem('email');
            localStorage.removeItem('balance');
          } else {
            // 存储普通用户特有的
            localStorage.setItem('email', email || '');
            localStorage.setItem('balance', balance || 0);
            localStorage.setItem('remark', remark || '');
          }
          this.setGlobalMessage(`[${role}] 登录成功！`, 'success');

          // 3. 根据角色进行页面跳转 (user 跳转到 /home, admin 跳转到 /admin)
          const redirectPath = role === 'admin' ? '/admin' : '/home';
          this.$router.replace(redirectPath);
       }

          
      } catch (error) {
        // 4. 登录失败处理
        const errorMsg = error.response 
                          ? error.response.data.message 
                          : '网络连接错误或后端服务不可用。';
                          
        this.setGlobalMessage(`登录失败：${errorMsg}`, 'error');

      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* 继承 AuthLayout.vue 中定义的 CSS 变量 */

.form-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-color-dark);
  font-size: 24px;
}

/* 输入组样式 */
.input-group { 
  margin-bottom: 20px; 
}
.input-group label { 
  display: block; 
  margin-bottom: 8px; 
  font-weight: 500;
  color: var(--text-color-dark);
}

/* ⭐淡化输入框背景(半透明白) */
.input-group input,
.input-group select { 
  width: 100%; 
  padding: 12px; 
  box-sizing: border-box; 
  background: rgba(255, 255, 255, 0.2); /* 白色淡化 */
  color: #726464; /* 字体亮一点才清晰 */
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 6px;
  transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
}

/* ⭐聚焦时更清晰，更蓝一点 */
.input-group input:focus,
.input-group select:focus {
  background: rgba(255, 255, 255, 0.1); /* 聚焦再淡一点 */
  border-color: var(--primary-color);
  box-shadow: 0 0 6px rgba(13, 110, 253, 0.6);
  outline: none;
}

/* Placeholder颜色柔和处理 */
.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

/* 登录按钮样式 */
.primary-btn { 
  width: 100%; 
  padding: 12px; 
  margin-top: 10px;
  background-color: var(--primary-color); 
  color: white; 
  border: none; 
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer; 
  transition: background-color 0.3s;
  font-weight: bold;
}
.primary-btn:hover:not(:disabled) {
  background-color: #0d6efd;
}
.primary-btn:disabled { 
  background-color: #a0cfff; 
  cursor: not-allowed;
}
</style>
