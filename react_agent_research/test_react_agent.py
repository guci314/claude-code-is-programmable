#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pytest>=7.0.0",
#   "pytest-mock>=3.10.0",
#   "langchain>=0.1.0",
#   "langchain-openai>=0.1.0",
#   "python-dotenv>=1.0.0",
#   "rich>=13.0.0",
#   "requests>=2.31.0",
# ]
# ///

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

# Import the modules we're testing
from react_agent_tools import (
    WebSearchTool, CodeAnalysisTool, FileSystemTool, 
    CalculatorTool, PythonREPLTool, APITool, DatabaseTool,
    get_basic_tools, get_advanced_tools
)

class TestWebSearchTool:
    """Test the WebSearchTool"""
    
    def test_init(self):
        """Test WebSearchTool initialization"""
        tool = WebSearchTool()
        assert tool.name == "web_search"
        assert "search" in tool.description.lower()
    
    @patch('requests.get')
    def test_search_with_abstract(self, mock_get):
        """Test search with abstract response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Abstract': 'Python is a programming language',
            'AbstractURL': 'https://example.com'
        }
        mock_get.return_value = mock_response
        
        tool = WebSearchTool()
        result = tool.search("Python programming")
        
        assert "Python is a programming language" in result
        assert "https://example.com" in result
    
    @patch('requests.get')
    def test_search_with_definition(self, mock_get):
        """Test search with definition response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Definition': 'Python: A high-level programming language',
            'DefinitionURL': 'https://example.com/def'
        }
        mock_get.return_value = mock_response
        
        tool = WebSearchTool()
        result = tool.search("Python")
        
        assert "Python: A high-level programming language" in result
        assert "https://example.com/def" in result
    
    @patch('requests.get')
    def test_search_network_error(self, mock_get):
        """Test search with network error"""
        mock_get.side_effect = Exception("Network error")
        
        tool = WebSearchTool()
        result = tool.search("test query")
        
        assert "Search error" in result
        assert "Network error" in result


class TestCodeAnalysisTool:
    """Test the CodeAnalysisTool"""
    
    def test_init(self):
        """Test CodeAnalysisTool initialization"""
        tool = CodeAnalysisTool()
        assert tool.name == "code_analysis"
        assert "analyze" in tool.description.lower()
    
    def test_analyze_nonexistent_path(self):
        """Test analyzing a non-existent path"""
        tool = CodeAnalysisTool()
        result = tool.analyze("/nonexistent/path")
        
        assert "does not exist" in result
    
    def test_analyze_file(self):
        """Test analyzing a Python file"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello():
    print("Hello, World!")

class TestClass:
    def method(self):
        pass

import os
from pathlib import Path
""")
            temp_file = f.name
        
        try:
            tool = CodeAnalysisTool()
            result = tool.analyze(temp_file)
            
            assert "File Analysis" in result
            assert "Functions: 2" in result  # hello() and method()
            assert "Classes: 1" in result
            assert "Imports: 2" in result
        finally:
            os.unlink(temp_file)
    
    def test_analyze_directory(self):
        """Test analyzing a directory"""
        # Create a temporary directory with Python files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python files
            (Path(temp_dir) / "file1.py").write_text("def func1(): pass")
            (Path(temp_dir) / "file2.py").write_text("class MyClass: pass")
            (Path(temp_dir) / "file3.txt").write_text("Not a code file")
            
            tool = CodeAnalysisTool()
            result = tool.analyze(temp_dir)
            
            assert "Directory Analysis" in result
            assert "Code files: 2" in result
            assert ".py: 2 files" in result


