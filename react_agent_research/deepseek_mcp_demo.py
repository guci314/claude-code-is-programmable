#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "mcp>=1.0.0",
#   "httpx[socks]>=0.24.0",
# ]
# ///

"""
DeepSeek ReAct Agent Demo with MCP Tools
使用 MCP (Model Context Protocol) 工具的 ReAct 智能体演示
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler

console = Console()

class MCPToolWrapper:
    """Wrapper to integrate MCP tools with LangChain"""
    
    def __init__(self, tool_name: str, tool_description: str, mcp_client):
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.mcp_client = mcp_client
        self._loop = None
    
    def _get_or_create_loop(self):
        """Get or create event loop"""
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def call_tool(self, input_str: str) -> str:
        """Call MCP tool synchronously for LangChain compatibility"""
        # Parse input based on tool requirements
        if self.tool_name == "calculate":
            args = {"expression": input_str}
        elif self.tool_name == "convert_units":
            # Parse format: "value from_unit to_unit"
            parts = input_str.split()
            if len(parts) >= 4 and parts[2] == "to":
                args = {
                    "value": float(parts[0]),
                    "from_unit": parts[1],
                    "to_unit": parts[3]
                }
            else:
                return "Error: Invalid format. Use: 'value from_unit to to_unit' (e.g., '100 meters to feet')"
        else:
            args = {"input": input_str}
        
        # Create new event loop for sync execution
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._call_tool_async(args))
            return result
        finally:
            loop.close()
    
    async def _call_tool_async(self, args: Dict[str, Any]) -> str:
        """Async method to call MCP tool"""
        try:
            result = await self.mcp_client.call_tool(self.tool_name, args)
            if isinstance(result, dict) and "content" in result:
                # Extract text from MCP response format
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", str(content))
            return str(result)
        except Exception as e:
            return f"Error calling MCP tool: {str(e)}"

class SimpleMCPClient:
    """Simplified MCP client for demo purposes"""
    
    def __init__(self):
        self.tools = {}
        
    async def initialize(self):
        """Initialize with hardcoded calculator tools for demo"""
        # Simulating MCP calculator tools
        self.tools = {
            "calculate": {
                "name": "calculate",
                "description": "Perform mathematical calculations. Supports basic arithmetic (+, -, *, /, //, %, **), trigonometry (sin, cos, tan), and other math functions (sqrt, log, exp, abs).",
            },
            "convert_units": {
                "name": "convert_units",
                "description": "Convert between different units (length, weight, temperature). Format: 'value from_unit to to_unit'"
            }
        }
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool (simulated for demo)"""
        if tool_name == "calculate":
            return await self._calculate(args)
        elif tool_name == "convert_units":
            return await self._convert_units(args)
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}
    
    async def _calculate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform calculation"""
        import math
        expression = args.get("expression", "")
        
        try:
            # Safe evaluation environment
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': math.sqrt,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'log': math.log, 'log10': math.log10, 'exp': math.exp,
                'pi': math.pi, 'e': math.e
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
    
    async def _convert_units(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Convert units"""
        value = args.get("value", 0)
        from_unit = args.get("from_unit", "").lower()
        to_unit = args.get("to_unit", "").lower()
        
        conversions = {
            ("meters", "feet"): 3.28084,
            ("feet", "meters"): 0.3048,
            ("kg", "pounds"): 2.20462,
            ("pounds", "kg"): 0.453592,
            ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
            ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
        }
        
        key = (from_unit, to_unit)
        if key in conversions:
            conversion = conversions[key]
            if callable(conversion):
                result = conversion(value)
            else:
                result = value * conversion
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"{value} {from_unit} = {result:.4f} {to_unit}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Cannot convert from {from_unit} to {to_unit}"
                }]
            }

class ReactAgentCallback(BaseCallbackHandler):
    """Callback handler to display ReAct reasoning"""
    
    def __init__(self):
        self.step_count = 0
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        self.step_count += 1
        console.print(f"\n[bold blue]🤔 步骤 {self.step_count}: 智能体推理[/bold blue]")
        console.print(Panel(
            f"[green]工具:[/green] {action.tool}\n[green]输入:[/green] {action.tool_input}",
            title="🛠️ 行动",
            border_style="green"
        ))
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when agent finishes"""
        console.print(f"\n[bold green]✅ 智能体完成[/bold green]")

async def create_mcp_tools(mcp_client: SimpleMCPClient) -> List[Tool]:
    """Create LangChain tools from MCP client"""
    tools = []
    
    for tool_name, tool_info in mcp_client.tools.items():
        wrapper = MCPToolWrapper(
            tool_name=tool_name,
            tool_description=tool_info["description"],
            mcp_client=mcp_client
        )
        
        tool = Tool(
            name=tool_name,
            description=tool_info["description"],
            func=wrapper.call_tool
        )
        tools.append(tool)
    
    return tools

def create_react_prompt(tools: List[Tool]) -> PromptTemplate:
    """Create ReAct prompt template"""
    tool_names = ", ".join([tool.name for tool in tools])
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
    
    template = """你是一个使用 ReAct (推理 + 行动) 方法解决问题的智能助手。

你可以使用以下工具：
{tools}

使用以下格式回答：

Question: 你需要回答的输入问题
Thought: 你应该思考要做什么
Action: 要采取的行动，应该是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对原始输入问题的最终答案

开始！

Question: {input}
Thought: {agent_scratchpad}"""
    
    return PromptTemplate(
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tools": tool_descriptions,
            "tool_names": tool_names
        },
        template=template
    )

async def main():
    """运行 MCP 工具的 ReAct 智能体演示"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 DeepSeek API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        console.print("请在 .env 文件中设置：DEEPSEEK_API_KEY=your-api-key")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct + MCP 工具演示[/bold cyan]\n"
        "使用 MCP 协议集成的工具进行推理和计算",
        border_style="cyan"
    ))
    
    try:
        # 初始化 MCP 客户端
        console.print("\n[yellow]正在初始化 MCP 客户端...[/yellow]")
        mcp_client = SimpleMCPClient()
        await mcp_client.initialize()
        
        # 创建 MCP 工具
        tools = await create_mcp_tools(mcp_client)
        
        # 初始化 DeepSeek LLM
        llm = ChatOpenAI(
            temperature=0,
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            max_tokens=8192
        )
        
        # 创建 ReAct prompt
        prompt = create_react_prompt(tools)
        
        # 创建 ReAct agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
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
        
        console.print(f"[green]✅ 智能体初始化成功！[/green]")
        console.print(f"[green]模型: deepseek-chat[/green]")
        console.print(f"[green]MCP 工具: {len(tools)} 个可用[/green]")
        
        # 显示可用工具
        console.print("\n[bold yellow]可用的 MCP 工具：[/bold yellow]")
        for tool in tools:
            console.print(f"  • {tool.name}: {tool.description}")
        
        # 运行测试问题
        test_questions = [
            "25 * 4 + 10 等于多少？",
            "计算 sqrt(144) + sin(pi/2) 的值",
            "将 100 米转换为英尺",
            "将 32 华氏度转换为摄氏度"
        ]
        
        for question in test_questions:
            console.print(f"\n[bold yellow]❓ 问题：{question}[/bold yellow]")
            
            try:
                result = agent_executor.invoke({"input": question})
                console.print(f"\n[bold green]💡 答案：[/bold green]{result.get('output', str(result))}")
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
            
            console.print("\n" + "="*50 + "\n")
        
    except Exception as e:
        console.print(f"[red]❌ 演示失败: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    console.print("\n[bold green]👋 演示完成！[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())