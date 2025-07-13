#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
# ]
# ///

"""
Problem Solving Scenario Example for LangChain ReAct Agent
Demonstrates how the agent can solve complex multi-step problems using various tools.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from langchain_react_agent import LangChainReactAgent
from react_agent_tools import get_basic_tools

console = Console()

def main():
    """Run the problem solving scenario"""
    load_dotenv()
    
    console.print(Panel(
        "[bold cyan]🧩 Problem Solving Scenario Example[/bold cyan]\n"
        "This example demonstrates how the ReAct agent can solve complex problems\n"
        "that require multiple tools and reasoning steps.",
        border_style="cyan"
    ))
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY[/red]")
        return
    
    # Initialize agent
    try:
        console.print("\n[yellow]Initializing ReAct Agent...[/yellow]")
        
        if os.getenv("OPENAI_API_KEY"):
            agent = LangChainReactAgent(
                llm_provider="openai",
                model_name="gpt-4",
                verbose=True
            )
        else:
            agent = LangChainReactAgent(
                llm_provider="anthropic",
                model_name="claude-3-sonnet-20240229",
                verbose=True
            )
        
        # Add tools
        tools = get_basic_tools()
        agent.add_tools(tools)
        
        console.print("[green]✅ Agent initialized successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {str(e)}[/red]")
        return
    
    # Problem solving scenarios
    problems = [
        {
            "title": "Mathematical Word Problem",
            "query": """Solve this problem step by step: 
            A company has 150 employees. 60% work in engineering, 25% in sales, and the rest in administration. 
            If the company grows by 20% next year, and the department proportions stay the same, 
            how many new employees will be hired for each department? 
            Create a file called 'hiring_plan.txt' with the detailed calculations."""
        },
        {
            "title": "Data Analysis Challenge",
            "query": """I need to analyze some data. First, create a file called 'sample_data.txt' with 
            10 rows of sample sales data (date, product, quantity, price). Then analyze this data 
            to find: 1) Total revenue, 2) Average order value, 3) Best-selling product. 
            Finally, create a summary report file called 'sales_analysis.txt'."""
        },
        {
            "title": "Research and Development Task",
            "query": """Research the current state of renewable energy technology. Find information about 
            solar, wind, and battery storage efficiency. Calculate the potential energy output 
            if a city of 100,000 people used 50% renewable energy. Create a presentation outline 
            in a file called 'renewable_energy_presentation.txt'."""
        },
        {
            "title": "Code Generation and Testing",
            "query": """Write a Python function that calculates the compound interest for an investment. 
            The function should take principal, rate, time, and compound frequency as parameters. 
            Test it with sample data, then create a file called 'investment_calculator.py' with 
            the function and test cases."""
        },
        {
            "title": "System Design Problem",
            "query": """Design a simple backup system for a small business. Research best practices 
            for data backup, calculate storage requirements for 1TB of data with 3-2-1 backup strategy, 
            and create a detailed plan in a file called 'backup_strategy.txt'. Include costs and timeline."""
        }
    ]
    
    # Run problem solving scenarios
    for i, problem in enumerate(problems, 1):
        console.print(f"\n[bold blue]🧩 Problem {i}: {problem['title']}[/bold blue]")
        console.print(f"[dim]Description: {problem['query'][:150]}...[/dim]")
        
        try:
            result = agent.run(problem['query'])
            
            console.print(f"\n[green]✅ Problem solved: {problem['title']}[/green]")
            console.print(Panel(
                result,
                title=f"🎯 Solution: {problem['title']}",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Problem solving failed for {problem['title']}: {str(e)}[/red]")
        
        # Ask user if they want to continue
        if i < len(problems):
            try:
                continue_solving = input(f"\nContinue to next problem? (y/n): ").lower().strip()
                if continue_solving not in ['y', 'yes', '']:
                    break
            except KeyboardInterrupt:
                console.print("\n[yellow]Problem solving interrupted by user.[/yellow]")
                break
    
    # Challenge problem
    console.print(f"\n[bold red]🎮 Challenge Problem[/bold red]")
    challenge_query = """CHALLENGE: Create a complete mini-project management system. 
    1) Research project management best practices
    2) Design a simple task tracking system
    3) Create a Python script that can add, list, and mark tasks as complete
    4) Generate sample project data with 5 tasks
    5) Calculate project completion percentage
    6) Create a project status report
    7) Save everything in appropriately named files
    This is a complex multi-step challenge that will test multiple capabilities!"""
    
    try:
        console.print("[yellow]Starting challenge problem...[/yellow]")
        result = agent.run(challenge_query)
        
        console.print(f"\n[green]✅ Challenge completed![/green]")
        console.print(Panel(
            result,
            title="🏆 Challenge Solution",
            border_style="red"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Challenge failed: {str(e)}[/red]")
    
    console.print("\n[bold green]🎉 Problem solving scenario completed![/bold green]")
    console.print("""
[bold cyan]What this example demonstrated:[/bold cyan]
• Multi-step problem decomposition
• Mathematical calculations and reasoning
• Data analysis and report generation
• Research and synthesis of information
• Code generation and testing
• File creation and data persistence
• Complex system design thinking
• Integration of multiple tools and capabilities
    """)

if __name__ == "__main__":
    main()