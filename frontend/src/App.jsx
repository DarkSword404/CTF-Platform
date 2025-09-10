import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import ChallengeList from './pages/ChallengeList';
import ChallengeDetail from './pages/ChallengeDetail';
import AIModelManager from './pages/AIModelManager';
import { isAuthenticated, hasRole } from './lib/auth';
import './App.css';

// 受保护的路由组件
const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

// 管理员路由组件
const AdminRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  if (!hasRole('admin')) {
    return <Navigate to="/challenges" />;
  }
  return children;
};

// 公开路由组件（已登录用户重定向）
const PublicRoute = ({ children }) => {
  return !isAuthenticated() ? children : <Navigate to="/challenges" />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />

        {/* 受保护的路由 */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout>
              <Navigate to="/challenges" />
            </Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/challenges" element={
          <ProtectedRoute>
            <Layout>
              <ChallengeList />
            </Layout>
          </ProtectedRoute>
        } />
        
        <Route path="/challenges/:id" element={
          <ProtectedRoute>
            <Layout>
              <ChallengeDetail />
            </Layout>
          </ProtectedRoute>
        } />

        <Route path="/admin/ai-models" element={
          <AdminRoute>
            <Layout>
              <AIModelManager />
            </Layout>
          </AdminRoute>
        } />

        {/* 404页面 */}
        <Route path="*" element={
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
              <p className="text-gray-600 mb-4">页面不存在</p>
              <a href="/" className="text-blue-600 hover:text-blue-500">
                返回首页
              </a>
            </div>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;
