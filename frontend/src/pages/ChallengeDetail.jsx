import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { 
  Trophy, 
  Users, 
  Clock, 
  Download, 
  Play, 
  Square, 
  CheckCircle, 
  Flag,
  Loader2,
  ArrowLeft,
  User
} from 'lucide-react';
import { challengeAPI } from '@/lib/api';

const ChallengeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [flagInput, setFlagInput] = useState('');
  const [containerStatus, setContainerStatus] = useState('stopped'); // stopped, starting, running

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

  const fetchChallenge = async () => {
    try {
      setLoading(true);
      const response = await challengeAPI.getChallenge(id);
      setChallenge(response.data);
    } catch (error) {
      setError(error.response?.data?.error || '获取题目详情失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFlag = async (e) => {
    e.preventDefault();
    if (!flagInput.trim()) {
      setSubmitMessage('请输入Flag');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      
      const response = await challengeAPI.submitFlag(id, {
        submitted_flag: flagInput.trim()
      });
      
      const { is_correct, score_awarded, message, note } = response.data;
      
      if (is_correct) {
        setSubmitMessage(`🎉 ${message}！获得 ${score_awarded} 分`);
        // 更新题目状态
        setChallenge(prev => ({
          ...prev,
          solved_by_user: true
        }));
      } else {
        setSubmitMessage('❌ Flag不正确，请重试');
      }
      
      if (note) {
        setSubmitMessage(prev => `${prev} (${note})`);
      }
      
    } catch (error) {
      setSubmitMessage(error.response?.data?.error || '提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStartContainer = () => {
    setContainerStatus('starting');
    // 模拟容器启动过程
    setTimeout(() => {
      setContainerStatus('running');
    }, 3000);
  };

  const handleStopContainer = () => {
    setContainerStatus('stopped');
  };

  useEffect(() => {
    fetchChallenge();
  }, [id]);

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

  if (error) {
    return (
      <div className="space-y-4">
        <Button
          variant="ghost"
          onClick={() => navigate('/challenges')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回题目列表
        </Button>
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!challenge) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 返回按钮 */}
      <Button
        variant="ghost"
        onClick={() => navigate('/challenges')}
        className="mb-4"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        返回题目列表
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 主要内容区域 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 题目信息 */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-2xl mb-3">
                    {challenge.title}
                    {challenge.solved_by_user && (
                      <CheckCircle className="inline-block ml-2 h-6 w-6 text-green-500" />
                    )}
                  </CardTitle>
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className={getCategoryColor(challenge.category)}>
                      {challenge.category}
                    </Badge>
                    <Badge className={getDifficultyColor(challenge.difficulty)}>
                      {challenge.difficulty}
                    </Badge>
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <Trophy className="h-4 w-4" />
                      <span>{challenge.score} 分</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      <span>作者: {challenge.author?.username}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      <span>{challenge.solve_count} 人解出</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>发布于 {new Date(challenge.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap text-gray-700">
                  {challenge.description || '暂无题目描述'}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 附件下载 */}
          {challenge.attachments && challenge.attachments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">题目附件</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {challenge.attachments.map((attachment, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Download className="h-4 w-4 text-gray-400" />
                        <div>
                          <div className="font-medium">{attachment.name}</div>
                          <div className="text-sm text-gray-500">{attachment.size}</div>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">
                        下载
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 侧边栏 */}
        <div className="space-y-6">
          {/* 容器管理 */}
          {challenge.container_image_name && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">题目环境</CardTitle>
                <CardDescription>
                  点击启动按钮来启动题目环境
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">状态:</span>
                  <Badge variant={
                    containerStatus === 'running' ? 'default' :
                    containerStatus === 'starting' ? 'secondary' : 'outline'
                  }>
                    {containerStatus === 'running' ? '运行中' :
                     containerStatus === 'starting' ? '启动中' : '已停止'}
                  </Badge>
                </div>

                {containerStatus === 'stopped' && (
                  <Button 
                    onClick={handleStartContainer}
                    className="w-full"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    启动环境
                  </Button>
                )}

                {containerStatus === 'starting' && (
                  <Button disabled className="w-full">
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    启动中...
                  </Button>
                )}

                {containerStatus === 'running' && (
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="text-sm font-medium text-green-800 mb-1">
                        访问地址:
                      </div>
                      <div className="text-sm text-green-700 font-mono">
                        http://127.0.0.1:8080
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      onClick={handleStopContainer}
                      className="w-full"
                    >
                      <Square className="h-4 w-4 mr-2" />
                      停止环境
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Flag提交 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">提交Flag</CardTitle>
              <CardDescription>
                找到Flag后在此处提交
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitFlag} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="flag" className="text-sm font-medium">
                    Flag
                  </label>
                  <Input
                    id="flag"
                    value={flagInput}
                    onChange={(e) => setFlagInput(e.target.value)}
                    placeholder="flag{...}"
                    disabled={submitting}
                  />
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={submitting || !flagInput.trim()}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      提交中...
                    </>
                  ) : (
                    <>
                      <Flag className="h-4 w-4 mr-2" />
                      提交Flag
                    </>
                  )}
                </Button>

                {submitMessage && (
                  <Alert className={
                    submitMessage.includes('🎉') ? 'border-green-200 bg-green-50' : 
                    submitMessage.includes('❌') ? 'border-red-200 bg-red-50' : ''
                  }>
                    <AlertDescription>{submitMessage}</AlertDescription>
                  </Alert>
                )}
              </form>
            </CardContent>
          </Card>

          {/* 提示系统 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">解题提示</CardTitle>
              <CardDescription>
                遇到困难？查看提示可能会有帮助
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  提示 1 (-10分)
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  提示 2 (-20分)
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  提示 3 (-30分)
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ChallengeDetail;

