import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Brain, Zap, Clock, CheckCircle, XCircle, BarChart3, Settings, Plus, Trash2, Edit } from 'lucide-react';
import { aiMultiAPI, aiAdminAPI } from '../lib/api';

const AIModelManager = () => {
  const [providers, setProviders] = useState([]);
  const [availableProviders, setAvailableProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({});
  
  // 表单状态
  const [challengeForm, setChallengeForm] = useState({
    challenge_type: 'Web',
    difficulty: 'Easy',
    prompt: '',
    provider: ''
  });
  
  const [flagForm, setFlagForm] = useState({
    challenge_description: '',
    challenge_type: 'Web',
    provider: ''
  });
  
  const [textForm, setTextForm] = useState({
    prompt: '',
    provider: '',
    max_tokens: 2000,
    temperature: 0.7
  });

  useEffect(() => {
    loadProviders();
    loadAvailableProviders();
    loadStats();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await aiAdminAPI.getProviders();
      setProviders(response.data.providers);
    } catch (err) {
      setError('加载AI提供商配置失败: ' + err.message);
    }
  };

  const loadAvailableProviders = async () => {
    try {
      const response = await aiMultiAPI.getProviders();
      setAvailableProviders(response.data.providers);
    } catch (err) {
      setError('加载可用AI提供商失败: ' + err.message);
    }
  };

  const loadStats = async () => {
    try {
      const response = await aiAdminAPI.getUsageStats();
      setStats(response.data);
    } catch (err) {
      console.error('加载统计数据失败:', err);
    }
  };

  const handleGenerateChallenge = async () => {
    if (!challengeForm.prompt.trim()) {
      setError('请输入题目要求');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiMultiAPI.generateChallenge(challengeForm);
      setResult({
        type: 'challenge',
        data: response.data
      });
    } catch (err) {
      setError('生成题目失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFlag = async () => {
    if (!flagForm.challenge_description.trim()) {
      setError('请输入题目描述');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiMultiAPI.generateFlag(flagForm);
      setResult({
        type: 'flag',
        data: response.data
      });
    } catch (err) {
      setError('生成Flag失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateText = async () => {
    if (!textForm.prompt.trim()) {
      setError('请输入提示词');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiMultiAPI.generateText(textForm);
      setResult({
        type: 'text',
        data: response.data
      });
    } catch (err) {
      setError('生成文本失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    switch (result.type) {
      case 'challenge':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                生成的题目 - {result.data.provider_used}
              </CardTitle>
              <CardDescription>
                生成时间: {result.data.generation_time_ms}ms
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="font-semibold">标题</Label>
                <p className="mt-1">{result.data.challenge?.title}</p>
              </div>
              <div>
                <Label className="font-semibold">描述</Label>
                <p className="mt-1 whitespace-pre-wrap">{result.data.challenge?.description}</p>
              </div>
              <div>
                <Label className="font-semibold">Flag</Label>
                <code className="mt-1 block p-2 bg-gray-100 rounded">{result.data.challenge?.flag}</code>
              </div>
              {result.data.challenge?.hints && result.data.challenge.hints.length > 0 && (
                <div>
                  <Label className="font-semibold">提示</Label>
                  <ul className="mt-1 list-disc list-inside">
                    {result.data.challenge.hints.map((hint, index) => (
                      <li key={index}>{hint}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 'flag':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                生成的Flag - {result.data.provider_used}
              </CardTitle>
              <CardDescription>
                生成时间: {result.data.generation_time_ms}ms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <code className="block p-4 bg-gray-100 rounded text-lg font-mono">
                {result.data.flag}
              </code>
            </CardContent>
          </Card>
        );

      case 'text':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                生成的文本 - {result.data.provider_used}
              </CardTitle>
              <CardDescription>
                生成时间: {result.data.generation_time_ms}ms | 词数: {result.data.token_count}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="whitespace-pre-wrap p-4 bg-gray-50 rounded">
                {result.data.text}
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI模型管理</h1>
          <p className="text-gray-600 mt-2">管理和使用多个AI模型进行题目生成</p>
        </div>
        <div className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          <span className="text-sm">可用提供商: {availableProviders.length}</span>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>可用提供商</CardTitle>
              <CardDescription>当前可用的AI提供商列表</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {availableProviders.map((provider) => (
                  <div key={provider} className="flex items-center justify-between p-2 border rounded">
                    <span className="text-sm font-mono">{provider}</span>
                    <Badge variant="outline">可用</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {stats.summary && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>使用统计</CardTitle>
                <CardDescription>AI模型使用情况</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-sm">
                    <div className="font-medium">总调用次数</div>
                    <div className="text-gray-600">{stats.summary.total_calls}</div>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium">成功率</div>
                    <div className="text-gray-600">{stats.summary.success_rate}%</div>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium">平均响应时间</div>
                    <div className="text-gray-600">{stats.summary.avg_response_time}ms</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="lg:col-span-3">
          <Tabs defaultValue="challenge" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="challenge">生成题目</TabsTrigger>
              <TabsTrigger value="flag">生成Flag</TabsTrigger>
              <TabsTrigger value="text">生成文本</TabsTrigger>
              <TabsTrigger value="config">配置管理</TabsTrigger>
            </TabsList>

            <TabsContent value="challenge">
              <Card>
                <CardHeader>
                  <CardTitle>AI生成题目</CardTitle>
                  <CardDescription>使用AI模型生成CTF题目</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="challenge_type">题目类型</Label>
                      <Select value={challengeForm.challenge_type} onValueChange={(value) => 
                        setChallengeForm({...challengeForm, challenge_type: value})
                      }>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Web">Web</SelectItem>
                          <SelectItem value="Pwn">Pwn</SelectItem>
                          <SelectItem value="Reverse">Reverse</SelectItem>
                          <SelectItem value="Crypto">Crypto</SelectItem>
                          <SelectItem value="Misc">Misc</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="difficulty">难度</Label>
                      <Select value={challengeForm.difficulty} onValueChange={(value) => 
                        setChallengeForm({...challengeForm, difficulty: value})
                      }>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Easy">Easy</SelectItem>
                          <SelectItem value="Medium">Medium</SelectItem>
                          <SelectItem value="Hard">Hard</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="provider">AI提供商（可选）</Label>
                    <Select value={challengeForm.provider} onValueChange={(value) => 
                      setChallengeForm({...challengeForm, provider: value})
                    }>
                      <SelectTrigger>
                        <SelectValue placeholder="使用默认提供商" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableProviders.map((provider) => (
                          <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="prompt">题目要求</Label>
                    <Textarea
                      id="prompt"
                      placeholder="请描述您想要生成的题目要求..."
                      value={challengeForm.prompt}
                      onChange={(e) => setChallengeForm({...challengeForm, prompt: e.target.value})}
                      rows={4}
                    />
                  </div>
                  <Button onClick={handleGenerateChallenge} disabled={loading} className="w-full">
                    {loading ? '生成中...' : '生成题目'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="flag">
              <Card>
                <CardHeader>
                  <CardTitle>AI生成Flag</CardTitle>
                  <CardDescription>根据题目描述生成合适的Flag</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="challenge_type">题目类型</Label>
                      <Select value={flagForm.challenge_type} onValueChange={(value) => 
                        setFlagForm({...flagForm, challenge_type: value})
                      }>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Web">Web</SelectItem>
                          <SelectItem value="Pwn">Pwn</SelectItem>
                          <SelectItem value="Reverse">Reverse</SelectItem>
                          <SelectItem value="Crypto">Crypto</SelectItem>
                          <SelectItem value="Misc">Misc</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="provider">AI提供商（可选）</Label>
                      <Select value={flagForm.provider} onValueChange={(value) => 
                        setFlagForm({...flagForm, provider: value})
                      }>
                        <SelectTrigger>
                          <SelectValue placeholder="使用默认提供商" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableProviders.map((provider) => (
                            <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="challenge_description">题目描述</Label>
                    <Textarea
                      id="challenge_description"
                      placeholder="请输入题目描述..."
                      value={flagForm.challenge_description}
                      onChange={(e) => setFlagForm({...flagForm, challenge_description: e.target.value})}
                      rows={4}
                    />
                  </div>
                  <Button onClick={handleGenerateFlag} disabled={loading} className="w-full">
                    {loading ? '生成中...' : '生成Flag'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="text">
              <Card>
                <CardHeader>
                  <CardTitle>AI生成文本</CardTitle>
                  <CardDescription>使用AI模型生成自定义文本内容</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="provider">AI提供商（可选）</Label>
                    <Select value={textForm.provider} onValueChange={(value) => 
                      setTextForm({...textForm, provider: value})
                    }>
                      <SelectTrigger>
                        <SelectValue placeholder="使用默认提供商" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableProviders.map((provider) => (
                          <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="max_tokens">最大Token数</Label>
                      <Input
                        id="max_tokens"
                        type="number"
                        min="1"
                        max="4000"
                        value={textForm.max_tokens}
                        onChange={(e) => setTextForm({...textForm, max_tokens: parseInt(e.target.value)})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="temperature">温度 (0-2)</Label>
                      <Input
                        id="temperature"
                        type="number"
                        min="0"
                        max="2"
                        step="0.1"
                        value={textForm.temperature}
                        onChange={(e) => setTextForm({...textForm, temperature: parseFloat(e.target.value)})}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="prompt">提示词</Label>
                    <Textarea
                      id="prompt"
                      placeholder="请输入提示词..."
                      value={textForm.prompt}
                      onChange={(e) => setTextForm({...textForm, prompt: e.target.value})}
                      rows={4}
                    />
                  </div>
                  <Button onClick={handleGenerateText} disabled={loading} className="w-full">
                    {loading ? '生成中...' : '生成文本'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="config">
              <Card>
                <CardHeader>
                  <CardTitle>AI模型配置管理</CardTitle>
                  <CardDescription>管理AI模型的API密钥和基础URL</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                    <AlertDescription>
                      AI模型配置功能正在开发中，敬请期待。
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {renderResult()}
        </div>
      </div>
    </div>
  );
};

export default AIModelManager;

