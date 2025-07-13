#!/usr/bin/env -S uv run --script

import subprocess

import os

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890" 
os.environ["NO_PROXY"] = "localhost,127.0.0.1"



prompt = """
修改hello1.py，让它输出"Hello, World 123"
"""


command = ["claude", "-p", prompt, "--allowedTools", "Edit", "Bash", "Write"]

# Capture Claude's output so we can display it
process = subprocess.run(
    command,
    check=True,
    capture_output=True,
    text=True,
)

print(f"Claude process exited with output: {process.stdout}")
