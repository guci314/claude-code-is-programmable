#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "requests>=2.31.0",
#   "beautifulsoup4>=4.12.0",
#   "httpx[socks]>=0.24.0",
# ]
# ///

"""
DeepSeek ReAct Agent Example
演示如何使用 DeepSeek 运行 ReAct 智能体
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain_react_agent import LangChainReactAgent
from react_agent_tools import get_basic_tools

console = Console()

def main():
    """使用 DeepSeek 运行 ReAct 智能体示例"""
    
    # 加载环境变量
    load_dotenv()
    
    # 检查 DeepSeek API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        console.print("[red]错误：未找到 DEEPSEEK_API_KEY 环境变量[/red]")
        console.print("请在 .env 文件中设置：DEEPSEEK_API_KEY=your-api-key")
        return
    
    console.print(Panel(
        "[bold cyan]🤖 DeepSeek ReAct 智能体示例[/bold cyan]\n"
        "使用 DeepSeek 模型进行推理和行动",
        border_style="cyan"
    ))
    
    try:
        # 创建 DeepSeek 智能体 - 直接使用 deepseek-chat
        console.print("\n[yellow]正在初始化 DeepSeek 智能体 (deepseek-chat)...[/yellow]")
        
        agent = LangChainReactAgent(
            llm_provider="deepseek",
            model_name="deepseek-chat",  # 固定使用 deepseek-chat
            verbose=True
        )
        
        # 添加工具
        tools = get_basic_tools()
        agent.add_tools(tools)
        
        console.print(f"[green]✅ DeepSeek 智能体初始化成功！[/green]")
        console.print(f"[green]已加载 {len(tools)} 个工具[/green]")
        
        # 示例问题
        questions = [
            "计算 25 * 4 + 10 的结果",
            "搜索关于人工智能的信息",
            "创建一个名为 'deepseek_test.txt' 的文件，内容为 'Hello from DeepSeek!'"
        ]
        
        console.print("\n[bold blue]🎯 运行示例问题[/bold blue]")
        
        for i, question in enumerate(questions, 1):
            console.print(f"\n[bold cyan]问题 {i}: {question}[/bold cyan]")
            
            try:
                result = agent.run(question)
                console.print(Panel(
                    result,
                    title=f"📋 答案 {i}",
                    border_style="green"
                ))
                
                # 询问是否继续
                if i < len(questions):
                    input("\n按回车键继续下一个问题...")
                
            except Exception as e:
                console.print(f"[red]❌ 问题 {i} 执行失败: {str(e)}[/red]")
        
        console.print("\n[bold green]🎉 DeepSeek 示例完成！[/bold green]")
        
    except Exception as e:
        console.print(f"[red]❌ 智能体初始化失败: {str(e)}[/red]")

if __name__ == "__main__":
    main()