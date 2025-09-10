# AI CTF Platform

🤖 基于人工智能的CTF题目生成和管理平台

## 项目简介

AI CTF Platform 是一个创新的CTF（Capture The Flag）平台，结合了人工智能技术来自动生成高质量的CTF题目。该平台参考了Vulfocus和CTFd的优秀设计，并在此基础上增加了AI驱动的题目生成功能，特别针对Web题目的容器支持进行了优化。

## ✨ 核心特性

### 🎯 AI智能生成
- **多模型支持**: 集成OpenAI GPT、DeepSeek、文心一言、通义千问等主流AI模型
- **三大题型**: 支持Misc、Crypto、Web类型题目的智能生成
- **自动化流程**: 从题目描述到flag生成，再到附件创建的全自动化
- **容器化部署**: Web题目自动生成Docker容器，支持动态部署

### 🏗️ 平台管理
- **用户系统**: 完整的用户注册、登录、权限管理
- **题目管理**: 题目的增删改查、分类管理、难度设置
- **容器管理**: Docker容器的启停、资源限制、安全隔离
- **管理后台**: 丰富的管理功能和统计信息

### 🔧 技术优势
- **模块化设计**: 清晰的代码结构，易于扩展和维护
- **API优先**: RESTful API设计，支持前后端分离
- **安全可靠**: 多层安全防护，容器隔离，权限控制
- **高性能**: 优化的数据库查询，异步处理，缓存机制

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Docker（可选，用于Web题目）
- 4GB+ RAM
- 10GB+ 磁盘空间

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/ai-ctf-platform.git
cd ai-ctf-platform
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

5. **启动应用**
```bash
cd src
python main.py
```

6. **访问平台**
打开浏览器访问 `http://localhost:5000`

## 📖 使用指南

### AI题目生成

1. **配置AI模型**
   - 进入"AI模型配置"页面
   - 添加您的API Key和模型配置
   - 测试连接状态

2. **生成题目**
   - 选择题目类型（Misc/Crypto/Web）
   - 设置难度级别（简单/中等/困难）
   - 输入主题关键词
   - 点击"生成题目"按钮

3. **管理题目**
   - 查看生成的题目列表
   - 编辑题目内容
   - 管理附件和容器

### 用户操作

1. **注册登录**
   - 新用户可以自由注册
   - 登录后可以查看和解答题目

2. **解答题目**
   - 浏览题目列表
   - 查看题目描述和提示
   - 下载附件或启动容器
   - 提交flag获得分数

## 🏗️ 架构设计

### 技术栈
- **后端**: Flask + SQLite/PostgreSQL
- **前端**: HTML/CSS/JavaScript
- **AI集成**: OpenAI API + 多模型支持
- **容器化**: Docker + Docker API
- **部署**: Nginx + Gunicorn

### 项目结构
```
ai_ctf_platform/
├── src/
│   ├── main.py                 # 应用入口
│   ├── models/                 # 数据模型
│   ├── routes/                 # 路由控制器
│   ├── services/               # 业务服务
│   └── static/                 # 静态文件
├── venv/                       # 虚拟环境
├── requirements.txt            # 依赖列表
├── deployment_guide.md         # 部署指南
└── README.md                  # 项目说明
```

## 🔧 配置说明

### AI模型配置

支持的AI模型提供商：

| 提供商 | 模型 | API Base |
|--------|------|----------|
| OpenAI | GPT-4, GPT-3.5-turbo | https://api.openai.com/v1 |
| DeepSeek | deepseek-chat | https://api.deepseek.com |
| 文心一言 | ERNIE-Bot | https://aip.baidubce.com |
| 通义千问 | qwen-turbo | https://dashscope.aliyuncs.com |

### 数据库配置

默认使用SQLite，生产环境建议PostgreSQL：

```python
# 生产环境配置
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/ai_ctf_platform'
```

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t ai-ctf-platform .
```

### 运行容器
```bash
docker run -d \
  --name ai-ctf-platform \
  -p 5000:5000 \
  -e OPENAI_API_KEY="your-api-key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ai-ctf-platform
```

## 🔒 安全特性

- **权限控制**: 基于角色的访问控制
- **容器隔离**: Docker容器安全隔离
- **API安全**: API Key加密存储
- **输入验证**: 严格的输入验证和过滤
- **审计日志**: 完整的操作日志记录

## 📊 功能特色

### 与现有平台对比

| 特性 | AI CTF Platform | CTFd | Vulfocus |
|------|----------------|------|----------|
| AI题目生成 | ✅ | ❌ | ❌ |
| Web容器支持 | ✅ | 部分 | ✅ |
| 多AI模型 | ✅ | ❌ | ❌ |
| 自动化部署 | ✅ | ❌ | ✅ |
| 用户管理 | ✅ | ✅ | ✅ |
| 题目管理 | ✅ | ✅ | ✅ |

### 创新亮点

1. **智能题目生成**: 首个集成多AI模型的CTF平台
2. **容器优化**: 针对Web题目的容器支持进行了专门优化
3. **模块化设计**: 易于扩展和定制的架构设计
4. **国产化支持**: 支持国内主流AI模型，适合国内用户

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 开发指南

- 遵循PEP 8代码规范
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过

## 📝 更新日志

### v1.0.0 (2025-09-10)
- 🎉 首次发布
- ✨ AI题目生成功能
- 🏗️ 基础平台架构
- 🐳 Docker容器支持
- 👥 用户管理系统

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Vulfocus](https://github.com/fofapro/vulfocus) - 优秀的漏洞靶场平台
- [CTFd](https://github.com/CTFd/CTFd) - 成熟的CTF平台解决方案
- [OpenAI](https://openai.com/) - 强大的AI模型支持

## 📞 联系我们

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/ai-ctf-platform/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/your-username/ai-ctf-platform/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

![GitHub stars](https://img.shields.io/github/stars/your-username/ai-ctf-platform?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/ai-ctf-platform?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/ai-ctf-platform)
![GitHub license](https://img.shields.io/github/license/your-username/ai-ctf-platform)

