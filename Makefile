ifndef COMPOSE_FILE
COMPOSE_FILE = docker-compose.yml
endif

.PHONY: dev prod prod-build up down logs status health clean backup backup-postgres backup-mongodb restore-postgres restore-mongodb shell-backend shell-frontend shell-db monitor security-scan perf-test ssl-cert

# 开发环境命令
dev:
	@echo "启动开发环境..."
	@$(shell which docker) compose -f docker-compose.dev.yml up -d
	@echo "开发环境已启动!"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:5000"
	@echo "PgAdmin: http://localhost:8080"
	@echo "Mongo Express: http://localhost:8081"
	@echo "Redis Commander: http://localhost:8082"

# 生产环境命令
prod:
	@echo "启动生产环境..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) up -d
	@echo "生产环境已启动!"
	@echo "应用入口: http://localhost"
	@echo "Nginx管理: http://localhost:8080"

# 生产环境构建并启动
prod-build:
	@echo "构建生产环境镜像并启动..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) build --no-cache
	@$(shell which docker) compose -f $(COMPOSE_FILE) up -d
	@echo "生产环境已构建并启动!"

# 启动所有服务
up:
	@echo "启动所有服务..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) up -d

# 停止所有服务
down:
	@echo "停止所有服务..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) down

# 查看所有服务日志
logs:
	@echo "查看所有服务日志..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) logs -f

# 查看特定服务日志
logs-%:
	@echo "查看 $* 服务日志..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) logs -f $*

# 查看服务状态
status:
	@echo "查看服务状态..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) ps

# 检查服务健康状态
health:
	@echo "检查服务健康状态..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) ps --filter health=healthy

# 清理未使用的Docker资源
clean:
	@echo "清理未使用的Docker资源..."
	@docker system prune -f --volumes
	@$(shell which docker) compose -f $(COMPOSE_FILE) down --volumes --rmi all

# 备份所有数据库
backup:
	@echo "备份所有数据库..."
	@mkdir -p backups
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec postgres pg_dump -U ctf_user ctf_platform > backups/postgres_backup_$(shell date +%Y%m%d%H%M%S).sql
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec mongodb mongodump --uri="mongodb://ctf_admin:ctf_mongo_password@localhost:27017/ctf_challenges?authSource=admin" --out=/backup
	@$(shell which docker) compose -f $(COMPOSE_FILE) cp ctf-mongodb:/backup backups/mongodb_backup_$(shell date +%Y%m%d%H%M%S)
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec redis redis-cli BGSAVE
	@$(shell which docker) compose -f $(COMPOSE_FILE) cp ctf-redis:/data/dump.rdb backups/redis_backup_$(shell date +%Y%m%d%H%M%S).rdb
	@echo "数据库备份完成，文件在 ./backups 目录"

# 备份PostgreSQL
backup-postgres:
	@echo "备份PostgreSQL数据库..."
	@mkdir -p backups
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec postgres pg_dump -U ctf_user ctf_platform > backups/postgres_backup_$(shell date +%Y%m%d%H%M%S).sql
	@echo "PostgreSQL备份完成"

# 备份MongoDB
backup-mongodb:
	@echo "备份MongoDB数据库..."
	@mkdir -p backups
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec mongodb mongodump --uri="mongodb://ctf_admin:ctf_mongo_password@localhost:27017/ctf_challenges?authSource=admin" --out=/backup
	@$(shell which docker) compose -f $(COMPOSE_FILE) cp ctf-mongodb:/backup backups/mongodb_backup_$(shell date +%Y%m%d%H%M%S)
	@echo "MongoDB备份完成"

# 恢复PostgreSQL
restore-postgres:
	@echo "恢复PostgreSQL数据库..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec postgres psql -U ctf_user ctf_platform < $(FILE)
	@echo "PostgreSQL恢复完成"

# 恢复MongoDB
restore-mongodb:
	@echo "恢复MongoDB数据库..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec mongodb mongorestore --uri="mongodb://ctf_admin:ctf_mongo_password@localhost:27017/ctf_challenges?authSource=admin" --drop /backup
	@$(shell which docker) compose -f $(COMPOSE_FILE) cp $(DIR) ctf-mongodb:/backup
	@echo "MongoDB恢复完成"

# 进入后端容器shell
shell-backend:
	@echo "进入后端容器shell..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec backend bash

# 进入前端容器shell
shell-frontend:
	@echo "进入前端容器shell..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec frontend sh

# 进入数据库容器shell
shell-db:
	@echo "进入数据库容器shell..."
	@$(shell which docker) compose -f $(COMPOSE_FILE) exec postgres bash

# 监控容器资源使用
monitor:
	@echo "监控容器资源使用..."
	@docker stats

# 运行安全扫描 (示例)
security-scan:
	@echo "运行安全扫描..."
	@echo "请安装并使用Trivy, Clair等工具进行镜像安全扫描"
	@# docker scan ctf-platform-backend

# 运行性能测试 (示例)
perf-test:
	@echo "运行性能测试..."
	@echo "请安装并使用Locust, JMeter等工具进行性能测试"
	@# docker run --rm -it --network=ctf-network williamyeh/wrk -t12 -c400 -d30s http://frontend/

# 生成自签名SSL证书 (开发环境使用)
ssl-cert:
	@echo "生成自签名SSL证书..."
	@mkdir -p ssl
	@openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem -subj "/CN=localhost"
	@echo "自签名证书已生成到 ./ssl/key.pem 和 ./ssl/cert.pem"


