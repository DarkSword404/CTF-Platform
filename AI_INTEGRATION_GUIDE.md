# CTF平台多AI模型集成指南

## 概述

CTF靶场平台现已支持多种AI模型集成，包括OpenAI、Anthropic Claude、Google Gemini、本地Ollama模型等。本指南将帮助您配置和使用这些AI服务。

## 支持的AI服务提供商

### 1. OpenAI (默认)
- **模型**: GPT-4, GPT-3.5-turbo
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要OpenAI API密钥

### 2. Anthropic Claude
- **模型**: Claude-3-Opus, Claude-3-Sonnet
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要Anthropic API密钥

### 3. Google Gemini
- **模型**: Gemini-Pro
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要Google API密钥

### 4. Ollama (本地模型)
- **模型**: Llama2, CodeLlama, 其他开源模型
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要本地Ollama服务

### 5. DeepSeek
- **模型**: deepseek-coder, deepseek-chat
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要DeepSeek API密钥

### 6. 百度文心一言 (ERNIE Bot)
- **模型**: ERNIE-Bot-4, ERNIE-Bot-turbo
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要百度智能云API Key (AK) 和 Secret Key (SK)

### 7. 阿里云通义千问 (Tongyi Qianwen)
- **模型**: qwen-turbo, qwen-plus
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要阿里云API Key

### 8. 智谱AI (Zhipu AI)
- **模型**: glm-4, glm-3-turbo
- **功能**: 题目生成、Flag生成、文本生成
- **配置**: 需要智谱AI API Key

## 环境配置

### 1. 环境变量设置

创建 `.env` 文件或设置系统环境变量：

```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic配置
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google配置
GOOGLE_API_KEY=your_google_api_key

# Ollama配置
OLLAMA_API_BASE=http://localhost:11434

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# ERNIE Bot配置
ERNIE_BOT_AK=your_ernie_bot_api_key
ERNIE_BOT_SK=your_ernie_bot_secret_key

# Tongyi Qianwen配置
TONGYI_QIANWEN_API_KEY=your_tongyi_qianwen_api_key

# Zhipu AI配置
ZHIPU_AI_API_KEY=your_zhipu_ai_api_key
```

### 2. 安装依赖

根据需要安装相应的Python包：

```bash
# 基础依赖（已包含）
pip install openai

# Anthropic Claude
pip install anthropic

# Google Gemini
pip install google-generativeai

# 本地模型支持
pip install transformers torch

# 百度文心一言
pip install qianfan

# 阿里云通义千问
pip install dashscope

# 智谱AI
pip install zhipuai
```

### 3. Ollama本地部署

如果使用本地模型，需要安装和配置Ollama：

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 下载模型
ollama pull llama2
ollama pull codellama
```

## API接口说明

### 1. 获取可用模型
```http
GET /api/ai-multi/models
Authorization: Bearer <jwt_token>
```

响应：
```json
{
  "models": ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "gemini-pro", "llama2"],
  "default_model": "gpt-4",
  "total_count": 5
}
```

### 2. 生成题目
```http
POST /api/ai-multi/generate-challenge
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "category": "Web",
  "difficulty": "Easy",
  "requirements": "创建一个SQL注入题目",
  "model": "gpt-4"
}
```

### 3. 生成Flag
```http
POST /api/ai-multi/generate-flag
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "challenge_description": "这是一个SQL注入题目",
  "challenge_type": "Web",
  "model": "claude-3-opus"
}
```

### 4. 生成文本
```http
POST /api/ai-multi/generate-text
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "prompt": "解释什么是SQL注入",
  "model": "gemini-pro",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

### 5. 模型比较
```http
POST /api/ai-multi/compare-models
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "prompt": "创建一个简单的Web题目",
  "models": ["gpt-4", "claude-3-opus", "gemini-pro"],
  "task_type": "challenge",
  "category": "Web",
  "difficulty": "Easy"
}
```

### 6. 获取使用统计
```http
GET /api/ai-multi/model-stats
Authorization: Bearer <jwt_token>
```

## 前端集成

### 1. AI模型管理页面

访问 `/ai-models` 页面可以：
- 查看可用的AI模型
- 生成题目、Flag和文本
- 比较不同模型的输出
- 查看使用统计

### 2. 在题目创建中使用

在题目创建页面，用户可以：
- 选择不同的AI模型
- 使用AI辅助生成题目内容
- 比较多个模型的输出结果

## 配置示例

### 1. 仅使用OpenAI
```bash
OPENAI_API_KEY=sk-xxx
```

### 2. 使用多个云服务
```bash
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=AIzaSyxxx
```

### 3. 混合云服务和本地模型
```bash
OPENAI_API_KEY=sk-xxx
OLLAMA_API_BASE=http://localhost:11434
```

### 4. 仅使用国内AI服务
```bash
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
ERNIE_BOT_AK=your_ernie_bot_api_key
ERNIE_BOT_SK=your_ernie_bot_secret_key
TONGYI_QIANWEN_API_KEY=your_tongyi_qianwen_api_key
ZHIPU_AI_API_KEY=your_zhipu_ai_api_key
```

## 性能优化建议

### 1. 模型选择策略
- **快速响应**: 使用GPT-3.5-turbo或本地模型
- **高质量输出**: 使用GPT-4或Claude-3-Opus
- **成本控制**: 使用本地Ollama模型

### 2. 缓存策略
- 对相似的请求进行缓存
- 设置合理的缓存过期时间
- 使用Redis进行分布式缓存

### 3. 并发控制
- 限制同时进行的AI调用数量
- 实现请求队列机制
- 设置超时时间

## 故障排除

### 1. 常见问题

**问题**: 模型不可用
**解决**: 检查API密钥和网络连接

**问题**: 响应时间过长
**解决**: 调整max_tokens参数或切换模型

**问题**: Ollama连接失败
**解决**: 确保Ollama服务正在运行

### 2. 日志分析

查看AI调用日志：
```http
GET /api/ai-multi/model-stats
```

### 3. 调试模式

在开发环境中启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展开发

### 1. 添加新的AI提供商

1. 继承 `BaseAIProvider` 类
2. 实现必需的方法
3. 在 `MultiAIService` 中注册
4. 更新配置和文档

### 2. 自定义提示词模板

```python
class CustomPromptTemplate:
    def generate_challenge_prompt(self, category, difficulty, requirements):
        return f"创建{difficulty}难度的{category}题目: {requirements}"
```

### 3. 结果后处理

```python
def post_process_challenge(raw_output):
    # 解析和验证AI输出
    # 格式化结果
    # 添加默认值
    return processed_result
```

## 安全考虑

### 1. API密钥管理
- 使用环境变量存储密钥
- 定期轮换API密钥
- 限制API密钥权限

### 2. 输入验证
- 验证用户输入长度
- 过滤敏感内容
- 防止提示词注入

### 3. 输出过滤
- 检查生成内容的安全性
- 过滤不当内容
- 验证Flag格式

## 监控和分析

### 1. 使用指标
- API调用次数
- 响应时间
- 成功率
- 成本分析

### 2. 告警设置
- API配额超限
- 响应时间异常
- 错误率过高

### 3. 用户行为分析
- 模型偏好统计
- 功能使用频率
- 生成内容质量评估

## 更新日志

### v1.1.0 (2024-09-10)
- 添加多AI模型支持
- 实现模型比较功能
- 添加使用统计
- 优化前端界面

### v1.0.0 (2024-09-10)
- 基础OpenAI集成
- 题目和Flag生成
- 基本AI调用日志

## 贡献指南

欢迎贡献代码和建议：
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 更新文档

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

