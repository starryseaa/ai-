"""
多模态视觉LLM - 图文问答
"""
import base64
import json
import requests
from io import BytesIO
from PIL import Image
from llm.base_llm import BaseLLM
from config.settings import settings
from utils.decorators import retry

class VisionLLM(BaseLLM):
    def __init__(self):
        super().__init__(model=settings.VISION_MODEL)
    
    @staticmethod
    def encode_image(image_file) -> str:
        if isinstance(image_file, Image.Image):
            buffered = BytesIO()
            image_file.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
        elif isinstance(image_file, str):
            with open(image_file, "rb") as f:
                img_bytes = f.read()
        else:
            img_bytes = image_file.read()
        
        return base64.b64encode(img_bytes).decode("utf-8")
    
    @retry(max_times=3, delay=1.0)
    def vision_chat(self, prompt: str, image_file, detail: str = "auto") -> str:
        base64_image = self.encode_image(image_file)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ]
        
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        response = requests.post(url, headers=self.headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def vision_chat_stream(self, prompt: str, image_file, detail: str = "auto"):
        base64_image = self.encode_image(image_file)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ]
        
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        with requests.post(url, headers=self.headers, json=payload, stream=True, timeout=120) as resp:
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
