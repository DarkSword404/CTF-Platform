"""
AI配置模型
用于存储和管理AI模型配置
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class AIProviderConfig(db.Model):
    """AI提供商配置表"""
    __tablename__ = 'ai_provider_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), unique=True, nullable=False)  # openai, deepseek, ernie_bot等
    display_name = db.Column(db.String(100), nullable=False)  # 显示名称
    model_name = db.Column(db.String(100))  # 模型名称
    api_key = db.Column(db.Text)  # API密钥（加密存储）
    api_base = db.Column(db.String(255))  # API基础URL
    enabled = db.Column(db.Boolean, default=False)  # 是否启用
    max_tokens = db.Column(db.Integer, default=2000)  # 最大token数
    temperature = db.Column(db.Float, default=0.7)  # 温度参数
    timeout = db.Column(db.Integer, default=30)  # 超时时间（秒）
    priority = db.Column(db.Integer, default=0)  # 优先级（数字越大优先级越高）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'display_name': self.display_name,
            'model_name': self.model_name,
            'api_base': self.api_base,
            'enabled': self.enabled,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'timeout': self.timeout,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'has_api_key': bool(self.api_key)  # 不返回实际的API密钥
        }
    
    def to_dict_with_key(self):
        """转换为字典（包含API密钥，仅管理员使用）"""
        data = self.to_dict()
        data['api_key'] = self.api_key
        return data

class AIUsageStats(db.Model):
    """AI使用统计表"""
    __tablename__ = 'ai_usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)  # 统计日期
    total_calls = db.Column(db.Integer, default=0)  # 总调用次数
    successful_calls = db.Column(db.Integer, default=0)  # 成功调用次数
    failed_calls = db.Column(db.Integer, default=0)  # 失败调用次数
    total_tokens = db.Column(db.Integer, default=0)  # 总token消耗
    avg_response_time = db.Column(db.Float, default=0.0)  # 平均响应时间（毫秒）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 复合唯一索引
    __table_args__ = (db.UniqueConstraint('provider_name', 'date', name='_provider_date_uc'),)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'date': self.date.isoformat() if self.date else None,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(self.successful_calls / self.total_calls * 100, 2) if self.total_calls > 0 else 0,
            'total_tokens': self.total_tokens,
            'avg_response_time': self.avg_response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

