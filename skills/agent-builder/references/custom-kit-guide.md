# 自定义Kit开发指南

本文档说明如何为hex_claw框架创建自定义Kit工具包。

## KitBase接口

所有Kit继承自 `hex_claw.kit.base.KitBase`：

```python
class KitBase(ABC):
    @abstractmethod
    def specs(self) -> list[dict]:
        """返回Anthropic格式的工具规格列表。"""

    @abstractmethod
    def tools(self) -> dict[str, Callable[[dict], str]]:
        """返回 tool_name -> callable(tool_input) -> str 的映射。"""

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        """可选：返回内部辅助函数映射（不暴露给模型）。"""
        return {}
```

三个方法的职责：
- `specs()` — 告诉模型有哪些工具可用，以及参数格式
- `tools()` — 将工具名映射到实际执行函数
- `helpers()` — 供agent_loop内部调用的钩子函数（如初始化、提醒等）

## 完整示例：KitHttp

```python
#!/usr/bin/env python3
import requests
from dataclasses import dataclass
from typing import Callable, Optional

from hex_claw.kit.base import KitBase


@dataclass
class KitHttpConfig:
    timeout_s: int = 30
    max_response_chars: int = 50000


class KitHttp(KitBase):

    def __init__(self, config: Optional[KitHttpConfig] = None):
        self._config = config or KitHttpConfig()

    def specs(self) -> list[dict]:
        return [{
            "name": "http_get",
            "description": "Send HTTP GET request and return response body.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "headers": {
                        "type": "object",
                        "description": "Optional HTTP headers",
                    },
                },
                "required": ["url"],
            },
        }, {
            "name": "http_post",
            "description": "Send HTTP POST request with JSON body.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "body": {"type": "object", "description": "JSON body"},
                    "headers": {"type": "object"},
                },
                "required": ["url", "body"],
            },
        }]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {
            "http_get": self._get,
            "http_post": self._post,
        }

    def _get(self, tool_input: dict) -> str:
        try:
            resp = requests.get(
                tool_input["url"],
                headers=tool_input.get("headers", {}),
                timeout=self._config.timeout_s,
            )
            return f"[{resp.status_code}]\n{resp.text[:self._config.max_response_chars]}"
        except Exception as e:
            return f"Error: {e}"

    def _post(self, tool_input: dict) -> str:
        try:
            resp = requests.post(
                tool_input["url"],
                json=tool_input["body"],
                headers=tool_input.get("headers", {}),
                timeout=self._config.timeout_s,
            )
            return f"[{resp.status_code}]\n{resp.text[:self._config.max_response_chars]}"
        except Exception as e:
            return f"Error: {e}"
```

## 使用自定义Kit

```python
from hex_claw.kit import KitManager, KitBash, KitBashConfig

kit_manager = KitManager([
    KitBash(KitBashConfig(work_dir=cur_work_dir)),
    KitHttp(KitHttpConfig(timeout_s=10)),
])
```

## Helpers机制

Helpers是不暴露给模型的内部函数，供agent_loop在代码层面调用。典型用途：

### 注入运行时依赖

KitAgent和KitCompact需要在创建后注入Anthropic client：

```python
def helpers(self) -> dict[str, Callable[[dict], str]]:
    return {"my_kit_set_client": self.__set_client}

def __set_client(self, helper_input: dict):
    self.__client = helper_input.get("client")
```

AgentMain在 `__init__` 中自动调用：
```python
self.__kit_manager.run_helper("task_set_client", {"client": self.client})
```

### 生成系统提示片段

KitSkill通过helper生成可用技能列表：

```python
system_prompt = f"...\nSkills:\n{kit_manager.run_helper('skill_get_system', {})}"
```

### 周期性提醒

KitTodo通过helper在3轮未更新后插入提醒：

```python
def helpers(self):
    return {"todo_reminder": self.__reminder}

def __reminder(self, input: dict) -> str:
    return {"type": "text", "text": "<reminder>Update your todos.</reminder>"}
```

## 工具规格 (specs) 编写要点

```python
{
    "name": "tool_name",            # 唯一标识，模型通过此名称调用
    "description": "简明描述工具功能",   # 模型根据此描述决定何时使用
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数说明",
            },
            "param2": {
                "type": "integer",
                "description": "可选参数",
            },
        },
        "required": ["param1"],      # 必填参数列表
    },
}
```

注意：
- `description` 要简洁但足够清晰，模型靠此判断何时使用该工具
- `input_schema` 遵循JSON Schema格式
- 工具函数返回值必须是 `str`

## 注册到Kit系统

若要作为框架内置Kit，需在 `hex_claw/kit/__init__.py` 中导出：

```python
from .kit_http import KitHttp, KitHttpConfig

__all__ = [
    # ... existing exports ...
    "KitHttp",
    "KitHttpConfig",
]
```

若仅在特定代理中使用，直接在代理脚本中导入即可。

## 设计原则

1. **一个Kit可以暴露多个工具**：如KitFiles暴露read_file/write_file/edit_file
2. **Config用dataclass**：保持配置声明式、可序列化
3. **工具函数返回str**：所有输出统一为字符串，由模型解读
4. **安全第一**：对路径做逃逸检查，对命令做危险拦截
5. **错误不抛异常**：工具函数内部捕获异常，返回 `f"Error: {e}"`
6. **输出截断**：大输出加截断保护，防止上下文溢出