class TestFileSystemTool:
    """Test the FileSystemTool"""
    
    def test_init(self):
        """Test FileSystemTool initialization"""
        tool = FileSystemTool()
        assert tool.name == "file_system"
        assert "read" in tool.description.lower() and "write" in tool.description.lower()
    
    def test_invalid_operation_format(self):
        """Test invalid operation format"""
        tool = FileSystemTool()
        result = tool.operate("invalid")
        
        assert "Invalid operation format" in result
    
    def test_read_file(self):
        """Test reading a file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            temp_file = f.name
        
        try:
            tool = FileSystemTool()
            result = tool.operate(f"read:{temp_file}")
            
            assert "Hello, World!" in result
        finally:
            os.unlink(temp_file)
    
    def test_write_file(self):
        """Test writing a file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")
            
            tool = FileSystemTool()
            result = tool.operate(f"write:{file_path}:Hello, Test!")
            
            assert "Successfully wrote" in result
            
            # Verify file was written
            with open(file_path, 'r') as f:
                content = f.read()
            assert content == "Hello, Test!"
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file"""
        tool = FileSystemTool()
        result = tool.operate("read:/nonexistent/file.txt")
        
        assert "does not exist" in result
    
    def test_security_check(self):
        """Test security check prevents reading outside current directory"""
        tool = FileSystemTool()
        result = tool.operate("read:../../../etc/passwd")
        
        assert "Access denied" in result


class TestCalculatorTool:
    """Test the CalculatorTool"""
    
    def test_init(self):
        """Test CalculatorTool initialization"""
        tool = CalculatorTool()
        assert tool.name == "calculator"
        assert "mathematical" in tool.description.lower()
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations"""
        tool = CalculatorTool()
        
        # Addition
        result = tool.calculate("2 + 3")
        assert "2 + 3 = 5" in result
        
        # Multiplication
        result = tool.calculate("4 * 5")
        assert "4 * 5 = 20" in result
        
        # Division
        result = tool.calculate("10 / 2")
        assert "10 / 2 = 5" in result
    
    def test_complex_expression(self):
        """Test complex mathematical expression"""
        tool = CalculatorTool()
        result = tool.calculate("(2 + 3) * 4")
        
        assert "= 20" in result
    
    def test_division_by_zero(self):
        """Test division by zero error"""
        tool = CalculatorTool()
        result = tool.calculate("1 / 0")
        
        assert "Division by zero" in result
    
    def test_invalid_characters(self):
        """Test invalid characters in expression"""
        tool = CalculatorTool()
        result = tool.calculate("2 + import")
        
        assert "invalid characters" in result
    
    def test_dangerous_operations(self):
        """Test dangerous operations are blocked"""
        tool = CalculatorTool()
        result = tool.calculate("__import__('os')")
        
        assert "Dangerous operation" in result


class TestPythonREPLTool:
    """Test the PythonREPLTool"""
    
    def test_init(self):
        """Test PythonREPLTool initialization"""
        tool = PythonREPLTool()
        assert tool.name == "python_repl"
        assert "python" in tool.description.lower()
    
    def test_simple_execution(self):
        """Test simple Python code execution"""
        tool = PythonREPLTool()
        result = tool.execute("print('Hello, World!')")
        
        assert "Hello, World!" in result
    
    def test_mathematical_computation(self):
        """Test mathematical computation"""
        tool = PythonREPLTool()
        result = tool.execute("result = 2 + 3\nprint(result)")
        
        assert "5" in result
    
    def test_dangerous_operations_blocked(self):
        """Test dangerous operations are blocked"""
        tool = PythonREPLTool()
        
        # Test dangerous imports
        result = tool.execute("import os")
        assert "Dangerous operation" in result
        
        # Test dangerous functions
        result = tool.execute("exec('print(1)')")
        assert "Dangerous operation" in result
    
    def test_syntax_error(self):
        """Test syntax error handling"""
        tool = PythonREPLTool()
        result = tool.execute("print('unclosed string")
        
        assert "execution error" in result


