# AI CTF Platform 部署指南

## 项目概述

AI CTF Platform 是一个基于人工智能的CTF（Capture The Flag）题目生成和管理平台。该平台结合了Vulfocus和CTFd的优势，并增加了AI自动生成题目的功能，支持Misc、Crypto和Web类型的题目生成。

## 核心功能

### 1. AI题目生成
- 支持多种AI模型（OpenAI GPT、DeepSeek、文心一言等）
- 自动生成Misc、Crypto、Web三类题目
- 智能生成题目描述、flag和附件
- 支持Docker容器化Web题目

### 2. 题目管理
- 完整的题目CRUD操作
- 题目分类和难度管理
- 附件上传和下载
- 容器化题目部署

### 3. 用户系统
- 用户注册、登录、权限管理
- 管理员后台
- 题目提交和评分

### 4. 容器管理
- Docker集成
- 动态容器启停
- 资源限制和安全隔离

## 技术架构

### 后端技术栈
- **框架**: Flask 3.1.1
- **数据库**: SQLite（可扩展为PostgreSQL/MySQL）
- **AI集成**: OpenAI API、多模型支持
- **容器化**: Docker API
- **认证**: Session-based认证

### 前端技术栈
- **框架**: 原生HTML/CSS/JavaScript
- **UI组件**: 自定义组件库
- **状态管理**: 原生JavaScript
- **网络请求**: Fetch API

### 项目结构
```
ai_ctf_platform/
├── src/
│   ├── main.py                 # 应用入口
│   ├── models/                 # 数据模型
│   │   ├── user.py            # 用户模型
│   │   └── challenge.py       # 题目模型
│   ├── routes/                 # 路由控制器
│   │   ├── auth.py            # 认证路由
│   │   ├── challenges.py      # 题目路由
│   │   ├── ai_challenges.py   # AI生成路由
│   │   ├── admin.py           # 管理员路由
│   │   └── user.py            # 用户路由
│   ├── services/               # 业务服务
│   │   ├── ai_generator.py    # AI生成服务
│   │   └── docker_manager.py  # Docker管理
│   └── static/                 # 静态文件
│       └── index.html         # 前端页面
├── venv/                       # 虚拟环境
├── requirements.txt            # 依赖列表
└── README.md                  # 项目说明
```

## 安装部署

### 环境要求
- Python 3.11+
- Docker（可选，用于Web题目）
- 4GB+ RAM
- 10GB+ 磁盘空间

### 本地开发部署

1. **克隆项目**
```bash
git clone <repository-url>
cd ai_ctf_platform
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"  # 可选
```

5. **启动应用**
```bash
cd src
python main.py
```

6. **访问应用**
打开浏览器访问 `http://localhost:5000`

### 生产环境部署

#### 使用Docker部署

1. **创建Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY . .

EXPOSE 5000

CMD ["python", "src/main.py"]
```

2. **构建镜像**
```bash
docker build -t ai-ctf-platform .
```

3. **运行容器**
```bash
docker run -d \
  --name ai-ctf-platform \
  -p 5000:5000 \
  -e OPENAI_API_KEY="your-api-key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ai-ctf-platform
```

#### 使用Nginx反向代理

1. **安装Nginx**
```bash
sudo apt update
sudo apt install nginx
```

2. **配置Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **启用配置**
```bash
sudo ln -s /etc/nginx/sites-available/ai-ctf-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 配置说明

### AI模型配置

平台支持多种AI模型，可在管理后台进行配置：

1. **OpenAI GPT系列**
   - API Key: 从OpenAI获取
   - Base URL: https://api.openai.com/v1
   - 模型: gpt-4, gpt-3.5-turbo等

2. **DeepSeek**
   - API Key: 从DeepSeek获取
   - Base URL: https://api.deepseek.com
   - 模型: deepseek-chat

3. **国产模型**
   - 文心一言、通义千问、智谱AI等
   - 需要相应的API Key和配置

### 数据库配置

默认使用SQLite，生产环境建议使用PostgreSQL：

```python
# 在main.py中修改数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/ai_ctf_platform'
```

### Docker配置

如果需要支持Web题目的容器化部署：

1. **安装Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **配置Docker权限**
```bash
sudo chmod 666 /var/run/docker.sock
```

## 使用指南

### 管理员操作

1. **首次登录**
   - 默认管理员账号需要在数据库中手动创建
   - 或通过注册后在数据库中修改is_admin字段

2. **AI模型配置**
   - 访问"AI模型配置"标签
   - 添加AI模型的API Key和配置
   - 测试模型连接状态

3. **题目管理**
   - 查看所有题目
   - 编辑、删除题目
   - 管理题目分类和难度

### 用户操作

1. **注册登录**
   - 用户可以自由注册账号
   - 登录后可以查看和解答题目

2. **AI生成题目**
   - 选择题目类型（Misc/Crypto/Web）
   - 选择难度级别
   - 输入主题关键词
   - 点击生成按钮

3. **解答题目**
   - 查看题目描述
   - 下载附件（如有）
   - 启动容器（Web题目）
   - 提交flag

## 安全考虑

### 1. API Key安全
- 使用环境变量存储API Key
- 定期轮换API Key
- 限制API调用频率

### 2. 容器安全
- 限制容器资源使用
- 使用非特权用户运行容器
- 定期清理过期容器

### 3. 用户权限
- 实现严格的权限控制
- 防止SQL注入和XSS攻击
- 使用HTTPS传输

### 4. 数据安全
- 定期备份数据库
- 加密敏感信息
- 实现审计日志

## 监控和维护

### 1. 日志管理
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 性能监控
- 监控API响应时间
- 监控数据库查询性能
- 监控容器资源使用

### 3. 定期维护
- 清理过期容器
- 清理临时文件
- 更新依赖包

## 故障排除

### 常见问题

1. **Docker连接失败**
   - 检查Docker服务状态
   - 检查权限配置
   - 查看错误日志

2. **AI模型调用失败**
   - 检查API Key配置
   - 检查网络连接
   - 查看API限制

3. **数据库连接问题**
   - 检查数据库配置
   - 检查文件权限
   - 查看连接字符串

### 调试模式

开发环境下启用调试模式：
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

生产环境下关闭调试模式：
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## 扩展开发

### 添加新的AI模型

1. **修改ai_generator.py**
```python
def get_ai_client(self, ai_model: AIModel):
    if ai_model.provider.lower() == 'new_provider':
        return NewProviderClient(
            api_key=ai_model.api_key,
            base_url=ai_model.api_base
        )
```

2. **更新前端配置**
在AI模型配置页面添加新的提供商选项

### 添加新的题目类型

1. **扩展生成逻辑**
```python
def generate_new_type_challenge(self, theme, difficulty, ai_model):
    # 实现新类型题目的生成逻辑
    pass
```

2. **更新前端界面**
在题目类型选择中添加新选项

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues]
- 邮箱: [your-email@example.com]

---

*最后更新: 2025年9月10日*

