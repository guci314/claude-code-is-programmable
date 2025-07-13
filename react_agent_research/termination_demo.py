#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
ReAct Agent 终止逻辑演示
展示不同的终止场景
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def show_termination_scenarios():
    """展示各种终止场景"""
    
    console.print(Panel(
        "[bold cyan]ReAct Agent 终止逻辑演示[/bold cyan]\n"
        "展示 Agent 在不同情况下如何终止执行",
        border_style="cyan"
    ))
    
    # 场景1: 正常终止（Final Answer）
    console.print("\n[bold green]✅ 场景 1: 正常终止（找到答案）[/bold green]")
    
    normal_flow = """
Iteration 1:
  Thought: 我需要计算 25 * 4 + 10
  Action: calculator
  Action Input: 25 * 4 + 10
  Observation: Result: 110
  
Iteration 2:
  Thought: 我现在知道了答案
  [bold green]Final Answer: 25 * 4 + 10 等于 110。[/bold green]
  
[bold yellow]→ 检测到 Final Answer，正常终止 ✓[/bold yellow]
"""
    console.print(Panel(normal_flow, border_style="green"))
    time.sleep(1)
    
    # 场景2: 达到最大迭代次数
    console.print("\n[bold yellow]⚠️ 场景 2: 达到最大迭代次数[/bold yellow]")
    
    # 创建迭代进度条
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]执行迭代...", total=10)
        
        for i in range(10):
            progress.update(task, advance=1, description=f"[cyan]迭代 {i+1}/10")
            time.sleep(0.2)
    
    max_iter_flow = """
配置: max_iterations = 10

Iteration 1-9: 持续搜索和计算...
Iteration 10: 仍在尝试...

[bold yellow]⚠️ 达到最大迭代次数限制！[/bold yellow]

终止策略: early_stopping_method = "generate"
[bold green]→ 强制生成答案: "基于当前信息，我的回答是..."[/bold green]
"""
    console.print(Panel(max_iter_flow, border_style="yellow"))
    time.sleep(1)
    
    # 场景3: 解析错误
    console.print("\n[bold red]❌ 场景 3: 解析错误终止[/bold red]")
    
    parse_error_flow = """
LLM 输出:
"我觉得应该用计算器工具来计算这个问题
但是我不确定具体的格式是什么..."

[bold red]❌ 解析错误: 无法识别 Action 和 Action Input[/bold red]

处理策略: handle_parsing_errors = True
[bold yellow]→ 尝试修复: 重新提示 LLM 使用正确格式[/bold yellow]

如果连续 3 次解析失败:
[bold red]→ 终止执行，返回错误信息[/bold red]
"""
    console.print(Panel(parse_error_flow, border_style="red"))
    time.sleep(1)
    
    # 场景4: 工具执行错误
    console.print("\n[bold magenta]🔧 场景 4: 工具执行错误[/bold magenta]")
    
    tool_error_flow = """
Action: web_search
Action Input: "最新的天气信息"

[bold red]工具执行错误: 网络连接超时[/bold red]

错误处理流程:
1. 记录错误信息
2. 尝试使用备用工具
3. 如果无备用方案 → 生成道歉信息

[bold yellow]Final Answer: 抱歉，我无法获取天气信息，因为网络连接失败。[/bold yellow]
"""
    console.print(Panel(tool_error_flow, border_style="magenta"))
    time.sleep(1)
    
    # 展示终止条件配置
    console.print("\n[bold blue]⚙️ 终止条件配置示例[/bold blue]")
    
    config_code = '''
# Agent Executor 配置
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    
    # 基本终止条件
    max_iterations=10,              # 最大迭代次数
    max_execution_time=60,          # 最大执行时间（秒）
    
    # 终止策略
    early_stopping_method="generate",  # "generate" 或 "force"
    
    # 错误处理
    handle_parsing_errors=True,     # 自动处理解析错误
    
    # 自定义终止条件
    termination_checker=lambda x: "无法回答" in x,
)
'''
    syntax = Syntax(config_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="终止条件配置", border_style="blue"))
    
    # 终止统计表
    console.print("\n[bold cyan]📊 终止原因统计[/bold cyan]")
    
    table = Table(title="常见终止原因分布")
    table.add_column("终止原因", style="cyan")
    table.add_column("占比", style="yellow")
    table.add_column("平均迭代次数", style="green")
    table.add_column("处理建议", style="magenta")
    
    table.add_row("Final Answer", "75%", "3.2", "正常情况")
    table.add_row("最大迭代", "15%", "10.0", "考虑优化提示词")
    table.add_row("解析错误", "5%", "1.5", "改进输出格式要求")
    table.add_row("工具错误", "3%", "4.1", "增加错误处理")
    table.add_row("超时", "2%", "7.8", "优化工具性能")
    
    console.print(table)
    
    # 最佳实践
    console.print("\n[bold green]💡 终止逻辑最佳实践[/bold green]")
    
    best_practices = [
        ("1️⃣", "设置合理的最大迭代", "简单任务 5-7 次，复杂任务 10-15 次"),
        ("2️⃣", "启用错误处理", "handle_parsing_errors=True"),
        ("3️⃣", "选择合适的终止策略", "generate 更友好，force 更快速"),
        ("4️⃣", "监控终止原因", "优化 Agent 性能的关键"),
        ("5️⃣", "实现优雅降级", "错误时也要给出有用信息")
    ]
    
    for num, practice, detail in best_practices:
        console.print(f"{num} [bold]{practice}[/bold]: [dim]{detail}[/dim]")
    
    console.print("\n[bold green]🎉 演示完成！[/bold green]")

if __name__ == "__main__":
    show_termination_scenarios()