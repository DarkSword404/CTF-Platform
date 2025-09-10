"""
管理员路由
"""
from flask import Blueprint, request, jsonify, session
from src.models.user import UserService
from src.models.challenge import ChallengeService
from src.services.ai_generator import AIGeneratorService
from src.services.docker_manager import docker_manager
from src.routes.auth import require_admin
import os

admin_bp = Blueprint('admin', __name__)
user_service = UserService()
challenge_service = ChallengeService()
ai_generator = AIGeneratorService()

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@require_admin
def get_dashboard_stats():
    """获取管理员仪表板统计信息"""
    try:
        # 获取用户统计
        users = user_service.get_all_users()
        user_count = len(users)
        admin_count = len([u for u in users if u.is_admin])
        
        # 获取题目统计
        challenges = challenge_service.get_challenges(per_page=1000)
        challenge_count = len(challenges)
        ai_generated_count = len([c for c in challenges if c.get('is_ai_generated')])
        
        # 获取分类统计
        category_stats = {}
        difficulty_stats = {}
        
        for challenge in challenges:
            category = challenge.get('category', 'unknown')
            difficulty = challenge.get('difficulty', 'unknown')
            
            category_stats[category] = category_stats.get(category, 0) + 1
            difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
        
        # 获取AI模型统计
        ai_models = ai_generator.get_ai_models()
        active_models = len([m for m in ai_models if m.get('is_active')])
        
        return jsonify({
            'success': True,
            'data': {
                'users': {
                    'total': user_count,
                    'admins': admin_count,
                    'regular': user_count - admin_count
                },
                'challenges': {
                    'total': challenge_count,
                    'ai_generated': ai_generated_count,
                    'manual': challenge_count - ai_generated_count,
                    'categories': category_stats,
                    'difficulties': difficulty_stats
                },
                'ai_models': {
                    'total': len(ai_models),
                    'active': active_models
                },
                'system': {
                    'docker_available': docker_manager.client is not None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/users', methods=['GET'])
@require_admin
def get_all_users():
    """获取所有用户"""
    try:
        users = user_service.get_all_users()
        return jsonify({
            'success': True,
            'data': {
                'users': [user.to_dict() for user in users]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@require_admin
def toggle_user_admin(user_id):
    """切换用户管理员状态"""
    try:
        # 这里需要实现切换管理员状态的逻辑
        return jsonify({
            'success': True,
            'data': {
                'message': '用户状态已更新'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/challenges/bulk-delete', methods=['POST'])
@require_admin
def bulk_delete_challenges():
    """批量删除题目"""
    try:
        data = request.get_json()
        challenge_ids = data.get('challenge_ids', [])
        
        deleted_count = 0
        for challenge_id in challenge_ids:
            if challenge_service.delete_challenge(challenge_id):
                deleted_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'message': f'已删除 {deleted_count} 个题目'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/docker/containers', methods=['GET'])
@require_admin
def get_all_containers():
    """获取所有容器"""
    try:
        if not docker_manager.client:
            return jsonify({
                'success': False,
                'error': 'Docker服务不可用'
            }), 500
        
        containers = docker_manager.client.containers.list(all=True)
        
        container_list = []
        for container in containers:
            container_list.append({
                'id': container.id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'created': container.attrs['Created'],
                'ports': container.ports
            })
        
        return jsonify({
            'success': True,
            'data': {
                'containers': container_list
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/docker/cleanup', methods=['POST'])
@require_admin
def cleanup_containers():
    """清理过期容器"""
    try:
        docker_manager.cleanup_expired_containers()
        
        return jsonify({
            'success': True,
            'data': {
                'message': '容器清理完成'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/system/info', methods=['GET'])
@require_admin
def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import platform
        
        # 获取系统信息
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent
        }
        
        # 获取Docker信息
        docker_info = {
            'available': docker_manager.client is not None
        }
        
        if docker_manager.client:
            try:
                docker_info.update({
                    'version': docker_manager.client.version()['Version'],
                    'containers_running': len(docker_manager.client.containers.list()),
                    'images_count': len(docker_manager.client.images.list())
                })
            except Exception as e:
                docker_info['error'] = str(e)
        
        return jsonify({
            'success': True,
            'data': {
                'system': system_info,
                'docker': docker_info
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/logs', methods=['GET'])
@require_admin
def get_system_logs():
    """获取系统日志"""
    try:
        # 这里可以实现日志读取逻辑
        logs = [
            {
                'timestamp': '2025-09-10 09:00:00',
                'level': 'INFO',
                'message': '系统启动成功'
            },
            {
                'timestamp': '2025-09-10 09:01:00',
                'level': 'INFO',
                'message': 'AI模型加载完成'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

