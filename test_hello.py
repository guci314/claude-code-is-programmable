import pytest
from hello import hello
import io
import sys

def test_hello_function_output(capsys):
    """Test that hello() prints 'hello world'"""
    hello()
    captured = capsys.readouterr()
    assert captured.out.strip() == "hello world"

def test_main_execution_output():
    """Test that main execution prints both messages"""
    import subprocess
    result = subprocess.run(
        ["python", "hello.py"], 
        capture_output=True, 
        text=True
    )
    output_lines = result.stdout.splitlines()
    assert len(output_lines) == 2
    assert output_lines[0] == "hello, world!"
    assert output_lines[1] == "hello world"

def test_hello_docstring():
    """Test that hello() has the correct docstring"""
    assert hello.__doc__ == "打印问候语"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
