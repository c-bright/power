<template>
  <div class="full-screen-profile">
    <header class="compact-gray-header">
      <div class="header-inner">
        <div class="user-info">
          <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></el-avatar>
          <div class="info-text">
            <h3 class="name">{{ user.nickname }}</h3>
            <p class="id">账号状态: 正常</p>
          </div>
        </div>

        <div class="asset-overview">
          <div class="asset-item">
            <span class="label">账户余额</span>
            <div class="value">￥{{ user.balance.toFixed(2) }}</div>
          </div>
          <el-divider direction="vertical"></el-divider>
          <div class="asset-item">
            <span class="label">信用积分</span>
            <div class="value credit">{{ user.credit }}</div>
          </div>
          <el-button type="primary" size="medium" round icon="el-icon-wallet" class="recharge-trigger" @click="rechargeVisible = true">
            充值
          </el-button>
        </div>
      </div>
    </header>

    <main class="bottom-main-content">
      <el-tabs v-model="activeTab" class="full-height-tabs">
        
   <el-tab-pane name="info">
          <span slot="label"><i class="el-icon-user"></i> 基本资料</span>
          <div class="pane-scroll-area">
            <el-form label-position="top" class="custom-form-layout">
              <el-row :gutter="40">
                <el-col :span="12">
                  <el-form-item label="昵称">
                    <el-input v-model="user.nickname" placeholder="请输入您的昵称" disabled></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="邮箱">
                    <el-input v-model="user.email"></el-input>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="个人简介">
                <el-input type="textarea" :rows="3" v-model="user.bio" placeholder="这家伙很懒，什么都没留下..." resize="none"></el-input>
              </el-form-item>
              <el-button type="primary" class="save-data-btn" @click="onSave">保存修改</el-button>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane name="safe">
          <span slot="label"><i class="el-icon-lock"></i> 安全中心</span>
          <div class="pane-content">
            <div class="setting-list-item">
              <div class="item-info">
                <div class="icon-wrap"><i class="el-icon-key"></i></div>
                <div>
                  <h4>密码修改</h4>
                  <p>建议每 3 个月更换一次密码以确安全</p>
                </div>
              </div>
              <el-button type="primary" plain size="small" round @click="pwdVisible = true">修改</el-button>
            </div>

            <div class="setting-list-item danger">
              <div class="item-info">
                <div class="icon-wrap"><i class="el-icon-delete"></i></div>
                <div>
                  <h4>注销账号</h4>
                  <p>永久删除账户及其关联的所有数据</p>
                </div>
              </div>
              <el-button type="danger" plain size="small" round @click="onDelete">注销</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </main>

    <el-dialog :visible.sync="rechargeVisible" width="400px" center custom-class="modern-dialog">
      <div slot="title" class="dialog-header">
        <i class="el-icon-coin"></i>
        <span>快速充值</span>
      </div>
      <div class="recharge-body">
        <div class="amt-grid">
          <div 
            v-for="amt in [20, 50, 100, 200, 500, 1000]" :key="amt"
            class="amt-card" :class="{ active: selAmt === amt }"
            @click="selAmt = amt"
          >
            <div class="amt-val"><span>￥</span>{{ amt }}</div>
            <div class="check-mark" v-if="selAmt === amt"><i class="el-icon-check"></i></div>
          </div>
        </div>
        <div class="custom-amt">
          <label>自定义金额</label>
          <el-input-number v-model="selAmt" :min="1" controls-position="right"></el-input-number>
        </div>
      </div>
      <span slot="footer">
        <el-button type="primary" class="confirm-pay-btn" @click="doRecharge">立即充值</el-button>
      </span>
    </el-dialog>

    <el-dialog :visible.sync="pwdVisible" width="400px" center custom-class="modern-dialog">
      <div slot="title" class="dialog-header">
        <i class="el-icon-unlock"></i>
        <span>修改密码</span>
      </div>
      <el-form :model="pwdForm" label-position="top" class="pwd-form">
        <el-form-item label="原密码">
          <el-input v-model="pwdForm.old" show-password placeholder="输入当前密码"></el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new" show-password placeholder="至少6位字符"></el-input>
          <div class="pwd-strength" v-if="pwdForm.new">
            强度：<span :class="pwdForm.new.length > 8 ? 'high' : 'low'">{{ pwdForm.new.length > 8 ? '高' : '弱' }}</span>
          </div>
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm" show-password placeholder="请再次输入新密码"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" @click="doUpdatePwd">保存新密码</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>

