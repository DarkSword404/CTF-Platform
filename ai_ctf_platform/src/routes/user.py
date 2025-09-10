from flask import Blueprint, jsonify, request
from src.models.user import UserService

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = user_service.get_all_users()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        user = user_service.create_user(
            username=data['username'], 
            email=data['email'],
            password=data.get('password', 'default123')
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 这里可以添加更新用户的逻辑
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    success = user_service.delete_user(user_id)
    if not success:
        return jsonify({'error': 'User not found'}), 404
    return '', 204
