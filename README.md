# Hex Claw - 基于DeepSeek的AI代理框架

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Hex Claw是一个轻量级、模块化的AI代理框架，基于DeepSeek API实现，整体设计与实现大量参考了 `learn-claude-code`（并非从零“重新实现”）。它提供了一个灵活的工具系统和技能系统，使开发者能够快速构建和部署智能代理。

## 目录

- [项目简介](#项目简介)
- [主要特性](#主要特性)
- [快速开始](#快速开始)
  - [安装](#安装)
  - [基本使用](#基本使用)
- [项目架构](#项目架构)
- [工具系统详细介绍](#工具系统详细介绍)
- [技能系统详细介绍](#技能系统详细介绍)
- [配置说明](#配置说明)
- [示例代码](#示例代码)
- [扩展开发指南](#扩展开发指南)
- [许可证](#许可证)
- [贡献指南](#贡献指南)

## 项目简介

Hex Claw是一个为AI代理设计的开发框架，核心思想是"模型本身就是代理，代码只是提供运行环境"。框架通过以下方式实现这一理念：

1. **工具系统**：提供文件操作、Shell命令、任务管理等基础能力
2. **技能系统**：支持按需加载领域专业知识
3. **上下文管理**：智能压缩和优化对话历史
4. **任务跟踪**：内置多步骤任务进度管理

框架设计遵循"最小化干预"原则，让AI模型自主决定如何完成任务，而不是预设复杂的流程。

## 主要特性

### 🛠️ 强大的工具系统
- **文件操作**：完整的文件读写、编辑功能
- **Shell执行**：安全的命令行操作
- **任务管理**：多步骤任务跟踪和进度管理
- **上下文压缩**：智能对话历史优化

### 📚 灵活的技能系统
- **按需加载**：只在需要时加载专业知识
- **Markdown格式**：使用YAML frontmatter定义技能元数据
- **自动发现**：自动扫描技能目录
- **领域适配**：轻松添加特定领域知识

### 🔄 智能代理循环
- **自主决策**：AI模型自主选择工具和行动
- **上下文感知**：保持对话连贯性
- **错误处理**：优雅的工具调用异常处理
- **日志记录**：完整的对话历史记录

### ⚙️ 模块化架构
- **插件化设计**：轻松添加新工具和技能
- **配置驱动**：通过配置文件定制代理行为
- **可扩展性**：支持自定义工具和技能开发

## 快速开始

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/IBNBlank/hex_claw.git
cd hex_claw
```

2. 创建虚拟环境并安装依赖：
```bash
./venv.sh
```

3. 配置API密钥：
```bash
echo "your-deepseek-api-key" > api_key
```

### 基本使用

运行基础示例：

```python
# s01_agent_loop.py - 基础代理循环
from hex_claw.agent import AgentMain, AgentMainConfig
from hex_claw.kit import KitManager, KitBash, KitBashConfig
import os

# 配置工具管理器
kit_manager = KitManager([
    KitBash(KitBashConfig(work_dir=os.getcwd())),
])

# 创建代理
agent = AgentMain(
    AgentMainConfig(
        system_prompt="You are a coding agent. Use bash to solve tasks.",
        kit_manager=kit_manager,
        log_path="logs/history.md",
        cur_work_dir=os.getcwd(),
    )
)

# 运行代理循环
history = []
history.append({"role": "user", "content": "列出当前目录的文件"})
history = agent.agent_loop(history)
```

## 项目架构

### 核心组件

```
hex_claw/
├── hex_claw/     # 核心框架
│   ├── agent/              # 代理实现
│   │   ├── agent_main.py   # 主代理循环
│   │   ├── agent_sub.py    # 子代理实现
│   │   └── log_util.py     # 日志工具
│   ├── kit/                # 工具包系统
│   │   ├── base.py         # 基础接口
│   │   ├── kit_bash.py     # Shell工具
│   │   ├── kit_files.py    # 文件工具
│   │   ├── kit_todo.py     # 任务管理
│   │   ├── kit_compact.py  # 上下文压缩
│   │   └── kit_skill.py    # 技能加载
│   └── common.py           # 公共配置
├── skills/                 # 技能库
│   ├── agent-builder/      # 代理构建技能
│   ├── code-review/        # 代码审查技能
│   ├── pdf/               # PDF处理技能
│   └── mcp-builder/       # MCP构建技能
├── example/               # 示例代码
│   ├── s01_agent_loop.py  # 基础代理
│   ├── s02_tool_use.py    # 工具使用
│   ├── s03_todo_write.py  # 任务管理
│   ├── s04_subagent.py    # 子代理模式
│   ├── s05_skill_loading.py # 技能加载
│   └── s06_context_compact.py # 上下文压缩
└── logs/                  # 日志目录
```

### 数据流

```
用户输入
    ↓
代理循环 (agent_loop)
    ↓
工具调用决策
    ↓
工具执行 (call_tool)
    ↓
结果处理
    ↓
上下文更新
    ↓
下一轮循环
```

## 工具系统详细介绍

### 基础工具接口

所有工具都继承自 `KitBase` 类，需要实现以下方法：

```python
class KitBase(ABC):
    def specs(self) -> list[dict]:
        """返回工具规格列表"""
        
    def tools(self) -> dict[str, Callable[[dict], str]]:
        """返回工具名称到可调用函数的映射"""
        
    def helpers(self) -> dict[str, Callable[[dict], str]]:
        """返回辅助函数映射"""
```

### 内置工具

#### 1. 文件工具 (KitFiles)
- **read_file**: 读取文件内容
- **write_file**: 写入文件内容
- **edit_file**: 替换文件中的文本

```python
# 使用示例
kit_manager.run_tool("read_file", {"path": "README.md", "limit": 10})
kit_manager.run_tool("write_file", {"path": "output.txt", "content": "Hello"})
```

#### 2. Shell工具 (KitBash)
- **bash**: 执行Shell命令

```python
# 使用示例
kit_manager.run_tool("bash", {"command": "ls -la"})
```

#### 3. 任务管理工具 (KitTodo)
- **todo**: 更新任务列表，跟踪多步骤任务进度

```python
# 使用示例
kit_manager.run_tool("todo", {
    "items": [
        {"id": "1", "text": "分析需求", "status": "completed"},
        {"id": "2", "text": "编写代码", "status": "in_progress"},
        {"id": "3", "text": "测试验证", "status": "pending"}
    ]
})
```

#### 4. 上下文压缩工具 (KitCompact)
- **compact**: 手动压缩对话历史
- 自动压缩：当上下文过长时自动触发

#### 5. 技能加载工具 (KitSkill)
- **load_skill**: 按名称加载专业技能

```python
# 使用示例
kit_manager.run_tool("load_skill", {"name": "agent-builder"})
```

### 工具管理器 (KitManager)

`KitManager` 负责组合多个工具包，提供统一的调用接口：

```python
# 创建工具管理器
kit_manager = KitManager([
    KitFiles(KitFilesConfig(work_dir=os.getcwd())),
    KitBash(KitBashConfig(work_dir=os.getcwd())),
    KitTodo(),
    KitCompact(),
    KitSkill(),
])

# 获取所有工具规格
specs = kit_manager.specs()

# 运行工具
result = kit_manager.run_tool("bash", {"command": "pwd"})

# 运行辅助函数
result = kit_manager.run_helper("todo_reminder", {})
```

## 技能系统详细介绍

### 技能文件格式

技能使用Markdown格式，包含YAML frontmatter和内容主体：

```markdown
---
name: skill-name
description: 技能描述
tags: tag1,tag2
---

# 技能标题

技能详细内容...

## 章节1

具体内容...

## 章节2

更多内容...
```

### 技能目录结构

```
skills/
├── skill-name/
│   └── SKILL.md          # 主技能文件
├── another-skill.md      # 独立技能文件
└── category/
    ├── sub-skill-1.md    # 分类技能
    └── sub-skill-2.md
```

### 内置技能

#### 1. 代理构建技能 (agent-builder)
- **用途**: 设计和构建AI代理
- **关键词**: agent, assistant, autonomous, workflow
- **包含**: 代理哲学、设计模式、实现示例

#### 2. 代码审查技能 (code-review)
- **用途**: 代码质量分析和改进建议
- **关键词**: code, review, quality, best-practices

#### 3. PDF处理技能 (pdf)
- **用途**: PDF文件解析和处理
- **关键词**: pdf, document, extract, parse

#### 4. MCP构建技能 (mcp-builder)
- **用途**: 构建模型上下文协议服务
- **关键词**: mcp, protocol, service, integration

### 技能加载机制

技能系统支持：
- **自动发现**: 扫描skills目录自动注册
- **按需加载**: 只在需要时加载技能内容
- **元数据提取**: 从frontmatter提取名称、描述、标签
- **系统提示集成**: 技能列表自动添加到系统提示

## 配置说明

### 代理配置 (AgentMainConfig)

```python
@dataclass
class AgentMainConfig:
    system_prompt: str        # 系统提示词
    kit_manager: KitManager   # 工具管理器
    log_path: str            # 日志文件路径
    
    # 可选参数
    api_key: str = API_KEY    # API密钥
    base_url: str = BASE_URL  # API基础URL
    model: str = MODEL       # 模型名称
    max_tokens: int = 16000  # 最大token数
    cur_work_dir: str = os.getcwd()  # 工作目录
```

### 工具配置

每个工具包都有对应的配置类：

```python
# 文件工具配置
@dataclass
class KitFilesConfig:
    work_dir: str = os.getcwd()  # 工作目录

# Shell工具配置  
@dataclass
class KitBashConfig:
    work_dir: str = os.getcwd()  # 工作目录
    timeout_s: int = 120         # 超时时间

# 技能工具配置
@dataclass
class KitSkillConfig:
    skills_dir: str = SKILLS_DIR  # 技能目录
```

### 环境配置

在 `hex_claw/common.py` 中定义：

```python
# API配置
API_KEY = read_api_key()  # 从api_key文件读取
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

# 目录配置
LOG_DIR = os.path.join(REPO_DIR, "logs")
SKILLS_DIR = os.path.join(REPO_DIR, "skills")
```

## 示例代码

### 示例1: 基础代理循环

```python
# s01_agent_loop.py
import os
from hex_claw.agent import AgentMain, AgentMainConfig
from hex_claw.kit import KitManager, KitBash, KitBashConfig

def main():
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
    ])
    
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=f"You are a coding agent at {cur_work_dir}.",
            kit_manager=kit_manager,
            log_path="logs/s01_history.md",
            cur_work_dir=cur_work_dir,
        )
    )
    
    history = []
    history.append({"role": "user", "content": "列出当前目录的文件"})
    history = agent.agent_loop(history)
    
    print("代理执行完成")

if __name__ == "__main__":
    main()
```

### 示例2: 完整工具集

```python
# s02_tool_use.py
import os
from hex_claw.agent import AgentMain, AgentMainConfig
from hex_claw.kit import *

def main():
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitTodo(),
        KitCompact(),
        KitSkill(),
    ])
    
    agent = AgentMain(
        AgentMainConfig(
            system_prompt="You are a full-featured coding assistant.",
            kit_manager=kit_manager,
            log_path="logs/s02_history.md",
            cur_work_dir=cur_work_dir,
        )
    )
    
    # 创建任务列表
    history = []
    history.append({"role": "user", "content": "创建一个Python项目"})
    history = agent.agent_loop(history)

if __name__ == "__main__":
    main()
```

### 示例3: 技能加载

```python
# s05_skill_loading.py
import os
from hex_claw.agent import AgentMain, AgentMainConfig
from hex_claw.kit import *

def main():
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitSkill(),
    ])
    
    agent = AgentMain(
        AgentMainConfig(
            system_prompt="You are an agent builder expert.",
            kit_manager=kit_manager,
            log_path="logs/s05_history.md",
            cur_work_dir=cur_work_dir,
        )
    )
    
    history = []
    history.append({"role": "user", "content": "如何构建一个AI代理？"})
    history = agent.agent_loop(history)

if __name__ == "__main__":
    main()
```

## 扩展开发指南

### 创建自定义工具

1. 继承 `KitBase` 类：

```python
from dataclasses import dataclass
from typing import Callable
from hex_claw.kit.base import KitBase

@dataclass
class MyToolConfig:
    work_dir: str = os.getcwd()

class MyTool(KitBase):
    def __init__(self, config: MyToolConfig):
        self._config = config
    
    def specs(self) -> list[dict]:
        return [{
            "name": "my_tool",
            "description": "我的自定义工具",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            }
        }]
    
    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"my_tool": self.run_tool}
    
    def run_tool(self, tool_input: dict) -> str:
        param1 = tool_input["param1"]
        param2 = tool_input.get("param2", 0)
        return f"执行成功: {param1}, {param2}"
```

2. 在代理中使用：

```python
kit_manager = KitManager([
    MyTool(MyToolConfig(work_dir=os.getcwd())),
    # 其他工具...
])
```

### 创建自定义技能

1. 创建技能文件：

```markdown
---
name: my-skill
description: 我的自定义技能
tags: custom,example
---

# 我的技能

这是自定义技能的内容...

## 使用方法

1. 第一步
2. 第二步
3. 第三步

## 示例

```python
# 示例代码
print("Hello from custom skill")
```

```

2. 放置在技能目录：
```
skills/
└── my-skill.md
```

3. 自动加载使用：

```python
# 代理会自动发现并加载技能
result = kit_manager.run_tool("load_skill", {"name": "my-skill"})
```

### 最佳实践

1. **工具设计**：
   - 保持工具功能单一
   - 提供清晰的错误信息
   - 限制危险操作

2. **技能设计**：
   - 使用清晰的frontmatter
   - 结构化的Markdown内容
   - 包含实际示例

3. **代理配置**：
   - 根据任务选择合适的工具组合
   - 设计明确的系统提示词
   - 合理设置工作目录

## 许可证

本项目采用 Apache License 2.0 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献指南

### 如何贡献

1. **报告问题**：
   - 使用GitHub Issues报告bug或提出功能建议
   - 提供详细的重现步骤和预期行为

2. **提交代码**：
   - Fork仓库并创建功能分支
   - 遵循现有的代码风格
   - 添加测试用例
   - 提交清晰的提交信息

3. **添加工具**：
   - 确保工具功能明确
   - 提供完整的文档
   - 包含使用示例

4. **添加技能**：
   - 使用标准Markdown格式
   - 包含YAML frontmatter
   - 提供实际有用的内容

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/IBNBlank/hex_claw.git
cd hex_claw

# 设置虚拟环境
./venv.sh

# 安装开发依赖
pip install -r requirements.txt
pip install black flake8 mypy pytest

# 运行测试
pytest tests/

# 代码格式化
black .
flake8 .
```

### 代码规范

- 使用类型注解
- 遵循PEP 8编码规范
- 添加docstring文档
- 保持函数单一职责

### 提交信息格式

```
类型(范围): 简短描述

详细描述（可选）

- 变更点1
- 变更点2

关联Issue: #123
```

类型包括：feat, fix, docs, style, refactor, test, chore

---

## 获取帮助

- 查看 [示例代码](example/) 了解更多用法
- 参考 [技能文档](skills/) 获取专业知识
- 提交 [GitHub Issues](https://github.com/IBNBlank/hex_claw/issues) 报告问题

## 致谢

Hex Claw受到以下项目的启发：
- [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code.git)

感谢项目的作者和贡献者。