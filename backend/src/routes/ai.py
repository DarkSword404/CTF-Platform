from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, AICallLog, UserRole
import openai
import json
import time
import os

ai_bp = Blueprint('ai', __name__)

def has_role(user_id, role_name):
    """检查用户是否有指定角色"""
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    roles = []
    for user_role in user_roles:
        roles.append(user_role.role.name)
    return role_name in roles

def log_ai_call(user_id, call_type, request_payload, response_payload, duration_ms, status, error_message=None):
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

@ai_bp.route('/ai/generate-challenge', methods=['POST'])
@jwt_required()
def generate_challenge():
    """AI生成题目内容"""
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
        
        if not prompt:
            return jsonify({'error': '题目描述不能为空'}), 400
        
        if challenge_type not in ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc']:
            return jsonify({'error': '题目类型无效'}), 400
        
        if difficulty not in ['Easy', 'Medium', 'Hard']:
            return jsonify({'error': '题目难度无效'}), 400
        
        start_time = time.time()
        
        # 构建AI提示词
        system_prompt = f"""你是一个专业的CTF题目设计师。请根据用户的需求，生成一个{difficulty}难度的{challenge_type}类型CTF题目。

请按照以下JSON格式返回题目内容：
{{
    "title": "题目标题",
    "description": "详细的题目描述，包括背景故事和解题提示",
    "flag": "flag{{生成的flag内容}}",
    "hints": ["提示1", "提示2"],
    "attachments_suggested": [
        {{"name": "文件名", "type": "文件类型", "description": "文件描述"}}
    ],
    "container_config_suggested": {{
        "ports": {{"80": "8080"}},
        "environment": {{"ENV_VAR": "value"}},
        "dockerfile_content": "Dockerfile内容（如果需要）"
    }}
}}

要求：
1. 题目要有一定的技术深度和教育意义
2. Flag格式为flag{{内容}}
3. 描述要详细，包含足够的信息让参赛者理解题目
4. 提示要有层次，从简单到复杂
5. 如果需要容器环境，提供合理的配置建议"""

        user_prompt = f"请生成一个{challenge_type}类型的{difficulty}难度CTF题目：{prompt}"
        
        try:
            # 调用OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 解析AI响应
            ai_content = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                # 提取JSON部分（去除可能的markdown格式）
                if '```json' in ai_content:
                    json_start = ai_content.find('```json') + 7
                    json_end = ai_content.find('```', json_start)
                    ai_content = ai_content[json_start:json_end].strip()
                elif '```' in ai_content:
                    json_start = ai_content.find('```') + 3
                    json_end = ai_content.find('```', json_start)
                    ai_content = ai_content[json_start:json_end].strip()
                
                generated_content = json.loads(ai_content)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回原始内容
                generated_content = {
                    "title": f"{challenge_type} Challenge",
                    "description": ai_content,
                    "flag": "flag{ai_generated_flag}",
                    "hints": ["请仔细分析题目描述"],
                    "attachments_suggested": [],
                    "container_config_suggested": {}
                }
            
            # 记录成功的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_challenge',
                request_payload={
                    'prompt': prompt,
                    'challenge_type': challenge_type,
                    'difficulty': difficulty
                },
                response_payload=generated_content,
                duration_ms=duration_ms,
                status='success'
            )
            
            return jsonify({
                'message': 'AI题目生成成功',
                'generated_content': generated_content
            }), 200
            
        except openai.OpenAIError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = f"OpenAI API调用失败: {str(e)}"
            
            # 记录失败的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_challenge',
                request_payload={
                    'prompt': prompt,
                    'challenge_type': challenge_type,
                    'difficulty': difficulty
                },
                response_payload=None,
                duration_ms=duration_ms,
                status='failed',
                error_message=error_message
            )
            
            return jsonify({'error': error_message}), 500
        
    except Exception as e:
        return jsonify({'error': f'AI生成题目失败: {str(e)}'}), 500

@ai_bp.route('/ai/generate-flag', methods=['POST'])
@jwt_required()
def generate_flag():
    """AI生成Flag"""
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
        flag_format = data.get('flag_format', 'flag{content}')
        
        if not challenge_description:
            return jsonify({'error': '题目描述不能为空'}), 400
        
        start_time = time.time()
        
        # 构建AI提示词
        system_prompt = f"""你是一个专业的CTF题目设计师。请根据题目描述生成一个合适的Flag。

要求：
1. Flag应该与题目内容相关
2. Flag格式：{flag_format}
3. Flag内容要有意义，不要是随机字符串
4. 考虑题目的技术特点和解题思路
5. 只返回Flag，不要其他内容"""

        user_prompt = f"题目类型：{challenge_type}\n题目描述：{challenge_description}\n\n请生成一个合适的Flag："
        
        try:
            # 调用OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 获取生成的Flag
            generated_flag = response.choices[0].message.content.strip()
            
            # 确保Flag格式正确
            if not generated_flag.startswith('flag{'):
                if '{' in generated_flag and '}' in generated_flag:
                    # 提取{}中的内容
                    content = generated_flag[generated_flag.find('{')+1:generated_flag.rfind('}')]
                    generated_flag = f"flag{{{content}}}"
                else:
                    generated_flag = f"flag{{{generated_flag}}}"
            
            # 记录成功的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_flag',
                request_payload={
                    'challenge_description': challenge_description,
                    'challenge_type': challenge_type,
                    'flag_format': flag_format
                },
                response_payload={'flag': generated_flag},
                duration_ms=duration_ms,
                status='success'
            )
            
            return jsonify({
                'flag': generated_flag
            }), 200
            
        except openai.OpenAIError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_message = f"OpenAI API调用失败: {str(e)}"
            
            # 记录失败的AI调用
            log_ai_call(
                user_id=user_id,
                call_type='generate_flag',
                request_payload={
                    'challenge_description': challenge_description,
                    'challenge_type': challenge_type,
                    'flag_format': flag_format
                },
                response_payload=None,
                duration_ms=duration_ms,
                status='failed',
                error_message=error_message
            )
            
            return jsonify({'error': error_message}), 500
        
    except Exception as e:
        return jsonify({'error': f'AI生成Flag失败: {str(e)}'}), 500

@ai_bp.route('/ai/call-logs', methods=['GET'])
@jwt_required()
def get_ai_call_logs():
    """获取AI调用日志"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        call_type = request.args.get('call_type')
        
        # 限制分页大小
        page_size = min(page_size, 100)
        
        # 构建查询
        query = AICallLog.query.filter_by(user_id=user_id)
        
        if call_type:
            query = query.filter(AICallLog.call_type == call_type)
        
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
            # 不返回敏感的请求和响应内容给普通用户
            if not has_role(user_id, 'admin'):
                log_data.pop('request_payload', None)
                log_data.pop('response_payload', None)
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

