#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "langchain-anthropic>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "requests>=2.31.0",
#   "beautifulsoup4>=4.12.0",
#   "httpx[socks]>=0.24.0",
# ]
# ///

"""
DeepSeek ReAct Agent Demo (Simplified)
直接使用 deepseek-chat 模型，无需选择
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain_react_agent import LangChainReactAgent
from react_agent_tools import get_basic_tools

console = Console()

def main():
    """运行简化版 DeepSeek ReAct 智能体演示"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 DeepSeek API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        console.print("请在 .env 文件中设置：DEEPSEEK_API_KEY=your-api-key")
        sys.exit(1)
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct 智能体演示[/bold cyan]\n"
        "使用 deepseek-chat 模型进行推理和行动",
        border_style="cyan"
    ))
    
    try:
        # 直接创建 DeepSeek 智能体
        console.print("\n[yellow]正在初始化 DeepSeek 智能体...[/yellow]")
        
        agent = LangChainReactAgent(
            llm_provider="deepseek",
            model_name="deepseek-chat",  # 固定使用 deepseek-chat
            verbose=True
        )
        
        # 添加基础工具集
        tools = get_basic_tools()
        agent.add_tools(tools)
        
        console.print(f"[green]✅ 智能体初始化成功！[/green]")
        console.print(f"[green]模型: deepseek-chat[/green]")
        console.print(f"[green]工具: {len(tools)} 个可用[/green]")
        
        # 显示可用工具
        console.print("\n[bold yellow]可用工具：[/bold yellow]")
        for tool in tools:
            console.print(f"  • {tool.name}: {tool.description}")
        
        # 直接运行指定问题
        question = "25 * 4 + 10 等于多少？"
        console.print(f"\n[bold yellow]🧮 运行问题：{question}[/bold yellow]")
        
        try:
            # 运行智能体
            result = agent.run(question)
            
            console.print(f"\n[bold green]智能体回答:[/bold green]")
            console.print(Panel(result, border_style="green"))
            
        except Exception as e:
            console.print(f"[red]错误: {str(e)}[/red]")
        
    except Exception as e:
        console.print(f"[red]❌ 智能体初始化失败: {str(e)}[/red]")
        sys.exit(1)
    
    console.print("\n[bold green]👋 演示完成！[/bold green]")

if __name__ == "__main__":
    main()