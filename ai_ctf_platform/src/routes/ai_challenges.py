from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import traceback

from src.models.challenge import Challenge, AIModel, GenerationHistory, db
from src.services.ai_generator import AIGeneratorService

ai_challenges_bp = Blueprint('ai_challenges', __name__)

@ai_challenges_bp.route('/ai-models', methods=['GET'])
@cross_origin()
def get_ai_models():
    """获取所有AI模型配置"""
    try:
        models = AIModel.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [model.to_dict() for model in models]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/ai-models', methods=['POST'])
@cross_origin()
def create_ai_model():
    """创建AI模型配置"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'provider', 'api_key', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # 检查名称是否已存在
        existing_model = AIModel.query.filter_by(name=data['name']).first()
        if existing_model:
            return jsonify({
                'success': False,
                'error': 'Model name already exists'
            }), 400
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if data.get('is_default', False):
            AIModel.query.update({'is_default': False})
        
        model = AIModel(
            name=data['name'],
            provider=data['provider'],
            api_key=data['api_key'],
            api_base=data.get('api_base'),
            model_name=data['model_name'],
            is_active=data.get('is_active', True),
            is_default=data.get('is_default', False),
            supports_misc=data.get('supports_misc', True),
            supports_crypto=data.get('supports_crypto', True),
            supports_web=data.get('supports_web', True)
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/ai-models/<int:model_id>', methods=['PUT'])
@cross_origin()
def update_ai_model(model_id):
    """更新AI模型配置"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 404
        
        data = request.get_json()
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if data.get('is_default', False) and not model.is_default:
            AIModel.query.filter(AIModel.id != model_id).update({'is_default': False})
        
        # 更新字段
        for field in ['name', 'provider', 'api_key', 'api_base', 'model_name', 
                     'is_active', 'is_default', 'supports_misc', 'supports_crypto', 'supports_web']:
            if field in data:
                setattr(model, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/ai-models/<int:model_id>', methods=['DELETE'])
@cross_origin()
def delete_ai_model(model_id):
    """删除AI模型配置"""
    try:
        model = AIModel.query.get(model_id)
        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 404
        
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/generate-challenge', methods=['POST'])
@cross_origin()
def generate_challenge():
    """生成AI挑战题目"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['category', 'difficulty']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # 获取AI模型ID
        ai_model_id = data.get('ai_model_id')
        if not ai_model_id:
            # 使用默认模型
            default_model = AIModel.query.filter_by(is_default=True, is_active=True).first()
            if not default_model:
                return jsonify({
                    'success': False,
                    'error': 'No default AI model configured'
                }), 400
            ai_model_id = default_model.id
        
        # 验证模型存在且激活
        ai_model = AIModel.query.get(ai_model_id)
        if not ai_model or not ai_model.is_active:
            return jsonify({
                'success': False,
                'error': 'Invalid or inactive AI model'
            }), 400
        
        # 创建AI生成器服务
        generator = AIGeneratorService()
        
        # 生成挑战
        result = generator.generate_challenge(
            category=data['category'],
            difficulty=data['difficulty'],
            ai_model_id=ai_model_id,
            theme=data.get('theme'),
            algorithm=data.get('algorithm'),
            vulnerability=data.get('vulnerability'),
            framework=data.get('framework'),
            hide_method=data.get('hide_method')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating challenge: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/challenges', methods=['GET'])
@cross_origin()
def get_challenges():
    """获取所有挑战题目"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        is_ai_generated = request.args.get('is_ai_generated')
        
        query = Challenge.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if is_ai_generated is not None:
            query = query.filter_by(is_ai_generated=is_ai_generated.lower() == 'true')
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'challenges': [challenge.to_dict() for challenge in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@cross_origin()
def get_challenge(challenge_id):
    """获取单个挑战题目详情"""
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({
                'success': False,
                'error': 'Challenge not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': challenge.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@cross_origin()
def delete_challenge(challenge_id):
    """删除挑战题目"""
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({
                'success': False,
                'error': 'Challenge not found'
            }), 404
        
        # 软删除
        challenge.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Challenge deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/generation-history', methods=['GET'])
@cross_origin()
def get_generation_history():
    """获取AI生成历史"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = GenerationHistory.query.order_by(
            GenerationHistory.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'history': [record.to_dict() for record in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_challenges_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """获取统计信息"""
    try:
        total_challenges = Challenge.query.filter_by(is_active=True).count()
        ai_generated_challenges = Challenge.query.filter_by(is_active=True, is_ai_generated=True).count()
        
        # 按类型统计
        category_stats = {}
        for category in ['misc', 'crypto', 'web']:
            category_stats[category] = Challenge.query.filter_by(
                is_active=True, 
                category=category
            ).count()
        
        # 按难度统计
        difficulty_stats = {}
        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_stats[difficulty] = Challenge.query.filter_by(
                is_active=True,
                difficulty=difficulty
            ).count()
        
        # 生成成功率
        total_generations = GenerationHistory.query.count()
        successful_generations = GenerationHistory.query.filter_by(success=True).count()
        success_rate = (successful_generations / total_generations * 100) if total_generations > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_challenges': total_challenges,
                'ai_generated_challenges': ai_generated_challenges,
                'manual_challenges': total_challenges - ai_generated_challenges,
                'category_stats': category_stats,
                'difficulty_stats': difficulty_stats,
                'generation_stats': {
                    'total_attempts': total_generations,
                    'successful_attempts': successful_generations,
                    'success_rate': round(success_rate, 2)
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

