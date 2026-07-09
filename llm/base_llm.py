"""
DeepSeek 大模型封装基类
"""
import json
import requests
from config.settings import settings
from utils.decorators import retry
from utils.logger import get_logger

logger = get_logger("llm_base")

class BaseLLM:
    def __init__(self, model: str = None):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = model or settings.CHAT_MODEL
        self.timeout = 60
    
    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(max_times=3, delay=1.0)
    def chat(self, messages: list, temperature: float = 0.7, **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            **kwargs
        }
        
        response = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def chat_stream(self, messages: list, temperature: float = 0.7, **kwargs):
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        with requests.post(url, headers=self.headers, json=payload, stream=True, timeout=self.timeout) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue
    
    def chat_json(self, messages: list, temperature: float = 0.1) -> dict:
        messages = messages.copy()
        messages.append({
            "role": "user",
            "content": "请严格按照JSON格式输出，不要输出任何额外文字，只输出JSON对象。"
        })
        
        result = self.chat(messages, temperature=temperature, response_format={"type": "json_object"})
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error(f"JSON解析失败: {result}")
            return {}
    
    def __call__(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)
