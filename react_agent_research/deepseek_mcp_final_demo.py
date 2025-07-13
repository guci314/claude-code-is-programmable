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
DeepSeek ReAct Agent with MCP-style Tools - Final Working Demo
最终可工作的 MCP 风格工具演示
"""

import os
import sys
import math
from typing import Any
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

console = Console()

class ReactAgentCallback(BaseCallbackHandler):
    """回调处理器显示推理过程"""
    
    def __init__(self):
        self.step_count = 0
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """当智能体执行动作时"""
        self.step_count += 1
        console.print(f"\n[bold blue]🤔 步骤 {self.step_count}[/bold blue]")
        console.print(f"[green]工具:[/green] {action.tool}")
        console.print(f"[yellow]输入:[/yellow] {action.tool_input}")

def mcp_calculate(expression: str) -> str:
    """MCP 风格的计算工具
    
    模拟 MCP 协议的响应格式
    """
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
        dangerous = ['__', 'import', 'exec', 'eval', 'open', 'file', 'input']
        for d in dangerous:
            if d in expression.lower():
                return f"错误: 表达式包含危险操作: {d}"
        
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # MCP 风格的响应
        return f"{expression} = {result}"
        
    except Exception as e:
        return f"计算错误: {str(e)}"

def mcp_convert_units(input_str: str) -> str:
    """MCP 风格的单位转换工具
    
    输入格式: "100 meters to feet"
    """
    try:
        # 解析输入
        parts = input_str.split()
        if len(parts) < 4 or parts[2] != "to":
            return "错误: 请使用格式 '值 源单位 to 目标单位' (例如: '100 meters to feet')"
        
        value = float(parts[0])
        from_unit = parts[1].lower()
        to_unit = parts[3].lower()
        
        # 转换因子数据库
        conversions = {
            # 长度
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("meters", "inches"): 39.3701,
            ("inches", "meters"): 0.0254,
            ("km", "miles"): 0.621371,
            ("miles", "km"): 1.60934,
            ("cm", "inches"): 0.393701,
            ("inches", "cm"): 2.54,
            
            # 重量
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("grams", "ounces"): 0.035274,
            ("ounces", "grams"): 28.3495,
            ("kg", "lbs"): 2.20462,
            ("lbs", "kg"): 0.453592,
            
            # 体积
            ("liters", "gallons"): 0.264172,
            ("gallons", "liters"): 3.78541,
            ("ml", "oz"): 0.033814,
            ("oz", "ml"): 29.5735,
        }
        
        # 温度转换（特殊处理）
        if from_unit in ["celsius", "c"] and to_unit in ["fahrenheit", "f"]:
            result = value * 9/5 + 32
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit in ["fahrenheit", "f"] and to_unit in ["celsius", "c"]:
            result = (value - 32) * 5/9
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit in ["celsius", "c"] and to_unit in ["kelvin", "k"]:
            result = value + 273.15
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit in ["kelvin", "k"] and to_unit in ["celsius", "c"]:
            result = value - 273.15
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        
        # 常规转换
        key = (from_unit, to_unit)
        if key in conversions:
            result = value * conversions[key]
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        else:
            # 尝试反向转换
            reverse_key = (to_unit, from_unit)
            if reverse_key in conversions:
                result = value / conversions[reverse_key]
                return f"{value} {from_unit} = {result:.2f} {to_unit}"
            
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
        "完整可工作的 MCP 协议风格实现",
        border_style="cyan"
    ))
    
    try:
        # 创建 MCP 风格的工具
        console.print("\n[yellow]正在创建 MCP 风格工具...[/yellow]")
        
        tools = [
            Tool(
                name="mcp_calculate",
                description="执行数学计算。支持基本运算(+,-,*,/)和函数(sqrt,sin,cos,tan,log,exp等)。直接输入数学表达式。",
                func=mcp_calculate
            ),
            Tool(
                name="mcp_convert_units",
                description="单位转换工具。输入格式: '值 源单位 to 目标单位' (例如: '100 meters to feet')",
                func=mcp_convert_units
            )
        ]
        
        console.print(f"[green]✅ 创建了 {len(tools)} 个 MCP 风格工具[/green]")
        
        # 显示工具
        console.print("\n[bold yellow]MCP 工具列表：[/bold yellow]")
        for tool in tools:
            console.print(f"  📦 [cyan]{tool.name}[/cyan]")
            console.print(f"     {tool.description}")
        
        # 初始化 DeepSeek
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
        
        template = """你是一个使用 ReAct (推理和行动) 方法解决问题的 AI 助手。

可用的 MCP 工具：
{tools}

使用以下格式回答：

Question: 你需要回答的输入问题
Thought: 你应该思考要做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入（字符串格式）
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

开始！

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
        
        # 创建 React agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # 创建 agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=10,
            callbacks=[ReactAgentCallback()],
            handle_parsing_errors=True
        )
        
        console.print("[green]✅ DeepSeek ReAct Agent 初始化完成！[/green]")
        
        # 测试用例
        test_cases = [
            {
                "question": "计算 25 * 4 + 10",
                "category": "基本计算"
            },
            {
                "question": "计算 sqrt(144) + sin(pi/2) 的值",
                "category": "数学函数"
            },
            {
                "question": "将 100 米转换为英尺",
                "category": "长度转换"
            },
            {
                "question": "将 32 华氏度转换为摄氏度",
                "category": "温度转换"
            },
            {
                "question": "先计算 2^8，然后将结果千克转换为磅",
                "category": "组合任务"
            }
        ]
        
        # 运行测试
        for i, test in enumerate(test_cases, 1):
            console.print(f"\n[bold cyan]测试 {i}: {test['category']}[/bold cyan]")
            console.print(f"[yellow]❓ 问题: {test['question']}[/yellow]")
            console.print("-" * 60)
            
            try:
                result = agent_executor.invoke({"input": test["question"]})
                output = result.get("output", "无输出")
                console.print(f"\n[bold green]💡 最终答案: {output}[/bold green]")
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
            
            console.print("\n" + "="*80)
        
    except Exception as e:
        console.print(f"[red]❌ 程序错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
    
    console.print("\n[bold green]✨ MCP 风格工具演示完成！[/bold green]")
    console.print("[dim]这个演示展示了如何使用 LangChain 标准方法创建 MCP 风格的工具[/dim]")

if __name__ == "__main__":
    main()