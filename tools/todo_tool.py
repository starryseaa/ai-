"""
待办事项工具 - 管理待办清单
"""
import json
import os
from tools.base_tool import BaseTool
from config.settings import settings

TODO_FILE = os.path.join(os.path.dirname(settings.DB_PATH), "todos.json")

class TodoTool(BaseTool):
    @property
    def name(self) -> str:
        return "todo_manager"
    
    @property
    def description(self) -> str:
        return "管理待办事项清单，可以添加待办、查看所有待办、标记完成、删除待办。用户提到要做什么事、记一下、待办清单时使用。"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["add", "list", "done", "delete"]
                },
                "content": {
                    "type": "string",
                    "description": "待办内容，action为add时必填"
                },
                "index": {
                    "type": "integer",
                    "description": "待办序号，action为done或delete时必填，从1开始"
                }
            },
            "required": ["action"]
        }
    
    def _load_todos(self) -> list:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_todos(self, todos: list):
        os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
    
    def execute(self, action: str, content: str = None, index: int = None, **kwargs) -> str:
        todos = self._load_todos()
        
        if action == "add":
            if not content:
                return "错误：请提供待办内容"
            todos.append({"content": content, "done": False})
            self._save_todos(todos)
            return f"已添加待办: {content}\n当前共 {len(todos)} 条待办"
        
        elif action == "list":
            if not todos:
                return "暂无待办事项"
            result = "📋 待办清单:\n"
            for i, todo in enumerate(todos, 1):
                status = "✅" if todo["done"] else "⬜"
                result += f"{i}. {status} {todo['content']}\n"
            return result
        
        elif action == "done":
            if index is None or index < 1 or index > len(todos):
                return "错误：请提供正确的待办序号"
            todos[index - 1]["done"] = True
            self._save_todos(todos)
            return f"已标记完成: {todos[index - 1]['content']}"
        
        elif action == "delete":
            if index is None or index < 1 or index > len(todos):
                return "错误：请提供正确的待办序号"
            deleted = todos.pop(index - 1)
            self._save_todos(todos)
            return f"已删除待办: {deleted['content']}"
        
        else:
            return f"不支持的操作: {action}"
