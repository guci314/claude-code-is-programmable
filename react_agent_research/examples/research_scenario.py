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
Research Scenario Example for LangChain ReAct Agent
Demonstrates how the agent can research a topic and provide comprehensive information.
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
    """Run the research scenario"""
    load_dotenv()
    
    console.print(Panel(
        "[bold cyan]🔬 Research Scenario Example[/bold cyan]\n"
        "This example demonstrates how the ReAct agent can research a complex topic\n"
        "by using multiple tools to gather and synthesize information.",
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
    
    # Research scenarios
    research_topics = [
        {
            "topic": "Machine Learning and AI",
            "query": """Research and explain the relationship between machine learning and artificial intelligence. 
            Include key differences, applications, and current trends. Also calculate what percentage of AI 
            applications use machine learning techniques."""
        },
        {
            "topic": "Climate Change Technology",
            "query": """Research current technologies being developed to combat climate change. 
            Find information about renewable energy, carbon capture, and calculate the potential 
            impact if these technologies were widely adopted."""
        },
        {
            "topic": "Quantum Computing",
            "query": """Research the current state of quantum computing technology. 
            Find information about recent breakthroughs, compare classical vs quantum computing power, 
            and calculate how quantum computers might impact cryptography."""
        }
    ]
    
    # Run research scenarios
    for i, scenario in enumerate(research_topics, 1):
        console.print(f"\n[bold blue]📊 Research Scenario {i}: {scenario['topic']}[/bold blue]")
        console.print(f"[dim]Query: {scenario['query'][:100]}...[/dim]")
        
        try:
            result = agent.run(scenario['query'])
            
            console.print(f"\n[green]✅ Research completed for: {scenario['topic']}[/green]")
            console.print(Panel(
                result,
                title=f"📋 Research Results: {scenario['topic']}",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Research failed for {scenario['topic']}: {str(e)}[/red]")
        
        # Ask user if they want to continue
        if i < len(research_topics):
            try:
                continue_research = input(f"\nContinue to next research topic? (y/n): ").lower().strip()
                if continue_research not in ['y', 'yes', '']:
                    break
            except KeyboardInterrupt:
                console.print("\n[yellow]Research interrupted by user.[/yellow]")
                break
    
    console.print("\n[bold green]🎉 Research scenario completed![/bold green]")
    console.print("""
[bold cyan]What this example demonstrated:[/bold cyan]
• Multi-step reasoning for complex topics
• Web search for current information
• Mathematical calculations as part of research
• Synthesis of information from multiple sources
• Real-time problem-solving approach
    """)

if __name__ == "__main__":
    main()