"""
定时提醒模块 - 基于APScheduler
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from memory.database import db
from utils.logger import get_logger

logger = get_logger("reminder")

class ReminderManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.scheduler.start()
        self.callbacks = []
        self._load_active_reminders()
        logger.info("定时提醒管理器启动")
    
    def on_remind(self, callback):
        self.callbacks.append(callback)
    
    def _trigger_reminder(self, title: str, reminder_id: int):
        logger.info(f"提醒触发: {title}")
        for callback in self.callbacks:
            try:
                callback(title, reminder_id)
            except Exception as e:
                logger.error(f"提醒回调执行失败: {e}")
    
    def _load_active_reminders(self):
        reminders = db.get_active_reminders()
        for r in reminders:
            self._schedule_reminder(r)
    
    def _schedule_reminder(self, reminder: dict):
        try:
            remind_time = datetime.strptime(reminder["remind_time"], "%Y-%m-%d %H:%M")
            
            if remind_time < datetime.now() and reminder["repeat_type"] == "once":
                return
            
            job_id = f"reminder_{reminder['id']}"
            
            if reminder["repeat_type"] == "once":
                trigger = DateTrigger(run_date=remind_time)
            elif reminder["repeat_type"] == "daily":
                trigger = CronTrigger(
                    hour=remind_time.hour,
                    minute=remind_time.minute
                )
            else:
                trigger = DateTrigger(run_date=remind_time)
            
            self.scheduler.add_job(
                self._trigger_reminder,
                trigger=trigger,
                args=[reminder["title"], reminder["id"]],
                id=job_id,
                replace_existing=True
            )
            logger.info(f"已调度提醒: {reminder['title']} - {reminder['remind_time']}")
        except Exception as e:
            logger.error(f"调度提醒失败: {e}")
    
    def add_reminder(self, title: str, remind_time_str: str, repeat_type: str = "once") -> int:
        reminder_id = db.add_reminder(title, remind_time_str, repeat_type)
        reminder = {
            "id": reminder_id,
            "title": title,
            "remind_time": remind_time_str,
            "repeat_type": repeat_type
        }
        self._schedule_reminder(reminder)
        return reminder_id
    
    def delete_reminder(self, reminder_id: int):
        job_id = f"reminder_{reminder_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        db.delete_reminder(reminder_id)
        logger.info(f"删除提醒: {reminder_id}")
    
    def get_all_reminders(self) -> list:
        return db.get_active_reminders()
    
    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("提醒调度器已关闭")

reminder_manager = ReminderManager()
