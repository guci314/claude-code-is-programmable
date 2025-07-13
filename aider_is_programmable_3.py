#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "python-dotenv"
# ]
# ///

import subprocess
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the target file
hello_file = "./hello1.py"

try:
    # Run aider directly to create hello world program with DeepSeek model
    print("Running aider with DeepSeek model to create hello world program...")
    aider_cmd = [
        "aider",
        "--no-git",  # We'll handle git ourselves if needed
        "--model", "deepseek/deepseek-chat",  # Use DeepSeek model
        hello_file,
        "--message",
        "CREATE ./hello1.py: a simple hello world program in Python with a main function.",
    ]
    
    # Set up environment with DeepSeek API key
    env = os.environ.copy()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_api_key:
        env["DEEPSEEK_API_KEY"] = deepseek_api_key
        print("Using DeepSeek API key from .env file")
    else:
        print("Warning: DEEPSEEK_API_KEY not found in .env file")
    
    subprocess.run(aider_cmd, env=env, check=True)

    print(f"Task completed. Hello world program created in: {hello_file}")

    # Optionally display the created file
    if os.path.exists(hello_file):
        print(f"\nContent of {hello_file}:")
        with open(hello_file, 'r') as f:
            print(f.read())

except subprocess.CalledProcessError as e:
    print(f"Aider command failed: {e}")
except Exception as e:
    print(f"Error: {e}")