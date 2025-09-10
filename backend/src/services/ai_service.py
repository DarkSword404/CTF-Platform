"""
多AI模型集成服务
支持OpenAI、Anthropic、Google Gemini、本地模型等
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum

class AIProvider(Enum):
    """AI服务提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    DEEPSEEK = "deepseek"
    ERNIE_BOT = "ernie_bot"
    TONGYI_QIANWEN = "tongyi_qianwen"
    ZHIPU_AI = "zhipu_ai"

class AIModel:
    """AI模型配置类"""
    def __init__(self, provider: AIProvider, model_name: str, api_key: str = None, 
                 api_base: str = None, max_tokens: int = 2000, temperature: float = 0.7):
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature

class BaseAIProvider(ABC):
    """AI服务提供商基类"""
    
    def __init__(self, model: AIModel):
        self.model = model
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        pass
    
    @abstractmethod
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=model.api_key or os.getenv("OPENAI_API_KEY"),
                base_url=model.api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.client.chat.completions.create(
                model=self.model.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.model.max_tokens),
                temperature=kwargs.get("temperature", self.model.temperature)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            # 尝试解析JSON响应
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            # 如果不是JSON格式，返回基本结构
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_ai}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        # 确保flag格式正确
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag
class DeepSeekProvider(BaseAIProvider):
    """DeepSeek服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=model.api_key or os.getenv("DEEPSEEK_API_KEY"),
                base_url=model.api_base or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
            )
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.client.chat.completions.create(
                model=self.model.model_name or "deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.model.max_tokens),
                temperature=kwargs.get("temperature", self.model.temperature)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_deepseek}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag

class ErnieBotProvider(BaseAIProvider):
    """百度文心一言服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            import qianfan
            self.client = qianfan.ChatCompletion()
        except ImportError:
            raise ImportError("请安装qianfan库: pip install qianfan")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            # 设置环境变量
            if self.model.api_key:
                os.environ["QIANFAN_AK"] = self.model.api_key
            
            response = self.client.do(
                model=self.model.model_name or "ERNIE-Bot-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.model.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.model.max_tokens)
            )
            return response["result"]
        except Exception as e:
            raise Exception(f"文心一言API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_ernie}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag

class TongyiQianwenProvider(BaseAIProvider):
    """阿里云通义千问服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            import dashscope
            self.dashscope = dashscope
            if model.api_key:
                dashscope.api_key = model.api_key
        except ImportError:
            raise ImportError("请安装dashscope库: pip install dashscope")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.dashscope.Generation.call(
                model=self.model.model_name or "qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.model.temperature),
                max_tokens=kwargs.get("max_tokens", self.model.max_tokens),
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise Exception(f"API调用失败: {response.message}")
        except Exception as e:
            raise Exception(f"通义千问API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_qianwen}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag

class ZhipuAIProvider(BaseAIProvider):
    """智谱AI服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=model.api_key or os.getenv("ZHIPU_AI_API_KEY"))
        except ImportError:
            raise ImportError("请安装zhipuai库: pip install zhipuai")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = self.client.chat.completions.create(
                model=self.model.model_name or "glm-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.model.temperature),
                max_tokens=kwargs.get("max_tokens", self.model.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_zhipu}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag

class GoogleGeminiProvider(BaseAIProvider):
    """Google Gemini服务提供商"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        try:
            import google.generativeai as genai
            if model.api_key:
                genai.configure(api_key=model.api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("请安装google-generativeai库: pip install google-generativeai")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            model = self.genai.GenerativeModel(self.model.model_name or "gemini-pro")
            response = model.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", self.model.temperature),
                    max_output_tokens=kwargs.get("max_tokens", self.model.max_tokens)
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Google Gemini API调用失败: {str(e)}")
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str) -> Dict[str, Any]:
        """生成CTF题目"""
        prompt = f"""
        请生成一个CTF题目，要求如下：
        - 分类: {category}
        - 难度: {difficulty}
        - 具体要求: {requirements}
        
        请以JSON格式返回，包含以下字段：
        - title: 题目标题
        - description: 题目描述
        - flag: 题目flag
        - hints: 提示列表
        - solution: 解题思路
        - dockerfile: 如果需要容器环境，提供Dockerfile内容
        - attachments: 如果需要附件，描述附件内容
        
        确保题目具有教育意义且符合CTF竞赛标准。
        """
        
        response = await self.generate_text(prompt)
        try:
            challenge_data = json.loads(response)
            return challenge_data
        except json.JSONDecodeError:
            return {
                "title": f"{category} Challenge",
                "description": response,
                "flag": "flag{generated_by_gemini}",
                "hints": [],
                "solution": "请参考题目描述",
                "dockerfile": None,
                "attachments": []
            }
    
    async def generate_flag(self, challenge_description: str, challenge_type: str) -> str:
        """生成Flag"""
        prompt = f"""
        根据以下CTF题目描述生成一个合适的flag：
        题目类型: {challenge_type}
        题目描述: {challenge_description}
        
        请生成一个符合CTF标准的flag，格式为 flag{{内容}}，内容应该与题目相关且有意义。
        只返回flag，不要其他内容。
        """
        
        flag = await self.generate_text(prompt, max_tokens=100)
        if not flag.startswith("flag{") or not flag.endswith("}"):
            flag = f"flag{{{flag.strip()}}}"
        return flag

class MultiAIService:
    """多AI模型服务管理器"""
    
    def __init__(self):
        self.providers = {}
        self.load_providers()
    
    def load_providers(self):
        """加载AI服务提供商"""
        # 定义提供商配置
        provider_configs = {
            AIProvider.OPENAI: {
                "class": OpenAIProvider,
                "model": AIModel(
                    provider=AIProvider.OPENAI,
                    model_name="gpt-3.5-turbo",
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE")
                )
            },
            AIProvider.DEEPSEEK: {
                "class": DeepSeekProvider,
                "model": AIModel(
                    provider=AIProvider.DEEPSEEK,
                    model_name="deepseek-chat",
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    api_base=os.getenv("DEEPSEEK_API_BASE")
                )
            },
            AIProvider.ERNIE_BOT: {
                "class": ErnieBotProvider,
                "model": AIModel(
                    provider=AIProvider.ERNIE_BOT,
                    model_name="ERNIE-Bot-turbo",
                    api_key=os.getenv("ERNIE_BOT_AK")
                )
            },
            AIProvider.TONGYI_QIANWEN: {
                "class": TongyiQianwenProvider,
                "model": AIModel(
                    provider=AIProvider.TONGYI_QIANWEN,
                    model_name="qwen-turbo",
                    api_key=os.getenv("TONGYI_QIANWEN_API_KEY")
                )
            },
            AIProvider.ZHIPU_AI: {
                "class": ZhipuAIProvider,
                "model": AIModel(
                    provider=AIProvider.ZHIPU_AI,
                    model_name="glm-4",
                    api_key=os.getenv("ZHIPU_AI_API_KEY")
                )
            },
            AIProvider.GOOGLE: {
                "class": GoogleGeminiProvider,
                "model": AIModel(
                    provider=AIProvider.GOOGLE,
                    model_name="gemini-pro",
                    api_key=os.getenv("GOOGLE_API_KEY")
                )
            }
        }
        
        # 初始化可用的提供商
        for provider, config in provider_configs.items():
            try:
                if config["model"].api_key:  # 只有配置了API密钥的才初始化
                    self.providers[provider] = config["class"](config["model"])
            except Exception as e:
                print(f"初始化{provider.value}提供商失败: {e}")
    
    def get_available_providers(self) -> List[AIProvider]:
        """获取可用的AI提供商列表"""
        return list(self.providers.keys())
    
    def get_provider(self, provider: AIProvider) -> Optional[BaseAIProvider]:
        """获取指定的AI提供商"""
        return self.providers.get(provider)
    
    async def generate_challenge(self, category: str, difficulty: str, requirements: str, 
                               preferred_provider: AIProvider = None) -> Dict[str, Any]:
        """生成CTF题目"""
        # 确定使用的提供商
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
        elif self.providers:
            # 使用第一个可用的提供商
            provider = list(self.providers.values())[0]
        else:
            raise Exception("没有可用的AI提供商")
        
        return await provider.generate_challenge(category, difficulty, requirements)
    
    async def generate_flag(self, challenge_description: str, challenge_type: str,
                          preferred_provider: AIProvider = None) -> str:
        """生成Flag"""
        # 确定使用的提供商
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
        elif self.providers:
            # 使用第一个可用的提供商
            provider = list(self.providers.values())[0]
        else:
            raise Exception("没有可用的AI提供商")
        
        return await provider.generate_flag(challenge_description, challenge_type)
    
    async def generate_text(self, prompt: str, preferred_provider: AIProvider = None, **kwargs) -> str:
        """生成文本"""
        # 确定使用的提供商
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
        elif self.providers:
            # 使用第一个可用的提供商
            provider = list(self.providers.values())[0]
        else:
            raise Exception("没有可用的AI提供商")
        
        return await provider.generate_text(prompt, **kwargs)

# 全局AI服务实例
multi_ai_service = MultiAIService()


