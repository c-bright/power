<template>
  <div class="device-container">
    <el-card shadow="never" class="table-card">
      <div slot="header" class="header-section">
        <div class="search-bar">
          <el-input 
            v-model="filter.location" 
            placeholder="按位置搜索" 
            size="small" 
            style="width: 200px; margin-right: 10px" 
            clearable
            @clear="handleSearch"
          ></el-input>
          
          <el-select v-model="filter.status" placeholder="状态选择" size="small" style="width: 110px; margin-right: 10px" @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="在线" value="online"></el-option>
            <el-option label="维修" value="repair"></el-option>
          </el-select>
          
          <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">查找</el-button>
        </div>
        <el-button type="success" size="small" icon="el-icon-plus" @click="handleAdd">新建设备</el-button>
      </div>

      <el-table :data="deviceList" stripe style="width: 100%" v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
        <el-table-column prop="id" label="设备ID" width="80" align="center"></el-table-column>
        <el-table-column prop="location" label="位置" min-width="140" show-overflow-tooltip></el-table-column>
        
        <el-table-column label="状态" width="90" align="center">
          <template slot-scope="scope">
            <el-tag :type="statusMap[scope.row.status]?.type || 'info'" size="mini" effect="dark">
              {{ statusMap[scope.row.status]?.text || scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="电量" width="140">
          <template slot-scope="scope">
            <el-progress 
              :percentage="scope.row.battery_level" 
              :color="getBatteryColor(scope.row.battery_level)"
              :stroke-width="8"
            ></el-progress>
          </template>
        </el-table-column>

        <el-table-column label="容量规格" width="100" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" type="info">{{ capacityLabels[scope.row.capacity] }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="功能类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag size="mini" :type="scope.row.function_type === 'fast' ? 'warning' : 'plain'">
              {{ scope.row.function_type === 'fast' ? '快充' : '普充' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="create_time" label="创建时间" width="160" align="center">
          <template slot-scope="scope">
            <span class="time-style">{{ scope.row.create_time }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="mini" icon="el-icon-edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" icon="el-icon-delete" style="color: #f56c6c" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" style="margin-top: 20px; text-align: right;">
        <el-pagination 
          background 
          @current-change="handlePageChange" 
          :current-page.sync="currentPage" 
          layout="total, prev, pager, next" 
          :total="total" 
          :page-size="pageSize"
        ></el-pagination>
      </div>
    </el-card>

    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="450px">
      <el-form :model="form" label-width="80px" size="small">
        <el-form-item label="投放位置">
          <el-input v-model="form.location" placeholder="输入详细投放地址"></el-input>
        </el-form-item>
        <el-form-item label="当前电量">
          <el-input-number v-model="form.battery_level" :min="0" :max="100"></el-input-number> %
        </el-form-item>
        <el-form-item label="容量规格">
          <el-select v-model="form.capacity" style="width: 100%">
            <el-option label="大容量" value="large"></el-option>
            <el-option label="中容量" value="medium"></el-option>
            <el-option label="小容量" value="small"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="功能类型">
          <el-radio-group v-model="form.function_type">
            <el-radio label="fast">快充</el-radio>
            <el-radio label="normal">普充</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="在线" value="online"></el-option>
            <el-option label="维修" value="repair"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button size="small" @click="dialogVisible = false">取 消</el-button>
        <el-button size="small" type="primary" @click="submitForm">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '../../utils/request'; 

export default {
  data() {
    return {
      loading: false,
      dialogVisible: false,
      dialogTitle: '新建设备',
      currentPage: 1,
      pageSize: 10,
      total: 0, 
      statusMap: {
        online: { text: '在线', type: 'success' },
        offline: { text: '在线', type: 'success' },
        repair: { text: '维修', type: 'info' }
      },
      capacityLabels: { small: '小容量', medium: '中容量', large: '大容量' },
      filter: { location: '', status: '' }, 
      form: { id: null, location: '', status: 'online', battery_level: 100, capacity: 'medium', function_type: 'normal' },
      deviceList: [] 
    }
  },
  methods: {
    // 1. 核心查询逻辑
    async handleSearch() {
      this.loading = true;
      try {
        const response = await request.get('/api/devices', {
          params: {
            location: this.filter.location,
            status: this.filter.status,
            currentPage: this.currentPage,
            pageSize: this.pageSize
          }
        });
        
        // 适配拦截器：如果返回的是原始 response，取其 data
        const res = response.data || response;
        console.log("解析出的数据内容:", res);

        let finalData = [];
        let finalTotal = 0;

        if (res && res.code === 200) {
          finalData = res.data;
          finalTotal = res.total;
        } else if (Array.isArray(res)) {
          finalData = res;
          finalTotal = res.length;
        }

        this.deviceList = finalData;
        this.total = finalTotal || 0;
      } catch (error) {
        console.error("获取列表失败:", error);
        this.$message.error("获取列表失败");
      } finally {
        this.loading = false;
      }
    },

    handlePageChange(val) {
      this.currentPage = val;
      this.handleSearch();
    },

    getBatteryColor(level) {
      return level < 20 ? '#f56c6c' : (level < 80 ? '#e6a23c' : '#67c23a');
    },

    handleAdd() {
      this.dialogTitle = '创建新设备';
      this.form = { id: null, location: '', status: 'online', battery_level: 100, capacity: 'medium', function_type: 'normal' };
      this.dialogVisible = true;
    },

    handleEdit(row) {
      this.dialogTitle = '编辑设备信息';
      this.form = { ...row };
      this.dialogVisible = true;
    },

    // 5. 提交操作
    async submitForm() {
      if (!this.form.location) return this.$message.error('请填写投放位置');
      
      try {
        const response = this.form.id 
          ? await request.put(`/api/devices/${this.form.id}`, this.form)
          : await request.post('/api/devices', this.form);

        const res = response.data; 

        if (res && res.code === 200) {
          // 顺序：关闭 -> 提示 -> 打印 -> 刷新
          this.dialogVisible = false;
          this.$message.success('操作成功');
          console.log("后端返回详情:");
          this.handleSearch();
        } else {
          this.$message.error(res.message || '保存失败');
        }
      } catch (error) {
        console.error("提交异常:", error);
        this.$message.error('网络请求异常');
      }
    },

    // 6. 删除操作
    async handleDelete(row) {
      try {
        await this.$confirm(`确定要删除位于【${row.location}】的设备吗？`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });

        const response = await request.delete(`/api/devices/${row.id}`);
        const res = response.data;

        if (res && res.code === 200) {
          this.$message.success('设备已成功删除');
          this.handleSearch(); 
        } else {
          this.$message.error(res.message || '删除失败');
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error("删除异常:", error);
          this.$message.error('请求接口失败');
        }
      }
    }
  },
  mounted() {
    this.handleSearch();
  }
}
</script>

<style scoped>
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  display: flex;
  align-items: center;
}
.time-style {
  font-family: monospace;
  color: #666;
}
</style>