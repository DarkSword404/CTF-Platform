"""
题目管理路由
"""
from flask import Blueprint, request, jsonify, session, send_file
from src.models.challenge import ChallengeService
from src.routes.auth import require_auth, require_admin
import os

challenges_bp = Blueprint('challenges', __name__)
challenge_service = ChallengeService()

@challenges_bp.route('/api/challenges', methods=['GET'])
def get_challenges():
    """获取题目列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        
        challenges = challenge_service.get_challenges(
            page=page, 
            per_page=per_page,
            category=category,
            difficulty=difficulty
        )
        
        return jsonify({
            'success': True,
            'data': {
                'challenges': [challenge.to_dict() for challenge in challenges]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """获取单个题目详情"""
    try:
        challenge = challenge_service.get_challenge_by_id(challenge_id)
        if not challenge:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'challenge': challenge.to_dict()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges', methods=['POST'])
@require_admin
def create_challenge():
    """创建题目（管理员）"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'category', 'difficulty', 'points', 'flag']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} 不能为空'
                }), 400
        
        challenge = challenge_service.create_challenge(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            difficulty=data['difficulty'],
            points=data['points'],
            flag=data['flag'],
            hints=data.get('hints', []),
            attachments=data.get('attachments', []),
            docker_config=data.get('docker_config'),
            is_ai_generated=data.get('is_ai_generated', False),
            ai_model_id=data.get('ai_model_id')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'challenge': challenge.to_dict(),
                'message': '题目创建成功'
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>', methods=['PUT'])
@require_admin
def update_challenge(challenge_id):
    """更新题目（管理员）"""
    try:
        data = request.get_json()
        
        challenge = challenge_service.update_challenge(challenge_id, data)
        if not challenge:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'challenge': challenge.to_dict(),
                'message': '题目更新成功'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>', methods=['DELETE'])
@require_admin
def delete_challenge(challenge_id):
    """删除题目（管理员）"""
    try:
        success = challenge_service.delete_challenge(challenge_id)
        if not success:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'message': '题目删除成功'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>/submit', methods=['POST'])
@require_auth
def submit_flag(challenge_id):
    """提交flag"""
    try:
        data = request.get_json()
        flag = data.get('flag')
        user_id = session.get('user_id')
        
        if not flag:
            return jsonify({
                'success': False,
                'error': 'Flag不能为空'
            }), 400
        
        result = challenge_service.submit_flag(challenge_id, user_id, flag)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>/attachments/<filename>')
def download_attachment(challenge_id, filename):
    """下载附件"""
    try:
        challenge = challenge_service.get_challenge_by_id(challenge_id)
        if not challenge:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        # 检查文件是否在附件列表中
        if filename not in challenge.attachments:
            return jsonify({
                'success': False,
                'error': '附件不存在'
            }), 404
        
        # 构建文件路径
        file_path = os.path.join('challenges', str(challenge_id), 'attachments', filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>/start', methods=['POST'])
@require_auth
def start_challenge(challenge_id):
    """启动题目容器"""
    try:
        user_id = session.get('user_id')
        
        result = challenge_service.start_challenge_container(challenge_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/<int:challenge_id>/stop', methods=['POST'])
@require_auth
def stop_challenge(challenge_id):
    """停止题目容器"""
    try:
        user_id = session.get('user_id')
        
        result = challenge_service.stop_challenge_container(challenge_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@challenges_bp.route('/api/challenges/categories', methods=['GET'])
def get_categories():
    """获取题目分类"""
    categories = [
        {'value': 'misc', 'label': 'Misc'},
        {'value': 'crypto', 'label': 'Crypto'},
        {'value': 'web', 'label': 'Web'},
        {'value': 'pwn', 'label': 'Pwn'},
        {'value': 'reverse', 'label': 'Reverse'},
        {'value': 'forensics', 'label': 'Forensics'}
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'categories': categories
        }
    })

@challenges_bp.route('/api/challenges/difficulties', methods=['GET'])
def get_difficulties():
    """获取难度级别"""
    difficulties = [
        {'value': 'easy', 'label': '简单', 'points': 100},
        {'value': 'medium', 'label': '中等', 'points': 200},
        {'value': 'hard', 'label': '困难', 'points': 300}
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'difficulties': difficulties
        }
    })

