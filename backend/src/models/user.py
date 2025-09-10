from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # 关系
    challenges = db.relationship('Challenge', backref='author', lazy=True)
    solves = db.relationship('Solve', backref='user', lazy=True)
    user_roles = db.relationship('UserRole', backref='user', lazy=True)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # 关系
    user_roles = db.relationship('UserRole', backref='role', lazy=True)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    flag_format = db.Column(db.String(50), default='plaintext')
    is_case_sensitive_flag = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='draft')
    container_image_name = db.Column(db.String(255))
    container_config_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # 关系
    solves = db.relationship('Solve', backref='challenge', lazy=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'category': self.category,
            'difficulty': self.difficulty,
            'score': self.score,
            'flag_format': self.flag_format,
            'is_case_sensitive_flag': self.is_case_sensitive_flag,
            'status': self.status,
            'container_image_name': self.container_image_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

class Solve(db.Model):
    __tablename__ = 'solves'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    submitted_flag = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'submitted_flag': self.submitted_flag,
            'is_correct': self.is_correct,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

class AICallLog(db.Model):
    __tablename__ = 'ai_call_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    call_type = db.Column(db.String(50), nullable=False)
    request_payload = db.Column(db.Text)
    response_payload = db.Column(db.Text)
    cost = db.Column(db.Numeric(10, 4))
    duration_ms = db.Column(db.Integer)
    called_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'call_type': self.call_type,
            'status': self.status,
            'called_at': self.called_at.isoformat() if self.called_at else None,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message
        }
