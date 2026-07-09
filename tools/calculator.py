"""
计算器工具 - 执行数学运算
"""
import re
from tools.base_tool import BaseTool

class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "执行数学计算，包括加减乘除、括号运算等。当用户需要计算数字、数学问题时使用此工具。"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如：2+3*4、(10+5)/3"
                }
            },
            "required": ["expression"]
        }
    
    def execute(self, expression: str, **kwargs) -> str:
        try:
            # 安全过滤，只允许数字和运算符
            if not re.match(r'^[\d+\-*/().%\s]+$', expression):
                return "错误：表达式包含非法字符，只支持数字和+-*/().%运算"
            
            # 计算
            result = eval(expression, {"__builtins__": {}}, {})
            return f"计算结果: {expression} = {result}"
        except Exception as e:
            return f"计算失败: {str(e)}"
