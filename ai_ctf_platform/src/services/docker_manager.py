"""
Docker容器管理服务
"""
import docker
import os
import json
import time
import random
import string
from typing import Dict, Optional

class DockerManager:
    """Docker容器管理器"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Docker连接失败: {e}")
            self.client = None
    
    def build_challenge_image(self, challenge_id: int, dockerfile_content: str, 
                            app_code: str, requirements: str = None) -> str:
        """构建题目Docker镜像"""
        if not self.client:
            raise Exception("Docker客户端未连接")
        
        # 创建临时构建目录
        build_dir = f"/tmp/challenge_{challenge_id}"
        os.makedirs(build_dir, exist_ok=True)
        
        try:
            # 写入Dockerfile
            with open(os.path.join(build_dir, 'Dockerfile'), 'w') as f:
                f.write(dockerfile_content)
            
            # 写入应用代码
            with open(os.path.join(build_dir, 'app.py'), 'w') as f:
                f.write(app_code)
            
            # 写入requirements.txt（如果有）
            if requirements:
                with open(os.path.join(build_dir, 'requirements.txt'), 'w') as f:
                    f.write(requirements)
            
            # 构建镜像
            image_tag = f"ctf-challenge-{challenge_id}:latest"
            image, logs = self.client.images.build(
                path=build_dir,
                tag=image_tag,
                rm=True
            )
            
            return image_tag
            
        except Exception as e:
            raise Exception(f"构建镜像失败: {str(e)}")
        finally:
            # 清理临时文件
            import shutil
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
    
    def start_challenge_container(self, challenge_id: int, user_id: int, 
                                image_tag: str, port: int = None) -> Dict:
        """启动题目容器"""
        if not self.client:
            return {
                'success': False,
                'error': 'Docker服务不可用',
                'container_url': None
            }
        
        try:
            # 生成容器名称
            container_name = f"ctf-{challenge_id}-{user_id}-{''.join(random.choices(string.ascii_lowercase, k=6))}"
            
            # 分配端口
            if not port:
                port = random.randint(30000, 40000)
            
            # 启动容器
            container = self.client.containers.run(
                image_tag,
                name=container_name,
                ports={'5000/tcp': port},
                detach=True,
                remove=True,  # 容器停止后自动删除
                mem_limit='256m',  # 限制内存
                cpu_quota=50000,   # 限制CPU
                network_mode='bridge'
            )
            
            # 等待容器启动
            time.sleep(2)
            
            # 检查容器状态
            container.reload()
            if container.status != 'running':
                return {
                    'success': False,
                    'error': '容器启动失败',
                    'container_url': None
                }
            
            return {
                'success': True,
                'container_id': container.id,
                'container_name': container_name,
                'container_url': f'http://localhost:{port}',
                'port': port,
                'message': '容器启动成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'启动容器失败: {str(e)}',
                'container_url': None
            }
    
    def stop_challenge_container(self, container_name: str) -> Dict:
        """停止题目容器"""
        if not self.client:
            return {
                'success': False,
                'error': 'Docker服务不可用'
            }
        
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            
            return {
                'success': True,
                'message': '容器已停止'
            }
            
        except docker.errors.NotFound:
            return {
                'success': False,
                'error': '容器不存在'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'停止容器失败: {str(e)}'
            }
    
    def list_user_containers(self, user_id: int) -> list:
        """列出用户的容器"""
        if not self.client:
            return []
        
        try:
            containers = self.client.containers.list(
                filters={'name': f'ctf-*-{user_id}-*'}
            )
            
            result = []
            for container in containers:
                result.append({
                    'id': container.id,
                    'name': container.name,
                    'status': container.status,
                    'ports': container.ports
                })
            
            return result
            
        except Exception as e:
            print(f"列出容器失败: {e}")
            return []
    
    def cleanup_expired_containers(self, max_age_hours: int = 2):
        """清理过期容器"""
        if not self.client:
            return
        
        try:
            containers = self.client.containers.list(
                filters={'name': 'ctf-*'}
            )
            
            current_time = time.time()
            
            for container in containers:
                # 获取容器创建时间
                created_time = container.attrs['Created']
                created_timestamp = time.mktime(time.strptime(created_time[:19], '%Y-%m-%dT%H:%M:%S'))
                
                # 如果容器运行时间超过限制，则停止
                if (current_time - created_timestamp) > (max_age_hours * 3600):
                    try:
                        container.stop()
                        print(f"已停止过期容器: {container.name}")
                    except Exception as e:
                        print(f"停止容器失败: {e}")
                        
        except Exception as e:
            print(f"清理容器失败: {e}")

# 全局Docker管理器实例
docker_manager = DockerManager()

