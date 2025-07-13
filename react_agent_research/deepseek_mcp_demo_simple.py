#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "httpx[socks]>=0.24.0",
# ]
# ///

"""
DeepSeek ReAct Agent Demo with MCP-style Tools (Simplified)
模拟 MCP 工具接口的简化版 ReAct 智能体演示
"""

import os
import sys
import math
from typing import Any, Dict
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

console = Console()

class ReactAgentCallback(BaseCallbackHandler):
    """简化的回调处理器"""
    
    def __init__(self):
        self.step_count = 0
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """当智能体执行动作时调用"""
        self.step_count += 1
        console.print(f"\n[bold blue]🤔 步骤 {self.step_count}[/bold blue]")
        console.print(f"工具: {action.tool}")
        console.print(f"输入: {action.tool_input}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """当智能体完成时调用"""
        console.print(f"\n[bold green]✅ 完成推理[/bold green]")

# MCP 风格的工具函数
def mcp_calculate(expression: str) -> str:
    """MCP 计算器工具"""
    try:
        # 安全的计算环境
        safe_dict = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow, 'sqrt': math.sqrt,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10, 'exp': math.exp,
            'pi': math.pi, 'e': math.e
        }
        
        # 检查危险操作
        dangerous = ['__', 'import', 'exec', 'eval', 'open']
        for d in dangerous:
            if d in expression.lower():
                return f"错误: 表达式包含危险操作: {d}"
        
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"{expression} = {result}"
        
    except Exception as e:
        return f"计算错误: {str(e)}"

def mcp_convert_units(input_str: str) -> str:
    """MCP 单位转换工具"""
    try:
        # 解析输入格式: "100 meters to feet"
        parts = input_str.split()
        if len(parts) < 4 or parts[2] != "to":
            return "错误: 请使用格式 '值 源单位 to 目标单位' (例如: '100 meters to feet')"
        
        value = float(parts[0])
        from_unit = parts[1].lower()
        to_unit = parts[3].lower()
        
        # 转换因子
        conversions = {
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("miles", "km"): 1.60934,
            ("km", "miles"): 0.621371,
        }
        
        # 温度转换（特殊处理）
        if from_unit == "celsius" and to_unit == "fahrenheit":
            result = value * 9/5 + 32
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit == "fahrenheit" and to_unit == "celsius":
            result = (value - 32) * 5/9
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        
        # 常规转换
        key = (from_unit, to_unit)
        if key in conversions:
            result = value * conversions[key]
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        else:
            return f"错误: 不支持从 {from_unit} 到 {to_unit} 的转换"
            
    except ValueError:
        return "错误: 无效的数值"
    except Exception as e:
        return f"转换错误: {str(e)}"

def main():
    """主程序"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        console.print("请在 .env 文件中设置：DEEPSEEK_API_KEY=your-api-key")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct + MCP 风格工具演示[/bold cyan]\n"
        "使用模拟 MCP 协议的工具进行推理和计算",
        border_style="cyan"
    ))
    
    try:
        # 创建工具
        tools = [
            Tool(
                name="calculate",
                description="执行数学计算。支持基本运算和函数(sin, cos, sqrt等)。输入数学表达式。",
                func=mcp_calculate
            ),
            Tool(
                name="convert_units",
                description="单位转换。输入格式: '值 源单位 to 目标单位' (例如: '100 meters to feet')",
                func=mcp_convert_units
            )
        ]
        
        # 初始化 LLM
        console.print("\n[yellow]正在初始化 DeepSeek 模型...[/yellow]")
        llm = ChatOpenAI(
            temperature=0,
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            max_tokens=4096
        )
        
        # 创建 ReAct prompt
        tool_names = ", ".join([tool.name for tool in tools])
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
        template = """你是一个使用 ReAct 方法解决问题的助手。

可用工具：
{tools}

请使用以下格式：

Question: 输入问题
Thought: 思考要做什么
Action: 要使用的工具，必须是 [{tool_names}] 之一
Action Input: 工具的输入
Observation: 工具返回的结果
... (可以重复多次)
Thought: 我知道答案了
Final Answer: 最终答案

Question: {input}
Thought: {agent_scratchpad}"""
        
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": tool_descriptions,
                "tool_names": tool_names
            },
            template=template
        )
        
        # 创建 agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # 创建 executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            callbacks=[ReactAgentCallback()],
            handle_parsing_errors=True
        )
        
        console.print("[green]✅ 初始化完成！[/green]")
        console.print(f"[green]可用工具: {len(tools)} 个[/green]")
        
        # 显示工具
        console.print("\n[bold yellow]MCP 风格工具：[/bold yellow]")
        for tool in tools:
            console.print(f"  • {tool.name}: {tool.description}")
        
        # 测试问题
        questions = [
            "计算 25 * 4 + 10",
            "将 100 米转换为英尺",
            "计算 sqrt(144) + sin(pi/2)"
        ]
        
        for question in questions:
            console.print(f"\n[bold yellow]❓ 问题：{question}[/bold yellow]")
            console.print("-" * 50)
            
            try:
                result = agent_executor.invoke({"input": question})
                output = result.get("output", str(result))
                console.print(f"\n[bold green]💡 答案：{output}[/bold green]")
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
            
            console.print("\n" + "="*60 + "\n")
        
    except Exception as e:
        console.print(f"[red]❌ 错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    console.print("\n[bold green]👋 演示完成！[/bold green]")

if __name__ == "__main__":
    main()