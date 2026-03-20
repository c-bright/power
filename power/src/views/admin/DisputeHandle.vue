<template>
  <div class="dispute-container">
    <el-card shadow="never" class="main-card">
      <div slot="header" class="header-actions">
        <el-input 
          v-model="searchId" 
          placeholder="搜索订单号/用户名" 
          size="small" 
          style="width: 250px"
          clearable
        >
          <el-button slot="append" icon="el-icon-search"></el-button>
        </el-input>
        
        <el-radio-group v-model="statusFilter" size="small" style="margin-left: 20px" @change="currentPage = 1">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="pending">未处理</el-radio-button>
          <el-radio-button label="processed">已处理</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="pagedDisputes" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="order_no" label="订单号" width="150"></el-table-column>
        <el-table-column prop="username" label="用户名" width="120"></el-table-column>
        <el-table-column prop="content" label="反馈内容" show-overflow-tooltip></el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'processed' ? 'success' : 'info'" size="mini">
              {{ scope.row.status === 'processed' ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="优先级" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.priority === 'high' ? 'danger' : 'info'" size="mini">
              {{ scope.row.priority === 'high' ? '紧急' : '普通' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="上报时间" width="160"></el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template slot-scope="scope">
            <el-button 
              :type="scope.row.status === 'processed' ? 'text' : 'primary'" 
              size="mini" 
              @click="handleProcess(scope.row)"
            >
              {{ scope.row.status === 'processed' ? '查看详情' : '立即处理' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-box">
        <el-pagination 
          background 
          layout="total, prev, pager, next" 
          :current-page.sync="currentPage"
          :page-size="pageSize"
          :total="filteredList.length"
        ></el-pagination>
      </div>
    </el-card>

  <el-dialog :title="activeTicket && activeTicket.status === 'processed' ? '工单详情' : '提交回复'" :visible.sync="dialogVisible" width="650px">
  <div v-if="activeTicket">
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="ID">{{ activeTicket.id }}</el-descriptions-item>
      <el-descriptions-item label="订单编号">{{ activeTicket.order_no }}</el-descriptions-item>
      
      <el-descriptions-item label="用户名">{{ activeTicket.username || '匿名' }}</el-descriptions-item>
      <el-descriptions-item label="投放地点">{{ activeTicket.location || '-' }}</el-descriptions-item>
      
      <el-descriptions-item label="设备容量">{{ activeTicket.capacity || '-' }}</el-descriptions-item>
      <el-descriptions-item label="功能类型">{{ activeTicket.function_type || '-' }}</el-descriptions-item>
      
      <el-descriptions-item label="租借时间" :span="2">{{ activeTicket.rent_time || '-' }}</el-descriptions-item>
      <el-descriptions-item label="归还时间" :span="2">{{ activeTicket.return_time || '-' }}</el-descriptions-item>
      
      <el-descriptions-item label="涉及费用">
        <b style="color: #F56C6C">￥ {{ activeTicket.cost || '0.00' }}</b>
      </el-descriptions-item>
      <el-descriptions-item label="当前状态">
        <el-tag size="mini" :type="activeTicket.status === 'processed' ? 'success' : 'warning'">
          {{ activeTicket.status === 'processed' ? '已处理' : '待处理' }}
        </el-tag>
      </el-descriptions-item>

      <el-descriptions-item label="反馈内容" :span="2">
        <div style="color: #409EFF; font-weight: bold;">{{ activeTicket.content }}</div>
      </el-descriptions-item>
    </el-descriptions>
    
    <el-form label-width="80px" style="margin-top: 20px">
      <el-form-item v-if="activeTicket.status === 'processed'" label="处理内容">
        <div style="padding: 10px; background: #f0f9eb; border: 1px solid #e1f3d8; border-radius: 4px; color: #67c23a">
          <i class="el-icon-circle-check"></i> {{ activeTicket.reply }}
        </div>
      </el-form-item>
      
      <el-form-item v-else label="处理备注">
        <el-input 
          v-model="processForm.remark" 
          type="textarea" 
          placeholder="请输入回复客户的内容" 
          rows="3" 
        />
      </el-form-item>
    </el-form>
  </div>
  <div slot="footer">
    <el-button @click="dialogVisible = false" size="small">取 消</el-button>
    <el-button 
      v-if="activeTicket && activeTicket.status !== 'processed'" 
      type="primary" 
      @click="submitProcess" 
      size="small"
    >提交处理</el-button>
  </div>
</el-dialog>
  </div>
</template>

<script>
import request from '../../utils/request';

export default {
  name: 'DisputeHandle',
  data() {
    return {
      loading: false,
      searchId: '',
      statusFilter: 'all',
      currentPage: 1,
      pageSize: 10,
      dialogVisible: false,
      activeTicket: null,
      processForm: { remark: '' }, // 🚩 确保有这个对象
      disputeList: []
    };
  },

  computed: {
    filteredList() {
      let tempData = this.disputeList;
      if (this.statusFilter !== 'all') {
        tempData = tempData.filter(item => item.status === this.statusFilter);
      }
      if (this.searchId) {
        const keyword = this.searchId.toLowerCase();
        tempData = tempData.filter(item => 
          (item.order_no && item.order_no.toString().toLowerCase().includes(keyword)) ||
          (item.username && item.username.toLowerCase().includes(keyword))
        );
      }
      return tempData;
    },
    pagedDisputes() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.filteredList.slice(start, start + this.pageSize);
    }
  },

  mounted() {
    this.fetchDisputes();
  },

  methods: {
    async fetchDisputes() {
      this.loading = true;
      try {
        const res = await request.get('/api/admin/feedback');
        const responseData = res.data || res;
        
        if (responseData.success) {
          this.disputeList = (responseData.data || []).map(item => {
            // 🚩 核心逻辑：根据 reply 是否为空判断显示状态
            // null, undefined, "", "待处理" 均视为未处理 (根据你后端的返回微调)
            const isProcessed = item.reply && item.reply !== "" && item.reply !== "待处理";
            
            return {
              ...item,
              priority: item.priority || 'normal',
              status: isProcessed ? 'processed' : 'pending' 
            };
          });
        }
      } catch (error) {
        this.$message.error("无法获取反馈数据");
      } finally {
        this.loading = false;
      }
    },

// 在 methods 里的 handleProcess 中修改
async handleProcess(row) {
  this.loading = true;
  try {
    const res = await request.get('/api/admin/rent_detail', {
      params: { order_no: row.order_no, username: row.username }
    });

    if (res.data && res.data.success) {
      let detailData = res.data.data;

      // 🚩 新增映射转换逻辑
      const capacityMap = {
        'small': '小容量',
        'medium': '中容量',
        'large': '大容量'
      };
      const functionMap = {
        'normal': '普通',
        'fast': '快充'
      };

      // 进行中文替换，如果没有匹配到则显示原值
      detailData.capacity = capacityMap[detailData.capacity] || detailData.capacity;
      detailData.function_type = functionMap[detailData.function_type] || detailData.function_type;

      this.activeTicket = { ...row, ...detailData };
      this.dialogVisible = true;
    } else {
      this.$message.warning("未找到关联订单详情");
      this.activeTicket = { ...row };
      this.dialogVisible = true;
    }
  } catch (error) {
    this.$message.error("关联详情请求失败");
  } finally {
    this.loading = false;
  }
},

  async submitProcess() {
  // 1. 验证备注是否为空
  if (!this.processForm.remark || !this.processForm.remark.trim()) {
    this.$message.warning("请输入处理备注内容");
    return;
  }

  this.loading = true;
  try {
    // 2. 发送 POST 请求
    const res = await request.post('/api/admin/feedback/process', {
      id: this.activeTicket.id,          // 当前工单的 ID
      remark: this.processForm.remark    // 管理员填写的处理备注
    });

    const responseData = res.data || res;
    if (responseData.success) {
      this.$message.success("工单处理成功！");
      this.dialogVisible = false;        // 关闭弹窗
      
      // 3. 🚩 关键：重新拉取列表，使页面显示“已处理”状态
      await this.fetchDisputes(); 
      
      // 清空备注框，防止下次打开还有内容
      this.processForm.remark = ''; 
    } else {
      this.$message.error(responseData.message || "提交失败");
    }
  } catch (error) {
    this.$message.error("提交请求发生错误");
  } finally {
    this.loading = false;
  }
}
  }
};
</script>

<style scoped>
.dispute-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.main-card { border-radius: 8px; border: none; }
.header-actions { display: flex; align-items: center; }
.pagination-box { margin-top: 20px; text-align: right; }
::v-deep .el-descriptions__title { font-size: 15px; color: #409EFF; }
</style>