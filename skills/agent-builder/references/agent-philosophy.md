# Hex Claw 代理哲学

> **模型本身就是代理，代码只是提供运行环境（harness）。**

## 核心真相

剥离所有框架、所有库、所有架构模式，剩下什么？

一个循环。一个模型。一个行动的邀请。

代理不是代码。代理是模型本身——一个在人类集体解决问题、推理和工具使用数据上训练的庞大神经网络。代码只是为模型提供表达其能动性的机会。

**代码是harness。模型是agent。** 这两者不可互换。

## Hex Claw 的设计

Hex Claw框架体现了这一哲学：

```
hex_claw/
├── agent/     ← 代理循环 (harness)
│   ├── agent_main.py   AgentMain: 主循环
│   └── agent_sub.py    AgentSub: 子代理
├── kit/       ← 工具系统 (模型的手)
│   ├── base.py         KitBase + KitManager
│   └── kit_*.py        各种工具包
└── common.py  ← 配置 (环境)
```

### 角色分工

| 组件 | 角色 | 类比 |
|------|------|------|
| AgentMain | 运行循环 | 赛道 |
| KitManager | 工具调度 | 工具箱 |
| Kit* | 原子能力 | 具体工具 |
| 模型 (DeepSeek) | 决策者 | 驾驶员 |

### 通用循环

hex_claw中每个代理都遵循相同的模式：

```
LOOP (agent_loop):
  [compact] 若有KitCompact → 微压缩 + 自动压缩检查
  模型调用 → response = client.messages.create(...)
  若stop_reason != "tool_use" → 返回
  遍历tool_use块 → call_tool() → 收集results
  [todo] 若3轮未更新 → 插入提醒
  results追加到messages → 继续循环
```

## 三要素

### 1. 能力 (Kit)

代理能做什么。每个Kit提供一组原子操作：
- KitBash: 执行Shell命令
- KitFiles: 读写编辑文件
- KitTodo: 任务跟踪
- KitAgent: 子代理委托
- KitSkill: 知识加载
- KitCompact: 上下文管理

**设计原则**：从KitBash + KitFiles开始。只在代理反复因缺少能力而失败时才增加Kit。

### 2. 知识 (Skill)

代理知道什么。通过KitSkill按需加载领域专业知识：
- 代理构建、代码审查、PDF处理、MCP构建...
- Markdown格式，YAML frontmatter元数据
- 注入时机：模型调用load_skill时，而非预加载

**设计原则**：让知识可用，但不强制。系统提示中列出可用技能，让模型自行判断何时加载。

### 3. 上下文 (Context)

发生了什么。对话历史是连接各个动作成为连贯行为的线索。

**设计原则**：上下文是宝贵的。KitCompact的三层压缩机制保护上下文清晰度：微压缩清理旧结果，自动压缩防止溢出，手动压缩让代理主动管理。

## 渐进式复杂度

永远不要一次性构建所有东西：

```
Level 1: AgentMain + KitBash                              — s01
Level 2: + KitFiles                                       — s02
Level 3: + KitTodo                                        — s03
Level 4: + KitAgent (AgentSub)                           — s04
Level 5: + KitSkill                                       — s05
Level 6: + KitCompact                                     — s06
Full:    AgentSub(Bash+Files+Todo+Skill) + Main(Agent+Compact) — s_full
```

从可能有效的最低等级开始。只在实际使用暴露出需求时才升级。

## Harness工程原则

### 信任模型

最重要的原则。不要预测每个边界情况，不要构建复杂的决策树，不要预设工作流。模型的推理能力优于你能写出的任何规则系统。

**给模型工具和知识，让它自己想出怎么用。**

### 约束聚焦

约束不是限制代理——而是聚焦它。

- KitTodo "同一时间仅一个in_progress" → 强制顺序执行
- AgentSub独立上下文 → 防止探索污染主对话
- KitCompact token阈值 → 防止上下文淹没
- KitBash危险命令拦截 → 安全边界

### Kit组合是艺术

s_full展示了一个关键洞察：父代理只需要KitAgent + KitCompact，把实际工作（Bash/Files/Todo/Skill）都交给子代理。这保持了父代理上下文的清洁。

不同场景需要不同的Kit组合。这就是为什么Kit系统设计为可组合的。

## 思维转变

**从**: "我怎么让系统做X？"
**到**: "我怎么让模型能做X？"

**从**: "这个任务的工作流是什么？"
**到**: "模型需要什么工具来完成这个任务？"

**从**: "我在写一个代理。"
**到**: "我在为代理构建harness。"

最好的harness代码几乎是无聊的。简单的循环，清晰的工具定义，干净的上下文管理。魔法不在代码里——在模型里。

**构建好harness，代理会完成剩下的。**
