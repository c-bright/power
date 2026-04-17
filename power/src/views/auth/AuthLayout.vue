<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      
      <transition name="fade">
        <div class="message-box" :class="messageType" v-if="globalMessage">
          {{ globalMessage }}
        </div>
      </transition>
      <div class="auth-tabs">
        <button 
          :class="{ active: currentTab === 'login' }" 
          @click="switchToLogin"
        >
          用户登录
        </button>
        <button 
          :class="{ active: currentTab === 'register' }" 
          @click="switchToRegister"
        >
          用户注册
        </button>
      </div>

      <div class="auth-content">
        <Login 
          v-if="currentTab === 'login'"
          :setGlobalMessage="setGlobalMessage"
        />
        <Register 
          v-if="currentTab === 'register'"
          :setGlobalMessage="setGlobalMessage"
          :switchToLogin="switchToLogin"
        />
      </div>
      
    </div>
  </div>
</template>

<script>
import Login from './Login.vue';
import Register from './Register.vue';

export default {
  components: {
    Login,
    Register
  },
  data() {
    return {
      currentTab: 'login', 
      globalMessage: '',
      messageType: '' 
    };
  },
  methods: {
    setGlobalMessage(message, type) {
      this.globalMessage = message;
      this.messageType = type;
      if (message) {
        setTimeout(() => {
          this.globalMessage = '';
          this.messageType = '';
        }, 3000);
      }
    },
    switchToLogin() {
      this.currentTab = 'login';
      this.$router.push('/auth/login');
    },
    switchToRegister() {
      this.currentTab = 'register';
      this.$router.push('/auth/register');
    }
  },
  created() {
    if (this.$route.path.includes('register')) {
      this.currentTab = 'register';
    } else {
      this.currentTab = 'login';
    }
  }
};
</script>

<style scoped>
/* 🌐 全局主题变量（共享充电宝 · 科技蓝视觉体系） */
:root {
  --primary-color: #0a74ff;
  --primary-hover: #0056d6;
  --success-color: #28a745;
  --error-color: #d9534f;
  --info-color: #0a84ff;
  --text-light: #ffffff;
  --text-dark: #1a1a1a;
}

/* 🛰 背景层（渐变光晕 + HUD网格 + 模糊科技层） */
.auth-wrapper {
  background:
    radial-gradient(circle at 15% 20%, rgba(0,140,255,0.28), transparent 65%),
    radial-gradient(circle at 85% 80%, rgba(0,120,255,0.25), transparent 65%),
    linear-gradient(135deg, rgba(0, 25, 60, 0.9), rgba(0, 75, 150, 0.85)),
    url("@/assets/bg-image.jpg") center/cover no-repeat;
  background-blend-mode: overlay;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 30px;
  color: var(--text-light);
}

/* 🧊 毛玻璃科技卡片 */
.auth-card {
  width: 450px;
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  border-radius: 18px;
  padding: 40px;
  border: 1px solid rgba(255,255,255,0.29);
  box-shadow: 0 25px 50px rgba(0,0,0,0.45);
  animation: floatIn .6s ease forwards;
}

/* 📍加载浮入动画 */
@keyframes floatIn {
  from { opacity: 0; transform: translateY(25px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 📌 Tab 切换导航 */
.auth-tabs {
  display: flex;
  margin-bottom: 32px;
  border-bottom: 1px solid rgba(255,255,255,0.25);
}
.auth-tabs button {
  flex: 1;
  padding: 14px 0;
  font-size: 16px;
  font-weight: bold;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.75);
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: 0.3s;
}
.auth-tabs button:hover {
  color: #fff;
}
.auth-tabs button.active {
  color: #fff;
  position: relative;
}
.auth-tabs button.active::after {
  content: "";
  display: block;
  width: 60%;
  height: 3px;
  background: var(--primary-color);
  margin: 10px auto 0;
  border-radius: 2px;
}

/* 📦 内容区 */
.auth-content {
  margin-top: 10px;
  color: var(--text-light);
}

/* 📢 统一提示条风格 */
.message-box {
  text-align: center;
  font-weight: 600;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 18px;
  background: rgba(0,0,0,0.25);
  backdrop-filter: blur(6px);
}
.success { background: rgba(40,167,69,.85); }
.error { background: rgba(217,83,79,.85); }
.info { background: rgba(10,132,255,.85); }

/* 🎞️ 显隐动效 */
.fade-enter-active, .fade-leave-active { transition: opacity .35s; }
.fade-enter, .fade-leave-to { opacity: 0; }

/* 📱 响应式适配（移动端优化） */
@media (max-width: 540px) {
  .auth-card {
    width: 92%;
    padding: 30px;
    border-radius: 15px;
  }
  .auth-tabs button {
    font-size: 15px;
  }
}
</style>
