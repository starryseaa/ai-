"""
工具基类 - 所有工具都继承这个类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """工具基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述，告诉大模型这个工具是干什么的"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """工具参数定义，JSON Schema格式"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行工具，返回结果字符串"""
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """转换为OpenAI Function Calling格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
