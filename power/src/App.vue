<template>
  <div id="app">
    <router-view></router-view>
    <FloatingAssistant v-if="shouldShowAssistant" />
  </div>
</template>

<script>
import FloatingAssistant from './components/FloatingAssistant.vue';

export default {
  name: 'App',
  components: { FloatingAssistant },
  computed: {
    shouldShowAssistant() {
      // 仅在用户端页面显示（/home 及其子路由）
      return this.$route && String(this.$route.path || '').startsWith('/home');
    }
  }
};
</script>
