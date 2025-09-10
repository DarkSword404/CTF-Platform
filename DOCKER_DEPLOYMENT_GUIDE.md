# CTF靶场平台 Docker 部署指南

本文档详细介绍了如何使用Docker和Docker Compose部署CTF靶场平台。

## 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [环境配置](#环境配置)
4. [部署模式](#部署模式)
5. [服务架构](#服务架构)
6. [数据持久化](#数据持久化)
7. [网络配置](#网络配置)
8. [安全配置](#安全配置)
9. [监控和日志](#监控和日志)
10. [故障排除](#故障排除)
11. [维护和更新](#维护和更新)

## 系统要求

### 最低配置
- CPU: 2核心
- 内存: 4GB RAM
- 存储: 20GB 可用空间
- 操作系统: Linux (Ubuntu 20.04+, CentOS 8+, Debian 10+)

### 推荐配置
- CPU: 4核心或更多
- 内存: 8GB RAM 或更多
- 存储: 50GB SSD 存储
- 操作系统: Ubuntu 22.04 LTS

### 软件依赖
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Make (可选，用于便捷管理)

## 快速开始

### 1. 安装Docker和Docker Compose

#### Ubuntu/Debian
```bash
# 更新包索引
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# 安装必要的包
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
```

### 2. 克隆项目
```bash
git clone <repository-url>
cd ctf-platform
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
vim .env
```

### 4. 启动服务

#### 开发环境
```bash
# 使用Makefile（推荐）
make dev

# 或直接使用docker-compose
docker-compose -f docker-compose.dev.yml up -d
```

#### 生产环境
```bash
# 使用Makefile（推荐）
make prod

# 或直接使用docker-compose
docker-compose up -d
```

## 环境配置

### 环境变量说明

#### 基础配置
```bash
# 应用密钥（生产环境必须修改）
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# 数据库配置
POSTGRES_DB=ctf_platform
POSTGRES_USER=ctf_user
POSTGRES_PASSWORD=ctf_password
MONGODB_URI=mongodb://ctf_admin:ctf_mongo_password@mongodb:27017/ctf_challenges?authSource=admin
REDIS_URL=redis://:ctf_redis_password@redis:6379/0
```

#### AI模型配置
```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1

# DeepSeek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 百度文心一言
ERNIE_BOT_AK=your-ernie-bot-api-key
ERNIE_BOT_SK=your-ernie-bot-secret-key

# 阿里云通义千问
TONGYI_QIANWEN_API_KEY=your-tongyi-qianwen-api-key

# 智谱AI
ZHIPU_AI_API_KEY=your-zhipu-ai-api-key
```

#### 网络配置
```bash
# 端口配置
BACKEND_PORT=5000
FRONTEND_PORT=80
NGINX_HTTP_PORT=8080
NGINX_HTTPS_PORT=8443

# 域名配置
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ORIGINS=http://localhost:3000,http://localhost:80,https://your-domain.com
```

### 生成安全密钥
```bash
# 生成SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 部署模式

### 开发模式

开发模式提供了完整的开发环境，包括：
- 热重载功能
- 调试工具
- 数据库管理界面
- 详细的日志输出

```bash
# 启动开发环境
make dev

# 查看服务状态
make status

# 查看日志
make dev-logs
```

访问地址：
- 前端应用: http://localhost:3000
- 后端API: http://localhost:5000
- PgAdmin: http://localhost:8080 (admin@ctf-platform.com / admin123)
- Mongo Express: http://localhost:8081 (admin / admin123)
- Redis Commander: http://localhost:8082

### 生产模式

生产模式针对性能和安全进行了优化：
- Nginx反向代理
- 静态文件优化
- 安全头配置
- 日志管理
- 健康检查

```bash
# 启动生产环境
make prod

# 查看服务状态
make status

# 查看日志
make prod-logs
```

访问地址：
- 应用入口: http://localhost
- Nginx管理: http://localhost:8080

### 混合模式

可以根据需要启用特定的服务配置文件：

```bash
# 启用Ollama本地AI服务
docker-compose --profile ollama up -d

# 启用生产级Nginx
docker-compose --profile production up -d
```

## 服务架构

### 服务组件

#### 核心服务
1. **frontend** - React前端应用
   - 基于Nginx提供静态文件服务
   - 支持SPA路由
   - 集成API代理

2. **backend** - Flask后端API
   - RESTful API服务
   - JWT认证
   - AI模型集成
   - Docker容器管理

3. **postgres** - PostgreSQL数据库
   - 用户数据存储
   - 题目基础信息
   - 系统配置

4. **mongodb** - MongoDB数据库
   - 题目详细内容
   - AI生成内容
   - 文件存储元数据

5. **redis** - Redis缓存
   - 会话存储
   - 缓存层
   - 任务队列

#### 可选服务
1. **ollama** - 本地AI模型服务
2. **nginx** - 生产环境反向代理
3. **pgadmin** - PostgreSQL管理界面
4. **mongo-express** - MongoDB管理界面
5. **redis-commander** - Redis管理界面

### 服务依赖关系

```mermaid
graph TD
    A[Nginx] --> B[Frontend]
    A --> C[Backend]
    C --> D[PostgreSQL]
    C --> E[MongoDB]
    C --> F[Redis]
    C --> G[Ollama]
    C --> H[Docker Engine]
```

## 数据持久化

### 数据卷配置

系统使用Docker数据卷来持久化重要数据：

```yaml
volumes:
  postgres_data:      # PostgreSQL数据
  mongodb_data:       # MongoDB数据
  redis_data:         # Redis数据
  ollama_data:        # Ollama模型数据
  challenge_files:    # 题目文件
  logs:              # 应用日志
```

### 数据备份

#### 自动备份
```bash
# 备份所有数据库
make backup

# 备份特定数据库
make backup-postgres
make backup-mongodb
```

#### 手动备份
```bash
# PostgreSQL备份
docker-compose exec postgres pg_dump -U ctf_user ctf_platform > backup.sql

# MongoDB备份
docker-compose exec mongodb mongodump --uri="mongodb://ctf_admin:ctf_mongo_password@localhost:27017/ctf_challenges?authSource=admin" --out=/backup

# Redis备份
docker-compose exec redis redis-cli BGSAVE
```

### 数据恢复

```bash
# 恢复PostgreSQL
make restore-postgres FILE=backup.sql

# 恢复MongoDB
make restore-mongodb DIR=backup_dir

# 恢复Redis
docker cp backup.rdb ctf-redis:/data/dump.rdb
docker-compose restart redis
```

## 网络配置

### 网络架构

系统使用自定义Docker网络来隔离服务：

```yaml
networks:
  ctf-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 端口映射

#### 开发环境端口
- 3000: 前端开发服务器
- 5000: 后端API服务
- 5432: PostgreSQL数据库
- 27017: MongoDB数据库
- 6379: Redis缓存
- 8080: PgAdmin管理界面
- 8081: Mongo Express管理界面
- 8082: Redis Commander管理界面
- 11434: Ollama AI服务

#### 生产环境端口
- 80: 前端应用
- 8080: Nginx管理端口
- 8443: HTTPS端口（需要SSL证书）

### 防火墙配置

#### Ubuntu/Debian (UFW)
```bash
# 启用防火墙
sudo ufw enable

# 允许SSH
sudo ufw allow ssh

# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许特定端口（如果需要外部访问）
sudo ufw allow 5000/tcp  # 后端API
sudo ufw allow 8080/tcp  # 管理界面
```

#### CentOS/RHEL (firewalld)
```bash
# 启用防火墙
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 允许HTTP和HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# 允许特定端口
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp

# 重新加载配置
sudo firewall-cmd --reload
```

## 安全配置

### SSL/TLS配置

#### 生成自签名证书（开发环境）
```bash
make ssl-cert
```

#### 使用Let's Encrypt证书（生产环境）
```bash
# 安装Certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

### 安全最佳实践

1. **更改默认密码**
   ```bash
   # 生成强密码
   openssl rand -base64 32
   ```

2. **限制网络访问**
   - 仅暴露必要的端口
   - 使用防火墙规则
   - 配置反向代理

3. **启用HTTPS**
   - 使用有效的SSL证书
   - 配置HSTS头
   - 重定向HTTP到HTTPS

4. **定期更新**
   ```bash
   # 更新Docker镜像
   docker-compose pull
   docker-compose up -d
   
   # 更新系统包
   sudo apt update && sudo apt upgrade
   ```

5. **监控和日志**
   - 启用访问日志
   - 监控异常活动
   - 定期检查安全漏洞

### 环境隔离

#### 开发环境隔离
```bash
# 使用不同的网络
docker network create ctf-dev-network

# 使用不同的数据卷
docker volume create ctf-dev-postgres
docker volume create ctf-dev-mongodb
```

#### 生产环境加固
```bash
# 限制容器权限
docker-compose exec backend adduser --disabled-password --gecos "" ctfuser
docker-compose exec backend su - ctfuser

# 使用只读文件系统
# 在docker-compose.yml中添加：
# read_only: true
# tmpfs:
#   - /tmp
#   - /var/tmp
```

## 监控和日志

### 日志管理

#### 查看日志
```bash
# 查看所有服务日志
make logs

# 查看特定服务日志
make logs-backend
make logs-frontend
make logs-db

# 实时跟踪日志
docker-compose logs -f backend
```

#### 日志配置

日志文件位置：
- 应用日志: `./logs/ctf-platform.log`
- Nginx访问日志: `/var/log/nginx/ctf-access.log`
- Nginx错误日志: `/var/log/nginx/ctf-error.log`

#### 日志轮转配置
```bash
# 创建logrotate配置
sudo tee /etc/logrotate.d/ctf-platform << EOF
/path/to/ctf-platform/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart nginx
    endscript
}
EOF
```

### 性能监控

#### 资源使用监控
```bash
# 查看容器资源使用情况
make monitor

# 查看详细统计信息
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### 健康检查
```bash
# 检查服务健康状态
make health

# 查看健康检查详情
docker-compose ps
```

#### 性能测试
```bash
# 运行性能测试
make perf-test

# 自定义性能测试
docker run --rm -it --network=ctf-platform_ctf-network \
    williamyeh/wrk -t12 -c400 -d30s --latency http://frontend/
```

### 监控工具集成

#### Prometheus + Grafana
```yaml
# 在docker-compose.yml中添加
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### ELK Stack
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false

logstash:
  image: docker.elastic.co/logstash/logstash:8.5.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.5.0
  ports:
    - "5601:5601"
```

## 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs <service-name>

# 检查配置文件
docker-compose config
```

#### 2. 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose ps postgres mongodb redis

# 测试数据库连接
docker-compose exec backend python -c "
from src.database import test_connection
test_connection()
"

# 检查网络连接
docker-compose exec backend ping postgres
```

#### 3. AI服务不可用
```bash
# 检查环境变量
docker-compose exec backend env | grep API_KEY

# 测试API连接
docker-compose exec backend python -c "
from src.services.ai_service import MultiAIService
service = MultiAIService()
print(service.get_available_models())
"
```

#### 4. 前端无法访问后端
```bash
# 检查Nginx配置
docker-compose exec frontend nginx -t

# 检查代理配置
curl -I http://localhost/api/health

# 检查CORS配置
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:5000/api/health
```

### 调试技巧

#### 进入容器调试
```bash
# 进入后端容器
make shell-backend

# 进入前端容器
make shell-frontend

# 进入数据库容器
make shell-db
```

#### 网络调试
```bash
# 检查网络连接
docker network ls
docker network inspect ctf-platform_ctf-network

# 测试服务间连接
docker-compose exec backend ping frontend
docker-compose exec frontend ping backend
```

#### 性能调试
```bash
# 分析容器性能
docker stats

# 检查磁盘使用
docker system df

# 清理未使用资源
make clean
```

### 错误代码参考

| 错误代码 | 描述 | 解决方案 |
|---------|------|----------|
| 500 | 服务器内部错误 | 检查后端日志和数据库连接 |
| 502 | 网关错误 | 检查Nginx配置和后端服务状态 |
| 503 | 服务不可用 | 检查服务是否正常启动 |
| 504 | 网关超时 | 增加超时时间或优化服务性能 |

## 维护和更新

### 定期维护任务

#### 每日任务
```bash
# 检查服务状态
make health

# 查看资源使用情况
make monitor

# 检查日志错误
docker-compose logs --tail=100 | grep -i error
```

#### 每周任务
```bash
# 备份数据
make backup

# 清理未使用的Docker资源
make clean

# 更新Docker镜像
docker-compose pull
```

#### 每月任务
```bash
# 系统更新
sudo apt update && sudo apt upgrade

# 安全扫描
make security-scan

# 性能测试
make perf-test
```

### 版本更新

#### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
make prod-build

# 验证更新
make health
```

#### 数据库迁移
```bash
# 备份数据
make backup

# 运行迁移
make db-migrate

# 验证数据完整性
make test
```

### 扩容和优化

#### 水平扩容
```bash
# 扩展后端服务
docker-compose up -d --scale backend=3

# 配置负载均衡
# 修改nginx配置添加upstream服务器
```

#### 垂直扩容
```yaml
# 在docker-compose.yml中增加资源限制
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### 性能优化
```bash
# 启用Redis缓存
# 配置数据库连接池
# 优化Nginx配置
# 启用CDN加速
```

### 灾难恢复

#### 备份策略
```bash
# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据库
make backup
mv backups/* $BACKUP_DIR/

# 备份配置文件
cp .env docker-compose.yml $BACKUP_DIR/

# 上传到远程存储
rsync -av $BACKUP_DIR/ user@backup-server:/backups/
```

#### 恢复流程
```bash
# 1. 停止所有服务
make prod-down

# 2. 恢复数据
make restore-postgres FILE=backup.sql
make restore-mongodb DIR=backup_dir

# 3. 恢复配置
cp backup/.env .env

# 4. 重新启动服务
make prod

# 5. 验证恢复
make health
make test
```

## 总结

本指南涵盖了CTF靶场平台Docker部署的各个方面，从基础安装到高级配置和维护。遵循本指南可以确保平台的稳定运行和安全性。

如果遇到问题，请参考故障排除部分或查看项目文档。建议定期更新系统和应用程序以保持最佳性能和安全性。

