"""
认证路由
"""
from flask import Blueprint, request, jsonify, session
from src.models.user import UserService

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        user = user_service.authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'message': '登录成功'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'error': '用户名、邮箱和密码不能为空'
            }), 400
        
        user = user_service.create_user(username, email, password)
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'message': '注册成功'
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

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({
        'success': True,
        'data': {
            'message': '登出成功'
        }
    })

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': '未登录'
        }), 401
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'error': '用户不存在'
        }), 401
    
    return jsonify({
        'success': True,
        'data': {
            'user': user.to_dict()
        }
    })

def require_auth(f):
    """认证装饰器"""
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_admin(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401
        
        if not is_admin:
            return jsonify({
                'success': False,
                'error': '需要管理员权限'
            }), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

