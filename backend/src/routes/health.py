"""
健康检查路由
"""
from flask import Blueprint, jsonify
from src.models.user import db
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # 检查环境变量
    env_status = {
        'database_url': bool(os.getenv('DATABASE_URL')),
        'secret_key': bool(os.getenv('SECRET_KEY')),
        'jwt_secret_key': bool(os.getenv('JWT_SECRET_KEY'))
    }
    
    # 检查AI提供商配置
    ai_providers = {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'deepseek': bool(os.getenv('DEEPSEEK_API_KEY')),
        'ernie_bot': bool(os.getenv('ERNIE_BOT_AK')),
        'tongyi_qianwen': bool(os.getenv('TONGYI_QIANWEN_API_KEY')),
        'zhipu_ai': bool(os.getenv('ZHIPU_AI_API_KEY')),
        'google_gemini': bool(os.getenv('GOOGLE_API_KEY'))
    }
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'database': db_status,
        'environment': env_status,
        'ai_providers': ai_providers,
        'version': '1.0.0'
    }), 200 if db_status == 'healthy' else 503

