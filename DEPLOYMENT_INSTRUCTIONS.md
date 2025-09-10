# CTF平台部署说明

## 快速部署指南

### 1. 环境准备

确保您的服务器已安装以下软件：
- Docker 20.0+
- Docker Compose 2.0+
- Git

### 2. 克隆项目

```bash
git clone https://github.com/DarkSword404/CTF-Platform.git
cd CTF-Platform
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env
```

**重要配置项：**

1. **数据库密码**：修改默认的数据库密码
2. **Flask密钥**：生成强密码用于SESSION和JWT
3. **AI API密钥**：配置您需要使用的AI服务API密钥

### 4. 启动服务

```bash
# 生产环境部署
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 访问平台

- **前端界面**：http://your-server-ip
- **后端API**：http://your-server-ip:5000
- **健康检查**：http://your-server-ip:5000/api/health

### 6. 初始化管理员

1. 访问前端界面注册一个账户
2. 进入数据库手动设置管理员权限：

```sql
-- 连接到PostgreSQL数据库
docker-compose exec postgres psql -U ctf_user -d ctf_platform

-- 查找用户ID
SELECT id, username FROM users WHERE username = 'your_username';

-- 创建管理员角色（如果不存在）
INSERT INTO roles (name, description) VALUES ('admin', '管理员') ON CONFLICT (name) DO NOTHING;

-- 给用户分配管理员角色
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'your_username' AND r.name = 'admin';
```

### 7. 配置AI模型

1. 登录管理员账户
2. 访问"AI模型管理"页面
3. 点击"初始化默认提供商"
4. 根据需要启用和配置AI模型

## 开发环境部署

如果您需要进行开发，可以使用开发环境配置：

```bash
# 使用开发环境配置
docker-compose -f docker-compose.dev.yml up -d

# 前端开发服务器
cd frontend
npm install --legacy-peer-deps
npm run dev

# 后端开发服务器
cd backend
pip install -r requirements.txt
python src/main.py
```

## 故障排除

### 1. 数据库连接失败

检查数据库服务是否正常启动：
```bash
docker-compose logs postgres
```

### 2. 前端无法访问后端

检查网络配置和CORS设置：
```bash
docker-compose logs backend
```

### 3. AI服务调用失败

1. 检查API密钥是否正确配置
2. 检查网络连接
3. 查看后端日志：
```bash
docker-compose logs backend | grep -i ai
```

### 4. 容器启动失败

检查Docker和Docker Compose版本：
```bash
docker --version
docker-compose --version
```

## 性能优化

### 1. 数据库优化

- 定期备份数据库
- 监控数据库性能
- 根据需要调整连接池大小

### 2. 缓存配置

- Redis缓存已配置，可根据需要调整缓存策略
- 监控Redis内存使用情况

### 3. 负载均衡

对于高并发场景，建议：
- 使用Nginx进行负载均衡
- 部署多个后端实例
- 使用CDN加速静态资源

## 安全建议

1. **定期更新**：保持系统和依赖包的最新版本
2. **防火墙配置**：只开放必要的端口
3. **SSL证书**：在生产环境中启用HTTPS
4. **备份策略**：定期备份数据库和重要文件
5. **监控日志**：监控异常访问和错误日志

## 备份与恢复

### 数据库备份

```bash
# PostgreSQL备份
docker-compose exec postgres pg_dump -U ctf_user ctf_platform > backup.sql

# MongoDB备份
docker-compose exec mongodb mongodump --authenticationDatabase admin -u ctf_admin -p ctf_mongo_password --db ctf_challenges --out /backup
```

### 数据库恢复

```bash
# PostgreSQL恢复
docker-compose exec -T postgres psql -U ctf_user ctf_platform < backup.sql

# MongoDB恢复
docker-compose exec mongodb mongorestore --authenticationDatabase admin -u ctf_admin -p ctf_mongo_password --db ctf_challenges /backup/ctf_challenges
```

## 联系支持

如果您在部署过程中遇到问题，请：

1. 查看项目文档：[README.md](README.md)
2. 提交Issue：[GitHub Issues](https://github.com/DarkSword404/CTF-Platform/issues)
3. 查看部署指南：[DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)

