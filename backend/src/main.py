import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db, Role
from src.models.ai_config import AIProviderConfig, AIUsageStats
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.challenge import challenge_bp
from src.routes.ai import ai_bp
from src.routes.ai_multi import ai_multi_bp  # 新增多AI路由
from src.routes.ai_admin import ai_admin_bp  # AI管理路由
from src.routes.health import health_bp  # 健康检查路由
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# 启用CORS
CORS(app, origins="*")

# 初始化JWT
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(challenge_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(ai_multi_bp, url_prefix='/api/ai-multi')  # 多AI路由
app.register_blueprint(ai_admin_bp, url_prefix='/api/ai-admin')  # AI管理路由
app.register_blueprint(health_bp, url_prefix='/api')  # 健康检查路由
app.register_blueprint(admin_bp, url_prefix='/api')

# 数据库配置
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://ctf_user:ctf_password@postgres:5432/ctf_platform")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_database():
    """初始化数据库和默认数据"""
    with app.app_context():
        db.create_all()
        
        # 创建默认角色
        roles_data = [
            {'name': 'user', 'description': '普通用户'},
            {'name': 'challenger', 'description': '出题人'},
            {'name': 'admin', 'description': '管理员'}
        ]
        
        for role_data in roles_data:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(name=role_data['name'], description=role_data['description'])
                db.session.add(role)
        
        db.session.commit()
        print("数据库初始化完成")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
