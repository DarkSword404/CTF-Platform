import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Search, 
  Filter, 
  Trophy, 
  Clock, 
  Users, 
  CheckCircle,
  Circle,
  Star
} from 'lucide-react';
import { challengeAPI } from '@/lib/api';

const ChallengeList = () => {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    difficulty: '',
    status: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 12,
    total_count: 0,
    total_pages: 0
  });

  const categories = [
    { value: '', label: '全部分类' },
    { value: 'Web', label: 'Web' },
    { value: 'Pwn', label: 'Pwn' },
    { value: 'Reverse', label: 'Reverse' },
    { value: 'Crypto', label: 'Crypto' },
    { value: 'Misc', label: 'Misc' }
  ];

  const difficulties = [
    { value: '', label: '全部难度' },
    { value: 'Easy', label: '简单' },
    { value: 'Medium', label: '中等' },
    { value: 'Hard', label: '困难' }
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Web': return 'bg-blue-100 text-blue-800';
      case 'Pwn': return 'bg-purple-100 text-purple-800';
      case 'Reverse': return 'bg-indigo-100 text-indigo-800';
      case 'Crypto': return 'bg-pink-100 text-pink-800';
      case 'Misc': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        page_size: pagination.page_size,
        ...(filters.search && { search: filters.search }),
        ...(filters.category && { category: filters.category }),
        ...(filters.difficulty && { difficulty: filters.difficulty }),
        ...(filters.status && { status: filters.status })
      };

      const response = await challengeAPI.getChallenges(params);
      const { challenges: challengeList, total_count, total_pages } = response.data;
      
      setChallenges(challengeList);
      setPagination(prev => ({
        ...prev,
        total_count,
        total_pages
      }));
    } catch (error) {
      setError(error.response?.data?.error || '获取题目列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallenges();
  }, [pagination.page, filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPagination(prev => ({
      ...prev,
      page: 1
    }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchChallenges();
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({
      ...prev,
      page: newPage
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">题目列表</h1>
          <p className="text-gray-600 mt-1">
            共 {pagination.total_count} 道题目
          </p>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="搜索题目名称..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <Select
                  value={filters.category}
                  onValueChange={(value) => handleFilterChange('category', value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="分类" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select
                  value={filters.difficulty}
                  onValueChange={(value) => handleFilterChange('difficulty', value)}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="难度" />
                  </SelectTrigger>
                  <SelectContent>
                    {difficulties.map(diff => (
                      <SelectItem key={diff.value} value={diff.value}>
                        {diff.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* 错误提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 题目网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {challenges.map((challenge) => (
          <Card key={challenge.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg line-clamp-2">
                    {challenge.title}
                  </CardTitle>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={getCategoryColor(challenge.category)}>
                      {challenge.category}
                    </Badge>
                    <Badge className={getDifficultyColor(challenge.difficulty)}>
                      {challenge.difficulty}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center ml-2">
                  {challenge.solved_by_user ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <Circle className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Trophy className="h-4 w-4" />
                    <span>{challenge.score} 分</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>{challenge.solve_count} 人解出</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  作者: {challenge.author?.username}
                </div>
                <Link to={`/challenges/${challenge.id}`}>
                  <Button size="sm">
                    {challenge.solved_by_user ? '查看详情' : '开始解题'}
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 分页 */}
      {pagination.total_pages > 1 && (
        <div className="flex justify-center items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={pagination.page === 1}
          >
            上一页
          </Button>
          
          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
              let pageNum;
              if (pagination.total_pages <= 5) {
                pageNum = i + 1;
              } else if (pagination.page <= 3) {
                pageNum = i + 1;
              } else if (pagination.page >= pagination.total_pages - 2) {
                pageNum = pagination.total_pages - 4 + i;
              } else {
                pageNum = pagination.page - 2 + i;
              }
              
              return (
                <Button
                  key={pageNum}
                  variant={pageNum === pagination.page ? "default" : "outline"}
                  size="sm"
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </Button>
              );
            })}
          </div>
          
          <Button
            variant="outline"
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={pagination.page === pagination.total_pages}
          >
            下一页
          </Button>
        </div>
      )}

      {/* 空状态 */}
      {challenges.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            没有找到题目
          </h3>
          <p className="text-gray-600">
            尝试调整搜索条件或筛选器
          </p>
        </div>
      )}
    </div>
  );
};

export default ChallengeList;

