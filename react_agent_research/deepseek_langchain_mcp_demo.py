#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "langgraph>=0.2.0",
#   "langchain-mcp-adapters>=0.1.0",
#   "mcp>=1.0.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "httpx[socks]>=0.24.0",
# ]
# ///

"""
DeepSeek ReAct Agent Demo with LangChain MCP Adapters
使用 LangChain 官方 MCP 适配器的 ReAct 智能体演示
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from typing import Any

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
        console.print(f"[green]输入:[/green] {action.tool_input}")
        return None
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """当智能体完成时"""
        console.print(f"\n[bold green]✅ 推理完成[/bold green]")
        return None

async def demo_single_server():
    """演示单个 MCP 服务器"""
    console.print("\n[bold cyan]演示 1: 单个 MCP 服务器（stdio）[/bold cyan]")
    
    # 获取计算器服务器路径
    calculator_path = Path(__file__).parent / "mcp_calculator_server.py"
    
    server_params = StdioServerParameters(
        command="python",
        args=[str(calculator_path)]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                
                # 加载 MCP 工具
                tools = await load_mcp_tools(session)
                console.print(f"[green]✅ 加载了 {len(tools)} 个工具[/green]")
                
                # 配置 DeepSeek
                model = ChatOpenAI(
                    model="deepseek-chat",
                    base_url="https://api.deepseek.com",
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    temperature=0,
                    max_tokens=4096
                )
                
                # 创建 React agent
                agent = create_react_agent(model, tools)
                
                # 测试问题
                questions = [
                    "计算 (3 + 5) x 12",
                    "sqrt(169) + pi 等于多少？"
                ]
                
                for question in questions:
                    console.print(f"\n[yellow]❓ 问题: {question}[/yellow]")
                    
                    # 运行 agent
                    response = await agent.ainvoke({
                        "messages": [{"role": "user", "content": question}]
                    })
                    
                    # 提取最终答案
                    if "messages" in response:
                        final_message = response["messages"][-1]
                        console.print(f"[green]💡 答案: {final_message.content}[/green]")
                    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

async def demo_multi_server():
    """演示多个 MCP 服务器"""
    console.print("\n[bold cyan]演示 2: 多个 MCP 服务器[/bold cyan]")
    
    # 获取服务器路径
    calculator_path = Path(__file__).parent / "mcp_calculator_server.py"
    
    # 创建多服务器客户端
    client = MultiServerMCPClient({
        "calculator": {
            "command": "python",
            "args": [str(calculator_path)],
            "transport": "stdio",
        }
        # 可以在这里添加更多服务器
    })
    
    try:
        # 获取所有工具
        tools = await client.get_tools()
        console.print(f"[green]✅ 从所有服务器加载了 {len(tools)} 个工具[/green]")
        
        # 显示工具
        console.print("\n[yellow]可用工具:[/yellow]")
        for tool in tools:
            console.print(f"  • {tool.name}: {tool.description}")
        
        # 配置 DeepSeek
        model = ChatOpenAI(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0,
            max_tokens=4096
        )
        
        # 创建 React agent
        agent = create_react_agent(model, tools)
        
        # 测试问题
        test_cases = [
            {
                "question": "25 的平方根是多少？",
                "expected_tool": "calculate"
            },
            {
                "question": "将 32 fahrenheit 转换为 celsius",
                "expected_tool": "convert_units"
            },
            {
                "question": "计算 log10(1000) + exp(0)",
                "expected_tool": "calculate"
            }
        ]
        
        for test in test_cases:
            console.print(f"\n[yellow]❓ 问题: {test['question']}[/yellow]")
            console.print(f"[dim]期望使用工具: {test['expected_tool']}[/dim]")
            
            # 运行 agent
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": test["question"]}]
            })
            
            # 提取最终答案
            if "messages" in response:
                final_message = response["messages"][-1]
                console.print(f"[green]💡 答案: {final_message.content}[/green]")
        
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

async def main():
    """主程序"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        console.print("请在 .env 文件中设置：DEEPSEEK_API_KEY=your-api-key")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct + LangChain MCP Adapters[/bold cyan]\n"
        "使用 LangChain 官方 MCP 适配器集成",
        border_style="cyan"
    ))
    
    try:
        # 运行演示 1：单服务器
        await demo_single_server()
        
        console.print("\n" + "="*60 + "\n")
        
        # 运行演示 2：多服务器
        await demo_multi_server()
        
    except Exception as e:
        console.print(f"[red]❌ 主程序错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
    
    console.print("\n[bold green]✨ 演示完成！[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())