<template>
  <div class="powerbank-rent-container">
    <h2 class="page-title">🔋 附近充电宝实时信息与租借</h2>

    <el-card class="search-panel">
      <el-form :inline="true" :model="searchForm" size="small" class="demo-form-inline">
        
        <el-form-item label="位置搜索">
          <el-input 
            v-model="searchForm.location" 
            placeholder="输入区域或地点" 
            clearable
            style="width: 180px;"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="状态筛选">
          <el-select v-model="searchForm.status" placeholder="选择状态" style="width: 120px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="在线" value="online"></el-option>
            <el-option label="使用" value="offline"></el-option>
            <el-option label="维修" value="repair"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="容量规格">
          <el-select v-model="searchForm.capacity" placeholder="选择容量" style="width: 120px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="小型" value="small"></el-option>
            <el-option label="中型" value="medium"></el-option>
            <el-option label="大型" value="large"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="功能类型">
          <el-select v-model="searchForm.functionType" placeholder="选择功能" style="width: 120px;">
            <el-option label="全部" value=""></el-option>
            <el-option label="快充" value="fast"></el-option>
            <el-option label="普通" value="normal"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">
            查询
          </el-button>
          <el-button icon="el-icon-refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table 
      :data="paginatedData" 
      stripe 
      border
      style="width: 100%; margin-top: 20px;"
      v-loading="loading"
    >
      <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
      
      <el-table-column prop="id" label="充电宝ID" width="100" align="center" sortable></el-table-column>

      <el-table-column prop="location" label="设备位置" min-width="100" align="center" sortable></el-table-column>
      
      <el-table-column label="状态" width="120" align="center">
        <template slot-scope="scope">
          <el-tag :type="getStatusTagType(scope.row.status)" size="medium">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="battery_level" label="电量" width="120" align="center" sortable>
        <template slot-scope="scope">
          <el-progress 
            :percentage="scope.row.battery_level" 
            :stroke-width="15" 
            :color="getBatteryColor(scope.row.battery_level)"
            text-inside
          ></el-progress>
        </template>
      </el-table-column>

      <el-table-column prop="capacity" label="规格" width="100" align="center">
        <template slot-scope="scope">
          {{ formatCapacity(scope.row.capacity) }}
        </template>
      </el-table-column>

      <el-table-column prop="function_type" label="功能" width="100" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.function_type === 'fast' ? 'warning' : 'info'" size="mini">
            {{ scope.row.function_type === 'fast' ? '快充' : '普通' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="160" fixed="right" align="center">
      <template slot-scope="scope">

        <!-- ✅ 当前用户正在使用 → 归还 -->
        <el-button
          v-if="scope.row.username === currentUsername"
          @click="simulateReturn(scope.row.id)"
          size="small"
          type="danger"
        >
          归还
        </el-button>

        <!-- ✅ 空闲设备 → 借出 -->
        <el-button
          v-else-if="!scope.row.username"
          @click="simulateRent(scope.row.id)"
          size="small"
          type="primary"
          :disabled="scope.row.status !== 'online' || scope.row.battery_level < 20"
        >
          借出
        </el-button>

        <!-- ❌ 被别人租用 -->
        <el-button
          v-else
          size="small"
          disabled
        >
          使用中
        </el-button>

      </template>
    </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
      ></el-pagination>
    </div>
  </div>
</template>

<script>

import request from '../../utils/request'; 

export default {
    name: 'PowerbankRent',
    data() {
        return {
            loading: false,
            searchForm: {
                location: '',
                status: 'online', // 默认只显示在线可用的
                capacity: '',
                functionType: ''
            },
            currentUsername: localStorage.getItem('username') || '',
            // 使用 tableData 存储实际数据
            tableData: [], 
            total: 0, // 🌟 新增：用于分页的总条目数
            
            // 模拟正在进行的订单 (保持不变，用于前端逻辑控制)
            currentOrder: null || { id: 2, currentBattery: 45 }, 
            
            // 分页状态
            currentPage: 1,
            pageSize: 10,
        };
    },
   
    computed: {
        paginatedData() {
            // 如果后端返回的就是当前页数据，则直接返回 tableData
            return this.tableData; 
        }
        
    },
    methods: {
        // 🌟 新增：从 Flask 后端接口获取数据
        async fetchData() {
            this.loading = true;
            try {
                // 构建查询参数 (对应 Flask 接口的 request.args.get())
                const params = {
                    location: this.searchForm.location,
                    status: this.searchForm.status,
                    capacity: this.searchForm.capacity,
                    function_type: this.searchForm.functionType,
                    
                    // 💡 如果您想让后端处理分页，还需要传递：
                    pageSize: this.pageSize,
                    currentPage: this.currentPage 
                };

                const response = await request.get(`/api/powerbanks`, {
                    params: params
                });

                if (response.data.data) {
                    this.tableData = response.data.data;
                    this.total = response.data.total;
                    this.$message.success(`查询成功！共找到 ${this.total} 个充电宝。`);
                } else {
                    this.tableData = [];
                    this.total = 0;
                    this.$message.info(response.data.message || '未找到符合条件的充电宝。');
                }

            } catch (error) {
                console.error("获取充电宝数据失败:", error);
                this.$message.error('网络错误或后端服务不可用，请稍后再试。');
                this.tableData = [];
                this.total = 0;
            } finally {
                this.loading = false;
            }
        },

        // --- 数据格式化方法 (保持不变) ---
        formatStatus(status) {
            const map = { 'online': '在线', 'offline': '使用', 'repair': '维修' };
            return map[status] || status;
        },
        getStatusTagType(status) {
            const map = { 'online': 'success', 'offline': 'info', 'repair': 'danger' };
            return map[status] || '';
        },
        formatCapacity(capacity) {
            const map = { 'small': '小型 (S)', 'medium': '中型 (M)', 'large': '大型 (L)' };
            return map[capacity] || capacity;
        },
        getBatteryColor(level) {
            if (level > 60) return '#67c23a'; // 绿色
            if (level > 20) return '#e6a23c'; // 黄色
            return '#f56c6c'; // 红色
        },

        // --- 操作方法 ---
        async simulateRent(id) {
          this.$confirm(`确认租借该充电宝吗？`, '确认租借', {
            confirmButtonText: '立即租借',
            cancelButtonText: '取消',
            type: 'info'
          }).then(async () => {
            try {
              const res = await request.post('/api/rent', {
                powerbank_id: id,
                username: this.currentUsername
              });

              this.$message.success(res.data.message || '租借成功');
              this.fetchData(); // 刷新列表

            } catch (e) {
              this.$message.error(e.response?.data?.message || '租借失败');
            }

          });
        },
        async simulateReturn(id) {
          this.$confirm('确认归还该充电宝？', '归还确认', {
            confirmButtonText: '确认归还',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(async () => {

            try {
              const res = await request.post('/api/return', {
                powerbank_id: id,
                username: this.currentUsername
              });

              this.$message.success(res.data.message || '归还成功');
              this.fetchData();

            } catch (e) {
              this.$message.error(e.response?.data?.message || '归还失败');
            }

          });
        },

        // --- 搜索/分页方法 (修改为调用 fetchData) ---
        handleSearch() {
            this.currentPage = 1; // 搜索后回到第一页
            this.fetchData(); // 🌟 调用实际数据获取方法
        },
        handleReset() {
            this.searchForm = { location: '', status: 'online', capacity: '', functionType: '' };
            this.handleSearch(); // 重置后执行搜索
        },
        handleSizeChange(val) {
            this.pageSize = val;
            this.fetchData(); // 改变每页大小后重新获取数据
        },
        handleCurrentChange(val) {
            this.currentPage = val;
            this.fetchData(); // 改变页码后重新获取数据
        }
    },
    // 🌟 钩子函数：组件挂载完成后立即获取数据
    mounted() {
        this.fetchData();
    }
};
</script>

<style scoped>
/* 保持与管理端一致的样式风格 */
.powerbank-rent-container {
  padding: 5px;
}
.page-title {
    color: #4a69bd;
    margin-bottom: 20px;
    font-size: 1.5rem;
}

/* 顶部查询面板样式 */
.search-panel {
    padding: 15px 20px 0;
    margin-bottom: 20px;
}
.el-form-item {
    margin-bottom: 15px;
}

/* 表格样式美化 */
.el-table {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}
/* 分页 */
.pagination-container {
    margin-top: 20px;
    text-align: right;
}
</style>