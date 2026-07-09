"""
对话LLM - 普通文本对话
"""
from llm.base_llm import BaseLLM
from config.settings import settings

class ChatLLM(BaseLLM):
    def __init__(self):
        super().__init__(model=settings.CHAT_MODEL)
    
    def chat_with_system(self, user_message: str, system_prompt: str, history: list = None) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return self.chat(messages)
    
    def chat_stream_with_system(self, user_message: str, system_prompt: str, history: list = None):
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        yield from self.chat_stream(messages)
