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
Code Analysis Scenario Example for LangChain ReAct Agent
Demonstrates how the agent can analyze code, suggest improvements, and create documentation.
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
    """Run the code analysis scenario"""
    load_dotenv()
    
    console.print(Panel(
        "[bold cyan]🔍 Code Analysis Scenario Example[/bold cyan]\n"
        "This example demonstrates how the ReAct agent can analyze code,\n"
        "suggest improvements, and create documentation automatically.",
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
    
    # Code analysis scenarios
    analysis_tasks = [
        {
            "title": "Project Structure Analysis",
            "query": """Analyze the structure of the react_agent_research directory. 
            Look at all Python files, count the functions and classes, and provide 
            a summary of the codebase architecture. Also calculate the total lines of code."""
        },
        {
            "title": "Code Quality Assessment",
            "query": """Analyze the langchain_react_agent.py file for code quality. 
            Check for proper error handling, documentation, and suggest improvements. 
            Create a simple quality score based on your analysis."""
        },
        {
            "title": "Tool Implementation Review",
            "query": """Review the react_agent_tools.py file and analyze the security measures 
            implemented in each tool. Check if the tools properly handle edge cases and 
            provide suggestions for additional security improvements."""
        },
        {
            "title": "Test Coverage Analysis",
            "query": """Analyze the test_react_agent.py file and assess the test coverage. 
            Count how many functions are tested vs total functions in the main modules. 
            Calculate the approximate test coverage percentage and suggest additional tests."""
        }
    ]
    
    # Run analysis scenarios
    for i, task in enumerate(analysis_tasks, 1):
        console.print(f"\n[bold blue]🔍 Analysis Task {i}: {task['title']}[/bold blue]")
        console.print(f"[dim]Query: {task['query'][:100]}...[/dim]")
        
        try:
            result = agent.run(task['query'])
            
            console.print(f"\n[green]✅ Analysis completed: {task['title']}[/green]")
            console.print(Panel(
                result,
                title=f"📊 Analysis Results: {task['title']}",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Analysis failed for {task['title']}: {str(e)}[/red]")
        
        # Ask user if they want to continue
        if i < len(analysis_tasks):
            try:
                continue_analysis = input(f"\nContinue to next analysis task? (y/n): ").lower().strip()
                if continue_analysis not in ['y', 'yes', '']:
                    break
            except KeyboardInterrupt:
                console.print("\n[yellow]Analysis interrupted by user.[/yellow]")
                break
    
    # Advanced analysis task
    console.print(f"\n[bold magenta]🚀 Advanced Analysis Task[/bold magenta]")
    advanced_query = """Create a comprehensive report about the entire react_agent_research project. 
    Include: 1) Project structure overview, 2) Code quality metrics, 3) Security analysis, 
    4) Test coverage report, 5) Suggestions for improvements, and 6) Calculate complexity metrics. 
    Save this report as a file called 'project_analysis_report.txt'."""
    
    try:
        console.print("[yellow]Running advanced analysis...[/yellow]")
        result = agent.run(advanced_query)
        
        console.print(f"\n[green]✅ Advanced analysis completed![/green]")
        console.print(Panel(
            result,
            title="🎯 Comprehensive Project Analysis",
            border_style="magenta"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Advanced analysis failed: {str(e)}[/red]")
    
    console.print("\n[bold green]🎉 Code analysis scenario completed![/bold green]")
    console.print("""
[bold cyan]What this example demonstrated:[/bold cyan]
• Automated code structure analysis
• Code quality assessment with metrics
• Security vulnerability identification
• Test coverage calculation
• Automated report generation
• File creation and data persistence
• Complex multi-step analysis workflows
    """)

if __name__ == "__main__":
    main()