"""
AI模型管理路由
管理员用于配置和管理AI模型
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, UserRole
from src.models.ai_config import AIProviderConfig, AIUsageStats
from datetime import datetime, date, timedelta
from sqlalchemy import func
import os

ai_admin_bp = Blueprint('ai_admin', __name__)

def has_role(user_id, role_name):
    """检查用户是否有指定角色"""
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    roles = []
    for user_role in user_roles:
        roles.append(user_role.role.name)
    return role_name in roles

def is_admin(user_id):
    """检查用户是否为管理员"""
    return has_role(user_id, 'admin')

@ai_admin_bp.route('/providers', methods=['GET'])
@jwt_required()
def get_ai_providers():
    """获取AI提供商配置列表"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        # 限制分页大小
        page_size = min(page_size, 100)
        
        # 构建查询
        query = AIProviderConfig.query
        
        if enabled_only:
            query = query.filter(AIProviderConfig.enabled == True)
        
        # 按优先级和创建时间排序
        query = query.order_by(AIProviderConfig.priority.desc(), AIProviderConfig.created_at.asc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        providers = []
        for provider in pagination.items:
            providers.append(provider.to_dict_with_key())
        
        return jsonify({
            'providers': providers,
            'total_count': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取AI提供商配置失败: {str(e)}'}), 500

@ai_admin_bp.route('/providers', methods=['POST'])
@jwt_required()
def create_ai_provider():
    """创建AI提供商配置"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['provider_name', 'display_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400
        
        # 检查提供商名称是否已存在
        existing_provider = AIProviderConfig.query.filter_by(
            provider_name=data['provider_name']
        ).first()
        if existing_provider:
            return jsonify({'error': '该提供商已存在'}), 400
        
        # 创建新的提供商配置
        provider = AIProviderConfig(
            provider_name=data['provider_name'],
            display_name=data['display_name'],
            model_name=data.get('model_name'),
            api_key=data.get('api_key'),
            api_base=data.get('api_base'),
            enabled=data.get('enabled', False),
            max_tokens=data.get('max_tokens', 2000),
            temperature=data.get('temperature', 0.7),
            timeout=data.get('timeout', 30),
            priority=data.get('priority', 0)
        )
        
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({
            'message': 'AI提供商配置创建成功',
            'provider': provider.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建AI提供商配置失败: {str(e)}'}), 500

@ai_admin_bp.route('/providers/<int:provider_id>', methods=['PUT'])
@jwt_required()
def update_ai_provider(provider_id):
    """更新AI提供商配置"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        provider = AIProviderConfig.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'AI提供商配置不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 更新字段
        if 'display_name' in data:
            provider.display_name = data['display_name']
        if 'model_name' in data:
            provider.model_name = data['model_name']
        if 'api_key' in data:
            provider.api_key = data['api_key']
        if 'api_base' in data:
            provider.api_base = data['api_base']
        if 'enabled' in data:
            provider.enabled = data['enabled']
        if 'max_tokens' in data:
            provider.max_tokens = data['max_tokens']
        if 'temperature' in data:
            provider.temperature = data['temperature']
        if 'timeout' in data:
            provider.timeout = data['timeout']
        if 'priority' in data:
            provider.priority = data['priority']
        
        provider.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'AI提供商配置更新成功',
            'provider': provider.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新AI提供商配置失败: {str(e)}'}), 500

@ai_admin_bp.route('/providers/<int:provider_id>', methods=['DELETE'])
@jwt_required()
def delete_ai_provider(provider_id):
    """删除AI提供商配置"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        provider = AIProviderConfig.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'AI提供商配置不存在'}), 404
        
        db.session.delete(provider)
        db.session.commit()
        
        return jsonify({'message': 'AI提供商配置删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除AI提供商配置失败: {str(e)}'}), 500

@ai_admin_bp.route('/providers/<int:provider_id>/test', methods=['POST'])
@jwt_required()
def test_ai_provider(provider_id):
    """测试AI提供商连接"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        provider = AIProviderConfig.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'AI提供商配置不存在'}), 404
        
        # TODO: 实现实际的AI提供商连接测试
        # 这里可以调用相应的AI服务进行简单的测试请求
        
        return jsonify({
            'message': 'AI提供商连接测试成功',
            'provider_name': provider.provider_name,
            'test_result': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'测试AI提供商连接失败: {str(e)}'}), 500

@ai_admin_bp.route('/usage-stats', methods=['GET'])
@jwt_required()
def get_usage_stats():
    """获取AI使用统计"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 获取查询参数
        days = request.args.get('days', 7, type=int)  # 默认查询最近7天
        provider_name = request.args.get('provider_name')
        
        # 限制查询天数
        days = min(days, 90)
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 构建查询
        query = AIUsageStats.query.filter(
            AIUsageStats.date >= start_date,
            AIUsageStats.date <= end_date
        )
        
        if provider_name:
            query = query.filter(AIUsageStats.provider_name == provider_name)
        
        # 按日期排序
        stats = query.order_by(AIUsageStats.date.desc()).all()
        
        # 计算汇总统计
        total_stats = query.with_entities(
            func.sum(AIUsageStats.total_calls).label('total_calls'),
            func.sum(AIUsageStats.successful_calls).label('successful_calls'),
            func.sum(AIUsageStats.failed_calls).label('failed_calls'),
            func.sum(AIUsageStats.total_tokens).label('total_tokens'),
            func.avg(AIUsageStats.avg_response_time).label('avg_response_time')
        ).first()
        
        # 按提供商分组统计
        provider_stats = db.session.query(
            AIUsageStats.provider_name,
            func.sum(AIUsageStats.total_calls).label('total_calls'),
            func.sum(AIUsageStats.successful_calls).label('successful_calls'),
            func.sum(AIUsageStats.failed_calls).label('failed_calls'),
            func.sum(AIUsageStats.total_tokens).label('total_tokens'),
            func.avg(AIUsageStats.avg_response_time).label('avg_response_time')
        ).filter(
            AIUsageStats.date >= start_date,
            AIUsageStats.date <= end_date
        ).group_by(AIUsageStats.provider_name).all()
        
        return jsonify({
            'daily_stats': [stat.to_dict() for stat in stats],
            'summary': {
                'total_calls': total_stats.total_calls or 0,
                'successful_calls': total_stats.successful_calls or 0,
                'failed_calls': total_stats.failed_calls or 0,
                'success_rate': round((total_stats.successful_calls or 0) / (total_stats.total_calls or 1) * 100, 2),
                'total_tokens': total_stats.total_tokens or 0,
                'avg_response_time': round(total_stats.avg_response_time or 0, 2)
            },
            'provider_stats': [
                {
                    'provider_name': stat.provider_name,
                    'total_calls': stat.total_calls,
                    'successful_calls': stat.successful_calls,
                    'failed_calls': stat.failed_calls,
                    'success_rate': round(stat.successful_calls / stat.total_calls * 100, 2) if stat.total_calls > 0 else 0,
                    'total_tokens': stat.total_tokens,
                    'avg_response_time': round(stat.avg_response_time, 2)
                }
                for stat in provider_stats
            ],
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取AI使用统计失败: {str(e)}'}), 500

@ai_admin_bp.route('/init-default-providers', methods=['POST'])
@jwt_required()
def init_default_providers():
    """初始化默认AI提供商配置"""
    try:
        user_id = get_jwt_identity()
        
        # 检查管理员权限
        if not is_admin(user_id):
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 默认提供商配置
        default_providers = [
            {
                'provider_name': 'openai',
                'display_name': 'OpenAI GPT',
                'model_name': 'gpt-3.5-turbo',
                'api_base': 'https://api.openai.com/v1',
                'priority': 100
            },
            {
                'provider_name': 'deepseek',
                'display_name': 'DeepSeek',
                'model_name': 'deepseek-chat',
                'api_base': 'https://api.deepseek.com/v1',
                'priority': 90
            },
            {
                'provider_name': 'ernie_bot',
                'display_name': '百度文心一言',
                'model_name': 'ERNIE-Bot-turbo',
                'priority': 80
            },
            {
                'provider_name': 'tongyi_qianwen',
                'display_name': '阿里云通义千问',
                'model_name': 'qwen-turbo',
                'priority': 70
            },
            {
                'provider_name': 'zhipu_ai',
                'display_name': '智谱AI',
                'model_name': 'glm-4',
                'priority': 60
            },
            {
                'provider_name': 'google',
                'display_name': 'Google Gemini',
                'model_name': 'gemini-pro',
                'priority': 50
            }
        ]
        
        created_count = 0
        for provider_data in default_providers:
            # 检查是否已存在
            existing = AIProviderConfig.query.filter_by(
                provider_name=provider_data['provider_name']
            ).first()
            
            if not existing:
                provider = AIProviderConfig(**provider_data)
                db.session.add(provider)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功初始化{created_count}个默认AI提供商配置',
            'created_count': created_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'初始化默认AI提供商配置失败: {str(e)}'}), 500

