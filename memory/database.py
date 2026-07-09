"""
SQLite数据库管理
"""
import sqlite3
import os
from datetime import date
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("database")

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()
    
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE DEFAULT 'default',
            first_chat_date TEXT,
            total_chat_days INTEGER DEFAULT 0,
            total_messages INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            last_chat_date TEXT,
            user_tags TEXT DEFAULT '[]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            session_id TEXT,
            role TEXT,
            content TEXT,
            emotion TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            title TEXT,
            remind_time TEXT,
            repeat_type TEXT DEFAULT 'once',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("SELECT id FROM user_profile WHERE user_id = 'default'")
        if not cursor.fetchone():
            today = date.today().isoformat()
            cursor.execute("""
            INSERT INTO user_profile (user_id, first_chat_date, last_chat_date)
            VALUES ('default', ?, ?)
            """, (today, today))
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def get_user_profile(self, user_id: str = "default") -> dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}
    
    def update_chat_stats(self, user_id: str = "default") -> dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
        profile = dict(cursor.fetchone())
        
        new_messages = profile["total_messages"] + 1
        
        new_days = profile["total_chat_days"]
        if profile["last_chat_date"] != today:
            new_days += 1
        
        new_exp = profile["exp"] + 10
        new_level = profile["level"]
        while new_exp >= new_level * 100:
            new_exp -= new_level * 100
            new_level += 1
        
        cursor.execute("""
        UPDATE user_profile 
        SET total_messages = ?, total_chat_days = ?, exp = ?, level = ?, last_chat_date = ?
        WHERE user_id = ?
        """, (new_messages, new_days, new_exp, new_level, today, user_id))
        
        conn.commit()
        
        cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
        updated = dict(cursor.fetchone())
        conn.close()
        
        logger.info(f"用户统计更新: Lv.{updated['level']}, 经验{updated['exp']}")
        return updated
    
    def save_message(self, role: str, content: str, session_id: str = "default", 
                     emotion: str = None, user_id: str = "default"):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO chat_history (user_id, session_id, role, content, emotion)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_id, role, content, emotion))
        conn.commit()
        conn.close()
    
    def get_recent_history(self, session_id: str = "default", limit: int = 20, 
                           user_id: str = "default") -> list:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT role, content FROM chat_history 
        WHERE session_id = ? AND user_id = ?
        ORDER BY id DESC LIMIT ?
        """, (session_id, user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        history = [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
        return history
    
    def get_all_history(self, session_id: str = "default", user_id: str = "default") -> list:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT role, content, created_at FROM chat_history 
        WHERE session_id = ? AND user_id = ?
        ORDER BY id ASC
        """, (session_id, user_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def clear_history(self, session_id: str = "default", user_id: str = "default"):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM chat_history WHERE session_id = ? AND user_id = ?
        """, (session_id, user_id))
        conn.commit()
        conn.close()
    
    def add_reminder(self, title: str, remind_time: str, repeat_type: str = "once",
                     user_id: str = "default") -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO reminders (user_id, title, remind_time, repeat_type)
        VALUES (?, ?, ?, ?)
        """, (user_id, title, remind_time, repeat_type))
        conn.commit()
        reminder_id = cursor.lastrowid
        conn.close()
        logger.info(f"新增提醒: {title} - {remind_time}")
        return reminder_id
    
    def get_active_reminders(self, user_id: str = "default") -> list:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM reminders WHERE user_id = ? AND is_active = 1
        ORDER BY remind_time ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_reminder(self, reminder_id: int, user_id: str = "default"):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM reminders WHERE id = ? AND user_id = ?
        """, (reminder_id, user_id))
        conn.commit()
        conn.close()
    
    def toggle_reminder(self, reminder_id: int, is_active: bool, user_id: str = "default"):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE reminders SET is_active = ? WHERE id = ? AND user_id = ?
        """, (1 if is_active else 0, reminder_id, user_id))
        conn.commit()
        conn.close()

db = Database()
