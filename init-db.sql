-- CTF平台数据库初始化脚本

-- 使用数据库
\c ctf_platform;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建用户角色表
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认角色
INSERT INTO roles (name, description) VALUES 
    ('user', '普通用户'),
    ('challenger', '出题人'),
    ('admin', '管理员')
ON CONFLICT (name) DO NOTHING;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id) DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    profile_data JSONB DEFAULT '{}'::jsonb
);

-- 创建题目分类表
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    icon VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认分类
INSERT INTO categories (name, description, icon, color) VALUES 
    ('Web', 'Web安全题目', 'globe', '#3B82F6'),
    ('Pwn', '二进制漏洞利用', 'terminal', '#EF4444'),
    ('Reverse', '逆向工程', 'search', '#8B5CF6'),
    ('Crypto', '密码学', 'lock', '#F59E0B'),
    ('Misc', '杂项题目', 'puzzle-piece', '#10B981')
ON CONFLICT (name) DO NOTHING;

-- 创建题目表
CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    flag VARCHAR(500) NOT NULL,
    points INTEGER DEFAULT 100,
    difficulty VARCHAR(20) DEFAULT 'Easy',
    category_id INTEGER REFERENCES categories(id),
    author_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_dynamic BOOLEAN DEFAULT FALSE,
    max_attempts INTEGER DEFAULT 0,
    hints JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    files JSONB DEFAULT '[]'::jsonb,
    docker_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建提交记录表
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES challenges(id),
    submitted_flag VARCHAR(500) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points_awarded INTEGER DEFAULT 0,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户解题记录表
CREATE TABLE IF NOT EXISTS user_solves (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES challenges(id),
    solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    points_earned INTEGER NOT NULL,
    UNIQUE(user_id, challenge_id)
);

-- 创建AI生成记录表
CREATE TABLE IF NOT EXISTS ai_generations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    model_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    generation_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认系统配置
INSERT INTO system_configs (key, value, description) VALUES 
    ('platform_name', '"CTF靶场平台"', '平台名称'),
    ('registration_enabled', 'true', '是否允许用户注册'),
    ('default_user_points', '0', '新用户默认积分'),
    ('max_submission_rate', '10', '每分钟最大提交次数'),
    ('ai_models_enabled', 'true', '是否启用AI模型功能')
ON CONFLICT (key) DO NOTHING;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_challenges_category ON challenges(category_id);
CREATE INDEX IF NOT EXISTS idx_challenges_author ON challenges(author_id);
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_challenge ON submissions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_user_solves_user ON user_solves(user_id);
CREATE INDEX IF NOT EXISTS idx_user_solves_challenge ON user_solves(challenge_id);
CREATE INDEX IF NOT EXISTS idx_ai_generations_user ON ai_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_generations_model ON ai_generations(model_name);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_challenges_updated_at BEFORE UPDATE ON challenges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建管理员用户（密码: admin123）
INSERT INTO users (username, email, password_hash, role_id) VALUES 
    ('admin', 'admin@ctf-platform.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5W', 3)
ON CONFLICT (username) DO NOTHING;

-- 授予权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ctf_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ctf_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO ctf_user;

