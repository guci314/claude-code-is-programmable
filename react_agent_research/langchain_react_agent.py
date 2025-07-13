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
import re
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

console = Console()

class ReactAgentCallback(BaseCallbackHandler):
    """Custom callback handler for ReAct agent to display reasoning process"""
    
    def __init__(self):
        self.step_count = 0
        
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        self.step_count += 1
        
        console.print(f"\n[bold blue]🤔 Step {self.step_count}: Agent Reasoning[/bold blue]")
        
        # Parse the thought process
        thought_match = re.search(r'Thought: (.*?)(?=\n(?:Action|Final Answer))', action.log, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()
            console.print(Panel(thought, title="💭 Thought", border_style="blue"))
        
        # Display action
        console.print(Panel(
            f"[bold green]Tool:[/bold green] {action.tool}\n[bold green]Input:[/bold green] {action.tool_input}",
            title="🛠️ Action",
            border_style="green"
        ))
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when agent finishes"""
        console.print(f"\n[bold green]✅ Agent Finished[/bold green]")
        console.print(Panel(finish.return_values["output"], title="📋 Final Answer", border_style="green"))


class LangChainReactAgent:
    """LangChain ReAct Agent implementation with custom tools and reasoning display"""
    
    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-4", verbose: bool = True):
        """
        Initialize the ReAct agent
        
        Args:
            llm_provider: "openai", "anthropic", or "deepseek"
            model_name: Model name (e.g., "gpt-4", "claude-3-sonnet-20240229", "deepseek-chat")
            verbose: Whether to display reasoning process
        """
        load_dotenv()
        
        self.console = Console()
        self.verbose = verbose
        
        # Initialize LLM
        self.llm = self._initialize_llm(llm_provider, model_name)
        
        # Initialize tools (will be set by subclasses or external setup)
        self.tools = []
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize callback manager
        self.callback_manager = CallbackManager([ReactAgentCallback()]) if verbose else None
        
        # Agent will be initialized when tools are set
        self.agent = None
        self.agent_executor = None
    
    def _initialize_llm(self, provider: str, model_name: str):
        """Initialize the LLM based on provider"""
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            return ChatOpenAI(
                model=model_name,
                temperature=0.1,
                openai_api_key=api_key
            )
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            return ChatAnthropic(
                model=model_name,
                temperature=0.1,
                anthropic_api_key=api_key
            )
        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            return ChatOpenAI(
                temperature=0,
                model=model_name,
                base_url="https://api.deepseek.com",
                api_key=api_key,
                max_tokens=8192
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def add_tools(self, tools: List[Tool]):
        """Add tools to the agent"""
        self.tools.extend(tools)
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the ReAct agent with tools"""
        if not self.tools:
            raise ValueError("No tools provided. Add tools before initializing agent.")
        
        # Get the ReAct prompt from hub
        try:
            react_prompt = hub.pull("hwchase17/react")
        except Exception:
            # Fallback to custom prompt if hub is not available
            react_prompt = self._create_react_prompt()
        
        # Initialize agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt,
        )
        
        # Initialize agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=10,
            early_stopping_method="generate",
            callbacks=self.callback_manager.handlers if self.callback_manager else None,
            handle_parsing_errors=True,
            return_intermediate_steps=False
        )
    
    def _create_react_prompt(self):
        """Create a custom ReAct prompt template"""
        from langchain.prompts import PromptTemplate
        
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        
        template = f"""You are a helpful AI assistant that uses a ReAct (Reasoning + Acting) approach to solve problems.

You have access to the following tools:
{tool_descriptions}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{', '.join([tool.name for tool in self.tools])}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""
        
        return PromptTemplate.from_template(template)
    
    def run(self, question: str) -> str:
        """Run the agent with a question"""
        if not self.agent_executor:
            raise ValueError("Agent not initialized. Add tools first.")
        
        if self.verbose:
            self.console.print(f"\n[bold cyan]🚀 Starting ReAct Agent[/bold cyan]")
            self.console.print(Panel(question, title="❓ Question", border_style="cyan"))
        
        try:
            # Use invoke instead of run for newer LangChain versions
            result = self.agent_executor.invoke({"input": question})
            # Extract the output from the result
            if isinstance(result, dict):
                return result.get("output", str(result))
            return str(result)
        except AttributeError:
            # Fallback to run method for older versions
            try:
                result = self.agent_executor.run(input=question)
                return result
            except Exception as e:
                error_msg = f"Agent execution failed: {str(e)}"
                if self.verbose:
                    self.console.print(f"[bold red]❌ Error: {error_msg}[/bold red]")
                return error_msg
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            if self.verbose:
                self.console.print(f"[bold red]❌ Error: {error_msg}[/bold red]")
            return error_msg
    
    def get_memory_summary(self) -> str:
        """Get a summary of the conversation history"""
        if self.memory.chat_memory.messages:
            return f"Conversation history contains {len(self.memory.chat_memory.messages)} messages"
        return "No conversation history"
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
        if self.verbose:
            self.console.print("[yellow]🧹 Memory cleared[/yellow]")
    
    def list_tools(self) -> Table:
        """List all available tools in a formatted table"""
        table = Table(title="Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")
        
        for tool in self.tools:
            table.add_row(tool.name, tool.description)
        
        return table


def create_basic_react_agent() -> LangChainReactAgent:
    """Create a basic ReAct agent with common tools"""
    from react_agent_tools import get_basic_tools
    
    # Choose provider based on available API keys
    if os.getenv("DEEPSEEK_API_KEY"):
        provider = "deepseek"
        model = "deepseek-chat"
    elif os.getenv("OPENAI_API_KEY"):
        provider = "openai"
        model = "gpt-4"
    elif os.getenv("ANTHROPIC_API_KEY"):
        provider = "anthropic"
        model = "claude-3-sonnet-20240229"
    else:
        raise ValueError("No API key found. Please set DEEPSEEK_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
    
    agent = LangChainReactAgent(
        llm_provider=provider,
        model_name=model,
        verbose=True
    )
    
    # Add basic tools
    tools = get_basic_tools()
    agent.add_tools(tools)
    
    return agent


if __name__ == "__main__":
    # Example usage
    console.print("[bold green]🤖 LangChain ReAct Agent Example[/bold green]")
    
    try:
        agent = create_basic_react_agent()
        
        # Display available tools
        console.print("\n")
        console.print(agent.list_tools())
        
        # Example question
        question = "What is the weather like in San Francisco and what is 25 * 4?"
        result = agent.run(question)
        
        console.print(f"\n[bold green]Final Result:[/bold green] {result}")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print("Make sure to set up your environment variables (OPENAI_API_KEY or ANTHROPIC_API_KEY)")