// 认证相关工具函数

/**
 * 获取存储的访问令牌
 */
export const getToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * 设置访问令牌
 */
export const setToken = (token) => {
  localStorage.setItem('access_token', token);
};

/**
 * 移除访问令牌
 */
export const removeToken = () => {
  localStorage.removeItem('access_token');
};

/**
 * 获取存储的用户信息
 */
export const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * 设置用户信息
 */
export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

/**
 * 移除用户信息
 */
export const removeUser = () => {
  localStorage.removeItem('user');
};

/**
 * 检查用户是否已登录
 */
export const isAuthenticated = () => {
  const token = getToken();
  const user = getUser();
  return !!(token && user);
};

/**
 * 检查用户是否有指定角色
 */
export const hasRole = (roleName) => {
  const user = getUser();
  return user && user.roles && user.roles.includes(roleName);
};

/**
 * 检查用户是否是管理员
 */
export const isAdmin = () => {
  return hasRole('admin');
};

/**
 * 检查用户是否是出题人
 */
export const isChallenger = () => {
  return hasRole('challenger');
};

/**
 * 登出用户
 */
export const logout = () => {
  removeToken();
  removeUser();
  window.location.href = '/login';
};

/**
 * 获取用户显示名称
 */
export const getUserDisplayName = () => {
  const user = getUser();
  return user ? (user.nickname || user.username) : '';
};

/**
 * 获取用户头像URL
 */
export const getUserAvatarUrl = () => {
  const user = getUser();
  return user?.avatar_url || '/default-avatar.png';
};

