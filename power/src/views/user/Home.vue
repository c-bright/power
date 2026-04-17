<template>
  <div class="user-home-container">
    <header class="home-header">
      <div class="header-title">⚡ 共享电源管理系统 (用户端)</div>
      <div class="user-info">
        <span class="username">
          欢迎您，{{ username }}
        </span>
        <button @click="logout" class="logout-btn">
          退出登录
        </button>
      </div>
    </header>

    <main class="home-main">
      <aside class="home-aside">
        <nav class="sidebar-menu">
          
          <h4 class="menu-group-title">首页功能</h4> 
          
          <router-link to="/home/rent" class="menu-item" active-class="active">
            🏠 租借服务
          </router-link>
          <router-link to="/home/query" class="menu-item" active-class="active">
            🔍 订单查询
          </router-link>
          <router-link to="/home/profile" class="menu-item" active-class="active">
            👤 个人信息
          </router-link>
          
        </nav>
      </aside>

      <section class="home-content">
          
          <div v-if="$route.path === '/home'" class="welcome-card">
              <div class="welcome-header">
                  <h2>🎉 欢迎回来，{{ username }}！</h2>
                  <p>您已成功登录共享电源管理系统。</p>
              </div>
              
              <div class="service-guide">
                  <p>请通过左侧菜单开始使用我们的服务：</p>
                  <ul>
                      <li><span class="icon">🏠</span> 租借服务： 查看附近的充电宝站点，进行租借和归还操作。</li>
                      <li><span class="icon">🔍</span> 订单查询： 随时跟踪您的当前订单和历史记录。</li>
                      <li><span class="icon">👤</span> 个人信息： 管理您的账户资料和安全设置。</li>
                  </ul>
              </div>
              
              <div class="tip-footer">
                  <button @click="$router.push('/home/rent')" class="start-btn">
                      立即开始租借
                  </button>
              </div>
          </div>
          
          <router-view v-else></router-view> 
          
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'UserHome',
  data() {
    return {
      username: localStorage.getItem('username') || '用户' 
    };
  },
  methods: {
    logout() {
      // 清除本地存储的认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('token_expires_at');
      localStorage.removeItem('role');
      localStorage.removeItem('username'); 

      // 跳转到登录页
      this.$router.push('/auth/login');
    }
  }
  // ⚠️ 注意：移除了 created() 钩子中的自动重定向，以满足新需求
};
</script>

<style scoped>
/* --- 布局容器 --- */
.user-home-container {
  display: flex;
  flex-direction: column;
  height: 100vh; 
  background-color: #f7f9fc; /* 浅背景色 */
}

/* --- Header 顶部栏 --- */
.home-header {
  height: 60px;
  background-color: #4a69bd; /* 深蓝色，专业感 */
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}
.header-title {
  font-size: 1.4rem;
  font-weight: 500;
}
.user-info {
  display: flex;
  align-items: center;
}
.username {
  margin-right: 20px;
  font-size: 0.95rem;
  opacity: 0.9;
}
.logout-btn {
  background: #f0f0f01a;
  border: none;
  color: white;
  padding: 8px 15px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s;
  font-size: 0.9rem;
}
.logout-btn:hover {
  background-color: #f0f0f033;
}

/* --- Main 主体 --- */
.home-main {
  flex-grow: 1; 
  display: flex;
}

/* --- Aside 侧边栏 --- */
.home-aside {
  width: 240px; 
  background-color: #ffffff;
  padding-top: 15px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  flex-shrink: 0; 
}
.menu-group-title {
    padding: 15px 20px 10px;
    font-size: 1.1rem;
    color: #4a69bd; /* 菜单标题色 */
    font-weight: 600;
    border-bottom: 1px solid #e0e0e0;
    margin: 0;
}
.sidebar-menu {
  display: flex;
  flex-direction: column;
  padding-top: 10px;
}
.menu-item {
  padding: 14px 25px;
  text-decoration: none;
  color: #333;
  font-size: 1rem;
  border-left: 4px solid transparent;
  transition: all 0.2s;
}
.menu-item:hover {
  background-color: #f0f4f7;
  color: #4a69bd;
}
.menu-item.active {
  background-color: #e3f2fd;
  border-left-color: #4a69bd; 
  color: #4a69bd;
  font-weight: 600;
}

/* --- Content 内容区 --- */
.home-content {
  flex-grow: 1; 
  padding: 30px;
  overflow-y: auto; 
}

/* --- 欢迎卡片样式 (Welcome Card) --- */
.welcome-card {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    max-width: 800px;
    margin: 0 auto;
    overflow: hidden;
}
.welcome-header {
    background-color: #5cb85c; /* 成功的绿色 */
    color: white;
    padding: 30px;
}
.welcome-header h2 {
    margin: 0;
    font-size: 2rem;
}
.welcome-header p {
    font-size: 1.1rem;
    opacity: 0.9;
}
.service-guide {
    padding: 30px;
}
.service-guide p {
    font-weight: 500;
    color: #333;
}
.service-guide ul {
    list-style-type: none;
    padding: 0;
    margin-top: 15px;
}
.service-guide li {
    padding: 10px 0;
    font-size: 1rem;
    border-bottom: 1px dashed #eee;
    color: #666;
}
.service-guide li:last-child {
    border-bottom: none;
}
.icon {
    margin-right: 10px;
    color: #4a69bd;
}
.tip-footer {
    padding: 20px 30px;
    border-top: 1px solid #eee;
    text-align: right;
}
.start-btn {
    background-color: #4a69bd;
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
}
.start-btn:hover {
    background-color: #3f51b5;
}
</style>
