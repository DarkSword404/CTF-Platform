"""
用户模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, 
                 is_admin=False, created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class UserService:
    def __init__(self, db_path='ctf_platform.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # 创建默认管理员账户
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            admin = User(username='admin', email='admin@ctf.local', is_admin=True)
            admin.set_password('admin123')
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin.username, admin.email, admin.password_hash, admin.is_admin, admin.created_at))
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password, is_admin=False):
        """创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            user = User(username=username, email=email, is_admin=is_admin)
            user.set_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user.username, user.email, user.password_hash, user.is_admin, user.created_at))
            
            user.id = cursor.lastrowid
            conn.commit()
            return user
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                raise ValueError("用户名已存在")
            elif 'email' in str(e):
                raise ValueError("邮箱已存在")
            else:
                raise ValueError("创建用户失败")
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0], username=row[1], email=row[2], password_hash=row[3],
                is_admin=bool(row[4]), created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None
            )
        return None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0], username=row[1], email=row[2], password_hash=row[3],
                is_admin=bool(row[4]), created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None
            )
        return None
    
    def authenticate_user(self, username, password):
        """验证用户"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            # 更新最后登录时间
            self.update_last_login(user.id)
            return user
        return None
    
    def update_last_login(self, user_id):
        """更新最后登录时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now(), user_id))
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """获取所有用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                id=row[0], username=row[1], email=row[2], password_hash=row[3],
                is_admin=bool(row[4]), created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None
            ))
        
        return users
    
    def delete_user(self, user_id):
        """删除用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
