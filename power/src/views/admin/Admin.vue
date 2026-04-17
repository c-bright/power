<template>
  <el-container class="admin-layout">
    <el-dialog :visible.sync="showGuide" width="700px" :close-on-click-modal="false" :show-close="false" center custom-class="guide-dialog">
      <div class="guide-wrapper">
        <h2 class="guide-title">欢迎使用管理系统</h2>
        <el-steps :active="activeStep" finish-status="success" align-center>
          <el-step title="设备管理" description="实时监控设备上下线状态"></el-step>
          <el-step title="定价规则" description="灵活配置全局计费标准"></el-step>
          <el-step title="数据分析" description="直观展示运营营收情况"></el-step>
        </el-steps>
        <div class="step-content">
          <div v-if="activeStep === 0" class="detail-box">
            <i class="el-icon-monitor detail-icon"></i>
            <p class="detail-text">您可以一键远程控制充电宝设备的上线与下线，查看投放地点详情。</p>
          </div>
          <div v-if="activeStep === 1" class="detail-box">
            <i class="el-icon-coin detail-icon"></i>
            <p class="detail-text">支持自定义每小时计费单价及每日封顶金额，修改后实时同步至所有终端。</p>
          </div>
          <div v-if="activeStep === 2" class="detail-box">
            <i class="el-icon-pie-chart detail-icon"></i>
            <p class="detail-text">多维度可视化报表，统计今日流水、租借频次及用户增长趋势。</p>
          </div>
        </div>
        <div class="guide-footer">
          <el-button v-if="activeStep < 2" type="primary" class="next-btn" @click="activeStep++">下一步</el-button>
          <el-button v-else type="primary" class="next-btn" @click="handleFinish">进入系统</el-button>
        </div>
      </div>
    </el-dialog>

    <el-header class="main-header" height="60px">
      <div class="logo-area"><i class="el-icon-eleme"></i> 共享电源管理系统 (管理端)</div>
      <div class="user-area">
        <el-dropdown>
          <span class="user-link">管理员: {{ adminName }} <i class="el-icon-arrow-down"></i></span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="sub-container">
      <el-aside width="240px" class="admin-aside">
        <div class="menu-title">后台管理功能</div>
        <el-menu 
          :default-active="$route.path" 
          class="custom-menu"
          style="border-right: none" 
        >
          <el-menu-item index="/admin/device" @click="handleAuthJump('info', '/admin/device')">
            <i class="el-icon-set-up"></i><span>设备上下线</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/pricing" @click="handleAuthJump('rules', '/admin/pricing')">
            <i class="el-icon-coin"></i><span>定价规则</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/visual" @click="$router.push('/admin/visual')">
            <i class="el-icon-pie-chart"></i><span>可视化大屏</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/dispute" @click="handleAuthJump('feedback', '/admin/dispute')">
            <i class="el-icon-warning-outline"></i><span>纠纷处理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="admin-main">
        <div class="page-container">
          <div v-if="$route.path === '/admin' && !showGuide" class="welcome-container">
             <i class="el-icon-s-promotion" style="font-size: 80px; color: #4e6ef2; opacity: 0.3"></i>
             <p>请从左侧菜单选择功能开始管理</p>
          </div>
          <router-view v-else></router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  data() {
    return {
      adminName: localStorage.getItem('username') || 'Admin',
      showGuide: false,
      activeStep: 0,
      // 🚩 预加载权限
      permissions: JSON.parse(localStorage.getItem('permissions') || '{"info":0,"rules":0,"feedback":0}')
    }
  },
  mounted() {
    if (this.$route.path === '/admin' && !sessionStorage.getItem('guideShown')) {
      this.showGuide = true;
    }
  },
  methods: {
    /**
     * 🚩 核心权限校验跳转方法
     */
    handleAuthJump(type, path) {
      if (this.permissions[type] === 1) {
        // 权限通过：正常跳转
        if (this.$route.path !== path) {
          this.$router.push(path);
        }
      } else {
        // 权限缺失：弹出警告
        this.$message({
          message: '抱歉，您没有相关操作权限，请联系系统管理员获取权限。',
          type: 'warning',
          showClose: true,
          duration: 4000
        });
      }
    },
    
    handleFinish() {
      this.showGuide = false;
      sessionStorage.setItem('guideShown', 'true');
      // 🚩 逻辑改进：引导页结束后，自动跳往第一个有权限的页面
      if (this.permissions.info === 1) {
        this.$router.push('/admin/device');
      } else if (this.permissions.rules === 1) {
        this.$router.push('/admin/pricing');
      } else {
        this.$router.push('/admin/visual');
      }
    },
    
    logout() {
      sessionStorage.removeItem('guideShown');
      localStorage.clear();
      this.$router.push('/auth/login');
    }
  }
}
</script>

<style scoped>
/* 1. 核心：外层容器撑满屏幕，禁止全局滚动 */
.admin-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden; /* 彻底消除最外层滚动条 */
  display: flex;
  flex-direction: column;
}

/* 2. 顶部样式固定 */
.main-header {
  background-color: #4e6ef2;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* 防止 Header 被压缩 */
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.sub-container {
  flex: 1; /* 自动撑满剩余高度 */
  overflow: hidden; /* 防止子容器撑破父级 */
}

/* 3. 侧边栏适配 */
.admin-aside {
  background-color: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.custom-menu {
  flex: 1;
  overflow-y: auto; /* 只有菜单项过多时才出现内部滚动条 */
}

/* 4. 内容区美化：取消外层滚动，内部自适应 */
.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto; /* 子页面内容过多时，在这里产生滚动条 */
}

/* 内部白色卡片容器，适配界面 */
.page-container {
  background: white;
  min-height: 100%;
  border-radius: 4px;
  padding: 20px;
  box-sizing: border-box;
}

/* 其他样式保持不变 */
.guide-wrapper { padding: 10px 20px 30px; text-align: center; }
.guide-title { margin-bottom: 40px; font-weight: 500; color: #333; }
.step-content { margin: 50px 0; min-height: 150px; }
.detail-icon { font-size: 64px; color: #4e6ef2; margin-bottom: 20px; }
.detail-text { color: #666; font-size: 16px; line-height: 1.6; max-width: 80%; margin: 0 auto; }
.next-btn { width: 150px; height: 45px; font-size: 16px; background-color: #4e6ef2; border-radius: 4px; border: none; }
.menu-title { padding: 20px; font-size: 18px; font-weight: bold; color: #4e6ef2; }
.welcome-container { text-align: center; margin-top: 15vh; color: #999; }
.user-link { color: white; cursor: pointer; }

::v-deep .el-step__title.is-process, ::v-deep .el-step__head.is-process { color: #4e6ef2; border-color: #4e6ef2; }

</style>
