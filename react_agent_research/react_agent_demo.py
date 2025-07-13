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

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from langchain_react_agent import LangChainReactAgent
from react_agent_tools import get_basic_tools, get_advanced_tools

console = Console()

class ReActAgentDemo:
    """Interactive demo for the LangChain ReAct Agent"""
    
    def __init__(self):
        self.agent = None
        self.current_provider = None
        self.current_model = None
        self.session_history = []
        
    def display_header(self):
        """Display the demo header"""
        title = Text("🤖 LangChain ReAct Agent Demo", style="bold cyan")
        subtitle = Text("Interactive AI Agent with Reasoning & Acting Capabilities", style="dim")
        
        console.print(Panel(
            f"{title}\n{subtitle}",
            border_style="cyan",
            padding=(1, 2)
        ))
    
    def setup_agent(self):
        """Setup the ReAct agent with user preferences"""
        console.print("\n[bold yellow]🚀 Agent Setup[/bold yellow]")
        
        # Choose LLM provider
        providers = ["openai", "anthropic", "deepseek"]
        console.print("\nAvailable LLM providers:")
        for i, provider in enumerate(providers, 1):
            console.print(f"  {i}. {provider.title()}")
        
        while True:
            try:
                choice = Prompt.ask("\nChoose provider (1-3)", default="3")  # Default to DeepSeek
                provider_idx = int(choice) - 1
                if 0 <= provider_idx < len(providers):
                    self.current_provider = providers[provider_idx]
                    break
                else:
                    console.print("[red]Invalid choice. Please select 1-3.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
        
        # Set model based on provider - no selection needed
        if self.current_provider == "openai":
            self.current_model = "gpt-4"
        elif self.current_provider == "anthropic":
            self.current_model = "claude-3-sonnet-20240229"
        else:  # deepseek
            self.current_model = "deepseek-chat"
        
        console.print(f"\nUsing model: {self.current_model}")
        
        # Choose tool set
        tool_sets = ["basic", "advanced"]
        console.print("\nAvailable tool sets:")
        console.print("  1. Basic (web search, calculator, file system, code analysis)")
        console.print("  2. Advanced (basic tools + additional capabilities)")
        
        while True:
            try:
                choice = Prompt.ask("\nChoose tool set (1-2)", default="1")
                tool_idx = int(choice) - 1
                if 0 <= tool_idx < len(tool_sets):
                    tool_set = tool_sets[tool_idx]
                    break
                else:
                    console.print("[red]Invalid choice. Please select 1 or 2.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
        
        # Initialize agent
        try:
            with console.status("[bold green]Initializing agent...", spinner="dots"):
                self.agent = LangChainReactAgent(
                    llm_provider=self.current_provider,
                    model_name=self.current_model,
                    verbose=True
                )
                
                # Add tools
                if tool_set == "basic":
                    tools = get_basic_tools()
                else:
                    tools = get_advanced_tools()
                
                self.agent.add_tools(tools)
            
            console.print(f"[bold green]✅ Agent initialized successfully![/bold green]")
            console.print(f"Provider: {self.current_provider}")
            console.print(f"Model: {self.current_model}")
            console.print(f"Tools: {len(tools)} available")
            
            # Display available tools
            console.print("\n")
            console.print(self.agent.list_tools())
            
        except Exception as e:
            console.print(f"[bold red]❌ Failed to initialize agent: {str(e)}[/bold red]")
            console.print("\nPlease check your environment variables:")
            console.print("- OPENAI_API_KEY (for OpenAI)")
            console.print("- ANTHROPIC_API_KEY (for Anthropic)")
            console.print("- DEEPSEEK_API_KEY (for DeepSeek)")
            sys.exit(1)
    
    def run_predefined_scenarios(self):
        """Run predefined scenarios to showcase agent capabilities"""
        scenarios = [
            {
                "name": "Mathematical Problem Solving",
                "description": "Solve a multi-step mathematical problem",
                "query": "What is 15% of 240, and then multiply that result by 3?"
            },
            {
                "name": "Web Research",
                "description": "Research a topic using web search",
                "query": "What is machine learning and how does it relate to artificial intelligence?"
            },
            {
                "name": "Code Analysis",
                "description": "Analyze code structure in current directory",
                "query": "Analyze the Python files in the current directory and tell me about their structure"
            },
            {
                "name": "File Operations",
                "description": "Create and read a file",
                "query": "Create a file called 'test_output.txt' with the content 'Hello from ReAct Agent!' and then read it back"
            },
            {
                "name": "Python Execution",
                "description": "Execute Python code to solve a problem",
                "query": "Write and execute Python code to calculate the factorial of 5"
            }
        ]
        
        console.print("\n[bold yellow]📋 Predefined Scenarios[/bold yellow]")
        console.print("Choose a scenario to run:")
        
        for i, scenario in enumerate(scenarios, 1):
            console.print(f"  {i}. {scenario['name']}: {scenario['description']}")
        
        while True:
            try:
                choice = Prompt.ask(f"\nChoose scenario (1-{len(scenarios)}) or 'skip' to continue", default="skip")
                
                if choice.lower() == 'skip':
                    break
                
                scenario_idx = int(choice) - 1
                if 0 <= scenario_idx < len(scenarios):
                    scenario = scenarios[scenario_idx]
                    console.print(f"\n[bold cyan]🎯 Running Scenario: {scenario['name']}[/bold cyan]")
                    console.print(f"Query: {scenario['query']}")
                    
                    result = self.agent.run(scenario['query'])
                    
                    # Add to session history
                    self.session_history.append({
                        'type': 'scenario',
                        'name': scenario['name'],
                        'query': scenario['query'],
                        'result': result
                    })
                    
                    console.print(f"\n[bold green]🎉 Scenario completed![/bold green]")
                    
                    if not Confirm.ask("\nRun another scenario?"):
                        break
                else:
                    console.print(f"[red]Invalid choice. Please select 1-{len(scenarios)}.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number or 'skip'.[/red]")
    
    def interactive_mode(self):
        """Run interactive mode where user can ask questions"""
        console.print("\n[bold yellow]💬 Interactive Mode[/bold yellow]")
        console.print("Ask the agent anything! Type 'quit' to exit, 'help' for commands.")
        
        while True:
            try:
                question = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="quit")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                elif question.lower() == 'help':
                    self.show_help()
                    continue
                elif question.lower() == 'memory':
                    console.print(f"[yellow]{self.agent.get_memory_summary()}[/yellow]")
                    continue
                elif question.lower() == 'clear':
                    self.agent.clear_memory()
                    continue
                elif question.lower() == 'history':
                    self.show_session_history()
                    continue
                
                # Run the agent
                result = self.agent.run(question)
                
                # Add to session history
                self.session_history.append({
                    'type': 'interactive',
                    'query': question,
                    'result': result
                })
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted by user.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
    
    def show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]
