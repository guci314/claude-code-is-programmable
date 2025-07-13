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
DeepSeek ReAct Agent with MCP-style Tools (LangChain Standard)
使用 LangChain 标准方法创建 MCP 风格的工具
"""

import os
import sys
import math
from typing import Any, Dict, List, Optional, Type
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain.tools import BaseTool, Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from pydantic import BaseModel, Field

console = Console()

# 使用 Pydantic 定义工具输入模式（MCP 风格）
class CalculateInput(BaseModel):
    """计算工具的输入模式"""
    expression: str = Field(description="要计算的数学表达式")

class ConvertUnitsInput(BaseModel):
    """单位转换工具的输入模式"""
    value: float = Field(description="要转换的数值")
    from_unit: str = Field(description="源单位")
    to_unit: str = Field(description="目标单位")

class MCPCalculateTool(BaseTool):
    """MCP 风格的计算工具"""
    name: str = "calculate"
    description: str = "执行数学计算。支持基本运算和函数(+,-,*,/,sqrt,sin,cos,log等)"
    args_schema: Type[BaseModel] = CalculateInput
    
    def _run(self, expression: str) -> str:
        """同步运行工具"""
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
            dangerous = ['__', 'import', 'exec', 'eval', 'open', 'file']
            for d in dangerous:
                if d in expression.lower():
                    return f"错误: 表达式包含危险操作: {d}"
            
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"{expression} = {result}"
            
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """异步运行（调用同步版本）"""
        return self._run(expression)

class MCPConvertUnitsTool(BaseTool):
    """MCP 风格的单位转换工具"""
    name: str = "convert_units"
    description: str = "单位转换（长度、重量、温度）"
    args_schema: Type[BaseModel] = ConvertUnitsInput
    
    def _run(self, value: float, from_unit: str, to_unit: str) -> str:
        """同步运行工具"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # 转换因子
        conversions = {
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("meters", "inches"): 39.3701,
            ("inches", "meters"): 0.0254,
            ("km", "miles"): 0.621371,
            ("miles", "km"): 1.60934,
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("grams", "ounces"): 0.035274,
            ("ounces", "grams"): 28.3495,
        }
        
        # 温度转换（特殊处理）
        if from_unit == "celsius" and to_unit == "fahrenheit":
            result = value * 9/5 + 32
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit == "fahrenheit" and to_unit == "celsius":
            result = (value - 32) * 5/9
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit == "celsius" and to_unit == "kelvin":
            result = value + 273.15
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        elif from_unit == "kelvin" and to_unit == "celsius":
            result = value - 273.15
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        
        # 常规转换
        key = (from_unit, to_unit)
        if key in conversions:
            result = value * conversions[key]
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        else:
            return f"错误: 不支持从 {from_unit} 到 {to_unit} 的转换"
    
    async def _arun(self, value: float, from_unit: str, to_unit: str) -> str:
        """异步运行（调用同步版本）"""
        return self._run(value, from_unit, to_unit)

class ReactAgentCallback(BaseCallbackHandler):
    """简化的回调处理器"""
    
    def __init__(self):
        self.step_count = 0
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """当智能体执行动作时"""
        self.step_count += 1
        console.print(f"\n[bold blue]🤔 步骤 {self.step_count}: 推理[/bold blue]")
        console.print(f"工具: [green]{action.tool}[/green]")
        console.print(f"输入: [yellow]{action.tool_input}[/yellow]")

def create_mcp_style_tools() -> List[BaseTool]:
    """创建 MCP 风格的工具集"""
    return [
        MCPCalculateTool(),
        MCPConvertUnitsTool()
    ]

def main():
    """主程序"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct + MCP 风格工具（LangChain 标准）[/bold cyan]\n"
        "使用 LangChain 标准 BaseTool 创建 MCP 风格的工具",
        border_style="cyan"
    ))
    
    try:
        # 创建 MCP 风格的工具
        console.print("\n[yellow]正在创建 MCP 风格工具...[/yellow]")
        tools = create_mcp_style_tools()
        
        # 显示工具信息
        console.print(f"[green]✅ 创建了 {len(tools)} 个工具[/green]\n")
        for tool in tools:
            console.print(f"📦 [bold]{tool.name}[/bold]")
            console.print(f"   描述: {tool.description}")
            if hasattr(tool, 'args_schema'):
                console.print(f"   输入模式: {tool.args_schema.__name__}")
        
        # 初始化 DeepSeek
        console.print("\n[yellow]正在初始化 DeepSeek 模型...[/yellow]")
        llm = ChatOpenAI(
            temperature=0,
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            max_tokens=4096
        )
        
        # 创建 ReAct prompt（中文版）
        tool_names = ", ".join([tool.name for tool in tools])
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" 
            for tool in tools
        ])
        
        template = """你是一个使用 ReAct (推理和行动) 方法解决问题的 AI 助手。

可用工具：
{tools}

使用以下格式：

Question: 你需要回答的输入问题
Thought: 你应该思考要做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入（JSON 格式）
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
        
        console.print("[green]✅ Agent 初始化完成！[/green]")
        
        # 测试用例
        test_cases = [
            {
                "question": "计算 25 * 4 + 10",
                "description": "基本数学计算"
            },
            {
                "question": "计算 sqrt(144) + sin(pi/2) + log10(1000)",
                "description": "复杂数学函数"
            },
            {
                "question": "将 100 米转换为英尺",
                "description": "长度单位转换"
            },
            {
                "question": "将 0 摄氏度转换为华氏度",
                "description": "温度单位转换"
            }
        ]
        
        # 运行测试
        for i, test in enumerate(test_cases, 1):
            console.print(f"\n[bold cyan]测试 {i}: {test['description']}[/bold cyan]")
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
    
    console.print("\n[bold green]✨ 演示完成！[/bold green]")

if __name__ == "__main__":
    main()