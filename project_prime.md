# Project Prime Data Export

*Generated from project:prime command on 2025-06-15*

## Project File Structure

```
./.aider.chat.history.md
./aider_is_programmable_1.sh
./aider_is_programmable_2.js
./aider_is_programmable_2.py
./aider_is_programmable_3.py
./ai_docs/anthropic_web_search_tool.md
./ai_docs/claude_code_best_practices.md
./ai_docs/claude_code_tech.md
./ai_docs/claude-code-tutorials.md
./ai_docs/fc_openai_agents.md
./ai_docs/uv-single-file-scripts.md
./anthropic_search.py
./bonus/claude_code_inside_openai_agent_sdk_4_bonus.py
./bonus/starter_notion_agent.py
./claude_code_is_programmable_1.sh
./claude_code_is_programmable_2.js
./claude_code_is_programmable_2.py
./claude_code_is_programmable_3.py
./claude_code_is_programmable_4.py
./claude_code_tutorial.md
./.claude/commands/prime.md
./CLAUDE.md
./.claude/settings.local.json
./claude_testing_v1.py
./hello1.py
./hello.py
./.mcp.sample.json
./.pytest_cache/README.md
./README.md
./repomap.json
./repository_summary.md
./reset.sh
./test_hello.py
./tests/test_claude_testing_v1.py
./voice_to_claude_code.py
```

## README.md Content

```markdown
# Claude Code 可编程项目

本仓库展示如何以编程方式使用 Claude Code，提供多种编程语言的示例。观看[此视频](https://youtu.be/2TIXl2rlA6Q)了解这对下一代工程的重要性。查看[语音转Claude Code](https://youtu.be/LvkZuY7rJOM)视频了解如何使用`voice_to_claude_code.py`脚本。

<img src="images/voice-to-claude-code.png" alt="语音转Claude Code" width="800">
<img src="images/programmable-agentic-coding.png" alt="Claude Code可编程" width="800">

## 项目概述

Claude Code 是一个可编程的 AI 编码工具，支持：
1. 通过自然语言调用任何工具
2. 多种输出格式（文本、JSON、流式 JSON）
3. 与外部服务（如 Notion）集成
4. 语音交互功能
5. 自定义工作流和命令

## 核心功能

*   **编程化 AI 交互**：通过 CLI 和 Python/JS API 与 AI 交互
*   **代码生成**：支持 JavaScript、TypeScript 等多种语言
*   **任务自动化**：与 Notion 集成实现任务管理自动化
*   **AI 网页搜索**：带引用和域名过滤的智能搜索
*   **语音编程**：语音转 Claude Code 操作
*   **多工具并行**：通过 Git worktrees 实现并行处理
*   **自定义命令**：创建项目专属的 slash 命令

## 快速开始

```bash
# Claude Code example (with only Write and Edit tools allowed)
claude -p "make a hello.js script that prints hello" --allowedTools "Write" "Edit"

# Aider equivalent example
aider --message "make a hello.js script that prints hello" hello.js
```

Here's the big trick - with Claude Code, you can call ANY TOOL IN ANY ORDER IN NATURAL LANGUAGE.

Check out the other examples in the repo to understand how to scale your impact with this feature.

Watch [this video](https://youtu.be/2TIXl2rlA6Q) to internalize how important this is for next generation engineering. View the brief anthropic documentation [here](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/tutorials#use-claude-as-a-unix-style-utility) and a more comprehensive write up on [agentic coding here](https://www.anthropic.com/engineering/claude-code-best-practices). The Claude Code team is doing incredible work.

You can also use [Aider](https://aider.chat/) as a programmable ai coding tool to do similar things although it's strictly limited to AI Coding (which is still incredibly useful). Check out the documentation [here](https://aider.chat/docs/scripting.html).

## Setup

### Configuration Files

1. **MCP (Multi-call Protocol) Configuration**
   - Copy the sample configuration file to create your own:
     ```bash
     cp .mcp.sample.json .mcp.json
     ```
   - Edit `.mcp.json` to add your Notion API key in the `OPENAPI_MCP_HEADERS` section:
     ```json
     {
       "mcpServers": {
         "notionApi": {
           "command": "npx",
           "args": ["-y", "@notionhq/notion-mcp-server"],
           "env": {
             "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer YOUR_NOTION_API_KEY\", \"Notion-Version\": \"2022-06-28\" }"
           }
         }
       }
     }
     ```

2. **Environment Variables**
   - Copy the sample environment file:
     ```bash
     cp .env.sample .env
     ```
   - Add the following API keys to your `.env` file:
     ```
     NOTION_INTERNAL_INTEGRATION_SECRET=your_notion_integration_secret
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
   - Note: The voice_to_claude_code.py script specifically requires both ANTHROPIC_API_KEY and OPENAI_API_KEY to be set.
   - The anthropic_search.py script requires ANTHROPIC_API_KEY to be set.

