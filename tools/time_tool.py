"""
时间工具 - 查询当前时间、日期
"""
from datetime import datetime
from tools.base_tool import BaseTool

class TimeTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_current_time"
    
    @property
    def description(self) -> str:
        return "获取当前的日期和时间。当用户问现在几点、今天几号、星期几等时间相关问题时使用。"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "可选，时间格式，默认返回完整时间",
                    "enum": ["full", "date", "time", "weekday"]
                }
            },
            "required": []
        }
    
    def execute(self, format: str = "full", **kwargs) -> str:
        now = datetime.now()
        
        if format == "date":
            return f"今天是: {now.strftime('%Y年%m月%d日')}"
        elif format == "time":
            return f"现在时间是: {now.strftime('%H:%M:%S')}"
        elif format == "weekday":
            weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
            return f"今天是: {weekdays[now.weekday()]}"
        else:
            weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
            return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')} {weekdays[now.weekday()]}"
