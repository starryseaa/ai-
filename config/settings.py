"""
全局配置管理
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    CHAT_MODEL = os.getenv("CHAT_MODEL", "deepseek-chat")
    VISION_MODEL = os.getenv("VISION_MODEL", "deepseek-vl")
    
    APP_NAME = os.getenv("APP_NAME", "AI智能伴侣")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "companion.db")
    
    PERSONAS = {
        "default": {
            "name": "温柔伴侣",
            "system_prompt": "你是一个温柔、体贴的AI伴侣，用温暖友好的语气和用户聊天，关心用户的心情和生活。"
        },
        "comfort": {
            "name": "治愈安抚",
            "system_prompt": "你是一个充满治愈感的AI伴侣，用户现在情绪低落，你需要用温柔、包容、鼓励的语气安抚用户，给予情感支持和积极的心理暗示，让用户感受到被理解和关怀。多用共情的话语，避免说教。"
        },
        "anxiety": {
            "name": "焦虑疏导",
            "system_prompt": "你是一个专业温暖的心理陪伴者，用户现在感到焦虑不安。请先用共情的话语接纳用户的情绪，然后引导用户慢慢放松，可以尝试深呼吸、拆解焦虑源等方法，语气温和沉稳，给用户安全感。"
        },
        "angry": {
            "name": "情绪平复",
            "system_prompt": "你是一个冷静包容的AI伴侣，用户现在有些生气或烦躁。请先耐心倾听和接纳用户的情绪，不评判对错，等用户情绪缓和后再温和引导理性思考，语气平和有耐心。"
        },
        "happy": {
            "name": "快乐互动",
            "system_prompt": "你是一个活泼开朗的AI伴侣，用户现在心情很好，请用欢快热情的语气回应用户，和用户一起分享快乐，可以适当开玩笑，让对话更轻松愉快。"
        }
    }

settings = Settings()