## File Descriptions

### Shell Scripts
- `claude_code_is_programmable_1.sh`: Simple shell script that uses Claude Code's CLI to generate a basic "hello.js" script with limited allowed tools.
  ```bash
  sh claude_code_is_programmable_1.sh
  ```
- `aider_is_programmable_1.sh`: Similar script using Aider to create a "hello.js" file.
  ```bash
  sh aider_is_programmable_1.sh
  ```
- `reset.sh`: Utility script to clean up branches and directories created by the demo scripts.
  ```bash
  sh reset.sh
  ```

### Python Files
- `claude_code_is_programmable_2.py`: Python script that executes Claude Code to create a TypeScript CLI todo app, with permissions for Edit, Replace, Bash, and Create tools.
  ```bash
  uv run claude_code_is_programmable_2.py
  ```
- `claude_code_is_programmable_3.py`: Advanced Python script integrating Claude Code with Notion API for todo management, including rich console output and streaming results. Requires a Notion page name as an argument.
  ```bash
  uv run claude_code_is_programmable_3.py "My Notion Page"
  ```
- `aider_is_programmable_2.py`: Python script that uses Aider to create a TypeScript todo application with git operations.
  ```bash
  uv run aider_is_programmable_2.py
  ```
- `anthropic_search.py`: A self-contained Python script for searching the web using Anthropic's Claude AI with web search capabilities.
  ```bash
  ./anthropic_search.py "your search query"
  ```

### JavaScript Files
- `claude_code_is_programmable_2.js`: JavaScript version of the Claude Code script that creates a TypeScript todo app, with permissions for Edit, Replace, Bash, and Create tools.
  ```bash
  bun claude_code_is_programmable_2.js
  ```
- `aider_is_programmable_2.js`: JavaScript version of the Aider script for creating a TypeScript todo app with git operations.
  ```bash
  bun aider_is_programmable_2.js
  ```

### Voice to Claude Code
- `voice_to_claude_code.py`: A voice-enabled Claude Code assistant that allows you to interact with Claude Code using speech commands. Combines RealtimeSTT for speech recognition and OpenAI TTS for speech output.
  ```bash
  uv run voice_to_claude_code.py

  # With a specific conversation ID
  uv run voice_to_claude_code.py --id "my-chat-id"

  # With an initial prompt
  uv run voice_to_claude_code.py --prompt "create a hello world script"

  # With both ID and prompt
  uv run voice_to_claude_code.py --id "my-chat-id" --prompt "create a hello world script"
  ```

### Bonus Directory
- `starter_notion_agent.py`: A starter template for creating a Notion agent using the OpenAI Agent SDK.
  ```bash
  uv run bonus/starter_notion_agent.py
  ```
- `claude_code_inside_openai_agent_sdk_4_bonus.py`: An advanced implementation that integrates Claude Code within the OpenAI Agent SDK. Requires a Notion page name as an argument.
  ```bash
  uv run bonus/claude_code_inside_openai_agent_sdk_4_bonus.py "My Notion Page"
  ```

## Core Tools Available in Claude Code

- Task: Launch an agent to perform complex tasks
- Bash: Execute bash commands in a shell
- Batch: Run multiple tools in parallel
- Glob: Find files matching patterns
- Grep: Search file contents with regex
- LS: **List** directory contents
- Read: Read file contents
- Edit: Make targeted edits to files
- Write: Create or overwrite files
- NotebookRead/Edit: Work with Jupyter notebooks
- WebFetch: Get content from websites

## Claude Code response formats

```sh
claude -p 'hello, run git ls-files, how many files are in the current directory' --output-format text > test.txt
claude -p 'hello, run git ls-files, how many files are in the current directory' --output-format json > test.json
claude -p --continue 'hello, run git ls-files, how many files are in the current directory' --output-format stream-json > test.stream.json
```

## Anthropic Web Search Tool
> See the [anthropic_search.py](anthropic_search.py) file for more details.

A command-line utility for searching the web using Anthropic's Claude AI with their web search tool capability.

### Prerequisites

- Python 3.8+
- UV package manager (`pip install uv`)
- Anthropic API key

### Setup

Make the script executable:
```
chmod +x anthropic_search.py
```

### Usage

Basic search:
```
./anthropic_search.py "your search query"
```