import request from '../../utils/request'; 

export default {
data() {
  return {
    activeTab: 'info',
    rechargeVisible: false,
    pwdVisible: false,
    selAmt: 50,
    user: { 
      nickname: localStorage.getItem('username') || '未登录', 
      balance: Number(localStorage.getItem('balance')) || 0, 
      credit: 100,
      email: localStorage.getItem('email') || '', 
      bio: (localStorage.getItem('remark') && localStorage.getItem('remark') !== 'null') 
              ? localStorage.getItem('remark') 
              : '这个人很懒，什么都没留下'
    },
    pwdForm: { old: '', new: '', confirm: '' }
  };
},

  methods: {
    async onSave() {
      try {
        const postData = {
          username: this.user.nickname,
          email: this.user.email,
          remark: this.user.bio
        };
        
        const res = await request.post('/user/update', postData);

        // 兼容性判断：有些封装返回 res，有些返回 res.data
        const responseData = res.data || res; 

        if (responseData.code === 200) {
          this.$message.success('更新资料成功');
          
          // 更新本地缓存
          localStorage.setItem('email', this.user.email);
          localStorage.setItem('remark', this.user.bio);
        } else {
          this.$message.error(responseData.message || '后端返回状态异常');
        }
      } catch (error) {
            console.error('保存报错详情:', error);
        this.$message.error('保存失败：网络或代码异常');
      }
    },

   async doRecharge() {
  try {
    const postData = {
      username: this.user.nickname,
      amount: this.selAmt
    };

    const res = await request.post('/user/recharge', postData);

    // --- 关键修复：统一处理响应结构 ---
    const responseData = res.data || res; 

    if (responseData.code === 200) {
      // 1. 使用后端返回的最准余额
      this.user.balance = responseData.new_balance;
      
      // 2. 同步更新本地缓存
      localStorage.setItem('balance', responseData.new_balance);
      
      // 3. 关闭弹窗并提示
      this.rechargeVisible = false;
      this.$notify({
        title: '充值成功',
        message: `已充值 ￥${this.selAmt}，当前余额 ￥${responseData.new_balance.toFixed(2)}`,
        type: 'success'
      });
    } else {
      // 如果后端返回了错误（例如 code 为 400/500）
      this.$message.error(responseData.message || '充值失败');
    }
  } catch (error) {
    console.error('充值异常详情:', error);
    this.$message.error('请求失败，请检查网络或后端配置');
  }
},
   async doUpdatePwd() {
  // 1. 前端基础校验
  if (!this.pwdForm.old || !this.pwdForm.new) {
    return this.$message.warning('请完整填写密码信息');
  }
  if (this.pwdForm.new.length < 6) {
    return this.$message.warning('新密码长度不能少于6位');
  }
  if (this.pwdForm.new !== this.pwdForm.confirm) {
    return this.$message.error('两次输入的新密码不一致');
  }

  try {
    const postData = {
      username: this.user.nickname,
      old: this.pwdForm.old,
      new: this.pwdForm.new
    };

    const res = await request.post('/user/update_pwd', postData);
    const responseData = res.data || res;

    if (responseData.code === 200) {
      this.$message.success('密码修改成功，下次请使用新密码登录');
      this.pwdVisible = false;
      // 清空表单
      this.pwdForm = { old: '', new: '', confirm: '' };
    } else {
      this.$message.error(responseData.message || '修改失败');
    }
  } catch (error) {
    console.error('修改密码异常:', error);
    this.$message.error('原密码错误或服务器繁忙');
  }
},
   async onDelete() {
  try {
    const checkRes = await request.post('/user/check_pending', { username: this.user.nickname });
    const responseData = checkRes.data || checkRes;

    // 情况 A：有未接订单 (count > 0)
    if (responseData.has_pending) {
      this.$alert(`检测到您还有 ${responseData.count} 个未结算订单，请归还设备并完成支付后再注销。`, '无法注销', {
        confirmButtonText: '前往结算页面',
        callback: () => {
         this.$router.push('/home/query');; // 跳转到 query 文件对应的历史页面
        }
      });
      return;
    }

    // 情况 B：没有订单 (count === 0)，执行注销确认
    this.$confirm('确定要注销账号吗？此操作不可逆！', '注销确认', {
      confirmButtonText: '确定',
      cancelButtonText: '点错了',
      type: 'warning'
    }).then(async () => {
      const delRes = await request.post('/user/delete', { username: this.user.nickname });
      if ((delRes.data || delRes).code === 200) {
        this.$message.success('注销成功，期待再次相遇');
        localStorage.clear();
        this.$router.push('/auth/login');
      }
    });

  } catch (error) {
    this.$message.error('请求失败，请检查后端服务');
  }
}
  }
};
</script>

