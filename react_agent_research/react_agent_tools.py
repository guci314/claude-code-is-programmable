#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "langchain>=0.1.0",
#   "requests>=2.31.0",
#   "beautifulsoup4>=4.12.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "sqlite3",
# ]
# ///

import os
import re
import json
import sqlite3
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from langchain.tools import Tool
from rich.console import Console

console = Console()

class WebSearchTool:
    """Tool for searching and extracting information from web"""
    
    def __init__(self):
        self.name = "web_search"
        self.description = "Search the web for information. Input should be a search query string."
    
    def search(self, query: str) -> str:
        """Search the web using a simple search engine"""
        try:
            # Using DuckDuckGo Instant Answer API as a simple search
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract abstract if available
                if data.get('Abstract'):
                    return f"Search Results for '{query}':\n{data['Abstract']}\nSource: {data.get('AbstractURL', 'Unknown')}"
                
                # Extract definition if available
                if data.get('Definition'):
                    return f"Definition for '{query}':\n{data['Definition']}\nSource: {data.get('DefinitionURL', 'Unknown')}"
                
                # Extract instant answer if available
                if data.get('Answer'):
                    return f"Answer for '{query}':\n{data['Answer']}"
                
                # Extract related topics
                if data.get('RelatedTopics'):
                    topics = []
                    for topic in data['RelatedTopics'][:3]:  # Limit to 3 topics
                        if isinstance(topic, dict) and 'Text' in topic:
                            topics.append(topic['Text'])
                    
                    if topics:
                        return f"Related information for '{query}':\n" + "\n".join(topics)
                
                return f"No specific information found for '{query}'. Try a more specific search term."
            
            return f"Search failed with status code: {response.status_code}"
        
        except Exception as e:
            return f"Search error: {str(e)}"