With domain filtering (only include results from these domains):
```
./anthropic_search.py "javascript best practices" --domains "developer.mozilla.org,javascript.info"
```

Block specific domains:
```
./anthropic_search.py "climate change" --blocked "unreliablesource.com,fakenews.org"
```

With location context:
```
./anthropic_search.py "local restaurants" --location "US,California,San Francisco" --timezone "America/Los_Angeles"
```

Increase maximum searches:
```
./anthropic_search.py "complex research topic" --max-uses 5
```

Use a different Claude model:
```
./anthropic_search.py "your query" --model "claude-3-5-sonnet-latest"
```

### Output

The script produces:
1. The search query used
2. Claude's response with inline citations marked as [1], [2], etc.
3. A list of sources at the end, numbered to match the citations
4. Usage information showing how many web searches were performed

### Notes

- Web search is available on Claude 3.7 Sonnet, Claude 3.5 Sonnet, and Claude 3.5 Haiku
- Each search counts as one use, regardless of the number of results returned
- Searches cost $10 per 1,000 searches, plus standard token costs for search-generated content
- Domain filtering doesn't need https:// prefixes and automatically includes subdomains

Built with ❤️ by [IndyDevDan](https://www.youtube.com/@indydevdan) with [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), and [Principled AI Coding](https://agenticengineer.com/principled-ai-coding)
```

## Aider Scripts Analysis

### aider_is_programmable_2.py
**Purpose**: Creates TypeScript todo app with git workflow
**Key Features**:
- Creates new git branch `feature-todo-app`
- Uses Aider to generate TypeScript CLI todo app with CRUD operations
- Automatically commits changes and returns to main branch
- Error handling with branch recovery

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

import subprocess
import os

# Create directory if it doesn't exist
todo_dir = "./cc_todo"
os.makedirs(todo_dir, exist_ok=True)
todo_file = f"{todo_dir}/todo.ts"

# Generate a random branch name
branch_name = f"feature-todo-app"

try:
    # 1. Create and checkout a new branch
    print(f"Creating and checking out new branch: {branch_name}")
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)

    # 2. Run aider directly with the todo task
    print("Running aider to create todo app...")
    aider_cmd = [
        "aider",
        "--no-git",  # We'll handle git ourselves
        todo_file,
        "--message",
        "CREATE ./cc_todo/todo.ts: a zero library CLI todo app with basic CRUD.",
    ]
    subprocess.run(aider_cmd, check=True)

    # 3. Git operations - stage and commit
    print("Staging and committing changes...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add TypeScript todo app with CRUD functionality"],
        check=True,
    )

    # 4. Switch back to main branch
    print("Switching back to main branch...")
    subprocess.run(["git", "checkout", "main"], check=True)

    print(f"Task completed. Changes committed to branch: {branch_name}")

except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")
except Exception as e:
    print(f"Error: {e}")
    # Try to return to main branch if something went wrong
    try:
        subprocess.run(["git", "checkout", "main"], check=True)
    except:
        pass
```

### aider_is_programmable_3.py
**Purpose**: Creates hello world program using DeepSeek model
**Key Features**:
- Uses DeepSeek AI model instead of default
- Loads API key from .env file
- No git branch switching - works on current branch
- Displays created file content

```python
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
```

## Claude Code Scripts Analysis

### claude_code_is_programmable_2.py
**Purpose**: Simple Claude Code invocation with proxy settings
**Key Features**:
- HTTP proxy configuration
- Basic prompt execution
- Tool restrictions (Edit, Bash, Write)

```python
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
```

### claude_code_is_programmable_3.py
**Purpose**: Advanced Notion API integration with Claude Code
**Key Features**:
- Rich console output with colors and formatting
- Streaming JSON output processing
- Comprehensive Notion API tool access
- Error handling and status reporting

**Architecture**: Complex agent that finds Notion pages, extracts todos, implements code changes, and marks todos as complete.

### claude_code_is_programmable_4.py
**Purpose**: Demonstrates multiple output formats
**Key Features**:
- Command-line argument parsing
- Support for text, json, and stream-json output formats
- Format-specific output processing functions

## Summary

This project serves as a comprehensive showcase of programmable AI coding workflows, demonstrating:

1. **Multi-language support**: Python, JavaScript, Shell scripts
2. **Multiple AI models**: Claude (various versions), DeepSeek
3. **Different output formats**: Text, JSON, streaming JSON
4. **External integrations**: Notion API, voice interaction, web search
5. **Security patterns**: Tool restriction and permission management
6. **Development workflows**: Git integration, testing, and automation

The repository effectively demonstrates the evolution from simple AI tool usage to complex automated workflows that can manage entire development lifecycles programmatically.