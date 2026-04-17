import Vue from 'vue'
import VueRouter from 'vue-router'

// --- 认证相关的组件 ---
import AuthLayout from '../views/auth/AuthLayout.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'

// --- 用户和管理员的顶层组件 ---
import Home from '@/views/user/Home.vue'
import Admin from '@/views/admin/Admin.vue'

// --- 用户首页的子组件 ---
import RentService from '@/views/user/RentService.vue';
import QueryRecord from '@/views/user/QueryRecord.vue';
import UserProfile from '@/views/user/UserProfile.vue';

//--- 管理员首页的子组件 ---
import DeviceManager from '@/views/admin/DeviceManager.vue';
import PricingRules from '@/views/admin/PricingRules.vue';
import VisualDashboard from '@/views/admin/VisualDashboard.vue';
import DisputeHandle from '@/views/admin/DisputeHandle.vue';


Vue.use(VueRouter)

const routes = [
  // 1. 根路径重定向到登录页
  {
    path: '/',
    redirect: '/auth/login'
  },

  // 2. 认证路由 (Login/Register)
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        component: Login
      },
      {
        path: 'register',
        component: Register
      }
    ]
  },

  // 3. 用户首页路由 (包含子路由)
 {
   path: '/home',
   component: Home,
   meta: { 
      role: 'users', 
      requiresAuth: true // 标记需要登录
 },
    // 🌟 用户首页的嵌套路由
    children: [
        { 
            path: 'rent',       // 完整路径: /home/rent
            component: RentService 
        },
        { 
            path: 'query',      // 完整路径: /home/query
            component: QueryRecord 
        },
        { 
            path: 'profile',    // 完整路径: /home/profile
            component: UserProfile 
        }
    ]
  },

  // 4. 管理员首页路由
 {
  path: '/admin',
  component: Admin, 
  meta: { 
    role: 'admin', 
    requiresAuth: true 
  },
  // 🌟 管理员首页的嵌套路由
  children: [
    { 
      path: 'device',    // 完整路径: /admin/device
      component: DeviceManager,
      meta: { title: '设备上下线' }
    },
    { 
      path: 'pricing',   // 完整路径: /admin/pricing
      component: PricingRules,
      meta: { title: '定价规则' }
    },
    { 
      path: 'visual',    // 完整路径: /admin/visual
      component: VisualDashboard,
      meta: { title: '可视化大屏' }
    },
    { 
      path: 'dispute',   // 完整路径: /admin/dispute
      component: DisputeHandle,
      meta: { title: '纠纷处理' }
    }
  ]
},
    
  // 5. 404 页面捕获
  {
      path: '*',
      redirect: '/auth/login' // 简单的 404 处理：回到登录页
  }
]


const router = new VueRouter({
 mode: 'history',
 routes
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(r => r.meta && r.meta.requiresAuth);
  if (!requiresAuth) return next();

  const token = localStorage.getItem('token');
  if (!token) return next('/auth/login');

  const expAt = Number(localStorage.getItem('token_expires_at') || 0);
  if (expAt && Date.now() > expAt) {
    localStorage.removeItem('token');
    localStorage.removeItem('token_expires_at');
    localStorage.removeItem('role');
    return next('/auth/login');
  }

  const requiredRole = to.matched.find(r => r.meta && r.meta.role)?.meta?.role;
  if (requiredRole) {
    const currentRole = localStorage.getItem('role');
    if (currentRole !== requiredRole) return next('/auth/login');
  }

  return next();
});

export default router
