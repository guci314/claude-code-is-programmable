# Claude Code 入门教程

## 什么是Claude Code？

Claude Code是Anthropic推出的AI编程助手，可以通过自然语言指令来编写、修改和分析代码。它集成了多种工具，能够执行bash命令、读写文件、搜索代码等。

## 安装和设置

### 1. 安装Claude Code CLI
```bash
# 通过npm安装
npm install -g @anthropic-ai/claude-code

# 或通过pip安装
pip install claude-code
```

### 2. 配置API密钥
```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key-here"

# 或在.env文件中设置
echo "ANTHROPIC_API_KEY=your-api-key-here" >> .env
```

## 基础用法

### 1. 简单的命令行使用
```bash
# 基础用法
claude -p "创建一个hello world的Python脚本"

# 限制工具使用（安全考虑）
claude -p "创建一个计算器应用" --allowedTools "Write" "Edit"

# 指定输出格式
claude -p "分析当前项目结构" --output-format json
```

### 2. 交互式使用
```bash
# 启动交互模式
claude

# 在交互模式中，你可以：
> 帮我创建一个React组件
> 优化这个函数的性能
> 解释这段代码的作用
```

## 核心工具介绍

Claude Code提供了多种内置工具：

### 文件操作工具
- **Read**: 读取文件内容
- **Write**: 创建或覆写文件
- **Edit**: 精确编辑文件的特定部分
- **Glob**: 查找匹配模式的文件
- **Grep**: 在文件中搜索内容

### 系统操作工具
- **Bash**: 执行shell命令
- **LS**: 列出目录内容

### 高级工具
- **Task**: 启动代理执行复杂任务
- **WebFetch**: 从网页获取内容
- **NotebookRead/Edit**: 处理Jupyter笔记本

## 实用示例

### 示例1：创建简单的Web应用
```bash
claude -p "创建一个简单的HTML页面，包含CSS样式和JavaScript交互" \
  --allowedTools "Write" "Edit" "Read"
```

### 示例2：代码重构
```bash
claude -p "重构这个Python文件，提高代码可读性和性能" \
  --allowedTools "Read" "Edit" "Bash"
```

### 示例3：项目分析
```bash
claude -p "分析这个项目的结构，找出潜在的改进点" \
  --allowedTools "Read" "Glob" "Grep" "LS"
```

## 编程方式使用Claude Code

### Python示例
```python
#!/usr/bin/env -S uv run --script
import subprocess
import json

def run_claude(prompt, allowed_tools=None, output_format="text"):
    """运行Claude Code并返回结果"""
    cmd = ["claude", "-p", prompt]
    
    if output_format != "text":
        cmd.extend(["--output-format", output_format])
    
    if allowed_tools:
        cmd.extend(["--allowedTools"] + allowed_tools)
    
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        check=True
    )
    
    return result.stdout

# 使用示例
if __name__ == "__main__":
    # 创建一个简单的Python脚本
    output = run_claude(
        "创建一个计算斐波那契数列的Python函数",
        allowed_tools=["Write", "Edit"],
        output_format="json"
    )
    
    print("Claude的响应:")
    print(output)
```

### JavaScript示例
```javascript
const { spawn } = require('child_process');

async function runClaude(prompt, allowedTools = [], outputFormat = 'text') {
    return new Promise((resolve, reject) => {
        const args = ['-p', prompt];
        
        if (outputFormat !== 'text') {
            args.push('--output-format', outputFormat);
        }
        
        if (allowedTools.length > 0) {
            args.push('--allowedTools', ...allowedTools);
        }
        
        const claude = spawn('claude', args);
        let output = '';
        let error = '';
        
        claude.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        claude.stderr.on('data', (data) => {
            error += data.toString();
        });
        
        claude.on('close', (code) => {
            if (code === 0) {
                resolve(output);
            } else {
                reject(new Error(error));
            }
        });
    });
}

// 使用示例
(async () => {
    try {
        const result = await runClaude(
            "创建一个React Todo组件", 
            ['Write', 'Edit'], 
            'json'
        );
        console.log('Claude响应:', result);
    } catch (error) {
        console.error('错误:', error);
    }
})();
```