class TestAPITool:
    """Test the APITool"""
    
    def test_init(self):
        """Test APITool initialization"""
        tool = APITool()
        assert tool.name == "api_request"
        assert "http" in tool.description.lower()
    
    def test_invalid_request_format(self):
        """Test invalid request format"""
        tool = APITool()
        result = tool.request("invalid")
        
        assert "Invalid request format" in result
    
    @patch('requests.get')
    def test_get_request(self, mock_get):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_get.return_value = mock_response
        
        tool = APITool()
        result = tool.request("GET:https://api.example.com/data")
        
        assert "Status: 200" in result
        assert '{"success": true}' in result
    
    @patch('requests.post')
    def test_post_request(self, mock_post):
        """Test POST request"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"created": true}'
        mock_post.return_value = mock_response
        
        tool = APITool()
        result = tool.request('POST:https://api.example.com/create:{"name": "test"}')
        
        assert "Status: 201" in result
        assert '{"created": true}' in result
    
    def test_invalid_json_data(self):
        """Test invalid JSON data for POST request"""
        tool = APITool()
        result = tool.request("POST:https://api.example.com/create:invalid json")
        
        assert "Invalid JSON data" in result


class TestDatabaseTool:
    """Test the DatabaseTool"""
    
    def test_init(self):
        """Test DatabaseTool initialization"""
        tool = DatabaseTool()
        assert tool.name == "database"
        assert "database" in tool.description.lower()
    
    def test_invalid_operation_format(self):
        """Test invalid operation format"""
        tool = DatabaseTool()
        result = tool.operate("invalid")
        
        assert "Invalid operation format" in result
    
    def test_create_table(self):
        """Test creating a table"""
        tool = DatabaseTool()
        result = tool.operate("CREATE:test_table")
        
        assert "Created table: test_table" in result
    
    def test_unknown_operation(self):
        """Test unknown operation"""
        tool = DatabaseTool()
        result = tool.operate("UNKNOWN:operation")
        
        assert "Unknown operation" in result


class TestToolIntegration:
    """Test tool integration and basic_tools function"""
    
    def test_get_basic_tools(self):
        """Test getting basic tools"""
        tools = get_basic_tools()
        
        assert len(tools) == 7  # Should have 7 basic tools
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "web_search", "code_analysis", "file_system", 
            "calculator", "python_repl", "api_request", "database"
        ]
        
        for expected in expected_tools:
            assert expected in tool_names
    
    def test_get_advanced_tools(self):
        """Test getting advanced tools"""
        tools = get_advanced_tools()
        
        # Should at least have the basic tools
        assert len(tools) >= 7
        tool_names = [tool.name for tool in tools]
        
        # Should include basic tools
        basic_tools = ["web_search", "code_analysis", "file_system", "calculator"]
        for basic in basic_tools:
            assert basic in tool_names
    
    def test_all_tools_have_required_attributes(self):
        """Test that all tools have required attributes"""
        tools = get_basic_tools()
        
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'func')
            assert tool.name is not None
            assert tool.description is not None
            assert callable(tool.func)


# Integration tests (require actual API keys)
class TestAgentIntegration:
    """Integration tests for the complete agent"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"),
        reason="No API keys available for integration tests"
    )
    def test_agent_creation(self):
        """Test creating an agent with tools"""
        from langchain_react_agent import LangChainReactAgent
        
        # Try OpenAI first, then Anthropic
        if os.getenv("OPENAI_API_KEY"):
            agent = LangChainReactAgent(
                llm_provider="openai",
                model_name="gpt-3.5-turbo",
                verbose=False
            )
        else:
            agent = LangChainReactAgent(
                llm_provider="anthropic",
                model_name="claude-3-haiku-20240307",
                verbose=False
            )
        
        tools = get_basic_tools()
        agent.add_tools(tools)
        
        assert agent.agent is not None
        assert agent.agent_executor is not None
        assert len(agent.tools) == 7


def run_tests():
    """Run all tests"""
    print("🧪 Running ReAct Agent Tests...")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_tests()
    exit(exit_code)