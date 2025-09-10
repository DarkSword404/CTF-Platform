import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  // 用户注册
  register: (data) => api.post('/register', data),
  
  // 用户登录
  login: (data) => api.post('/login', data),
  
  // 获取当前用户信息
  getCurrentUser: () => api.get('/me'),
  
  // 更新当前用户信息
  updateCurrentUser: (data) => api.put('/me', data),
  
  // 修改密码
  changePassword: (data) => api.put('/me/password', data),
};

// 题目相关API
export const challengeAPI = {
  // 获取题目列表
  getChallenges: (params) => api.get('/challenges', { params }),
  
  // 获取题目详情
  getChallenge: (id) => api.get(`/challenges/${id}`),
  
  // 创建题目
  createChallenge: (data) => api.post('/challenges', data),
  
  // 更新题目
  updateChallenge: (id, data) => api.put(`/challenges/${id}`, data),
  
  // 删除题目
  deleteChallenge: (id) => api.delete(`/challenges/${id}`),
  
  // 提交Flag
  submitFlag: (id, data) => api.post(`/challenges/${id}/submit-flag`, data),
};

// AI相关API
export const aiAPI = {
  // AI生成题目
  generateChallenge: (data) => api.post('/ai/generate-challenge', data),
  
  // AI生成Flag
  generateFlag: (data) => api.post('/ai/generate-flag', data),
  
  // 获取AI调用日志
  getCallLogs: (params) => api.get('/ai/call-logs', { params }),
};

// 多AI模型API
export const aiMultiAPI = {
  // 获取可用的AI提供商
  getProviders: () => api.get('/ai-multi/providers'),
  
  // 多AI模型生成题目
  generateChallenge: (data) => api.post('/ai-multi/generate-challenge', data),
  
  // 多AI模型生成Flag
  generateFlag: (data) => api.post('/ai-multi/generate-flag', data),
  
  // 多AI模型生成文本
  generateText: (data) => api.post('/ai-multi/generate-text', data),
};

// AI管理API
export const aiAdminAPI = {
  // 获取AI提供商配置列表
  getProviders: (params) => api.get('/ai-admin/providers', { params }),
  
  // 创建AI提供商配置
  createProvider: (data) => api.post('/ai-admin/providers', data),
  
  // 更新AI提供商配置
  updateProvider: (id, data) => api.put(`/ai-admin/providers/${id}`, data),
  
  // 删除AI提供商配置
  deleteProvider: (id) => api.delete(`/ai-admin/providers/${id}`),
  
  // 测试AI提供商连接
  testProvider: (id) => api.post(`/ai-admin/providers/${id}/test`),
  
  // 获取AI使用统计
  getUsageStats: (params) => api.get('/ai-admin/usage-stats', { params }),
  
  // 初始化默认AI提供商配置
  initDefaultProviders: () => api.post('/ai-admin/init-default-providers'),
};

// 管理员相关API
export const adminAPI = {
  // 获取所有用户
  getAllUsers: (params) => api.get('/admin/users', { params }),
  
  // 更新用户信息
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  
  // 删除用户
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  
  // 审核题目
  reviewChallenge: (id, data) => api.post(`/admin/challenges/${id}/review`, data),
  
  // 更新题目状态
  updateChallengeStatus: (id, data) => api.put(`/admin/challenges/${id}/status`, data),
  
  // 获取统计信息
  getStatistics: () => api.get('/admin/statistics'),
  
  // 获取所有AI调用日志
  getAllAILogs: (params) => api.get('/admin/ai/logs', { params }),
};

export default api;

