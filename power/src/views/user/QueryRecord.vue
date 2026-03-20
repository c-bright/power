<template>
  <div class="rent-history-container app-main-content">
    <div class="header-section">
      <h2 class="page-title">📝 借还记录查询</h2>
      
      <div class="message-box">
        <el-popover
          placement="bottom-end"
          width="320"
          trigger="click"
          @show="handleReadMessages"
        >
          <div class="notification-container">
            <div class="notif-header">
              <span>🔔 系统通知</span>
              <el-button type="text" size="mini" @click="clearLocalMessages">清空本地</el-button>
            </div>
            
            <div v-if="notifications.length === 0" class="empty-state">
              <i class="el-icon-chat-round"></i>
              <p>暂无新信息</p>
            </div>
            
            <div v-else class="notif-list">
              <div v-for="(msg, index) in notifications" :key="index" class="notif-item">
                <div class="notif-time">{{ msg.time }}</div>
                <div class="notif-body">{{ msg.content }}</div>
              </div>
            </div>
          </div>

          <el-badge 
            :value="unreadCount" 
            :hidden="unreadCount === 0" 
            class="msg-badge" 
            slot="reference"
          >
            <el-button icon="el-icon-message" circle class="mail-btn"></el-button>
          </el-badge>
        </el-popover>
      </div>
    </div>

    <el-card class="search-panel mb-20" shadow="hover">
      <el-form :inline="true" :model="searchForm" size="small">
        
        <el-form-item label="订单编号">
          <el-input 
            v-model="searchForm.orderNo" 
            placeholder="请输入订单编号" 
            clearable
            style="width: 200px;"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="状态筛选">
          <el-select v-model="searchForm.status" placeholder="选择状态" style="width: 120px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="进行中" value="in_progress"></el-option>
            <el-option label="已完成" value="completed"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :default-time="['00:00:00', '23:59:59']"
            style="width: 380px;"
          >
          </el-date-picker>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">查询</el-button>
          <el-button icon="el-icon-refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table 
      :data="historyData" 
      stripe 
      border
      v-loading="loading"
      class="table-data-list"
    >
      <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
      
      <el-table-column prop="order_no" label="订单编号" min-width="180" align="center" sortable></el-table-column>

      <el-table-column prop="location" label="借出地点" min-width="160" align="center"></el-table-column>
      
      <el-table-column prop="capacity" label="规格" width="80" align="center">
        <template slot-scope="scope">
            {{ formatCapacity(scope.row.capacity) }}
        </template>
      </el-table-column>

      <el-table-column prop="function_type" label="功能" width="100" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.function_type === 'fast' ? 'danger' : 'info'" size="mini">
            {{ scope.row.function_type === 'fast' ? '快充' : '普通' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="borrow_time" label="借出时间" width="160" align="center" sortable></el-table-column>
      
      <el-table-column prop="return_time" label="归还时间" width="160" align="center">
        <template slot-scope="scope">
            <span v-if="!scope.row.return_time" style="color: #E6A23C; font-weight: bold;">-- 待归还 --</span>
            <span v-else>{{ scope.row.return_time }}</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="cost" label="金额 (元)" width="100" align="center">
        <template slot-scope="scope">
            <span v-if="scope.row.status === 'completed'" style="color: #F56C6C; font-weight: bold;">
              ￥{{ scope.row.cost.toFixed(2) }}
            </span>
            <span v-else style="color: #909399;">计费中</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" align="center">
        <template slot-scope="scope">
          <el-button 
            v-if="scope.row.status === 'in_progress'"
            size="mini" 
            type="success" 
            icon="el-icon-wallet"
            @click="handleSettle(scope.row)">结算</el-button>

          <el-button 
            v-if="scope.row.status === 'completed'"
            size="mini" 
            type="primary" 
            icon="el-icon-view"
            @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container mt-20">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        background
      ></el-pagination>
    </div>

    <el-dialog title="订单详情" :visible.sync="viewVisible" width="450px">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="订单编号">{{ currentOrder.order_no }}</el-descriptions-item>
      <el-descriptions-item label="借出位置">{{ currentOrder.location }}</el-descriptions-item>
      <el-descriptions-item label="使用费用">
        <span style="color: #f56c6c; font-weight: bold">￥{{ currentOrder.cost }}</span>
      </el-descriptions-item>
    </el-descriptions>

    <div style="margin-top: 20px;">
      <p style="margin-bottom: 8px; font-size: 14px; font-weight: bold; color: #606266;">您的反馈/评价：</p>
      <el-input
        type="textarea"
        :rows="3"
        placeholder="若设备有损或计费异常，请在此留言..."
        v-model="feedbackContent">
      </el-input>
    </div>

  <div slot="footer" class="dialog-footer">
      <el-button @click="viewVisible = false">退 出</el-button>
      <el-button type="primary" @click="submitView" :loading="loading">提交</el-button>
    </div>
  </el-dialog>

      <el-dialog title="费用结算" :visible.sync="settleVisible" width="400px">
      <div style="text-align: center; padding: 20px;">
        <p>您正在结算订单：<strong>{{ currentOrder.order_no }}</strong></p>
        <h2 style="color: #67C23A">预估费用: ￥{{ calculateTempCost(currentOrder.borrow_time) }}</h2>
        <p style="font-size: 12px; color: #909399">实际费用以归还时刻为准</p>
      </div>
        <div slot="footer" style="display: flex; justify-content: space-between; align-items: center;">
          <el-button @click="settleVisible = false">返回</el-button>
          <el-button type="success" @click="confirmSettle">结算</el-button>
        </div>   
    </el-dialog>
  
  </div>
</template>

<script>
import request from '../../utils/request'; 

export default {
  name: 'RentHistory',
  data() {
    return {
      loading: false,
      viewVisible: false,
      settleVisible: false,
      currentOrder: {},

      Username: localStorage.getItem('username') || '',
      feedbackContent: '', // 新增：存储反馈内容
      searchForm: {
        orderNo: '', // 修改变量名
        status: '', 
        dateRange: null,
      },
      historyData: [], 
      currentPage: 1,
      pageSize: 10,
      total: 0,

      // 消息通知相关
      notifications: [],
      unreadCount: 0,
      pollingTimer: null,
      currentUsername: localStorage.getItem('username') || '',
    };
  },
  mounted() {
    this.fetchHistory();      // 载入表格数据
    this.fetchNotifications(); // 载入初始消息
    this.startPolling();      // 启动5秒轮询
  },
  beforeDestroy() {
    this.stopPolling();       // 必须销毁定时器，防止内存泄漏
  },
  methods: {

// ------------------- 消息轮询核心逻辑 -------------------
    startPolling() {
      this.pollingTimer = setInterval(() => {
        this.fetchNotifications();
      }, 60000); // 5秒
    },
    stopPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
      }
    },
 async fetchNotifications() {
    try {
      // 携带用户名请求接口
      const res = await request.get('/api/notifications', {
        params: { username: this.currentUsername }
      });
      
      if (res.data && res.data.success) {
        const newMsgs = res.data.data;
        
        // 逻辑：如果新消息数量增加，触发弹窗提醒
        if (newMsgs.length > this.notifications.length && this.notifications.length >= 0) {
          // 只有在不是页面初始化加载的情况下才弹出 notify
          if (this.notifications.length > 0) {
            this.$notify({
              title: '工单回复提醒',
              message: newMsgs[0].content, // 显示最新的一条
              type: 'success',
              position: 'bottom-right',
              duration: 5000 // 5秒后自动关闭
            });
          }
        }
        
        this.notifications = newMsgs;
        this.unreadCount = this.notifications.length;
      }
    } catch (err) {
      console.warn("消息轮询失败");
    }},
    handleReadMessages() {
      // 用户点击展开邮箱时，视为已读，未读数清零
      this.unreadCount = 0;
    },
    clearLocalMessages() {
      this.notifications = [];
      this.unreadCount = 0;
    },

    async fetchHistory() {
      this.loading = true;
      
      let params = {
        orderNo: this.searchForm.orderNo, // 传参修改
        status: this.searchForm.status,
        pageSize: this.pageSize,
        page: this.currentPage,
        username: this.currentUsername
      };

      if (this.searchForm.dateRange && this.searchForm.dateRange.length === 2) {
        params.startTime = this.searchForm.dateRange[0].toISOString();
        params.endTime = this.searchForm.dateRange[1].toISOString();
      }

      try {
        const response = await request.get('/api/history', { params });
        // 确保后端返回的字段包含 order_no
        if (response.data && response.data.data) {
          // 注意：这里改为赋值给您 template 中引用的 historyData
          this.historyData = response.data.data;
          this.total = response.data.total;
        
          // 成功提示：更新为“条记录”更符合历史查询语境
          this.$message.success(`查询成功！共找到 ${this.total} 条借还记录。`);
        } else {
          this.historyData = [];
          this.total = 0;
          this.$message.info(response.data.message || '未找到符合条件的借还记录。');
        }

        } catch (error) {
          // 异常处理
          this.$message.error('获取借还记录失败，请检查网络或后端服务！');
          console.error("Rent history fetch error:", error);
          this.historyData = [];
          this.total = 0;
        } finally {
          this.loading = false;
        }
    },

    handleSearch() {
      this.currentPage = 1;
      this.fetchHistory();
    },
    
    handleReset() {
      this.searchForm = {
        orderNo: '',
        status: '',
        dateRange: null,
      };
      this.handleSearch();
    },

    handleSizeChange(val) {
      this.pageSize = val;
      this.fetchHistory();
    },
    handleCurrentChange(val) {
      this.currentPage = val;
      this.fetchHistory();
    },

    formatStatus(status) {
      const statusMap = {
        in_progress: '使用中',
        completed: '已结算',
      };
      return statusMap[status] || '其他';
    },
    getStatusTagType(status) {
      const typeMap = {
        in_progress: 'warning',
        completed: 'success',
      };
      return typeMap[status] || 'info';
    },
    formatCapacity(capacity) {
      const map = { small: '小型 (S)', medium: '中型 (M)', large: '大型 (L)' };
      return map[capacity] || capacity;
    },

    // 点击查看按钮
    handleView(row) {
      this.currentOrder = { ...row };
      this.feedbackContent = '';
      this.viewVisible = true;
    },
    // 点击结算按钮
    handleSettle(row) {
      this.currentOrder = { ...row };
      this.settleVisible = true;
    },
    // 提交已结算订单反馈

  // 点击“查看”按钮时触发

  // 提交反馈逻辑
  async submitView() {
  // 此时 feedbackContent 已经通过 v-model 绑定
  if (!this.feedbackContent.trim()) {
    this.$message.warning('请输入反馈内容');
    return;
  }

  try {
    this.loading = true;
    const res = await request.post('/api/feedback', {
      order_no: this.currentOrder.order_no,
      username: localStorage.getItem('username'),
      content: this.feedbackContent
    });

    if (res.data.success) {
      this.$message.success(res.data.message);
      this.viewVisible = false; // 成功后关闭弹窗
      this.feedbackContent = ''; // 清空内容
      // 如果需要，可以在此处调用 fetchHistory() 刷新页面状态
    }
  } catch (error) {
    // 这里会捕获后端返回的 400 或 500 错误
    this.$message.error(error.response?.data?.message || '提交失败');
  } finally {
    this.loading = false;
  }
},

    // 执行结算逻辑
    // 修改后的 confirmSettle 方法
    async confirmSettle() {
      try {
        this.loading = true;
        // 调用归还与结算接口
        const res = await request.post('/api/history', {
          order_no: this.currentOrder.order_no, // 推荐使用订单号作为结算凭证
          username: localStorage.getItem('username') // 确保获取当前用户
        });
        
        if (res.data.success) {
          const finalCost = res.data.data ? res.data.data.cost : 0;
        
          this.$message({
            message: `结算成功！扣除费用：￥${parseFloat(finalCost).toFixed(2)}`,
            type: 'success',
            duration: 5000 
          });
          this.settleVisible = false;
          this.fetchHistory(); // 刷新历史记录列表
        }
      } catch (e) {
        this.$message.error(e.response?.data?.message || '结算接口异常');
      } finally {
        this.loading = false;
      }
    },
    // 模拟计算当前实时费用
  calculateTempCost(rentTime) {
    if (!rentTime) return "0.00";
    
    // 🌟 修复 NaN 的关键：将横杠替换为斜杠，确保所有浏览器都能识别
    const startTimeStr = String(rentTime).replace(/-/g, '/');
    const start = new Date(startTimeStr);
    const now = new Date();
    
    // 检查转换是否成功
    if (isNaN(start.getTime())) return "4.00"; 

    const diffMs = now - start;
    // 逻辑：不满1小时按1小时算，每小时4元
    const hours = Math.max(1, Math.ceil(diffMs / (1000 * 60 * 60)));
    return (hours * 4).toFixed(2);
  },
  },
};
</script>

