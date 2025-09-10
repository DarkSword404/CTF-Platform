# CTF靶场平台

一个基于AI自动创建题目的CTF平台，支持多种AI模型集成，提供完整的题目管理、用户管理和比赛功能。

## 功能特性

### 🤖 AI驱动的题目生成
- **多AI模型支持**：集成OpenAI GPT、DeepSeek、百度文心一言、阿里云通义千问、智谱AI、Google Gemini等多种AI模型
- **智能题目生成**：根据指定类型、难度和要求自动生成CTF题目
- **自动Flag生成**：基于题目描述智能生成相关的Flag
- **可视化管理**：管理员可通过Web界面配置和管理AI模型

### 🏆 完整的CTF平台功能
- **题目管理**：支持Web、Pwn、Reverse、Crypto、Misc等多种题目类型
- **用户系统**：完整的用户注册、登录、权限管理系统
- **角色管理**：支持普通用户、出题人、管理员三种角色
- **容器化部署**：支持Docker容器化部署，便于环境隔离

### 📊 数据统计与监控
- **AI使用统计**：详细的AI模型调用统计和性能监控
- **用户活动监控**：用户解题记录、活动统计
- **系统健康检查**：完整的系统状态监控

## 技术栈

### 后端
- **框架**：Flask (Python)
- **数据库**：PostgreSQL + MongoDB
- **认证**：JWT Token
- **容器**：Docker
- **AI集成**：OpenAI API

### 前端
- **框架**：React 18
- **构建工具**：Vite
- **样式**：Tailwind CSS
- **组件库**：shadcn/ui
- **图标**：Lucide React
- **路由**：React Router

## 项目结构

```
ctf-platform/
├── backend/                 # 后端服务
│   ├── src/
│   │   ├── main.py         # 应用入口
│   │   ├── models/         # 数据模型
│   │   └── routes/         # API路由
│   ├── requirements.txt    # Python依赖
│   └── venv/              # 虚拟环境
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── lib/           # 工具库
│   │   └── App.jsx        # 应用入口
│   ├── package.json       # Node.js依赖
│   └── vite.config.js     # Vite配置
└── design_document.md     # 设计文档
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- MongoDB 5.0+
- Docker (可选)

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py
```

后端服务将在 http://localhost:5000 启动

### 前端启动

```bash
cd frontend
pnpm install
pnpm run dev
```

前端应用将在 http://localhost:5173 启动

## API文档

### 认证接口
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息

### 题目接口
- `GET /challenges` - 获取题目列表
- `GET /challenges/{id}` - 获取题目详情
- `POST /challenges` - 创建题目
- `POST /challenges/{id}/submit-flag` - 提交Flag

### AI接口
- `POST /ai/generate-challenge` - AI生成题目
- `POST /ai/generate-flag` - AI生成Flag

### 管理接口
- `GET /admin/users` - 获取用户列表
- `GET /admin/statistics` - 获取统计信息

## 配置说明

### 环境变量
```bash
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/ctf_platform
MONGODB_URL=mongodb://localhost:27017/ctf_platform

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key
```

## 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t ctf-platform-backend ./backend
docker build -t ctf-platform-frontend ./frontend

# 运行容器
docker run -d -p 5000:5000 ctf-platform-backend
docker run -d -p 3000:3000 ctf-platform-frontend
```

### 生产环境
- 使用Nginx作为反向代理
- 配置HTTPS证书
- 设置数据库连接池
- 启用日志记录和监控

## 开发指南

### 代码规范
- 后端遵循PEP 8规范
- 前端使用ESLint和Prettier
- 提交信息遵循Conventional Commits

### 测试
```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
pnpm test
```

## 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至：admin@ctf-platform.com

## 更新日志

### v1.0.0 (2024-09-10)
- 初始版本发布
- 基础用户系统
- 题目管理功能
- AI辅助出题
- 后台管理界面

