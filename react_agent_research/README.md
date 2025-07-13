# LangChain ReAct 智能体研究

基于LangChain的ReAct（推理+行动）范式的综合实现，展示了能够推理问题并使用一套自定义工具进行行动的自主AI智能体。

## 🎯 概述

该项目实现了一个结合**推理**和**行动**的ReAct智能体，能够自主解决复杂问题。该智能体可以：

- 🧠 通过多步骤问题进行**推理**
- 🛠️ 使用各种工具（网络搜索、文件系统、计算器、代码执行等）进行**行动**
- 🔄 在思考和行动之间**迭代**，直到找到解决方案
- 📊 从观察中**学习**并调整方法

## 🏗️ 架构

### 核心组件

1. **LangChain ReAct 智能体** (`langchain_react_agent.py`)
   - 使用ReAct推理循环的主要智能体实现
   - 支持多个LLM提供商（OpenAI、Anthropic）
   - 对话记忆和回调处理
   - 用于推理可视化的丰富控制台输出

2. **自定义工具套件** (`react_agent_tools.py`)
   - 用于信息收集的网络搜索工具
   - 用于项目检查的代码分析工具
   - 用于安全文件操作的文件系统工具
   - 用于数学计算的计算器工具
   - 用于代码执行的Python REPL工具
   - 用于HTTP请求的API工具
   - 用于SQLite操作的数据库工具

3. **交互式演示** (`react_agent_demo.py`)
   - 功能完整的CLI界面
   - 预定义场景和交互模式
   - 会话历史和内存管理
   - 丰富的控制台格式化

4. **测试套件** (`test_react_agent.py`)
   - 所有工具的综合单元测试
   - 智能体工作流程的集成测试
   - 用于可靠测试的模拟外部依赖

5. **示例场景** (`examples/`)
   - 用于信息收集的研究场景
   - 用于项目检查的代码分析场景
   - 用于复杂挑战的问题解决场景

## 🚀 快速开始

### 前提条件

- Python 3.9+
- UV包管理器（包含内联依赖）
- OpenAI、Anthropic或DeepSeek的API密钥

### 环境设置

1. **设置API密钥**（选择一个或多个）：
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export DEEPSEEK_API_KEY="your-deepseek-key"
   ```
   
   或者在 `.env` 文件中设置：
   ```env
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   OPENAI_API_KEY=sk-your-openai-key
   ANTHROPIC_API_KEY=sk-your-anthropic-key
   ```

2. **运行交互式演示**：
   ```bash
   uv run react_agent_demo.py
   ```

3. **测试工具**：
   ```bash
   uv run react_agent_tools.py
   ```

4. **运行测试套件**：
   ```bash
   uv run test_react_agent.py
   ```

## 📋 使用示例

### 基本智能体使用

```python
from langchain_react_agent import LangChainReactAgent
from react_agent_tools import get_basic_tools

# 初始化智能体
agent = LangChainReactAgent(
    llm_provider="openai",
    model_name="gpt-4",
    verbose=True
)

# 添加工具
tools = get_basic_tools()
agent.add_tools(tools)

# 提问
result = agent.run("240的15%是多少，Python是什么编程语言？")
print(result)
```

### 高级问题解决

```python
# 复杂的多步骤问题
query = """
研究可再生能源趋势，计算1000平方米屋顶的潜在太阳能输出，
并创建一个包含分析的文件。
"""

result = agent.run(query)
```

### 代码分析

```python
# 分析项目结构
query = "分析此目录中的Python文件并创建质量报告"
result = agent.run(query)
```

## 🛠️ 可用工具

| 工具 | 描述 | 使用方法 |
|------|-------------|-------|
| **网络搜索** | 在线搜索信息 | `"搜索Python编程"` |
| **代码分析** | 分析代码文件和目录 | `"analyze:/path/to/code"` |
| **文件系统** | 安全地读写文件 | `"read:file.txt"` 或 `"write:file.txt:content"` |
| **计算器** | 数学计算 | `"2 + 3 * 4"` |
| **Python REPL** | 安全执行Python代码 | `"print('Hello, World!')"` |
| **API请求** | 发送HTTP请求 | `"GET:https://api.example.com/data"` |
| **数据库** | SQLite操作 | `"CREATE:table_name"` |

## 🎭 ReAct模式

ReAct模式遵循以下循环：

1. **思考**：智能体对问题进行推理
2. **行动**：智能体选择并使用工具
3. **观察**：智能体观察结果
4. **重复**：继续直到找到解决方案

### ReAct跟踪示例

```
思考：我需要找到关于Python编程的信息，还需要计算240的15%。
行动：web_search
行动输入：Python编程语言
观察：Python是一种以简单性著称的高级编程语言...

思考：现在我需要计算240的15%。
行动：calculator  
行动输入：240 * 0.15
观察：结果：240 * 0.15 = 36.0

思考：我现在有了回答问题所需的两个信息。
最终答案：Python是一种高级编程语言...，240的15%是36。
```

## 🔧 配置

### LLM提供商

支持多个LLM提供商：

```python
# OpenAI
agent = LangChainReactAgent(
    llm_provider="openai",
    model_name="gpt-4"
)

