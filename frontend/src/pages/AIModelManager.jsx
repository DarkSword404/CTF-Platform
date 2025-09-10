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
                生成的题目 - {result.data.model_used}
              </CardTitle>
              <CardDescription>
                生成时间: {result.data.generation_time_ms}ms
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="font-semibold">标题</Label>
                <p className="mt-1">{result.data.challenge.title}</p>
              </div>
              <div>
                <Label className="font-semibold">描述</Label>
                <p className="mt-1 whitespace-pre-wrap">{result.data.challenge.description}</p>
              </div>
              <div>
                <Label className="font-semibold">Flag</Label>
                <code className="mt-1 block p-2 bg-gray-100 rounded">{result.data.challenge.flag}</code>
              </div>
              {result.data.challenge.hints && result.data.challenge.hints.length > 0 && (
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
                生成的Flag - {result.data.model_used}
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
                生成的文本 - {result.data.model_used}
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

      case 'compare':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                模型比较结果
              </CardTitle>
              <CardDescription>
                总耗时: {result.data.total_duration_ms}ms | 比较模型: {result.data.models_compared}个
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(result.data.results).map(([modelName, modelResult]) => (
                <div key={modelName} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{modelName}</h4>
                    <div className="flex items-center gap-2">
                      {modelResult.status === 'success' ? (
                        <Badge variant="success" className="flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          成功
                        </Badge>
                      ) : (
                        <Badge variant="destructive" className="flex items-center gap-1">
                          <XCircle className="h-3 w-3" />
                          失败
                        </Badge>
                      )}
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {modelResult.duration_ms}ms
                      </Badge>
                    </div>
                  </div>
                  {modelResult.status === 'success' ? (
                    <div className="text-sm whitespace-pre-wrap bg-gray-50 p-3 rounded">
                      {typeof modelResult.result === 'string' 
                        ? modelResult.result 
                        : JSON.stringify(modelResult.result, null, 2)}
                    </div>
                  ) : (
                    <div className="text-sm text-red-600">
                      错误: {modelResult.error}
                    </div>
                  )}
                </div>
              ))}
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
          <span className="text-sm">默认模型: {defaultModel}</span>
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
              <CardTitle>可用模型</CardTitle>
              <CardDescription>当前可用的AI模型列表</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {models.map((model) => (
                  <div key={model} className="flex items-center justify-between p-2 border rounded">
                    <span className="text-sm font-mono">{model}</span>
                    {model === defaultModel && (
                      <Badge variant="outline">默认</Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {Object.keys(stats).length > 0 && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>使用统计</CardTitle>
                <CardDescription>您的AI模型使用情况</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(stats).map(([model, stat]) => (
                    <div key={model} className="text-sm">
                      <div className="font-medium">{model}</div>
                      <div className="text-gray-600">
                        调用: {stat.total_calls} | 成功: {stat.successful_calls}
                      </div>
                      <div className="text-gray-600">
                        平均耗时: {stat.avg_duration_ms}ms
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="lg:col-span-3">
          <Tabs defaultValue="challenge" className="space-y-4">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="challenge">生成题目</TabsTrigger>
              <TabsTrigger value="flag">生成Flag</TabsTrigger>
              <TabsTrigger value="text">生成文本</TabsTrigger>
              <TabsTrigger value="compare">模型比较</TabsTrigger>
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
                      <Label htmlFor="category">题目类型</Label>
                      <Select value={challengeForm.category} onValueChange={(value) => 
                        setChallengeForm({...challengeForm, category: value})
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
                    <Label htmlFor="model">AI模型（可选）</Label>
                    <Select value={challengeForm.model} onValueChange={(value) => 
                      setChallengeForm({...challengeForm, model: value})
                    }>
                      <SelectTrigger>
                        <SelectValue placeholder="使用默认模型" />
                      </SelectTrigger>
                      <SelectContent>
                        {models.map((model) => (
                          <SelectItem key={model} value={model}>{model}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="requirements">题目要求</Label>
                    <Textarea
                      id="requirements"
                      placeholder="请描述您想要生成的题目要求..."
                      value={challengeForm.requirements}
                      onChange={(e) => setChallengeForm({...challengeForm, requirements: e.target.value})}
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
                      <Label htmlFor="flag_model">AI模型（可选）</Label>
                      <Select value={flagForm.model} onValueChange={(value) => 
                        setFlagForm({...flagForm, model: value})
                      }>
                        <SelectTrigger>
                          <SelectValue placeholder="使用默认模型" />
                        </SelectTrigger>
                        <SelectContent>
                          {models.map((model) => (
                            <SelectItem key={model} value={model}>{model}</SelectItem>
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
                  <CardDescription>使用AI模型生成任意文本内容</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="text_model">AI模型（可选）</Label>
                    <Select value={textForm.model} onValueChange={(value) => 
                      setTextForm({...textForm, model: value})
                    }>
                      <SelectTrigger>
                        <SelectValue placeholder="使用默认模型" />
                      </SelectTrigger>
                      <SelectContent>
                        {models.map((model) => (
                          <SelectItem key={model} value={model}>{model}</SelectItem>
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

            <TabsContent value="compare">
              <Card>
                <CardHeader>
                  <CardTitle>模型比较</CardTitle>
                  <CardDescription>比较多个AI模型的输出结果</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="task_type">任务类型</Label>
                    <Select value={compareForm.task_type} onValueChange={(value) => 
                      setCompareForm({...compareForm, task_type: value})
                    }>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="text">文本生成</SelectItem>
                        <SelectItem value="challenge">题目生成</SelectItem>
                        <SelectItem value="flag">Flag生成</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {compareForm.task_type === 'challenge' && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>题目类型</Label>
                        <Select value={compareForm.category} onValueChange={(value) => 
                          setCompareForm({...compareForm, category: value})
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
                        <Label>难度</Label>
                        <Select value={compareForm.difficulty} onValueChange={(value) => 
                          setCompareForm({...compareForm, difficulty: value})
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
                  )}
                  
                  {compareForm.task_type === 'flag' && (
                    <div>
                      <Label>题目类型</Label>
                      <Select value={compareForm.challenge_type} onValueChange={(value) => 
                        setCompareForm({...compareForm, challenge_type: value})
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
                  )}
                  
                  <div>
                    <Label>选择模型</Label>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {models.map((model) => (
                        <label key={model} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={compareForm.models.includes(model)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setCompareForm({
                                  ...compareForm,
                                  models: [...compareForm.models, model]
                                });
                              } else {
                                setCompareForm({
                                  ...compareForm,
                                  models: compareForm.models.filter(m => m !== model)
                                });
                              }
                            }}
                          />
                          <span className="text-sm">{model}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="compare_prompt">提示词</Label>
                    <Textarea
                      id="compare_prompt"
                      placeholder="请输入提示词..."
                      value={compareForm.prompt}
                      onChange={(e) => setCompareForm({...compareForm, prompt: e.target.value})}
                      rows={4}
                    />
                  </div>
                  <Button onClick={handleCompareModels} disabled={loading} className="w-full">
                    {loading ? '比较中...' : '开始比较'}
                  </Button>
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



            <TabsContent value="config">
              <Card>
                <CardHeader>
                  <CardTitle>AI模型配置管理</CardTitle>
                  <CardDescription>管理AI模型的API密钥和基础URL</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                    <AlertDescription>
                      请在后端服务器的环境变量中配置API密钥和基础URL。此页面仅用于查看当前已加载的模型配置状态。
                    </AlertDescription>
                  </Alert>
                  <div className="space-y-4">
                    {models.length > 0 ? (
                      models.map((modelName) => {
                        const modelConfig = stats[modelName] || {};
                        return (
                          <div key={modelName} className="border rounded p-4">
                            <h4 className="font-semibold text-lg mb-2">{modelName}</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <Label>API Key</Label>
                                <Input type="text" value={modelConfig.api_key_configured ? "已配置" : "未配置"} readOnly />
                              </div>
                              <div>
                                <Label>API Base URL</Label>
                                <Input type="text" value={modelConfig.api_base_configured ? "已配置" : "未配置"} readOnly />
                              </div>
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <p className="text-gray-500">没有可用的AI模型配置。</p>
                    )}
                  </div>
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

