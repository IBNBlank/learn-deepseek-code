---
name: agent-builder
description: |
  使用hex_claw框架创建AI代理。适用场景：
  (1) 需要创建一个新的hex_claw代理脚本
  (2) 需要了解hex_claw框架的Agent/Kit架构
  (3) 需要组合不同的Kit构建不同能力的代理
  (4) 需要创建自定义Kit工具扩展代理能力
  Keywords: agent, hex_claw, kit, 代理, 工具, 创建代理
---

# Hex Claw Agent Builder

使用hex_claw框架快速创建AI代理 —— 从最简bash代理到具备子代理、技能加载、上下文压缩的完整代理。

## 核心理念

> **模型本身就是代理，代码只是提供运行环境（harness）。**

hex_claw框架的代理循环：

```
LOOP:
  模型看到: 对话历史 + 可用工具
  模型决策: 调用工具 or 返回回答
  若调用工具: 执行工具，结果加入上下文，继续循环
  若回答: 返回给用户
```

## 框架架构

```
hex_claw/
├── agent/
│   ├── agent_main.py   # AgentMain: 主代理循环
│   └── agent_sub.py    # AgentSub: 子代理（由KitAgent调用）
├── kit/
│   ├── base.py         # KitBase(ABC) + KitManager
│   ├── kit_bash.py     # KitBash: Shell命令
│   ├── kit_files.py    # KitFiles: 文件读写编辑
│   ├── kit_todo.py     # KitTodo: 任务跟踪
│   ├── kit_agent.py    # KitAgent: 子代理委托
│   ├── kit_skill.py    # KitSkill: 技能加载
│   └── kit_compact.py  # KitCompact: 上下文压缩
└── common.py           # API配置、路径、工具函数
```

## 代理创建模式

所有hex_claw代理都遵循相同的四步模式：

### 步骤1: 配置工具集 (KitManager)

```python
kit_manager = KitManager([
    KitBash(KitBashConfig(work_dir=cur_work_dir)),
    KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
])
```

### 步骤2: 创建代理 (AgentMain)

```python
agent = AgentMain(
    AgentMainConfig(
        system_prompt="You are a coding agent. Use tools to solve tasks.",
        kit_manager=kit_manager,
        log_path=os.path.join(LOG_DIR, "history.md"),
        cur_work_dir=cur_work_dir,
    ))
```

### 步骤3: 运行代理循环

```python
history = []
history.append({"role": "user", "content": query})
history = agent.agent_loop(history)
```

### 步骤4: 显示结果

```python
print_answer(history)
```

## 渐进式能力等级

通过选择不同的Kit组合，构建不同能力等级的代理：

| 等级 | Kit组合 | 能力 | 对应示例 |
|------|---------|------|----------|
| L1 | KitBash | 仅Shell命令 | `example/s01_agent_loop.py` |
| L2 | KitBash + KitFiles | Shell + 文件操作 | `example/s02_tool_use.py` |
| L3 | + KitTodo | + 多步任务跟踪 | `example/s03_todo_write.py` |
| L4 | + KitAgent | + 子代理委托 | `example/s04_subagent.py` |
| L5 | + KitSkill | + 技能加载 | `example/s05_skill_loading.py` |
| L6 | + KitCompact | + 上下文压缩 | `example/s06_context_compact.py` |
| Full | 全部Kit | 完整能力 | `example/s_full.py` |

**原则**：从最低能满足需求的等级开始。大多数场景L2即可。

## 可用Kit详解

### KitBash — Shell命令

```python
KitBash(KitBashConfig(work_dir=cur_work_dir, timeout_s=120))
```

提供 `bash` 工具。内置危险命令拦截。

### KitFiles — 文件操作

```python
KitFiles(KitFilesConfig(work_dir=cur_work_dir))
```

提供 `read_file`、`write_file`、`edit_file` 三个工具。内置路径逃逸保护。

### KitTodo — 任务管理

```python
KitTodo(KitTodoConfig())
```

提供 `todo` 工具。同一时间仅允许一个任务处于 `in_progress`。代理3轮未更新todo时自动提醒。

### KitAgent — 子代理

```python
child_kits = KitManager([
    KitBash(KitBashConfig(work_dir=cur_work_dir)),
    KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
])
child_agent_cfg = AgentSubConfig(
    system_prompt="You are a coding subagent. Complete the task, then summarize.",
    kit_manager=child_kits,
    log_path=os.path.join(LOG_DIR, "history.sub.md"),
    cur_work_dir=cur_work_dir,
)
KitAgent(KitAgentConfig(sub_agent=child_agent_cfg))
```

提供 `task` 工具。子代理使用独立上下文，共享文件系统。防止子代理嵌套委托（不给子代理KitAgent）。

### KitSkill — 技能加载

```python
KitSkill(KitSkillConfig())
```

提供 `load_skill` 工具。自动扫描 `skills/` 目录。系统提示中需包含技能列表：

```python
system_prompt = f"""...\nSkills available:\n{kit_manager.run_helper("skill_get_system", {})}"""
```

### KitCompact — 上下文压缩

```python
KitCompact(KitCompactConfig())
```

提供 `compact` 工具。三层压缩机制：
1. **微压缩**：每轮自动清理旧工具结果
2. **自动压缩**：token超阈值时自动触发摘要
3. **手动压缩**：代理主动调用compact工具

## 脚手架脚本

快速生成代理脚本：

```bash
python skills/agent-builder/scripts/init_agent.py <agent-name> --level <1-6|full>
```

示例：

```bash
python skills/agent-builder/scripts/init_agent.py my_bot --level 2      # Shell + 文件
python skills/agent-builder/scripts/init_agent.py my_bot --level 4      # + 子代理
python skills/agent-builder/scripts/init_agent.py my_bot --level full   # 全部能力
```

## 自定义Kit开发

继承 `KitBase` 实现自定义工具：

```python
from hex_claw.kit.base import KitBase

class MyKit(KitBase):
    def specs(self) -> list[dict]:
        return [{"name": "my_tool", "description": "...", "input_schema": {...}}]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"my_tool": self.run}

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        return {}  # 可选：供agent_loop内部调用的辅助函数

    def run(self, tool_input: dict) -> str:
        return "result"
```

详见 `references/custom-kit-guide.md`。

## 资源

- `references/agent-philosophy.md` — 代理harness工程哲学
- `references/custom-kit-guide.md` — 自定义Kit开发指南
- `scripts/init_agent.py` — 代理脚手架脚本
- `example/s01~s06, s_full` — 完整示例代码
