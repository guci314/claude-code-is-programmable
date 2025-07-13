#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///

"""
ReAct Agent 执行流程可视化演示
展示 ReAct 模式的详细执行步骤
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax

console = Console()

def show_react_flow():
    """展示 ReAct 执行流程"""
    
    console.print(Panel(
        "[bold cyan]ReAct Agent 执行流程演示[/bold cyan]\n"
        "Reasoning (推理) + Acting (行动) = ReAct",
        border_style="cyan"
    ))
    
    # 1. 显示问题
    console.print("\n[bold yellow]📥 Step 1: 用户输入[/bold yellow]")
    console.print(Panel("25 * 4 + 10 等于多少？", title="用户问题", border_style="yellow"))
    time.sleep(1)
    
    # 2. 显示推理循环
    console.print("\n[bold blue]🔄 Step 2: ReAct 推理循环开始[/bold blue]")
    
    # 创建流程树
    tree = Tree("🤖 ReAct Agent")
    
    # Thought 节点
    thought_node = tree.add("💭 [bold]Thought[/bold] (思考)")
    thought_node.add('[dim]"我需要计算数学表达式 25 * 4 + 10"[/dim]')
    thought_node.add('[dim]"我可以使用 calculator 工具来计算"[/dim]')
    
    # Action 节点
    action_node = tree.add("🛠️ [bold]Action[/bold] (选择工具)")
    action_node.add('[green]Tool: calculator[/green]')
    
    # Action Input 节点
    input_node = tree.add("📝 [bold]Action Input[/bold] (准备输入)")
    input_node.add('[cyan]"25 * 4 + 10"[/cyan]')
    
    # Tool Execution 节点
    exec_node = tree.add("⚙️ [bold]Tool Execution[/bold] (执行工具)")
    exec_node.add('[yellow]eval("25 * 4 + 10") → 110[/yellow]')
    
    # Observation 节点
    obs_node = tree.add("👁️ [bold]Observation[/bold] (观察结果)")
    obs_node.add('[magenta]"Result: 25 * 4 + 10 = 110"[/magenta]')
    
    # Final Answer 节点
    final_node = tree.add("✅ [bold]Final Answer[/bold] (最终答案)")
    final_node.add('[green]"25 * 4 + 10 等于 110。"[/green]')
    
    console.print(tree)
    time.sleep(2)
    
    # 3. 显示工具执行细节
    console.print("\n[bold green]🔧 Step 3: 工具执行细节[/bold green]")
    
    # 创建工具表格
    table = Table(title="Calculator 工具执行")
    table.add_column("步骤", style="cyan")
    table.add_column("操作", style="yellow")
    table.add_column("结果", style="green")
    
    table.add_row("1", "接收输入", "25 * 4 + 10")
    table.add_row("2", "执行计算", "100 + 10")
    table.add_row("3", "返回结果", "110")
    
    console.print(table)
    time.sleep(1)
    
    # 4. 显示完整流程
    console.print("\n[bold magenta]📊 Step 4: 完整执行流程[/bold magenta]")
    
    flow_steps = [
        ("1️⃣", "用户提问", "25 * 4 + 10 等于多少？"),
        ("2️⃣", "LLM 思考", "需要进行数学计算"),
        ("3️⃣", "选择工具", "calculator"),
        ("4️⃣", "准备输入", "25 * 4 + 10"),
        ("5️⃣", "执行工具", "calculator(\"25 * 4 + 10\")"),
        ("6️⃣", "获得结果", "Result: 110"),
        ("7️⃣", "生成答案", "25 * 4 + 10 等于 110。"),
        ("8️⃣", "返回用户", "✅ 完成")
    ]
    
    for emoji, step, detail in flow_steps:
        console.print(f"{emoji} [bold]{step}[/bold]: {detail}")
        time.sleep(0.5)
    
    # 5. 显示代码实现
    console.print("\n[bold red]💻 Step 5: 核心代码实现[/bold red]")
    
    code = '''
# ReAct 执行核心代码
def run(self, question: str) -> str:
    """执行 ReAct Agent"""
    
    # 1. 初始化上下文
    context = {"input": question}
    
    # 2. 执行推理循环
    while not self.is_finished():
        # Thought: LLM 推理
        thought = self.llm.think(context)
        
        # Action: 选择工具
        action = self.parse_action(thought)
        
        if action.is_final_answer:
            return action.answer
        
        # Tool Execution: 执行工具
        observation = self.tools[action.tool].run(action.input)
        
        # 更新上下文
        context.update(observation)
    
    return self.final_answer
'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="简化的 ReAct 实现", border_style="red"))
    
    # 6. 关键特性
    console.print("\n[bold green]✨ ReAct 模式的关键特性[/bold green]")
    
    features = [
        ("🧠", "推理透明", "可以看到 AI 的思考过程"),
        ("🔄", "迭代求解", "通过多轮推理解决复杂问题"),
        ("🛠️", "工具增强", "使用外部工具扩展能力"),
        ("🎯", "目标导向", "始终围绕解决用户问题"),
        ("🛡️", "错误处理", "遇到问题可以重试或换策略")
    ]
    
    for icon, feature, desc in features:
        console.print(f"{icon} [bold]{feature}[/bold]: [dim]{desc}[/dim]")
    
    console.print("\n[bold green]🎉 演示完成！[/bold green]")

if __name__ == "__main__":
    show_react_flow()