import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  User, 
  LogOut, 
  Settings, 
  Shield, 
  PlusCircle,
  BarChart3,
  Users,
  FileText
} from 'lucide-react';
import { isAuthenticated, isAdmin, isChallenger, getUserDisplayName, logout } from '@/lib/auth';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const isLoggedIn = isAuthenticated();
  const userDisplayName = getUserDisplayName();

  const handleLogout = () => {
    logout();
  };

  const navigation = [
    { name: '题目列表', href: '/challenges', icon: FileText },
    ...(isChallenger() || isAdmin() ? [
      { name: '创建题目', href: '/create-challenge', icon: PlusCircle },
      { name: '我的题目', href: '/my-challenges', icon: FileText },
      { name: 'AI助手', href: '/ai-assistant', icon: Settings }
    ] : []),
    ...(isAdmin() ? [
      { name: '用户管理', href: '/admin/users', icon: Users },
      { name: '题目审核', href: '/admin/challenges', icon: Shield },
      { name: 'AI模型管理', href: '/admin/ai-models', icon: Settings },
      { name: '统计面板', href: '/admin/statistics', icon: BarChart3 }
    ] : [])
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo和主导航 */}
            <div className="flex">
              <Link to="/" className="flex items-center px-4 text-xl font-bold text-blue-600">
                CTF靶场平台
              </Link>
              
              {isLoggedIn && (
                <div className="hidden md:flex space-x-8 ml-8">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          location.pathname === item.href
                            ? 'text-blue-600 bg-blue-50'
                            : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                        }`}
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 用户菜单 */}
            <div className="flex items-center space-x-4">
              {isLoggedIn ? (
                <>
                  <Link
                    to="/profile"
                    className="flex items-center space-x-2 text-gray-600 hover:text-blue-600"
                  >
                    <User className="w-5 h-5" />
                    <span className="hidden md:block">{userDisplayName}</span>
                  </Link>
                  <Button
                    onClick={handleLogout}
                    variant="ghost"
                    size="sm"
                    className="text-gray-600 hover:text-red-600"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    退出
                  </Button>
                </>
              ) : (
                <div className="flex space-x-2">
                  <Button
                    onClick={() => navigate('/login')}
                    variant="ghost"
                    size="sm"
                  >
                    登录
                  </Button>
                  <Button
                    onClick={() => navigate('/register')}
                    size="sm"
                  >
                    注册
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 移动端导航菜单 */}
        {isLoggedIn && (
          <div className="md:hidden border-t">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                      location.pathname === item.href
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* 主内容区域 */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            © 2024 CTF靶场平台. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;

