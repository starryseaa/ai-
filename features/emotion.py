"""
情感识别与情绪适配模块
"""
from llm.chat_llm import ChatLLM
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("emotion")

EMOTION_MAP = {
    "sad": "comfort",
    "depressed": "comfort",
    "down": "comfort",
    "anxious": "anxiety",
    "worried": "anxiety",
    "nervous": "anxiety",
    "angry": "angry",
    "frustrated": "angry",
    "annoyed": "angry",
    "happy": "happy",
    "excited": "happy",
    "joyful": "happy",
    "normal": "default",
    "calm": "default",
    "neutral": "default"
}

class EmotionDetector:
    def __init__(self):
        self.llm = ChatLLM()
    
    def detect_emotion(self, user_message: str, recent_history: list = None) -> dict:
        prompt = f"""
请分析以下用户输入的情绪状态，从以下选项中选择最匹配的情绪标签：
可选标签: sad(难过低落), anxious(焦虑担忧), angry(生气烦躁), happy(开心兴奋), normal(平静正常)

用户输入: "{user_message}"

请输出JSON格式，包含以下字段:
- emotion: 情绪标签字符串
- confidence: 置信度0-1的浮点数
- reason: 简短判断理由，不超过20字
"""
        
        try:
            result = self.llm.chat_json([{"role": "user", "content": prompt}])
            emotion = result.get("emotion", "normal")
            persona_key = EMOTION_MAP.get(emotion, "default")
            result["persona_key"] = persona_key
            logger.info(f"情绪识别结果: {emotion} → 人设: {persona_key}")
            return result
        except Exception as e:
            logger.error(f"情绪识别失败: {e}")
            return {"emotion": "normal", "confidence": 0.5, "persona_key": "default"}
    
    def get_persona_prompt(self, persona_key: str) -> str:
        persona = settings.PERSONAS.get(persona_key, settings.PERSONAS["default"])
        return persona["system_prompt"]
    
    def get_persona_name(self, persona_key: str) -> str:
        persona = settings.PERSONAS.get(persona_key, settings.PERSONAS["default"])
        return persona["name"]
