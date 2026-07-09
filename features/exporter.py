"""
对话导出模块 - Markdown / TXT 格式
"""
from io import BytesIO
from datetime import datetime
from memory.database import db
from utils.logger import get_logger

logger = get_logger("exporter")

class ChatExporter:
    @staticmethod
    def export_markdown(session_id: str = "default", title: str = None) -> BytesIO:
        history = db.get_all_history(session_id)
        
        if not title:
            today = datetime.now().strftime("%Y-%m-%d")
            title = f"AI伴侣对话记录 - {today}"
        
        md_content = f"# {title}\n\n"
        md_content += f"> 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += "---\n\n"
        
        for msg in history:
            role_name = "🧑 用户" if msg["role"] == "user" else "🤖 AI伴侣"
            time_str = msg.get("created_at", "")
            md_content += f"### {role_name}\n\n"
            if time_str:
                md_content += f"*[{time_str}]*\n\n"
            md_content += f"{msg['content']}\n\n"
        
        bio = BytesIO()
        bio.write(md_content.encode("utf-8"))
        bio.seek(0)
        
        logger.info(f"Markdown导出完成，共{len(history)}条消息")
        return bio
    
    @staticmethod
    def export_txt(session_id: str = "default", title: str = None) -> BytesIO:
        history = db.get_all_history(session_id)
        
        if not title:
            today = datetime.now().strftime("%Y-%m-%d")
            title = f"AI伴侣对话记录 - {today}"
        
        txt_content = f"{'='*50}\n"
        txt_content += f"{title}\n"
        txt_content += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += f"{'='*50}\n\n"
        
        for msg in history:
            role_name = "用户" if msg["role"] == "user" else "AI伴侣"
            time_str = msg.get("created_at", "")
            txt_content += f"[{time_str}] {role_name}:\n"
            txt_content += f"{msg['content']}\n\n"
        
        bio = BytesIO()
        bio.write(txt_content.encode("utf-8"))
        bio.seek(0)
        
        logger.info(f"TXT导出完成，共{len(history)}条消息")
        return bio
    
    @staticmethod
    def get_filename(fmt: str = "markdown") -> str:
        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if fmt == "markdown" else "txt"
        return f"chat_history_{today}.{ext}"