<style scoped>
/* 全屏基础 */
.full-screen-profile {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
}

/* 顶层浅灰区 */
.compact-gray-header {
  height: 100px;
  background: #f8f9fa;
  border-bottom: 1px solid #f0f1f3;
  display: flex;
  align-items: center;
  padding: 0 40px;
}

.header-inner {
  width: 100%; max-width: 1000px; margin: 0 auto;
  display: flex; justify-content: space-between; align-items: center;
}

.user-info { display: flex; align-items: center; gap: 12px; }
.info-text .name { margin: 0; font-size: 18px; color: #333; }
.info-text .id { margin: 2px 0 0; font-size: 12px; color: #999; }

.asset-overview { display: flex; align-items: center; gap: 30px; }
.asset-item { text-align: center; }
.asset-item .label { font-size: 11px; color: #999; margin-bottom: 4px; display: block; }
.asset-item .value { font-size: 22px; font-weight: bold; color: #333; }
.value.credit { color: #67C23A; }

/* 内容主体 */
.bottom-main-content {
  flex: 1; padding: 20px 40px;
  max-width: 1000px; width: 100%; margin: 0 auto;
}
.custom-form-layout { max-width: 600px; }
.pane-content { padding: 30px 0; }

/* 安全中心列表 */
.setting-list-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 15px 20px; background: #fafbfc; border-radius: 12px; margin-bottom: 16px;
}
.item-info { display: flex; align-items: center; gap: 15px; }
.icon-wrap { width: 40px; height: 40px; background: #eff6ff; color: #409EFF; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; }
.item-info h4 { margin: 0 0 4px; font-size: 14px; }
.item-info p { margin: 0; font-size: 12px; color: #999; }
.danger.setting-list-item { background: #fff5f5; }
.danger .icon-wrap { background: #fee2e2; color: #ef4444; }

/* 对话框通用美化 */
.modern-dialog { border-radius: 16px !important; overflow: hidden; }
.dialog-header { display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 16px; color: #333; }
.dialog-header i { color: #409EFF; }

/* 充值网格美化 */
.amt-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.amt-card {
  position: relative; padding: 18px 0; border: 2px solid #f0f1f3; border-radius: 10px;
  text-align: center; cursor: pointer; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.amt-card .amt-val { font-size: 18px; font-weight: bold; color: #444; }
.amt-card .amt-val span { font-size: 12px; }
.amt-card:hover { border-color: #d9ecff; background: #fdfeff; }
.amt-card.active {
  border-color: #409EFF; background: #f0f7ff; color: #409EFF;
  transform: translateY(-3px); box-shadow: 0 6px 15px rgba(64,158,255,0.2);
}
.check-mark { position: absolute; top: -5px; right: -5px; background: #409EFF; color: #fff; width: 18px; height: 18px; border-radius: 50%; font-size: 10px; line-height: 18px; }

.custom-amt { margin-top: 25px; padding-top: 20px; border-top: 1px solid #f0f1f3; }
.custom-amt label { display: block; font-size: 12px; color: #999; margin-bottom: 10px; }
.confirm-pay-btn { width: 100%; height: 45px; font-size: 16px; border-radius: 10px; }

/* 密码强度 */
.pwd-form { padding-top: 10px; }
.pwd-strength { font-size: 11px; margin-top: 5px; color: #999; }
.pwd-strength span.low { color: #F56C6C; }
.pwd-strength span.high { color: #67C23A; font-weight: bold; }

/* 隐藏滚动条 */
::-webkit-scrollbar { width: 0; }
</style>
