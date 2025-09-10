from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Challenge, Solve, UserRole, Role
from datetime import datetime
import json
import re

challenge_bp = Blueprint('challenge', __name__)

def get_user_roles(user_id):
    """获取用户角色列表"""
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    roles = []
    for user_role in user_roles:
        roles.append(user_role.role.name)
    return roles

def has_role(user_id, role_name):
    """检查用户是否有指定角色"""
    roles = get_user_roles(user_id)
    return role_name in roles

@challenge_bp.route('/challenges', methods=['POST'])
@jwt_required()
def create_challenge():
    """创建题目"""
    try:
        user_id = get_jwt_identity()
        
        # 检查用户权限（出题人或管理员）
        if not (has_role(user_id, 'challenger') or has_role(user_id, 'admin')):
            return jsonify({'error': '没有创建题目的权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['title', 'category', 'difficulty', 'score', 'flag']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 不能为空'}), 400
        
        title = data['title'].strip()
        category = data['category'].strip()
        difficulty = data['difficulty'].strip()
        score = data['score']
        flag = data['flag'].strip()
        
        # 验证数据格式
        if len(title) > 255:
            return jsonify({'error': '题目标题长度不能超过255个字符'}), 400
        
        if category not in ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc']:
            return jsonify({'error': '题目分类无效'}), 400
        
        if difficulty not in ['Easy', 'Medium', 'Hard']:
            return jsonify({'error': '题目难度无效'}), 400
        
        if not isinstance(score, int) or score <= 0:
            return jsonify({'error': '题目分数必须是正整数'}), 400
        
        # 检查题目标题是否重复
        if Challenge.query.filter_by(title=title).first():
            return jsonify({'error': '题目标题已存在'}), 400
        
        # 创建题目
        challenge = Challenge(
            title=title,
            author_id=user_id,
            category=category,
            difficulty=difficulty,
            score=score,
            flag=flag,
            flag_format=data.get('flag_format', 'plaintext'),
            is_case_sensitive_flag=data.get('is_case_sensitive_flag', True),
            container_image_name=data.get('container_image_name'),
            container_config_json=json.dumps(data.get('container_config', {}))
        )
        
        db.session.add(challenge)
        db.session.commit()
        
        return jsonify({
            'message': '题目创建成功',
            'challenge_id': challenge.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建题目失败: {str(e)}'}), 500

@challenge_bp.route('/challenges', methods=['GET'])
@jwt_required()
def get_challenges():
    """获取题目列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        status = request.args.get('status')
        author_id = request.args.get('author_id', type=int)
        
        # 限制分页大小
        page_size = min(page_size, 100)
        
        # 构建查询
        query = Challenge.query
        
        # 非管理员只能看到已发布的题目或自己创建的题目
        if not has_role(user_id, 'admin'):
            query = query.filter(
                (Challenge.status == 'published') | 
                (Challenge.author_id == user_id)
            )
        
        # 应用过滤条件
        if category:
            query = query.filter(Challenge.category == category)
        
        if difficulty:
            query = query.filter(Challenge.difficulty == difficulty)
        
        if status:
            query = query.filter(Challenge.status == status)
        
        if author_id:
            query = query.filter(Challenge.author_id == author_id)
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=page_size, 
            error_out=False
        )
        
        challenges = []
        for challenge in pagination.items:
            challenge_data = challenge.to_dict()
            # 添加作者信息
            author = User.query.get(challenge.author_id)
            challenge_data['author'] = {
                'id': author.id,
                'username': author.username
            } if author else None
            
            # 添加解题统计
            total_solves = Solve.query.filter_by(
                challenge_id=challenge.id, 
                is_correct=True
            ).count()
            challenge_data['solve_count'] = total_solves
            
            # 检查当前用户是否已解出
            user_solve = Solve.query.filter_by(
                challenge_id=challenge.id,
                user_id=user_id,
                is_correct=True
            ).first()
            challenge_data['solved_by_user'] = user_solve is not None
            
            challenges.append(challenge_data)
        
        return jsonify({
            'challenges': challenges,
            'total_count': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取题目列表失败: {str(e)}'}), 500

@challenge_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """获取题目详情"""
    try:
        user_id = get_jwt_identity()
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        # 权限检查
        if not has_role(user_id, 'admin'):
            # 非管理员只能查看已发布的题目或自己创建的题目
            if challenge.status != 'published' and challenge.author_id != user_id:
                return jsonify({'error': '没有权限查看此题目'}), 403
        
        challenge_data = challenge.to_dict()
        
        # 添加作者信息
        author = User.query.get(challenge.author_id)
        challenge_data['author'] = {
            'id': author.id,
            'username': author.username
        } if author else None
        
        # 添加解题统计
        total_solves = Solve.query.filter_by(
            challenge_id=challenge.id, 
            is_correct=True
        ).count()
        challenge_data['solve_count'] = total_solves
        
        # 检查当前用户是否已解出
        user_solve = Solve.query.filter_by(
            challenge_id=challenge.id,
            user_id=user_id,
            is_correct=True
        ).first()
        challenge_data['solved_by_user'] = user_solve is not None
        
        # 解析容器配置
        if challenge.container_config_json:
            try:
                challenge_data['container_config'] = json.loads(challenge.container_config_json)
            except:
                challenge_data['container_config'] = {}
        else:
            challenge_data['container_config'] = {}
        
        # 非作者和管理员不返回Flag
        if challenge.author_id != user_id and not has_role(user_id, 'admin'):
            challenge_data.pop('flag', None)
        
        return jsonify(challenge_data), 200
        
    except Exception as e:
        return jsonify({'error': f'获取题目详情失败: {str(e)}'}), 500

@challenge_bp.route('/challenges/<int:challenge_id>/submit-flag', methods=['POST'])
@jwt_required()
def submit_flag(challenge_id):
    """提交Flag"""
    try:
        user_id = get_jwt_identity()
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        # 只能提交已发布的题目
        if challenge.status != 'published':
            return jsonify({'error': '题目未发布，无法提交Flag'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        submitted_flag = data.get('submitted_flag', '').strip()
        if not submitted_flag:
            return jsonify({'error': 'Flag不能为空'}), 400
        
        # 检查是否已经解出
        existing_solve = Solve.query.filter_by(
            challenge_id=challenge_id,
            user_id=user_id,
            is_correct=True
        ).first()
        
        if existing_solve:
            return jsonify({
                'message': 'Flag提交成功',
                'is_correct': True,
                'score_awarded': 0,  # 已解出，不再给分
                'note': '您已经解出过此题目'
            }), 200
        
        # 验证Flag
        is_correct = False
        if challenge.flag_format == 'regex':
            # 正则表达式匹配
            try:
                pattern = challenge.flag
                if challenge.is_case_sensitive_flag:
                    is_correct = bool(re.match(pattern, submitted_flag))
                else:
                    is_correct = bool(re.match(pattern, submitted_flag, re.IGNORECASE))
            except re.error:
                # 正则表达式无效，回退到普通匹配
                if challenge.is_case_sensitive_flag:
                    is_correct = submitted_flag == challenge.flag
                else:
                    is_correct = submitted_flag.lower() == challenge.flag.lower()
        else:
            # 普通文本匹配
            if challenge.is_case_sensitive_flag:
                is_correct = submitted_flag == challenge.flag
            else:
                is_correct = submitted_flag.lower() == challenge.flag.lower()
        
        # 记录提交
        solve = Solve(
            user_id=user_id,
            challenge_id=challenge_id,
            submitted_flag=submitted_flag,
            is_correct=is_correct
        )
        
        db.session.add(solve)
        db.session.commit()
        
        score_awarded = challenge.score if is_correct else 0
        
        return jsonify({
            'message': 'Flag提交成功',
            'is_correct': is_correct,
            'score_awarded': score_awarded
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'提交Flag失败: {str(e)}'}), 500

@challenge_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@jwt_required()
def update_challenge(challenge_id):
    """更新题目"""
    try:
        user_id = get_jwt_identity()
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        # 权限检查：只有作者或管理员可以更新
        if challenge.author_id != user_id and not has_role(user_id, 'admin'):
            return jsonify({'error': '没有权限更新此题目'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 更新允许的字段
        if 'title' in data:
            title = data['title'].strip()
            if len(title) > 255:
                return jsonify({'error': '题目标题长度不能超过255个字符'}), 400
            # 检查标题是否与其他题目重复
            existing = Challenge.query.filter(
                Challenge.title == title,
                Challenge.id != challenge_id
            ).first()
            if existing:
                return jsonify({'error': '题目标题已存在'}), 400
            challenge.title = title
        
        if 'category' in data:
            if data['category'] not in ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc']:
                return jsonify({'error': '题目分类无效'}), 400
            challenge.category = data['category']
        
        if 'difficulty' in data:
            if data['difficulty'] not in ['Easy', 'Medium', 'Hard']:
                return jsonify({'error': '题目难度无效'}), 400
            challenge.difficulty = data['difficulty']
        
        if 'score' in data:
            if not isinstance(data['score'], int) or data['score'] <= 0:
                return jsonify({'error': '题目分数必须是正整数'}), 400
            challenge.score = data['score']
        
        if 'flag' in data:
            challenge.flag = data['flag'].strip()
        
        if 'flag_format' in data:
            challenge.flag_format = data['flag_format']
        
        if 'is_case_sensitive_flag' in data:
            challenge.is_case_sensitive_flag = data['is_case_sensitive_flag']
        
        if 'container_image_name' in data:
            challenge.container_image_name = data['container_image_name']
        
        if 'container_config' in data:
            challenge.container_config_json = json.dumps(data['container_config'])
        
        challenge.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '题目更新成功',
            'challenge_id': challenge.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新题目失败: {str(e)}'}), 500

@challenge_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@jwt_required()
def delete_challenge(challenge_id):
    """删除题目"""
    try:
        user_id = get_jwt_identity()
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': '题目不存在'}), 404
        
        # 权限检查：只有作者（未发布题目）或管理员可以删除
        if not has_role(user_id, 'admin'):
            if challenge.author_id != user_id:
                return jsonify({'error': '没有权限删除此题目'}), 403
            if challenge.status == 'published':
                return jsonify({'error': '已发布的题目不能删除，请联系管理员'}), 403
        
        # 删除相关的解题记录
        Solve.query.filter_by(challenge_id=challenge_id).delete()
        
        # 删除题目
        db.session.delete(challenge)
        db.session.commit()
        
        return jsonify({'message': '题目删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除题目失败: {str(e)}'}), 500