<style scoped>
  /* 1. 顶部布局控制 */
.header-section {
  display: flex;
  justify-content: space-between; /* 关键：标题在左，邮箱在右 */
  align-items: center;
  margin-bottom: 5px;
}
.page-title { margin: 0; color: #303133; }

/* 2. 消息通知框样式 */
.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 8px;
  margin-bottom: 10px;
}
.notif-header span { font-weight: bold; color: #409EFF; }

.notif-list { max-height: 280px; overflow-y: auto; }
.notif-item {
  padding: 10px 0;
  border-bottom: 1px dashed #f0f0f0;
}
.notif-time { font-size: 11px; color: #999; margin-bottom: 4px; }
.notif-body { font-size: 13px; color: #606266; line-height: 1.4; }

.empty-state {
  text-align: center;
  padding: 30px 0;
  color: #C0C4CC;
}
.empty-state i { font-size: 30px; margin-bottom: 8px; }

/* 3. 邮箱按钮动画 */
.mail-btn {
  font-size: 18px;
  transition: all 0.3s;
}
.mail-btn:hover {
  background-color: #ecf5ff;
  color: #409EFF;
  transform: scale(1.1);
}

/* 常用间距 */
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.pagination-container { display: flex; justify-content: flex-end; }
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.page-title { margin-bottom: 25px; color: #303133; }
.pagination-container { display: flex; justify-content: flex-end; }

.dialog-footer {
  text-align: right;
  padding: 10px 0 0;
}

/* 如果您想给两个按钮之间增加一点间距 */
.dialog-footer .el-button + .el-button {
  margin-left: 265px;
}
</style>