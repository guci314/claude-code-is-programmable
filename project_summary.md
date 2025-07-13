# 项目总结

## 项目概述
这是一个演示如何以编程方式使用 Claude Code 的项目集合，展示了通过子进程调用和结构化输出格式实现 AI 编程的核心模式。

## 核心组件

### 1. 基础演示脚本

**claude_code_is_programmable_2.py**
- 基本的 Claude Code 调用演示
- 设置 HTTP 代理
- 使用 Edit、Bash、Write 工具
- 修改 hello1.py 文件输出

**claude_code_is_programmable_3.py**
- 高级 Notion API 集成演示
- 支持流式 JSON 输出
- Todo 项目自动化处理工作流
- 连接 Notion 页面读取任务并自动实现代码

**claude_code_is_programmable_4.py**
- 多种输出格式支持演示
- 支持 text、json、stream-json 格式
- 展示如何通过 --output-format 控制响应格式

### 2. 语音集成

**voice_to_claude_code.py**
- RealtimeSTT + OpenAI TTS + Claude Code 集成
- 支持语音触发词 ["claude", "cloud", "sonnet", "sonny"]
- 对话历史追踪（保存为 YAML 格式）
- 响应压缩（适合语音输出）
- 实时语音转文本和文本转语音

### 3. Web 搜索功能

**anthropic_search.py**
- AI 增强的网络搜索工具
- 支持域名过滤和引用追踪
- 使用 Anthropic Claude 模型处理搜索结果
- 支持地理位置和时区配置
- Rich 格式化输出

### 4. 测试工具

**claude_testing_v1.py**
- Claude Code 编程调用的实用工具
- 提供 `run_claude()` 和 `run_claude_json()` 函数
- 支持自定义工具限制和输出格式

**hello.py & test_hello.py**
- 简单的 Hello World 程序和对应测试
- 演示基本的 Python 测试模式

### 5. Aider 集成

**aider_is_programmable_2.py**
- Aider AI 编程助手的自动化脚本
- 创建新分支、生成代码、提交更改的完整工作流
- 生成 TypeScript Todo 应用

**aider_is_programmable_3.py**
- 使用 DeepSeek 模型的 Aider 集成
- 支持不同 AI 模型的编程任务

## 关键技术特点

### 1. UV 脚本模式
所有 Python 脚本使用内联依赖声明：
```python
# /// script
# dependencies = ["anthropic", "rich", "python-dotenv"]
# ///
```

### 2. 工具限制策略
通过 `--allowedTools` 参数限制 Claude 的能力以提高安全性：
```python
["Bash", "Edit", "Write", "GlobTool", "GrepTool"]
```

### 3. 多种输出格式
- `text`: 普通文本输出
- `json`: 结构化 JSON 响应  
- `stream-json`: 流式 JSON 输出

### 4. 外部 API 集成
- **Notion API**: 自动化任务管理
- **OpenAI TTS**: 文本转语音
- **RealtimeSTT**: 实时语音识别
- **Anthropic Search**: Web 搜索增强

## 开发工作流

1. **设置**: 复制示例配置文件并添加 API 密钥
2. **开发**: 使用 UV 运行 Python 脚本，pytest 进行测试
3. **演示**: 运行示例脚本查看编程 AI 编码模式
4. **集成**: 为自定义用例扩展模式

## 环境要求

- Python 3.9+
- UV 包管理器
- 各种 API 密钥：
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY` 
  - `NOTION_INTERNAL_INTEGRATION_SECRET`
  - `DEEPSEEK_API_KEY`

## 项目架构亮点

这个项目展示了如何将 Claude Code 作为基础工具构建编程 AI 编码工作流的综合示例，包括：

- **多模态集成**: 语音输入/输出、网络搜索、外部 API 集成
- **流式处理**: 实时输出和响应处理  
- **对话历史**: 持久化对话状态管理
- **工具安全**: 通过工具限制实现安全的 AI 交互
- **格式控制**: 结构化输出用于程序化处理

该项目作为使用 Claude Code 构建编程 AI 编码工作流的完整参考实现。