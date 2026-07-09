"""
智能体工厂 - 创建预设Agent
"""
from llm.chat_llm import ChatLLM
from agent.agent_core import Agent
from tools.calculator import CalculatorTool
from tools.time_tool import TimeTool
from tools.todo_tool import TodoTool
from config.settings import settings

def create_companion_agent(persona_prompt: str = None) -> Agent:
    """
    创建伴侣智能体 - 带工具调用能力
    """
    llm = ChatLLM()
    
    tools = [
        CalculatorTool(),
        TimeTool(),
        TodoTool(),
    ]
    
    system_prompt = persona_prompt or settings.PERSONAS["default"]["system_prompt"]
    system_prompt += "\n\n你可以使用工具来帮助用户：计算器用于数学计算，时间工具用于查询当前时间日期，待办工具用于管理用户的待办清单。"
    
    return Agent(llm=llm, tools=tools, system_prompt=system_prompt)
