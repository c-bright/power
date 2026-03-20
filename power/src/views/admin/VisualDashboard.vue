<template>
  <div class="dashboard-container" v-loading="loading">
    <div class="header-section">
      <h2 class="dashboard-title">运营数据总览</h2>
      <div class="filter-tools">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          value-format="yyyy-MM-dd"
          @change="fetchDashboardData"
        ></el-date-picker>
        <el-button type="primary" size="small" icon="el-icon-refresh" @click="fetchDashboardData" style="margin-left: 10px">刷新数据</el-button>
      </div>
    </div>

    <el-row :gutter="20" class="metric-cards">
      <el-col :span="6" v-for="(item, key) in metricConfigs" :key="key">
        <el-card shadow="hover" :class="['metric-card', item.type]">
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-value">
            <span v-if="item.isMoney">￥</span>
            <template v-if="key === 'topLocation'">
              <span class="text-value">{{ metrics[key] }}</span>
            </template>
            <template v-else>
              {{ metrics[key] | formatValue }}
            </template>
            <small v-if="item.unit" class="unit-text">{{ item.unit }}</small>
          </div>
          <div class="metric-growth">
            <template v-if="key === 'topLocation'">
              订单贡献: <b style="margin-left:5px">{{ metrics.topLocationValue }}</b> 单
            </template>
            <template v-else>
              <i :class="metrics[key + 'Growth'] >= 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
              {{ Math.abs(metrics[key + 'Growth']) }}% (周环比)
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-rows">
      <el-col :span="14">
        <el-card shadow="hover" class="chart-card">
          <div slot="header"><span>营收走势</span></div>
          <div id="revenueChart" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" class="chart-card">
          <div slot="header"><span>地区使用占比</span></div>
          <div id="locationPieChart" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import request from '../../utils/request';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      loading: false,
      dateRange: [],
      // 🚩 指标卡片配置
      metricConfigs: {
        totalRevenue: { label: '总营收', type: 'success', isMoney: true },
        topLocation: { label: '最受欢迎地区', type: 'primary' },
        totalOrders: { label: '总订单数', type: 'warning', unit: '单' },
        avgUsageTime: { label: '平均时长', type: 'danger', unit: '分钟' }
      },
      metrics: {
        totalRevenue: 0, totalRevenueGrowth: 0,
        topLocation: '-', topLocationValue: 0,
        totalOrders: 0, totalOrdersGrowth: 0,
        avgUsageTime: 0, avgUsageTimeGrowth: 0
      },
      chartData: { dates: [], revenueTrend: [], locationData: [] },
      chartInstances: {}
    };
  },
  filters: {
    formatValue(val) {
      return typeof val === 'number' ? val.toLocaleString() : val;
    }
  },
  mounted() {
    this.fetchDashboardData();
    window.addEventListener('resize', this.handleResize);
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true;
      try {
        const res = await request.get('/api/admin/dashboard-stats', {
          params: { start: this.dateRange?.[0], end: this.dateRange?.[1] }
        });
        if (res.data.success) {
          this.metrics = res.data.metrics;
          this.chartData = res.data.charts;
          this.$nextTick(() => {
            this.initRevenueChart();
            this.initLocationPieChart();
          });
        }
      } catch (error) {
        this.$message.error('数据加载失败');
      } finally {
        this.loading = false;
      }
    },
    initRevenueChart() {
      const chart = echarts.init(document.getElementById('revenueChart'));
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: this.chartData.dates },
        yAxis: { type: 'value' },
        series: [{ 
          name: '营收', type: 'line', smooth: true, 
          data: this.chartData.revenueTrend, 
          itemStyle: { color: '#67C23A' },
          areaStyle: { color: 'rgba(103, 194, 58, 0.1)' }
        }]
      });
      this.chartInstances.revenue = chart;
    },
    initLocationPieChart() {
      const chart = echarts.init(document.getElementById('locationPieChart'));
      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}单 ({d}%)' },
        legend: { bottom: '0' },
        series: [{
          type: 'pie', radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
          data: this.chartData.locationData
        }]
      });
      this.chartInstances.location = chart;
    },
    handleResize() {
      Object.values(this.chartInstances).forEach(i => i && i.resize());
    }
  }
};
</script>

<style scoped>
.dashboard-container { padding: 20px; background: #f5f7f9; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.metric-card { border-radius: 12px; height: 140px; }
.metric-card.primary { border-left: 5px solid #409EFF; }
.metric-card.success { border-left: 5px solid #67C23A; }
.metric-card.warning { border-left: 5px solid #E6A23C; }
.metric-card.danger { border-left: 5px solid #F56C6C; }
.text-value { font-size: 22px; color: #409EFF; font-weight: bold; }
.metric-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
.metric-growth { font-size: 13px; color: #909399; }
.chart-box { height: 320px; width: 100%; }
.unit-text { font-size: 14px; margin-left: 4px; color: #666; }
</style>