from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from src.models.user import db, User, Role, UserRole
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # 验证必填字段
        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 50:
            return jsonify({'error': '用户名长度必须在3-50个字符之间'}), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 验证密码强度
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            nickname=username  # 默认昵称为用户名
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 分配默认角色（普通用户）
        default_role = Role.query.filter_by(name='user').first()
        if default_role:
            user_role = UserRole(user_id=user.id, role_id=default_role.id)
            db.session.add(user_role)
            db.session.commit()
        
        return jsonify({'message': '注册成功，请登录'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': '用户名/邮箱和密码不能为空'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名/邮箱或密码错误'}), 401
        
        # 检查用户状态
        if not user.is_active:
            return jsonify({'error': '账户未激活'}), 401
        
        if user.is_locked:
            return jsonify({'error': '账户已被锁定'}), 401
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # 创建访问令牌
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        # 获取用户角色
        roles = []
        for user_role in user.user_roles:
            roles.append(user_role.role.name)
        
        user_data = user.to_dict()
        user_data['roles'] = roles
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 86400,  # 24小时
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户角色
        roles = []
        for user_role in user.user_roles:
            roles.append(user_role.role.name)
        
        user_data = user.to_dict()
        user_data['roles'] = roles
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """更新当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 更新允许的字段
        if 'nickname' in data:
            nickname = data['nickname'].strip()
            if len(nickname) > 100:
                return jsonify({'error': '昵称长度不能超过100个字符'}), 400
            user.nickname = nickname
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        if 'bio' in data:
            bio = data['bio'].strip()
            if len(bio) > 1000:
                return jsonify({'error': '个人简介长度不能超过1000个字符'}), 400
            user.bio = bio
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新用户信息失败: {str(e)}'}), 500

@auth_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'error': '旧密码和新密码不能为空'}), 400
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'error': '旧密码不正确'}), 400
        
        # 验证新密码强度
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 更新密码
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'修改密码失败: {str(e)}'}), 500

