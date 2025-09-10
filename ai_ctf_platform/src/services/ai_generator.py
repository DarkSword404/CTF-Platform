import os
import json
import time
import random
import string
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import zipfile

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import docker
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from src.models.challenge import AIModel, Challenge, GenerationHistory, db


class AIGeneratorService:
    """AI题目生成服务"""
    
    def __init__(self):
        # 尝试连接Docker，如果失败则设为None
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Docker连接失败: {e}")
            self.docker_client = None
        self.temp_dir = tempfile.mkdtemp()
    
    def get_ai_client(self, ai_model: AIModel):
        """根据AI模型配置获取客户端"""
        if ai_model.provider.lower() == 'openai':
            return OpenAI(
                api_key=ai_model.api_key,
                base_url=ai_model.api_base if ai_model.api_base else None
            )
        elif ai_model.provider.lower() == 'deepseek':
            return OpenAI(
                api_key=ai_model.api_key,
                base_url="https://api.deepseek.com"
            )
        # 可以继续添加其他AI模型的支持
        else:
            raise ValueError(f"Unsupported AI provider: {ai_model.provider}")
    
    def generate_challenge(self, category: str, difficulty: str, 
                         ai_model_id: int, **kwargs) -> Dict:
        """生成挑战题目"""
        start_time = time.time()
        
        # 获取AI模型配置
        ai_model = AIModel.query.get(ai_model_id)
        if not ai_model or not ai_model.is_active:
            raise ValueError("Invalid or inactive AI model")
        
        # 检查模型是否支持该类型题目
        if not self._check_model_support(ai_model, category):
            raise ValueError(f"AI model {ai_model.name} does not support {category} challenges")
        
        try:
            # 根据类型生成题目
            if category.lower() == 'misc':
                result = self._generate_misc_challenge(ai_model, difficulty, **kwargs)
            elif category.lower() == 'crypto':
                result = self._generate_crypto_challenge(ai_model, difficulty, **kwargs)
            elif category.lower() == 'web':
                result = self._generate_web_challenge(ai_model, difficulty, **kwargs)
            else:
                raise ValueError(f"Unsupported challenge category: {category}")
            
            generation_time = time.time() - start_time
            
            # 记录生成历史
            self._record_generation_history(
                ai_model_id=ai_model_id,
                category=category,
                difficulty=difficulty,
                input_params=kwargs,
                success=True,
                generation_time=generation_time,
                challenge_id=result.get('challenge_id')
            )
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            
            # 记录失败历史
            self._record_generation_history(
                ai_model_id=ai_model_id,
                category=category,
                difficulty=difficulty,
                input_params=kwargs,
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
            
            raise e
    
    def _check_model_support(self, ai_model: AIModel, category: str) -> bool:
        """检查AI模型是否支持指定类型的题目"""
        category_lower = category.lower()
        if category_lower == 'misc':
            return ai_model.supports_misc
        elif category_lower == 'crypto':
            return ai_model.supports_crypto
        elif category_lower == 'web':
            return ai_model.supports_web
        return False
    
    def _generate_misc_challenge(self, ai_model: AIModel, difficulty: str, **kwargs) -> Dict:
        """生成Misc类型题目"""
        client = self.get_ai_client(ai_model)
        
        # 生成随机Flag
        flag = self._generate_flag()
        
        # 构建AI提示词
        prompt = self._build_misc_prompt(difficulty, flag, **kwargs)
        
        # 调用AI生成题目描述和隐藏方案
        response = client.chat.completions.create(
            model=ai_model.model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的CTF题目设计师，擅长设计Misc类型的题目。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # 解析AI响应
        challenge_data = self._parse_misc_response(ai_response, flag)
        
        # 生成附件
        files = self._create_misc_files(challenge_data, flag)
        
        # 创建挑战记录
        challenge = Challenge(
            name=challenge_data['name'],
            description=challenge_data['description'],
            category='misc',
            difficulty=difficulty,
            flag=flag,
            points=self._calculate_points(difficulty),
            is_ai_generated=True,
            ai_model_used=ai_model.name
        )
        
        challenge.set_files(files)
        challenge.set_generation_params({
            'ai_response': ai_response,
            'hide_method': challenge_data.get('hide_method'),
            **kwargs
        })
        
        db.session.add(challenge)
        db.session.commit()
        
        return {
            'challenge_id': challenge.id,
            'challenge': challenge.to_dict(),
            'files': files
        }
    
    def _generate_crypto_challenge(self, ai_model: AIModel, difficulty: str, **kwargs) -> Dict:
        """生成Crypto类型题目"""
        client = self.get_ai_client(ai_model)
        
        # 生成随机Flag
        flag = self._generate_flag()
        
        # 构建AI提示词
        prompt = self._build_crypto_prompt(difficulty, flag, **kwargs)
        
        # 调用AI生成题目
        response = client.chat.completions.create(
            model=ai_model.model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的CTF题目设计师，擅长设计密码学题目。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # 解析AI响应
        challenge_data = self._parse_crypto_response(ai_response, flag)
        
        # 生成加密文件
        files = self._create_crypto_files(challenge_data, flag)
        
        # 创建挑战记录
        challenge = Challenge(
            name=challenge_data['name'],
            description=challenge_data['description'],
            category='crypto',
            difficulty=difficulty,
            flag=flag,
            points=self._calculate_points(difficulty),
            is_ai_generated=True,
            ai_model_used=ai_model.name
        )
        
        challenge.set_files(files)
        challenge.set_generation_params({
            'ai_response': ai_response,
            'encryption_method': challenge_data.get('encryption_method'),
            **kwargs
        })
        
        db.session.add(challenge)
        db.session.commit()
        
        return {
            'challenge_id': challenge.id,
            'challenge': challenge.to_dict(),
            'files': files
        }
    
    def _generate_web_challenge(self, ai_model: AIModel, difficulty: str, **kwargs) -> Dict:
        """生成Web类型题目"""
        client = self.get_ai_client(ai_model)
        
        # 生成随机Flag
        flag = self._generate_flag()
        
        # 构建AI提示词
        prompt = self._build_web_prompt(difficulty, flag, **kwargs)
        
        # 调用AI生成Web应用代码
        response = client.chat.completions.create(
            model=ai_model.model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的CTF题目设计师，擅长设计Web安全题目。请生成完整的Web应用代码和Dockerfile。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # 解析AI响应并生成代码文件
        challenge_data = self._parse_web_response(ai_response, flag)
        
        # 构建Docker镜像
        docker_image, docker_config = self._build_web_docker(challenge_data, flag)
        
        # 创建挑战记录
        challenge = Challenge(
            name=challenge_data['name'],
            description=challenge_data['description'],
            category='web',
            difficulty=difficulty,
            flag=flag,
            points=self._calculate_points(difficulty),
            is_ai_generated=True,
            ai_model_used=ai_model.name,
            docker_image=docker_image
        )
        
        challenge.set_docker_config(docker_config)
        challenge.set_generation_params({
            'ai_response': ai_response,
            'vulnerability_type': challenge_data.get('vulnerability_type'),
            **kwargs
        })
        
        db.session.add(challenge)
        db.session.commit()
        
        return {
            'challenge_id': challenge.id,
            'challenge': challenge.to_dict(),
            'docker_image': docker_image,
            'docker_config': docker_config
        }
    
    def _generate_flag(self) -> str:
        """生成随机Flag"""
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"flag{{{random_part}}}"
    
    def _calculate_points(self, difficulty: str) -> int:
        """根据难度计算分数"""
        points_map = {
            'easy': 100,
            'medium': 200,
            'hard': 300
        }
        return points_map.get(difficulty.lower(), 100)
    
    def _build_misc_prompt(self, difficulty: str, flag: str, **kwargs) -> str:
        """构建Misc题目的AI提示词"""
        theme = kwargs.get('theme', '随机主题')
        hide_method = kwargs.get('hide_method', '自动选择')
        
        prompt = f"""
请设计一个{difficulty}难度的Misc类型CTF题目。

要求：
1. 题目主题：{theme}
2. Flag：{flag}
3. 隐藏方式：{hide_method}（如果是自动选择，请选择合适的隐藏方式）
4. 难度：{difficulty}

请按以下JSON格式返回：
{{
    "name": "题目名称",
    "description": "题目描述，包含背景故事和解题提示",
    "hide_method": "具体的隐藏方式（如LSB隐写、文件头隐藏、压缩包密码等）",
    "file_type": "需要生成的文件类型（如image、audio、document等）",
    "hints": ["提示1", "提示2"],
    "solution": "解题步骤说明"
}}
"""
        return prompt
    
    def _build_crypto_prompt(self, difficulty: str, flag: str, **kwargs) -> str:
        """构建Crypto题目的AI提示词"""
        algorithm = kwargs.get('algorithm', '自动选择')
        theme = kwargs.get('theme', '随机主题')
        
        prompt = f"""
请设计一个{difficulty}难度的密码学CTF题目。

要求：
1. 题目主题：{theme}
2. Flag：{flag}
3. 加密算法：{algorithm}（如果是自动选择，请选择合适的算法）
4. 难度：{difficulty}

请按以下JSON格式返回：
{{
    "name": "题目名称",
    "description": "题目描述，包含背景故事和加密信息",
    "encryption_method": "具体的加密方法（如RSA、AES、Caesar等）",
    "key_info": "密钥相关信息或提示",
    "ciphertext": "加密后的密文",
    "hints": ["提示1", "提示2"],
    "solution": "解题步骤说明"
}}
"""
        return prompt
    
    def _build_web_prompt(self, difficulty: str, flag: str, **kwargs) -> str:
        """构建Web题目的AI提示词"""
        vulnerability = kwargs.get('vulnerability', '自动选择')
        framework = kwargs.get('framework', 'Flask')
        
        prompt = f"""
请设计一个{difficulty}难度的Web安全CTF题目。

要求：
1. 漏洞类型：{vulnerability}（如果是自动选择，请选择合适的漏洞类型）
2. 框架：{framework}
3. Flag：{flag}
4. 难度：{difficulty}

请生成完整的Web应用代码，包括：
1. 主应用文件
2. HTML模板
3. Dockerfile
4. 漏洞利用点

请按以下格式返回：
```json
{{
    "name": "题目名称",
    "description": "题目描述和背景",
    "vulnerability_type": "漏洞类型",
    "flag_location": "Flag存放位置",
    "solution": "解题步骤"
}}
```

```python
# app.py - 主应用文件
[Python代码]
```

```html
<!-- templates/index.html -->
[HTML代码]
```

```dockerfile
# Dockerfile
[Dockerfile内容]
```
"""
        return prompt
    
    def _parse_misc_response(self, response: str, flag: str) -> Dict:
        """解析Misc题目的AI响应"""
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # 如果解析失败，返回默认结构
        return {
            'name': 'AI生成的Misc题目',
            'description': response,
            'hide_method': 'LSB隐写',
            'file_type': 'image',
            'hints': ['仔细观察文件'],
            'solution': '使用相应工具提取隐藏信息'
        }
    
    def _parse_crypto_response(self, response: str, flag: str) -> Dict:
        """解析Crypto题目的AI响应"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            'name': 'AI生成的密码学题目',
            'description': response,
            'encryption_method': 'Caesar',
            'key_info': '密钥为13',
            'ciphertext': self._caesar_encrypt(flag, 13),
            'hints': ['这是一个简单的替换密码'],
            'solution': '使用Caesar解密'
        }
    
    def _parse_web_response(self, response: str, flag: str) -> Dict:
        """解析Web题目的AI响应"""
        # 提取JSON部分
        challenge_data = {
            'name': 'AI生成的Web题目',
            'description': '这是一个Web安全题目',
            'vulnerability_type': 'SQL注入',
            'flag_location': '数据库中',
            'solution': '利用SQL注入获取Flag'
        }
        
        # 提取代码部分
        code_sections = {
            'app.py': '',
            'index.html': '',
            'Dockerfile': ''
        }
        
        # 简单的代码提取逻辑
        lines = response.split('\n')
        current_section = None
        current_code = []
        
        for line in lines:
            if '```python' in line or '# app.py' in line:
                current_section = 'app.py'
                current_code = []
            elif '```html' in line or '<!-- templates/index.html -->' in line:
                current_section = 'index.html'
                current_code = []
            elif '```dockerfile' in line or '# Dockerfile' in line:
                current_section = 'Dockerfile'
                current_code = []
            elif '```' in line and current_section:
                if current_section in code_sections:
                    code_sections[current_section] = '\n'.join(current_code)
                current_section = None
            elif current_section:
                current_code.append(line)
        
        challenge_data['code_sections'] = code_sections
        return challenge_data
    
    def _create_misc_files(self, challenge_data: Dict, flag: str) -> List[str]:
        """创建Misc题目的附件"""
        files = []
        hide_method = challenge_data.get('hide_method', 'LSB隐写')
        file_type = challenge_data.get('file_type', 'image')
        
        if file_type == 'image' and 'LSB' in hide_method:
            # 创建带有LSB隐写的图片
            image_path = self._create_lsb_image(flag)
            files.append(image_path)
        
        return files
    
    def _create_crypto_files(self, challenge_data: Dict, flag: str) -> List[str]:
        """创建Crypto题目的文件"""
        files = []
        encryption_method = challenge_data.get('encryption_method', 'Caesar')
        
        # 创建密文文件
        cipher_file = os.path.join(self.temp_dir, 'cipher.txt')
        with open(cipher_file, 'w') as f:
            if encryption_method == 'Caesar':
                ciphertext = self._caesar_encrypt(flag, 13)
            else:
                ciphertext = challenge_data.get('ciphertext', flag)
            f.write(ciphertext)
        
        files.append(cipher_file)
        return files
    
    def _create_lsb_image(self, flag: str) -> str:
        """创建带有LSB隐写的图片"""
        # 创建一个简单的图片
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "Find the hidden message!", fill='black')
        
        # 简单的LSB隐写实现
        pixels = list(img.getdata())
        flag_binary = ''.join(format(ord(c), '08b') for c in flag) + '1111111111111110'  # 结束标记
        
        for i, bit in enumerate(flag_binary):
            if i < len(pixels):
                r, g, b = pixels[i]
                # 修改红色通道的最低位
                r = (r & 0xFE) | int(bit)
                pixels[i] = (r, g, b)
        
        img.putdata(pixels)
        
        image_path = os.path.join(self.temp_dir, 'hidden_message.png')
        img.save(image_path)
        return image_path
    
    def _caesar_encrypt(self, text: str, shift: int) -> str:
        """Caesar密码加密"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    def _build_web_docker(self, challenge_data: Dict, flag: str) -> Tuple[str, Dict]:
        """构建Web题目的Docker镜像"""
        # 创建临时目录
        build_dir = os.path.join(self.temp_dir, f'web_challenge_{int(time.time())}')
        os.makedirs(build_dir, exist_ok=True)
        
        # 生成默认的Web应用代码（如果AI没有生成）
        code_sections = challenge_data.get('code_sections', {})
        
        if not code_sections.get('app.py'):
            code_sections['app.py'] = self._generate_default_web_app(flag)
        
        if not code_sections.get('Dockerfile'):
            code_sections['Dockerfile'] = self._generate_default_dockerfile()
        
        # 写入文件
        for filename, content in code_sections.items():
            if content:
                file_path = os.path.join(build_dir, filename)
                if filename == 'index.html':
                    # 创建templates目录
                    templates_dir = os.path.join(build_dir, 'templates')
                    os.makedirs(templates_dir, exist_ok=True)
                    file_path = os.path.join(templates_dir, 'index.html')
                
                with open(file_path, 'w') as f:
                    f.write(content)
        
        # 构建Docker镜像
        image_name = f"ctf_web_challenge_{int(time.time())}"
        
        try:
            image, logs = self.docker_client.images.build(
                path=build_dir,
                tag=image_name,
                rm=True
            )
            
            docker_config = {
                'image': image_name,
                'ports': {'5000/tcp': None},  # 随机端口
                'environment': {'FLAG': flag},
                'mem_limit': '256m',
                'cpu_quota': 50000
            }
            
            return image_name, docker_config
            
        except Exception as e:
            raise Exception(f"Failed to build Docker image: {str(e)}")
    
    def _generate_default_web_app(self, flag: str) -> str:
        """生成默认的Web应用代码"""
        return f'''
from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flags (
            id INTEGER PRIMARY KEY,
            flag TEXT
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO flags (id, flag) VALUES (1, ?)", ("{flag}",))
    cursor.execute("INSERT OR REPLACE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string("""
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>Login System</h1>
        <form method="post" action="/login">
            <p>Username: <input type="text" name="username"></p>
            <p>Password: <input type="password" name="password"></p>
            <p><input type="submit" value="Login"></p>
        </form>
    </body>
    </html>
    """)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # 存在SQL注入漏洞
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{{username}}' AND password='{{password}}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return "Login successful! But you need to find the flag..."
    else:
        return "Login failed!"

@app.route('/flag')
def get_flag():
    # 只有管理员才能访问
    return "Access denied! Only admin can view flags."

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
    
    def _generate_default_dockerfile(self) -> str:
        """生成默认的Dockerfile"""
        return '''
FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install flask

EXPOSE 5000

CMD ["python", "app.py"]
'''
    
    def _record_generation_history(self, ai_model_id: int, category: str, 
                                 difficulty: str, input_params: Dict,
                                 success: bool, generation_time: float,
                                 challenge_id: Optional[int] = None,
                                 error_message: Optional[str] = None):
        """记录生成历史"""
        history = GenerationHistory(
            challenge_id=challenge_id,
            ai_model_id=ai_model_id,
            category=category,
            difficulty=difficulty,
            input_params=json.dumps(input_params),
            success=success,
            error_message=error_message,
            generation_time=generation_time
        )
        
        db.session.add(history)
        db.session.commit()