class CodeAnalysisTool:
    """Tool for analyzing code files and directories"""
    
    def __init__(self):
        self.name = "code_analysis"
        self.description = "Analyze code files and directories. Input should be a file path or directory path."
    
    def analyze(self, path: str) -> str:
        """Analyze code at the given path"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return f"Path does not exist: {path}"
            
            if path_obj.is_file():
                return self._analyze_file(path_obj)
            elif path_obj.is_dir():
                return self._analyze_directory(path_obj)
            else:
                return f"Invalid path type: {path}"
        
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def _analyze_file(self, file_path: Path) -> str:
        """Analyze a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            analysis = {
                'file': str(file_path),
                'lines': len(lines),
                'size': len(content),
                'extension': file_path.suffix,
                'functions': self._count_functions(content, file_path.suffix),
                'classes': self._count_classes(content, file_path.suffix),
                'imports': self._count_imports(content, file_path.suffix)
            }
            
            result = f"File Analysis: {file_path.name}\n"
            result += f"Lines: {analysis['lines']}\n"
            result += f"Size: {analysis['size']} bytes\n"
            result += f"Functions: {analysis['functions']}\n"
            result += f"Classes: {analysis['classes']}\n"
            result += f"Imports: {analysis['imports']}\n"
            
            return result
        
        except Exception as e:
            return f"File analysis error: {str(e)}"
    
    def _analyze_directory(self, dir_path: Path) -> str:
        """Analyze a directory"""
        try:
            files = list(dir_path.glob('**/*'))
            code_files = [f for f in files if f.is_file() and f.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']]
            
            result = f"Directory Analysis: {dir_path.name}\n"
            result += f"Total files: {len([f for f in files if f.is_file()])}\n"
            result += f"Code files: {len(code_files)}\n"
            result += f"Subdirectories: {len([f for f in files if f.is_dir()])}\n"
            
            if code_files:
                result += "\nCode files by type:\n"
                extensions = {}
                for file in code_files:
                    ext = file.suffix
                    extensions[ext] = extensions.get(ext, 0) + 1
                
                for ext, count in extensions.items():
                    result += f"  {ext}: {count} files\n"
            
            return result
        
        except Exception as e:
            return f"Directory analysis error: {str(e)}"
    
    def _count_functions(self, content: str, extension: str) -> int:
        """Count functions in code"""
        if extension == '.py':
            return len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
        elif extension in ['.js', '.ts']:
            return len(re.findall(r'function\s+\w+|^\s*\w+\s*:\s*function|\w+\s*=\s*function', content, re.MULTILINE))
        return 0
    
    def _count_classes(self, content: str, extension: str) -> int:
        """Count classes in code"""
        if extension == '.py':
            return len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
        elif extension in ['.js', '.ts']:
            return len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
        return 0
    
    def _count_imports(self, content: str, extension: str) -> int:
        """Count imports in code"""
        if extension == '.py':
            return len(re.findall(r'^(?:import|from)\s+', content, re.MULTILINE))
        elif extension in ['.js', '.ts']:
            return len(re.findall(r'^import\s+', content, re.MULTILINE))
        return 0


class FileSystemTool:
    """Tool for safe file system operations"""
    
    def __init__(self):
        self.name = "file_system"
        self.description = "Read or write files safely. Input format: 'read:path' or 'write:path:content'"
    
    def operate(self, operation: str) -> str:
        """Perform file system operation"""
        try:
            parts = operation.split(':', 2)
            
            if len(parts) < 2:
                return "Invalid operation format. Use 'read:path' or 'write:path:content'"
            
            op_type = parts[0].lower()
            path = parts[1]
            
            if op_type == 'read':
                return self._read_file(path)
            elif op_type == 'write':
                if len(parts) < 3:
                    return "Write operation requires content. Use 'write:path:content'"
                content = parts[2]
                return self._write_file(path, content)
            else:
                return f"Unknown operation: {op_type}. Use 'read' or 'write'"
        
        except Exception as e:
            return f"File system error: {str(e)}"
    
    def _read_file(self, path: str) -> str:
        """Read a file safely"""
        try:
            # Security check - prevent reading outside current directory
            path_obj = Path(path).resolve()
            current_dir = Path.cwd().resolve()
            
            if not str(path_obj).startswith(str(current_dir)):
                return "Access denied: Cannot read files outside current directory"
            
            if not path_obj.exists():
                return f"File does not exist: {path}"
            
            if path_obj.is_dir():
                return f"Path is a directory, not a file: {path}"
            
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"File content of {path}:\n{content}"
        
        except Exception as e:
            return f"Read error: {str(e)}"
    
    def _write_file(self, path: str, content: str) -> str:
        """Write a file safely"""
        try:
            # Security check - prevent writing outside current directory
            path_obj = Path(path).resolve()
            current_dir = Path.cwd().resolve()
            
            if not str(path_obj).startswith(str(current_dir)):
                return "Access denied: Cannot write files outside current directory"
            
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote to {path}"
        
        except Exception as e:
            return f"Write error: {str(e)}"


class CalculatorTool:
    """Tool for mathematical calculations"""
    
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform mathematical calculations. Input should be a mathematical expression."
    
    def calculate(self, expression: str) -> str:
        """Perform calculation safely"""
        try:
            # Security: only allow safe mathematical operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Expression contains invalid characters"
            
            # Prevent potentially dangerous operations
            dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open', 'file']
            for pattern in dangerous_patterns:
                if pattern in expression.lower():
                    return f"Error: Dangerous operation detected: {pattern}"
            
            result = eval(expression)
            return f"Result: {expression} = {result}"
        
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Calculation error: {str(e)}"


class PythonREPLTool:
    """Tool for executing Python code safely"""
    
    def __init__(self):
        self.name = "python_repl"
        self.description = "Execute Python code safely. Input should be Python code to execute."
    
    def execute(self, code: str) -> str:
        """Execute Python code safely"""
        try:
            # Security checks
            dangerous_imports = ['os', 'sys', 'subprocess', 'shutil', 'glob', 'pathlib']
            dangerous_functions = ['open', 'exec', 'eval', 'compile', '__import__']
            
            code_lower = code.lower()
            for danger in dangerous_imports + dangerous_functions:
                if danger in code_lower:
                    return f"Error: Dangerous operation detected: {danger}"
            
            # Create a restricted environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                }
            }
            
            # Capture output
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, safe_globals)
            
            result = output.getvalue()
            return f"Python execution result:\n{result}" if result else "Code executed successfully (no output)"
        
        except Exception as e:
            return f"Python execution error: {str(e)}"


