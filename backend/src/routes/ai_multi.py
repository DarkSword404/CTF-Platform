"""
多AI模型路由
支持多种AI模型的统一接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, AICallLog, UserRole
from src.services.ai_service import multi_ai_service, AIProvider
import json
import time
import asyncio

ai_multi_bp = Blueprint('ai_multi', __name__)

def has_role(user_id, role_name):
    """检查用户是否有指定角色"""
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    roles = []
    for user_role in user_roles:
        roles.append(user_role.role.name)
    return role_name in roles

def log_ai_call(user_id, call_type, request_payload, response_payload, duration_ms, status, error_message=None, provider=None):
    """记录AI调用日志"""
    try:
        log = AICallLog(
            user_id=user_id,
            call_type=call_type,
            request_payload=json.dumps(request_payload) if request_payload else None,
            response_payload=json.dumps(response_payload) if response_payload else None,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"记录AI调用日志失败: {str(e)}")

@ai_multi_bp.route('/providers', methods=['GET'])
@jwt_required()
def get_available_providers():
    """获取可用的AI提供商列表"""
    try:
        user_id = get_jwt_identity()
        
        # 检查用户权限
        if not (has_role(user_id, 'challenger') or has_role(user_id, 'admin')):
            return jsonify({'error': '没有访问AI服务的权限'}), 403
        
        providers = multi_ai_service.get_available_providers()
        provider_list = []
        
        for provider in providers:
            provider_list.append({
                'name': provider.value,
                'display_name': {
                    'openai': 'OpenAI GPT',
                    'deepseek': 'DeepSeek',
                    'ernie_bot': '百度文心一言',
                    'tongyi_qianwen': '阿里云通义千问',
                    'zhipu_ai': '智谱AI',
                    'google': 'Google Gemini'
                }.get(provider.value, provider.value),
                'available': True
            })
        
        return jsonify({
            'providers': provider_list,
            'total_count': len(provider_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取AI提供商列表失败: {str(e)}'}), 500

@ai_multi_bp.route('/generate-challenge', methods=['POST'])
@jwt_required()
def generate_challenge_multi():
    """使用多AI模型生成题目内容"""
    try:
        user_id = get_jwt_identity()
        
        # 检查用户权限（出题人或管理员）
        if not (has_role(user_id, 'challenger') or has_role(user_id, 'admin')):
            return jsonify({'error': '没有使用AI生成题目的权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        prompt = data.get('prompt', '').strip()
        challenge_type = data.get('challenge_type', '').strip()
        difficulty = data.get('difficulty', '').strip()
        provider_name = data.get('provider', '').strip()
        
        if not prompt:
            return jsonify({'error': '题目描述不能为空'}), 400
        
        if challenge_type not in ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc']:
            return jsonify({'error': '题目类型无效'}), 400
        
        if difficulty not in ['Easy', 'Medium', 'Hard']:
            return jsonify({'error': '题目难度无效'}), 400
        
        # 确定使用的AI提供商
        preferred_provider = None
        if provider_name:
            try:
                preferred_provider = AIProvider(provider_name)
            except ValueError:
                return jsonify({'error': f'不支持的AI提供商: {provider_name}'}), 400
        
        start_time = time.time()
        
        try:
            # 调用AI服务生成题目
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            generated_content = loop.run_until_complete(
                multi_ai_service.generate_challenge(
                    category=challenge_type,
                    difficulty=difficulty,
                    requirements=prompt,
                    preferred_provider=preferred_provider
                )
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 记录成功的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_challenge_multi',
                request_payload={
                    'prompt': prompt,
                    'challenge_type': challenge_type,
                    'difficulty': difficulty,
                    'provider': provider_name
                },
                response_payload=generated_content,
                duration_ms=duration_ms,
                status='success',
                provider=provider_name
            )
            
            return jsonify({
                'message': 'AI题目生成成功',
                'generated_content': generated_content,
                'provider_used': provider_name or 'auto'
            }), 200
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = f"AI生成题目失败: {str(e)}"
            
            # 记录失败的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_challenge_multi',
                request_payload={
                    'prompt': prompt,
                    'challenge_type': challenge_type,
                    'difficulty': difficulty,
                    'provider': provider_name
                },
                response_payload=None,
                duration_ms=duration_ms,
                status='failed',
                error_message=error_message,
                provider=provider_name
            )
            
            return jsonify({'error': error_message}), 500
        
    except Exception as e:
        return jsonify({'error': f'AI生成题目失败: {str(e)}'}), 500

@ai_multi_bp.route('/generate-flag', methods=['POST'])
@jwt_required()
def generate_flag_multi():
    """使用多AI模型生成Flag"""
    try:
        user_id = get_jwt_identity()
        
        # 检查用户权限（出题人或管理员）
        if not (has_role(user_id, 'challenger') or has_role(user_id, 'admin')):
            return jsonify({'error': '没有使用AI生成Flag的权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        challenge_description = data.get('challenge_description', '').strip()
        challenge_type = data.get('challenge_type', '').strip()
        provider_name = data.get('provider', '').strip()
        
        if not challenge_description:
            return jsonify({'error': '题目描述不能为空'}), 400
        
        # 确定使用的AI提供商
        preferred_provider = None
        if provider_name:
            try:
                preferred_provider = AIProvider(provider_name)
            except ValueError:
                return jsonify({'error': f'不支持的AI提供商: {provider_name}'}), 400
        
        start_time = time.time()
        
        try:
            # 调用AI服务生成Flag
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            generated_flag = loop.run_until_complete(
                multi_ai_service.generate_flag(
                    challenge_description=challenge_description,
                    challenge_type=challenge_type,
                    preferred_provider=preferred_provider
                )
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 记录成功的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_flag_multi',
                request_payload={
                    'challenge_description': challenge_description,
                    'challenge_type': challenge_type,
                    'provider': provider_name
                },
                response_payload={'flag': generated_flag},
                duration_ms=duration_ms,
                status='success',
                provider=provider_name
            )
            
            return jsonify({
                'flag': generated_flag,
                'provider_used': provider_name or 'auto'
            }), 200
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = f"AI生成Flag失败: {str(e)}"
            
            # 记录失败的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_flag_multi',
                request_payload={
                    'challenge_description': challenge_description,
                    'challenge_type': challenge_type,
                    'provider': provider_name
                },
                response_payload=None,
                duration_ms=duration_ms,
                status='failed',
                error_message=error_message,
                provider=provider_name
            )
            
            return jsonify({'error': error_message}), 500
        
    except Exception as e:
        return jsonify({'error': f'AI生成Flag失败: {str(e)}'}), 500

@ai_multi_bp.route('/generate-text', methods=['POST'])
@jwt_required()
def generate_text_multi():
    """使用多AI模型生成文本"""
    try:
        user_id = get_jwt_identity()
        
        # 检查用户权限（出题人或管理员）
        if not (has_role(user_id, 'challenger') or has_role(user_id, 'admin')):
            return jsonify({'error': '没有使用AI生成文本的权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        prompt = data.get('prompt', '').strip()
        provider_name = data.get('provider', '').strip()
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
        
        # 确定使用的AI提供商
        preferred_provider = None
        if provider_name:
            try:
                preferred_provider = AIProvider(provider_name)
            except ValueError:
                return jsonify({'error': f'不支持的AI提供商: {provider_name}'}), 400
        
        start_time = time.time()
        
        try:
            # 调用AI服务生成文本
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            generated_text = loop.run_until_complete(
                multi_ai_service.generate_text(
                    prompt=prompt,
                    preferred_provider=preferred_provider,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 记录成功的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_text_multi',
                request_payload={
                    'prompt': prompt,
                    'provider': provider_name,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                },
                response_payload={'text': generated_text},
                duration_ms=duration_ms,
                status='success',
                provider=provider_name
            )
            
            return jsonify({
                'text': generated_text,
                'provider_used': provider_name or 'auto'
            }), 200
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = f"AI生成文本失败: {str(e)}"
            
            # 记录失败的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_text_multi',
                request_payload={
                    'prompt': prompt,
                    'provider': provider_name,
                    'max_tokens': max_tokens,
                    'temperature': temperature
                },
                response_payload=None,
                duration_ms=duration_ms,
                status='failed',
                error_message=error_message,
                provider=provider_name
            )
            
            return jsonify({'error': error_message}), 500
        
    except Exception as e:
        return jsonify({'error': f'AI生成文本失败: {str(e)}'}), 500

