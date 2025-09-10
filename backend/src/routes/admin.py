from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Challenge, Solve, Role, UserRole, AICallLog
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def has_role(user_id, role_name):
    """检查用户是否有指定角色"""
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    roles = []
    for user_role in user_roles:
        roles.append(user_role.role.name)
    return role_name in roles

def require_admin(f):
    """装饰器：要求管理员权限"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not has_role(user_id, 'admin'):
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@require_admin
def get_all_users():
    """获取所有用户列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        username = request.args.get('username')
        email = request.args.get('email')
        is_active = request.args.get('is_active')
        is_locked = request.args.get('is_locked')
        
        # 限制分页大小
        page_size = min(page_size, 100)
        
        # 构建查询
        query = User.query
        
        if username:
            query = query.filter(User.username.contains(username))
        
        if email:
            query = query.filter(User.email.contains(email))
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter(User.is_active == is_active_bool)
        
        if is_locked is not None:
            is_locked_bool = is_locked.lower() == 'true'
            query = query.filter(User.is_locked == is_locked_bool)
        
        # 按创建时间倒序排列
        query = query.order_by(User.created_at.desc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        users = []
        for user in pagination.items:
            user_data = user.to_dict()
            
            # 获取用户角色
            roles = []
            for user_role in user.user_roles:
                roles.append(user_role.role.name)
            user_data['roles'] = roles
            
            # 获取用户统计信息
            solve_count = Solve.query.filter_by(user_id=user.id, is_correct=True).count()
            challenge_count = Challenge.query.filter_by(author_id=user.id).count()
            user_data['solve_count'] = solve_count
            user_data['challenge_count'] = challenge_count
            
            users.append(user_data)
        
        return jsonify({
            'users': users,
            'total_count': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin
def update_user(user_id):
    """更新用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 更新允许的字段
        if 'nickname' in data:
            user.nickname = data['nickname']
        
        if 'email' in data:
            email = data['email'].strip()
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': '邮箱已被其他用户使用'}), 400
            user.email = email
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'is_locked' in data:
            user.is_locked = data['is_locked']
        
        # 更新角色
        if 'roles' in data:
            # 删除现有角色
            UserRole.query.filter_by(user_id=user_id).delete()
            
            # 添加新角色
            for role_name in data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user_role = UserRole(user_id=user_id, role_id=role.id)
                    db.session.add(user_role)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 返回更新后的用户信息
        user_data = user.to_dict()
        roles = []
        for user_role in user.user_roles:
            roles.append(user_role.role.name)
        user_data['roles'] = roles
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新用户信息失败: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 不能删除管理员用户
        if has_role(user_id, 'admin'):
            return jsonify({'error': '不能删除管理员用户'}), 400
        
        # 删除相关数据
        UserRole.query.filter_by(user_id=user_id).delete()
        Solve.query.filter_by(user_id=user_id).delete()
        AICallLog.query.filter_by(user_id=user_id).delete()
        
        # 将用户创建的题目转移给当前管理员或删除
        challenges = Challenge.query.filter_by(author_id=user_id).all()
        current_admin_id = get_jwt_identity()
        for challenge in challenges:
            if challenge.status == 'draft':
                # 删除草稿题目
                db.session.delete(challenge)
            else:
                # 转移已发布的题目给当前管理员
                challenge.author_id = current_admin_id
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除用户失败: {str(e)}'}), 500

@admin_bp.route('/admin/challenges/<int:challenge_id>/review', methods=['POST'])
@jwt_required()
@require_admin
def review_challenge(challenge_id):
    """审核题目"""
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        action = data.get('action')
        reason = data.get('reason', '')
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': '审核操作无效'}), 400
        
        if action == 'approve':
            challenge.status = 'published'
            challenge.published_at = datetime.utcnow()
            message = '题目审核通过'
        else:  # reject
            challenge.status = 'rejected'
            message = '题目审核驳回'
        
        challenge.updated_at = datetime.utcnow()
        db.session.commit()
        
        # TODO: 发送通知给题目作者
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'审核题目失败: {str(e)}'}), 500

@admin_bp.route('/admin/challenges/<int:challenge_id>/status', methods=['PUT'])
@jwt_required()
@require_admin
def update_challenge_status(challenge_id):
    """更新题目状态"""
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        status = data.get('status')
        if status not in ['published', 'offline', 'pending_review']:
            return jsonify({'error': '题目状态无效'}), 400
        
        old_status = challenge.status
        challenge.status = status
        
        if status == 'published' and old_status != 'published':
            challenge.published_at = datetime.utcnow()
        
        challenge.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '题目状态更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新题目状态失败: {str(e)}'}), 500

@admin_bp.route('/admin/statistics', methods=['GET'])
@jwt_required()
@require_admin
def get_statistics():
    """获取平台统计信息"""
    try:
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        locked_users = User.query.filter_by(is_locked=True).count()
        
        # 题目统计
        total_challenges = Challenge.query.count()
        published_challenges = Challenge.query.filter_by(status='published').count()
        pending_challenges = Challenge.query.filter_by(status='pending_review').count()
        
        # 解题统计
        total_solves = Solve.query.filter_by(is_correct=True).count()
        total_attempts = Solve.query.count()
        
        # AI调用统计
        total_ai_calls = AICallLog.query.count()
        successful_ai_calls = AICallLog.query.filter_by(status='success').count()
        
        # 分类统计
        category_stats = {}
        categories = ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc']
        for category in categories:
            count = Challenge.query.filter_by(category=category, status='published').count()
            category_stats[category] = count
        
        # 难度统计
        difficulty_stats = {}
        difficulties = ['Easy', 'Medium', 'Hard']
        for difficulty in difficulties:
            count = Challenge.query.filter_by(difficulty=difficulty, status='published').count()
            difficulty_stats[difficulty] = count
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'locked': locked_users
            },
            'challenges': {
                'total': total_challenges,
                'published': published_challenges,
                'pending_review': pending_challenges,
                'by_category': category_stats,
                'by_difficulty': difficulty_stats
            },
            'solves': {
                'total_correct': total_solves,
                'total_attempts': total_attempts,
                'success_rate': round(total_solves / total_attempts * 100, 2) if total_attempts > 0 else 0
            },
            'ai_calls': {
                'total': total_ai_calls,
                'successful': successful_ai_calls,
                'success_rate': round(successful_ai_calls / total_ai_calls * 100, 2) if total_ai_calls > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

@admin_bp.route('/admin/ai/logs', methods=['GET'])
@jwt_required()
@require_admin
def get_all_ai_logs():
    """获取所有AI调用日志"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        call_type = request.args.get('call_type')
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        # 限制分页大小
        page_size = min(page_size, 100)
        
        # 构建查询
        query = AICallLog.query
        
        if call_type:
            query = query.filter(AICallLog.call_type == call_type)
        
        if status:
            query = query.filter(AICallLog.status == status)
        
        if user_id:
            query = query.filter(AICallLog.user_id == user_id)
        
        # 按时间倒序排列
        query = query.order_by(AICallLog.called_at.desc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        logs = []
        for log in pagination.items:
            log_data = log.to_dict()
            
            # 添加用户信息
            if log.user_id:
                user = User.query.get(log.user_id)
                log_data['user'] = {
                    'id': user.id,
                    'username': user.username
                } if user else None
            
            logs.append(log_data)
        
        return jsonify({
            'logs': logs,
            'total_count': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取AI调用日志失败: {str(e)}'}), 500

