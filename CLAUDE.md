# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running Python Scripts
All Python scripts use UV package manager with inline dependency management:
```bash
# Basic script execution
uv run script_name.py

# Scripts that require arguments
uv run claude_code_is_programmable_3.py "My Notion Page"
uv run voice_to_claude_code.py --id "my-chat-id" --prompt "create hello world"
uv run anthropic_search.py "search query"
```

### Testing
```bash
# Run basic unit tests
uv run pytest test_hello.py

# Run Claude CLI integration tests (requires RUN_CLAUDE_TESTS=1)
RUN_CLAUDE_TESTS=1 uv run pytest tests/test_claude_testing_v1.py

# Run all tests
uv run pytest
```

### JavaScript Scripts
```bash
# Using Bun runtime
bun claude_code_is_programmable_2.js
bun aider_is_programmable_2.js
```

### Cleanup
```bash
# Reset demo branches and generated files
sh reset.sh
```

## Environment Setup

Required environment variables in `.env`:
- `ANTHROPIC_API_KEY` - For Claude Code and anthropic_search.py
- `OPENAI_API_KEY` - For voice_to_claude_code.py TTS functionality  
- `NOTION_INTERNAL_INTEGRATION_SECRET` - For Notion API integration scripts

Copy `.env.sample` to `.env` and `.mcp.sample.json` to `.mcp.json` for full setup.

## Architecture Overview

### Core Pattern: Programmatic AI Integration
This repository demonstrates how to use Claude Code programmatically through subprocess calls with structured output formats. Key patterns:

1. **UV Script Pattern**: Python scripts use inline dependency declarations with `# /// script` blocks
2. **Tool Restriction**: Scripts use `--allowedTools` to limit Claude's capabilities for security
3. **Output Format Control**: Scripts leverage `--output-format json|stream-json|text` for structured responses
4. **Multi-Modal Integration**: Voice input/output, web search, and external API integrations

### Key Components

**Core Demonstration Scripts**:
- `claude_code_is_programmable_2.py` - Basic TypeScript app generation
- `claude_code_is_programmable_3.py` - Advanced Notion API integration with streaming output
- `claude_code_is_programmable_4.py` - Multiple output format demonstration

**Voice Integration**:
- `voice_to_claude_code.py` - RealtimeSTT + OpenAI TTS + Claude Code integration
- Supports conversation history and hands-free coding

**Web Search**:
- `anthropic_search.py` - AI-enhanced web search with domain filtering and citation tracking

**Testing Infrastructure**:
- `claude_testing_v1.py` - Utilities for testing Claude Code programmatically
- `tests/test_claude_testing_v1.py` - Integration tests for Claude CLI (requires `RUN_CLAUDE_TESTS=1`)

### Configuration Files

**Aider Configuration** (`.aider.conf.yml`):
- `auto-commits: false` - Manual commit control
- `yes-always: true` - Skip confirmations
- `suggest-shell-commands: false` - Reduced verbosity
- `detect-urls: false` - Disable URL detection

**MCP Configuration** (`.mcp.json`):
- Notion API server configuration for external integrations
- Requires proper headers with API keys

## Project Structure

```
├── ai_docs/           # Claude Code documentation and tutorials
├── bonus/             # Advanced integration examples (OpenAI Agent SDK)
├── tests/             # pytest test files
├── cc_todo/           # Generated todo applications (created by scripts)
├── deepseek/          # DeepSeek integration files
└── images/            # Documentation assets
```

## Development Workflow

1. **Setup**: Copy sample config files and add API keys
2. **Development**: Use UV for Python scripts, test with pytest
3. **Demonstration**: Run example scripts to see programmatic AI coding patterns
4. **Integration**: Extend patterns for custom use cases

The repository serves as a comprehensive example of how to build programmatic AI coding workflows using Claude Code as a foundational tool.