## 输出格式详解

### 1. Text格式（默认）
```bash
claude -p "Hello world" --output-format text
```
输出纯文本，适合人类阅读。

### 2. JSON格式
```bash
claude -p "Hello world" --output-format json
```
输出结构化JSON，适合程序处理。

### 3. Stream JSON格式
```bash
claude -p "创建一个复杂应用" --output-format stream-json
```
流式JSON输出，适合实时处理大型任务。

## 安全最佳实践

### 1. 限制工具权限
```bash
# 只允许读取和编辑，不允许执行系统命令
claude -p "分析代码" --allowedTools "Read" "Edit" "Grep"
```

### 2. 避免敏感信息
```bash
# 不要在命令中包含API密钥或密码
# 使用环境变量或配置文件
```

### 3. 验证输出
```bash
# 对于重要操作，先使用--dry-run或限制工具
claude -p "删除所有临时文件" --allowedTools "LS" "Read"
```

## 高级功能

### 1. 与外部服务集成
```python
# 集成Notion API
cmd = [
    "claude", "-p", f"在Notion页面'{page_name}'中处理待办事项",
    "--allowedTools",
    "mcp__notionApi__API-post-search",
    "mcp__notionApi__API-get-block-children",
    "Bash", "Edit", "Write"
]
```

### 2. 语音交互
```python
# 使用语音输入
import speech_recognition as sr
import subprocess

def voice_to_claude():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        audio = r.listen(source)
    
    try:
        prompt = r.recognize_google(audio, language='zh-CN')
        print(f"识别到: {prompt}")
        
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True
        )
        
        print("Claude响应:", result.stdout)
    except Exception as e:
        print(f"错误: {e}")
```

### 3. 批量处理
```python
# 批量处理多个文件
import os
import subprocess

def process_files(directory, pattern):
    for filename in os.listdir(directory):
        if pattern in filename:
            prompt = f"优化文件 {filename} 的代码质量"
            subprocess.run([
                "claude", "-p", prompt,
                "--allowedTools", "Read", "Edit"
            ])
```

## 常见问题和解决方案

### Q: Claude Code无法找到命令
```bash
# 检查安装
which claude
npm list -g @anthropic-ai/claude-code

# 重新安装
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code
```

### Q: API密钥认证失败
```bash
# 验证环境变量
echo $ANTHROPIC_API_KEY

# 测试连接
claude -p "hello" --allowedTools "Bash"
```

### Q: 工具权限被拒绝
```bash
# 检查允许的工具列表
claude --help | grep allowedTools

# 使用正确的工具名称
claude -p "读取文件" --allowedTools "Read" "LS"
```

## 最佳实践

### 1. 项目结构
```
project/
├── .env                 # 环境变量
├── .mcp.json           # MCP配置
├── CLAUDE.md           # Claude指导文档
└── scripts/
    ├── claude_helper.py # Claude辅助工具
    └── automation/     # 自动化脚本
```

### 2. 编写清晰的提示
```bash
# 好的提示
claude -p "创建一个RESTful API服务器，使用Express.js，包含用户认证和数据库连接"

# 不够清楚的提示
claude -p "做个网站"
```

### 3. 渐进式开发
```bash
# 先规划
claude -p "为电商网站设计数据库架构" --allowedTools "Write"

# 再实现
claude -p "根据设计创建数据库模型" --allowedTools "Write" "Read"

# 最后测试
claude -p "为数据库模型编写单元测试" --allowedTools "Write" "Read" "Bash"
```

## 总结

Claude Code是一个强大的AI编程助手，通过合理使用其工具和功能，可以大大提高开发效率。记住：

1. **安全第一**：合理限制工具权限
2. **清晰沟通**：提供详细的任务描述
3. **渐进开发**：将复杂任务分解为简单步骤
4. **持续学习**：探索新功能和最佳实践

开始你的Claude Code之旅吧！🚀