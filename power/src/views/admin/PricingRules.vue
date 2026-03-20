<template>
  <div class="pricing-page-container">
    <header class="page-header">
      <div class="title-group">
        <h2 class="title-main">计费标准配置</h2>
        <p class="title-sub">全局计费逻辑设置，修改后实时下发至终端</p>
      </div>
      <div class="status-indicator" :class="{ 'is-editing': isEditing }">
        <span class="dot"></span>
        {{ isEditing ? '编辑模式' : '运行中' }}
      </div>
    </header>

    <main class="main-content">
      <el-row :gutter="24" class="full-height-row">
        <el-col :span="15" class="full-height-col">
          <el-card shadow="never" class="config-card flex-card">
            <el-form :model="pricingForm" label-position="top" class="compact-form">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="🆓 免费时长 (分钟)">
                    <el-input-number v-model="pricingForm.free_minutes" :min="0" :disabled="!isEditing" class="w100"></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="💰 每小时单价 (元)">
                    <el-input-number v-model="pricingForm.hourly_price" :precision="2" :step="0.5" :disabled="!isEditing" class="w100"></el-input-number>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="🚫 每日封顶 (元)">
                    <el-input-number v-model="pricingForm.daily_max" :precision="2" :disabled="!isEditing" class="w100"></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="🛡️ 押金金额 (元)">
                    <el-input-number v-model="pricingForm.deposit" :precision="2" :disabled="!isEditing" class="w100"></el-input-number>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="spacer"></div>

              <div class="action-footer">
                <el-button v-if="!isEditing" type="primary" size="medium" @click="startEdit">修改计费规则</el-button>
                <template v-else>
                  <el-button type="success" size="medium" @click="saveRules">发布生效</el-button>
                  <el-button size="medium" @click="cancelEdit">取消</el-button>
                </template>
              </div>
            </el-form>
          </el-card>
        </el-col>

        <el-col :span="9" class="full-height-col">
          <div class="side-panel">
            <el-card shadow="never" class="preview-card">
              <div slot="header" class="small-header">预览摘要</div>
              <div class="preview-list">
                <div class="p-item"><span>免费期</span><strong>{{ pricingForm.free_minutes }} min</strong></div>
                <div class="p-item"><span>单价</span><strong>￥{{ pricingForm.hourly_price.toFixed(2) }}</strong></div>
                <div class="p-item"><span>封顶</span><strong>￥{{ pricingForm.daily_max.toFixed(2) }}</strong></div>
              </div>
            </el-card>

            <el-card shadow="never" class="tip-card">
              <div class="tip-content">
                <i class="el-icon-info"></i>
                <div>
                  <h4>计费说明</h4>
                  <p>修改后，新产生的订单将执行新标准。系统将自动向所有在线充电桩发送配置更新包。</p>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </main>
  </div>
</template>

<script>
import request from '../../utils/request'; // 确保路径正确

export default {
  data() {
    return {
      isEditing: false,
      // 这些是“默认值”，如果后端没数据，页面就显示这些
      pricingForm: { 
        free_minutes: 5, 
        hourly_price: 3.00, 
        daily_max: 30.00, 
        deposit: 99.00 
      },
      backupForm: {}
    }
  },
  methods: {
    // --- 新增：从后端获取数据的方法 ---
    async fetchPricingRules() {
      try {
        const response = await request.get('/api/pricing-rules');
        const res = response.data;
        
        // 🚨 关键判断：后端有数据 (code 200 且 data 不为空) 才覆盖
        if (res && res.code === 200 && res.data) {
          console.log("成功获取后端配置，覆盖默认值:", res.data);
          this.pricingForm = { ...res.data };
        } else {
          console.log("后端未配置或返回为空，使用前端默认值");
        }
      } catch (error) {
        console.error("获取计费标准失败，保持默认配置:", error);
      }
    },

    startEdit() {
      this.backupForm = { ...this.pricingForm };
      this.isEditing = true;
    },

    // --- 修改：保存时需要同步到后端数据库 ---
    saveRules() {
      this.$confirm('确定更新计费标准吗？', '系统提示', { type: 'warning' }).then(async () => {
        try {
          // 这里假设后端用 POST 或 PUT 保存配置
          const response = await request.post('/api/pricing-rules', this.pricingForm);
          if (response.data.code === 200) {
            this.isEditing = false;
            this.$message.success('配置已发布到数据库');
          }
        } catch (error) {
          this.$message.error('保存失败，请检查后端接口');
        }
      });
    },

    cancelEdit() {
      this.pricingForm = { ...this.backupForm };
      this.isEditing = false;
    }
  },
  
  // --- 生命周期钩子：进入页面立刻执行 ---
  mounted() {
    this.fetchPricingRules();
  }
}
</script>

<style scoped>
/* 取消溢出滚动，锁定高度 */
.pricing-page-container {
  height: calc(100vh - 120px); /* 减去父组件可能存在的header和padding */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0; /* 禁止页头缩放 */
}

.title-main { margin: 0; font-size: 20px; color: #303133; }
.title-sub { margin: 5px 0 0; font-size: 13px; color: #909399; }

/* 状态指示灯 */
.status-indicator {
  padding: 6px 14px;
  background: #e1f3d8;
  color: #67c23a;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
}
.status-indicator.is-editing { background: #faecd8; color: #e6a23c; }
.dot { width: 6px; height: 6px; background: currentColor; border-radius: 50%; margin-right: 8px; }

/* 内容布局 */
.main-content {
  flex: 1; /* 占据剩余所有空间 */
  min-height: 0; /* 关键：允许 flex 项目收缩 */
}

.full-height-row, .full-height-col {
  height: 100%;
}

.flex-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #ebeef5;
}

.compact-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.spacer { flex: 1; } /* 自动撑开，将按钮推到底部 */

.w100 { width: 100% !important; }

/* 侧边面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.preview-card, .tip-card { border: 1px solid #ebeef5; }
.preview-card { flex: 0 0 auto; }
.tip-card { flex: 1; background-color: #fdfaf5; }

.preview-list .p-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f2f6fc;
}

.tip-content {
  display: flex;
  gap: 15px;
  color: #8a6d3b;
}
.tip-content h4 { margin: 0 0 8px; font-size: 14px; }
.tip-content p { margin: 0; font-size: 12px; line-height: 1.6; }

.action-footer {
  padding-top: 20px;
  border-top: 1px solid #f2f6fc;
  text-align: right;
}
</style>