• quit/exit/q - Exit the demo
• help - Show this help message
• memory - Show memory status
• clear - Clear conversation memory
• history - Show session history

[bold cyan]Example Questions:[/bold cyan]
• "What is 25 * 4 + 10?"
• "Search for information about Python programming"
• "Analyze the code in the current directory"
• "Create a file with some content"
• "Execute Python code to solve a problem"

[bold cyan]Tips:[/bold cyan]
• The agent will reason through problems step by step
• You can ask follow-up questions
• The agent has access to web search, calculator, file system, and more
        """
        console.print(Panel(help_text, border_style="cyan"))
    
    def show_session_history(self):
        """Show session history"""
        if not self.session_history:
            console.print("[yellow]No session history yet.[/yellow]")
            return
        
        table = Table(title="Session History")
        table.add_column("Type", style="cyan")
        table.add_column("Query", style="white")
        table.add_column("Result Preview", style="green")
        
        for entry in self.session_history:
            result_preview = entry['result'][:100] + "..." if len(entry['result']) > 100 else entry['result']
            table.add_row(
                entry['type'],
                entry['query'],
                result_preview
            )
        
        console.print(table)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.agent:
            console.print("[yellow]🧹 Cleaning up...[/yellow]")
            # Any cleanup needed
    
    def run(self):
        """Run the complete demo"""
        try:
            self.display_header()
            
            # Check environment
            load_dotenv()
            
            # Setup agent
            self.setup_agent()
            
            # Run predefined scenarios
            self.run_predefined_scenarios()
            
            # Interactive mode
            self.interactive_mode()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]Unexpected error: {str(e)}[/red]")
        finally:
            self.cleanup()
            console.print("\n[bold green]👋 Thanks for using the ReAct Agent Demo![/bold green]")


def main():
    """Main function"""
    # Check for required environment variables
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'DEEPSEEK_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if len(missing_vars) == len(required_vars):
        console.print("[bold red]❌ Error: No API keys found![/bold red]")
        console.print("Please set at least one of the following environment variables:")
        for var in required_vars:
            console.print(f"  - {var}")
        sys.exit(1)
    
    # Run demo
    demo = ReActAgentDemo()
    demo.run()


if __name__ == "__main__":
    main()