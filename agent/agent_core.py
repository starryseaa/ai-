"""
AI Agent 智能体核心 - 支持Function Calling工具调用
"""
import json
from typing import List, Dict, Any, Generator
from llm.base_llm import BaseLLM
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger("agent")

class Agent:
    """AI智能体 - 带工具调用能力"""
    
    def __init__(self, llm: BaseLLM, tools: List[BaseTool], system_prompt: str = None):
        self.llm = llm
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt or "你是一个有能力调用工具的AI助手，当用户的问题需要使用工具时，请调用合适的工具来获取准确答案。"
    
    @property
    def tools_schema(self) -> List[Dict[str, Any]]:
        """获取所有工具的Function Calling格式定义"""
        return [tool.to_function_schema() for tool in self.tools]
    
    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """执行指定工具"""
        if tool_name not in self.tool_map:
            return f"错误：未知工具 {tool_name}"
        
        tool = self.tool_map[tool_name]
        logger.info(f"调用工具: {tool_name}, 参数: {tool_args}")
        
        try:
            result = tool.execute(**tool_args)
            return str(result)
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return f"工具执行出错: {str(e)}"
    
    def chat(self, user_message: str, history: List[Dict] = None, max_iterations: int = 3) -> Dict[str, Any]:
        """
        完整Agent对话，自动判断是否调用工具
        返回: {
            "final_answer": str,
            "tool_calls": [{"name": str, "args": dict, "result": str}],
            "thought_process": list
        }
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        tool_calls = []
        thought_process = []
        
        for iteration in range(max_iterations):
            # 调用大模型，传入工具定义
            response = self._chat_with_tools(messages)
            
            # 判断是否有工具调用
            if "tool_calls" in response and response["tool_calls"]:
                # 有工具调用
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                try:
                    tool_args = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}
                
                thought_process.append(f"第{iteration+1}轮：决定调用工具「{tool_name}」")
                
                # 保存assistant的tool_call消息
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": response["tool_calls"]
                })
                
                # 执行工具
                tool_result = self._execute_tool(tool_name, tool_args)
                tool_calls.append({
                    "name": tool_name,
                    "args": tool_args,
                    "result": tool_result
                })
                
                thought_process.append(f"工具执行结果: {tool_result[:100]}..." if len(tool_result) > 100 else f"工具执行结果: {tool_result}")
                
                # 把工具结果加回消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })
                
            else:
                # 没有工具调用，直接返回最终答案
                final_answer = response.get("content", "")
                thought_process.append("生成最终回答")
                return {
                    "final_answer": final_answer,
                    "tool_calls": tool_calls,
                    "thought_process": thought_process
                }
        
        # 达到最大迭代次数，生成最终回答
        final_response = self.llm.chat(messages)
        thought_process.append("达到最大迭代次数，生成最终回答")
        return {
            "final_answer": final_response,
            "tool_calls": tool_calls,
            "thought_process": thought_process
        }
    
    def chat_stream(self, user_message: str, history: List[Dict] = None, 
                    max_iterations: int = 3) -> Generator[Dict[str, Any], None, None]:
        """
        流式Agent对话 - yield每一步的状态
        yield类型:
        - {"type": "thinking", "content": "思考中..."}
        - {"type": "tool_call", "name": "...", "args": {...}}
        - {"type": "tool_result", "result": "..."}
        - {"type": "answer_chunk", "content": "..."}
        - {"type": "done", "final_answer": "...", "tool_calls": [...]}
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        tool_calls = []
        full_answer = ""
        
        for iteration in range(max_iterations):
            yield {"type": "thinking", "content": f"第{iteration+1}轮思考中..."}
            
            # 先判断是否需要调用工具（非流式）
            response = self._chat_with_tools(messages)
            
            if "tool_calls" in response and response["tool_calls"]:
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                try:
                    tool_args = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}
                
                yield {"type": "tool_call", "name": tool_name, "args": tool_args}
                
                # 保存assistant消息
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": response["tool_calls"]
                })
                
                # 执行工具
                tool_result = self._execute_tool(tool_name, tool_args)
                tool_calls.append({
                    "name": tool_name,
                    "args": tool_args,
                    "result": tool_result
                })
                
                yield {"type": "tool_result", "result": tool_result}
                
                # 工具结果加回消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })
                
            else:
                # 直接流式输出最终答案
                final_content = response.get("content", "")
                if final_content:
                    # 已经有内容了，分段yield
                    for i in range(0, len(final_content), 3):
                        yield {"type": "answer_chunk", "content": final_content[i:i+3]}
                    full_answer = final_content
                else:
                    # 走流式
                    for chunk in self.llm.chat_stream(messages):
                        full_answer += chunk
                        yield {"type": "answer_chunk", "content": chunk}
                
                yield {"type": "done", "final_answer": full_answer, "tool_calls": tool_calls}
                return
        
        # 最大迭代后流式输出
        yield {"type": "thinking", "content": "整理最终答案..."}
        for chunk in self.llm.chat_stream(messages):
            full_answer += chunk
            yield {"type": "answer_chunk", "content": chunk}
        
        yield {"type": "done", "final_answer": full_answer, "tool_calls": tool_calls}
    
    def _chat_with_tools(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用带工具的Chat Completion接口"""
        import requests
        
        url = f"{self.llm.base_url}/chat/completions"
        payload = {
            "model": self.llm.model,
            "messages": messages,
            "tools": self.tools_schema,
            "tool_choice": "auto",
            "stream": False
        }
        
        response = requests.post(url, headers=self.llm.headers, json=payload, timeout=self.llm.timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]
