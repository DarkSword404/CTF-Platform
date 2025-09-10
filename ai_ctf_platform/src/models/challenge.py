from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Challenge(db.Model):
    """挑战题目模型"""
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # misc, crypto, web
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    flag = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=100)
    
    # AI生成相关字段
    is_ai_generated = db.Column(db.Boolean, default=False)
    ai_model_used = db.Column(db.String(100))
    generation_params = db.Column(db.Text)  # JSON格式存储生成参数
    
    # 文件和容器相关
    files = db.Column(db.Text)  # JSON格式存储文件路径列表
    docker_image = db.Column(db.String(200))
    docker_config = db.Column(db.Text)  # JSON格式存储Docker配置
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'is_ai_generated': self.is_ai_generated,
            'ai_model_used': self.ai_model_used,
            'generation_params': json.loads(self.generation_params) if self.generation_params else None,
            'files': json.loads(self.files) if self.files else [],
            'docker_image': self.docker_image,
            'docker_config': json.loads(self.docker_config) if self.docker_config else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
    
    def set_files(self, file_list):
        """设置文件列表"""
        self.files = json.dumps(file_list)
    
    def get_files(self):
        """获取文件列表"""
        return json.loads(self.files) if self.files else []
    
    def set_generation_params(self, params):
        """设置生成参数"""
        self.generation_params = json.dumps(params)
    
    def get_generation_params(self):
        """获取生成参数"""
        return json.loads(self.generation_params) if self.generation_params else {}
    
    def set_docker_config(self, config):
        """设置Docker配置"""
        self.docker_config = json.dumps(config)
    
    def get_docker_config(self):
        """获取Docker配置"""
        return json.loads(self.docker_config) if self.docker_config else {}


class AIModel(db.Model):
    """AI模型配置"""
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    provider = db.Column(db.String(50), nullable=False)  # openai, gemini, deepseek等
    api_key = db.Column(db.String(500), nullable=False)
    api_base = db.Column(db.String(200))
    model_name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # 支持的题目类型
    supports_misc = db.Column(db.Boolean, default=True)
    supports_crypto = db.Column(db.Boolean, default=True)
    supports_web = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式（不包含敏感信息）"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'model_name': self.model_name,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'supports_misc': self.supports_misc,
            'supports_crypto': self.supports_crypto,
            'supports_web': self.supports_web,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class GenerationHistory(db.Model):
    """AI生成历史记录"""
    __tablename__ = 'generation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'))
    
    # 生成参数
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    input_params = db.Column(db.Text)  # JSON格式
    
    # 生成结果
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    generation_time = db.Column(db.Float)  # 生成耗时（秒）
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    challenge = db.relationship('Challenge', backref='generation_records')
    ai_model = db.relationship('AIModel', backref='generation_records')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'ai_model_id': self.ai_model_id,
            'category': self.category,
            'difficulty': self.difficulty,
            'input_params': json.loads(self.input_params) if self.input_params else None,
            'success': self.success,
            'error_message': self.error_message,
            'generation_time': self.generation_time,
            'created_at': self.created_at.isoformat()
        }



class ChallengeService:
    """题目服务类"""
    
    def __init__(self, db_path='ctf_platform.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                flag TEXT NOT NULL,
                points INTEGER DEFAULT 100,
                is_ai_generated BOOLEAN DEFAULT FALSE,
                ai_model_used TEXT,
                generation_params TEXT,
                files TEXT,
                docker_image TEXT,
                docker_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER,
                user_id INTEGER,
                flag TEXT,
                is_correct BOOLEAN,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES challenges (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_challenge(self, name, description, category, difficulty, points, flag, 
                        hints=None, attachments=None, docker_config=None, 
                        is_ai_generated=False, ai_model_id=None):
        """创建题目"""
        import sqlite3
        import json
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO challenges (
                    name, description, category, difficulty, points, flag,
                    is_ai_generated, ai_model_used, generation_params,
                    files, docker_config, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, description, category, difficulty, points, flag,
                is_ai_generated, ai_model_id, 
                json.dumps(hints) if hints else None,
                json.dumps(attachments) if attachments else None,
                json.dumps(docker_config) if docker_config else None,
                datetime.now(), datetime.now()
            ))
            
            challenge_id = cursor.lastrowid
            conn.commit()
            
            # 返回创建的题目
            return self.get_challenge_by_id(challenge_id)
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_challenge_by_id(self, challenge_id):
        """根据ID获取题目"""
        import sqlite3
        import json
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_challenge(row)
        return None
    
    def get_challenges(self, page=1, per_page=20, category=None, difficulty=None):
        """获取题目列表"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM challenges WHERE is_active = TRUE'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if difficulty:
            query += ' AND difficulty = ?'
            params.append(difficulty)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        challenges = []
        for row in rows:
            challenges.append(self._row_to_challenge(row))
        
        return challenges
    
    def update_challenge(self, challenge_id, data):
        """更新题目"""
        import sqlite3
        import json
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建更新语句
        update_fields = []
        params = []
        
        for field in ['name', 'description', 'category', 'difficulty', 'points', 'flag']:
            if field in data:
                update_fields.append(f'{field} = ?')
                params.append(data[field])
        
        if update_fields:
            update_fields.append('updated_at = ?')
            params.append(datetime.now())
            params.append(challenge_id)
            
            query = f'UPDATE challenges SET {", ".join(update_fields)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        return self.get_challenge_by_id(challenge_id)
    
    def delete_challenge(self, challenge_id):
        """删除题目（软删除）"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE challenges SET is_active = FALSE, updated_at = ? WHERE id = ?',
            (datetime.now(), challenge_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def submit_flag(self, challenge_id, user_id, flag):
        """提交flag"""
        import sqlite3
        from datetime import datetime
        
        # 获取题目
        challenge = self.get_challenge_by_id(challenge_id)
        if not challenge:
            raise ValueError("题目不存在")
        
        # 检查flag是否正确
        is_correct = challenge['flag'] == flag
        
        # 记录提交
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions (challenge_id, user_id, flag, is_correct, submitted_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (challenge_id, user_id, flag, is_correct, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return {
            'correct': is_correct,
            'message': '恭喜！答案正确！' if is_correct else '答案错误，请再试一次',
            'points': challenge['points'] if is_correct else 0
        }
    
    def start_challenge_container(self, challenge_id, user_id):
        """启动题目容器"""
        # 这里可以集成Docker API来启动容器
        return {
            'message': '容器启动功能待实现',
            'container_url': f'http://challenge-{challenge_id}-{user_id}.ctf.local'
        }
    
    def stop_challenge_container(self, challenge_id, user_id):
        """停止题目容器"""
        # 这里可以集成Docker API来停止容器
        return {
            'message': '容器已停止'
        }
    
    def _row_to_challenge(self, row):
        """将数据库行转换为题目字典"""
        import json
        
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'category': row[3],
            'difficulty': row[4],
            'flag': row[5],
            'points': row[6],
            'is_ai_generated': bool(row[7]),
            'ai_model_used': row[8],
            'generation_params': json.loads(row[9]) if row[9] else None,
            'attachments': json.loads(row[10]) if row[10] else [],
            'docker_image': row[11],
            'docker_config': json.loads(row[12]) if row[12] else None,
            'created_at': row[13],
            'updated_at': row[14],
            'is_active': bool(row[15])
        }

