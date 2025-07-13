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
DeepSeek ReAct Agent - Clean Output
简洁版输出，只显示问题和答案
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
    """运行简洁版 DeepSeek ReAct 智能体"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 DeepSeek API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]❌ 错误：未找到 DEEPSEEK_API_KEY[/red]")
        sys.exit(1)
    
    try:
        # 创建 DeepSeek 智能体（关闭详细输出）
        agent = LangChainReactAgent(
            llm_provider="deepseek",
            model_name="deepseek-chat",
            verbose=False  # 关闭详细输出
        )
        
        # 添加基础工具集
        tools = get_basic_tools()
        agent.add_tools(tools)
        
        # 运行问题
        question = "25 * 4 + 10 等于多少？"
        
        console.print(Panel(
            f"[bold cyan]问题：[/bold cyan]{question}",
            border_style="cyan"
        ))
        
        # 运行智能体
        result = agent.run(question)
        
        console.print(Panel(
            f"[bold green]答案：[/bold green]{result}",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ 错误: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()