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
DeepSeek ReAct Agent Demo with MCP-style Tools (Synchronous)
完全同步的 MCP 风格工具演示，避免异步问题
"""

import os
import sys
import math
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

console = Console()

class MCPCalculatorServer:
    """模拟 MCP 计算器服务器（同步版本）"""
    
    def __init__(self):
        self.name = "calculator"
        self.version = "1.0.0"
        self.tools = {
            "calculate": {
                "description": "Perform mathematical calculations",
                "handler": self._calculate
            },
            "convert_units": {
                "description": "Convert between different units",
                "handler": self._convert_units
            }
        }
    
    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具并返回 MCP 格式的响应"""
        if tool_name in self.tools:
            return self.tools[tool_name]["handler"](args)
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {tool_name}"
                }]
            }
    
    def _calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行数学计算"""
        expression = args.get("expression", "")
        
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
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Error: Expression contains dangerous operation: {d}"
                        }]
                    }
            
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"{expression} = {result}"
                }]
            }
            
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Calculation error: {str(e)}"
                }]
            }
    
    def _convert_units(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """单位转换"""
        value = args.get("value", 0)
        from_unit = args.get("from_unit", "").lower()
        to_unit = args.get("to_unit", "").lower()
        
        conversions = {
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("miles", "km"): 1.60934,
            ("km", "miles"): 0.621371,
        }
        
        # 温度转换
        if from_unit == "celsius" and to_unit == "fahrenheit":
            result = value * 9/5 + 32
            return {
                "content": [{
                    "type": "text",
                    "text": f"{value} {from_unit} = {result:.2f} {to_unit}"
                }]
            }
        elif from_unit == "fahrenheit" and to_unit == "celsius":
            result = (value - 32) * 5/9
            return {
                "content": [{
                    "type": "text",
                    "text": f"{value} {from_unit} = {result:.2f} {to_unit}"
                }]
            }
        
        key = (from_unit, to_unit)
        if key in conversions:
            result = value * conversions[key]
            return {
                "content": [{
                    "type": "text",
                    "text": f"{value} {from_unit} = {result:.2f} {to_unit}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Cannot convert from {from_unit} to {to_unit}"
                }]
            }

class MCPToolWrapper:
    """MCP 工具的 LangChain 包装器（同步版本）"""
    
    def __init__(self, tool_name: str, mcp_server: MCPCalculatorServer):
        self.tool_name = tool_name
        self.mcp_server = mcp_server
    
    def call(self, input_str: str) -> str:
        """调用 MCP 工具"""
        # 解析输入
        if self.tool_name == "calculate":
            args = {"expression": input_str}
        elif self.tool_name == "convert_units":
            # 解析格式: "100 meters to feet"
            parts = input_str.split()
            if len(parts) >= 4 and parts[2] == "to":
                args = {
                    "value": float(parts[0]),
                    "from_unit": parts[1],
                    "to_unit": parts[3]
                }
            else:
                return "Error: Use format '100 meters to feet'"
        else:
            args = {"input": input_str}
        
        # 调用 MCP 服务器
        result = self.mcp_server.call_tool(self.tool_name, args)
        
        # 提取文本响应
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                return content[0].get("text", str(content))
        
        return str(result)

def main():
    """主程序"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct + MCP 工具演示（同步版）[/bold cyan]\n"
        "使用同步 MCP 风格的工具进行推理和计算",
        border_style="cyan"
    ))
    
    try:
        # 初始化 MCP 服务器
        console.print("\n[yellow]正在初始化 MCP 服务器...[/yellow]")
        mcp_server = MCPCalculatorServer()
        
        # 创建 LangChain 工具
        tools = [
            Tool(
                name="calculate",
                description="执行数学计算。输入数学表达式。",
                func=MCPToolWrapper("calculate", mcp_server).call
            ),
            Tool(
                name="convert_units",
                description="单位转换。格式: '100 meters to feet'",
                func=MCPToolWrapper("convert_units", mcp_server).call
            )
        ]
        
        # 初始化 DeepSeek
        llm = ChatOpenAI(
            temperature=0,
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            max_tokens=4096
        )
        
        # 创建 ReAct prompt
        tool_names = ", ".join([tool.name for tool in tools])
        tool_descs = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
        template = """你是一个使用 ReAct 方法的助手。

工具：
{tools}

格式：
Question: 输入问题
Thought: 思考
Action: 工具名称 [{tool_names}]
Action Input: 输入
Observation: 结果
... (可重复)
Thought: 我知道答案了
Final Answer: 答案

Question: {input}
Thought: {agent_scratchpad}"""
        
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            partial_variables={"tools": tool_descs, "tool_names": tool_names},
            template=template
        )
        
        # 创建 agent
        agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
        
        # 创建 executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        console.print("[green]✅ 初始化完成！[/green]")
        console.print(f"[green]MCP 服务器: {mcp_server.name} v{mcp_server.version}[/green]")
        console.print(f"[green]可用工具: {len(tools)} 个[/green]\n")
        
        # 测试问题
        questions = [
            "计算 25 * 4 + 10",
            "将 100 米转换为英尺",
            "计算 sqrt(144) + sin(pi/2)"
        ]
        
        for i, question in enumerate(questions, 1):
            console.print(f"[bold yellow]测试 {i}: {question}[/bold yellow]")
            console.print("-" * 50)
            
            try:
                result = agent_executor.invoke({"input": question})
                output = result.get("output", "")
                console.print(f"\n[bold green]结果: {output}[/bold green]")
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
            
            console.print("=" * 60 + "\n")
        
    except Exception as e:
        console.print(f"[red]❌ 错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
    
    console.print("[bold green]✨ 演示完成！[/bold green]")

if __name__ == "__main__":
    main()