# Anthropic
agent = LangChainReactAgent(
    llm_provider="anthropic", 
    model_name="claude-3-sonnet-20240229"
)

# DeepSeek
agent = LangChainReactAgent(
    llm_provider="deepseek", 
    model_name="deepseek-chat"
)
```

### 工具定制

添加自定义工具：

```python
from langchain.tools import Tool

def my_custom_tool(input_text: str) -> str:
    return f"已处理：{input_text}"

custom_tool = Tool(
    name="custom_tool",
    description="我的自定义文本处理工具",
    func=my_custom_tool
)

agent.add_tools([custom_tool])
```

## 📊 示例场景

### 1. 研究场景

```bash
uv run examples/research_scenario.py
```

演示：
- 多步骤研究过程
- 信息综合
- 数学计算
- 报告生成

### 2. 代码分析场景

```bash
uv run examples/code_analysis_scenario.py
```

演示：
- 项目结构分析
- 代码质量评估
- 安全分析
- 自动文档生成

### 3. 问题解决场景

```bash
uv run examples/problem_solving_scenario.py
```

演示：
- 复杂问题分解
- 多工具集成
- 文件生成
- 系统设计思维

## 🧪 测试

### 运行所有测试

```bash
uv run test_react_agent.py
```

### 测试覆盖率

测试套件涵盖：
- 个别工具功能
- 错误处理和边界情况
- 安全措施
- 集成工作流程
- 模拟外部依赖

### 测试结构

```
test_react_agent.py
├── TestWebSearchTool
├── TestCodeAnalysisTool  
├── TestFileSystemTool
├── TestCalculatorTool
├── TestPythonREPLTool
├── TestAPITool
├── TestDatabaseTool
├── TestToolIntegration
└── TestAgentIntegration
```

## 🔒 安全特性

### 安全工具执行

- **文件系统**：限制对当前目录的访问
- **Python REPL**：沙箱执行环境
- **计算器**：防止代码注入
- **API工具**：请求超时和验证
- **数据库**：使用内存SQLite以确保安全

### 输入验证

所有工具都实现：
- 输入清理
- 危险操作检测
- 错误处理和优雅降级
- 资源使用限制

## 📁 项目结构

```
react_agent_research/
├── langchain_react_agent.py      # 主要智能体实现
├── react_agent_tools.py          # 自定义工具套件
├── react_agent_demo.py           # 交互式演示
├── test_react_agent.py           # 测试套件
├── README.md                     # 此文件
└── examples/
    ├── research_scenario.py      # 研究演示
    ├── code_analysis_scenario.py # 代码分析演示
    └── problem_solving_scenario.py # 问题解决演示
```

## 🔗 与Claude Code的集成

该项目遵循父仓库中建立的模式：

- **UV脚本模式**：内联依赖管理
- **环境变量**：一致的API密钥处理
- **Rich控制台**：美观的终端输出
- **错误处理**：优雅的故障模式
- **测试**：全面的测试覆盖

### 与Claude Code一起运行

```bash
# 从父目录运行
uv run react_agent_research/react_agent_demo.py
```

## 🎯 使用案例

### 研究与分析
- 市场研究自动化
- 技术文档分析
- 竞争情报收集
- 学术研究协助

### 代码开发
- 自动代码审查
- 项目结构分析
- 文档生成
- 错误检测和修复

### 问题解决
- 数学问题解决
- 系统设计挑战
- 数据分析任务
- 多步骤计算

### 商业应用
- 流程自动化
- 报告生成
- 数据处理工作流程
- 决策支持系统

## 🚧 限制

### 当前限制
- 工具执行是顺序的（无并行处理）
- 限于基于文本的交互
- 会话间无持久内存
- API速率限制可能影响性能

### 未来增强
- 并行工具执行
- 持久内存系统
- 多模态能力（图像、音频）
- 自定义工具市场
- 性能优化

## 🤝 贡献

### 添加新工具

1. 在`react_agent_tools.py`中创建新工具类
2. 实现具有适当错误处理的必需方法
3. 添加安全措施和输入验证
4. 在`test_react_agent.py`中创建测试
5. 更新文档

### 示例工具模板

```python
class MyCustomTool:
    def __init__(self):
        self.name = "my_tool"
        self.description = "此工具功能的描述"
    
    def execute(self, input_data: str) -> str:
        try:
            # 实现工具逻辑
            # 添加安全检查
            # 优雅地处理错误
            return f"结果：{input_data}"
        except Exception as e:
            return f"错误：{str(e)}"
```

## 📚 参考资料

### ReAct论文
- [ReAct：在语言模型中协同推理和行动](https://arxiv.org/abs/2210.03629)
- 作者：Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao

### LangChain文档
- [LangChain智能体](https://python.langchain.com/docs/modules/agents/)
- [自定义工具](https://python.langchain.com/docs/modules/agents/tools/)
- [ReAct智能体](https://python.langchain.com/docs/modules/agents/agent_types/react/)

### 相关项目
- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI API](https://openai.com/api/)
- [Anthropic API](https://docs.anthropic.com/)

## 📄 许可证

该项目是claude-code-is-programmable仓库的一部分，遵循相同的许可条款。

---

*使用LangChain、Claude Code和ReAct范式构建，满怀❤️*