class APITool:
    """Tool for making HTTP requests to external APIs"""
    
    def __init__(self):
        self.name = "api_request"
        self.description = "Make HTTP requests to APIs. Input format: 'GET:url' or 'POST:url:json_data'"
    
    def request(self, request_info: str) -> str:
        """Make HTTP request"""
        try:
            parts = request_info.split(':', 2)
            
            if len(parts) < 2:
                return "Invalid request format. Use 'GET:url' or 'POST:url:json_data'"
            
            method = parts[0].upper()
            url = parts[1]
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
                return f"GET {url}\nStatus: {response.status_code}\nResponse: {response.text[:500]}"
            
            elif method == 'POST':
                if len(parts) < 3:
                    return "POST request requires data. Use 'POST:url:json_data'"
                
                data = json.loads(parts[2])
                response = requests.post(url, json=data, timeout=10)
                return f"POST {url}\nStatus: {response.status_code}\nResponse: {response.text[:500]}"
            
            else:
                return f"Unsupported method: {method}. Use GET or POST"
        
        except json.JSONDecodeError:
            return "Error: Invalid JSON data for POST request"
        except requests.RequestException as e:
            return f"Request error: {str(e)}"
        except Exception as e:
            return f"API request error: {str(e)}"


class DatabaseTool:
    """Tool for simple SQLite database operations"""
    
    def __init__(self):
        self.name = "database"
        self.description = "Perform SQLite database operations. Input format: 'CREATE:table_name' or 'SELECT:query' or 'INSERT:table:data'"
    
    def operate(self, operation: str) -> str:
        """Perform database operation"""
        try:
            parts = operation.split(':', 2)
            
            if len(parts) < 2:
                return "Invalid operation format"
            
            op_type = parts[0].upper()
            
            # Use in-memory database for safety
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            
            if op_type == 'CREATE':
                table_name = parts[1]
                cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, data TEXT)")
                conn.commit()
                return f"Created table: {table_name}"
            
            elif op_type == 'SELECT':
                query = parts[1]
                cursor.execute(query)
                results = cursor.fetchall()
                return f"Query results: {results}"
            
            elif op_type == 'INSERT':
                if len(parts) < 3:
                    return "INSERT operation requires table and data"
                
                table_name = parts[1]
                data = parts[2]
                cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (data,))
                conn.commit()
                return f"Inserted data into {table_name}"
            
            else:
                return f"Unknown operation: {op_type}"
        
        except Exception as e:
            return f"Database error: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()


def get_basic_tools() -> List[Tool]:
    """Get a list of basic tools for the ReAct agent"""
    
    # Initialize tool instances
    web_search = WebSearchTool()
    code_analysis = CodeAnalysisTool()
    file_system = FileSystemTool()
    calculator = CalculatorTool()
    python_repl = PythonREPLTool()
    api_tool = APITool()
    database = DatabaseTool()
    
    # Create LangChain Tool objects
    tools = [
        Tool(
            name=web_search.name,
            description=web_search.description,
            func=web_search.search
        ),
        Tool(
            name=code_analysis.name,
            description=code_analysis.description,
            func=code_analysis.analyze
        ),
        Tool(
            name=file_system.name,
            description=file_system.description,
            func=file_system.operate
        ),
        Tool(
            name=calculator.name,
            description=calculator.description,
            func=calculator.calculate
        ),
        Tool(
            name=python_repl.name,
            description=python_repl.description,
            func=python_repl.execute
        ),
        Tool(
            name=api_tool.name,
            description=api_tool.description,
            func=api_tool.request
        ),
        Tool(
            name=database.name,
            description=database.description,
            func=database.operate
        )
    ]
    
    return tools


def get_advanced_tools() -> List[Tool]:
    """Get a list of advanced tools with additional capabilities"""
    basic_tools = get_basic_tools()
    
    # Add more advanced tools here as needed
    # For example: image processing, PDF reading, etc.
    
    return basic_tools


if __name__ == "__main__":
    # Test the tools
    console.print("[bold green]🛠️ Testing ReAct Agent Tools[/bold green]")
    
    tools = get_basic_tools()
    
    console.print(f"\n[bold cyan]Available Tools: {len(tools)}[/bold cyan]")
    for tool in tools:
        console.print(f"- {tool.name}: {tool.description}")
    
    # Test calculator
    calc = CalculatorTool()
    result = calc.calculate("2 + 3 * 4")
    console.print(f"\n[bold yellow]Calculator test:[/bold yellow] {result}")
    
    # Test web search
    web = WebSearchTool()
    result = web.search("Python programming language")
    console.print(f"\n[bold yellow]Web search test:[/bold yellow] {result[:200]}...")
    
    console.print("\n[bold green]✅ Tools testing completed[/bold green]")