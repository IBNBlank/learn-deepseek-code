#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from typing import TYPE_CHECKING, Any

from .base import KitManager
from .kit_bash import KitBash, KitBashConfig
from .kit_files import KitFiles, KitFilesConfig
from .kit_skill import KitSkill, KitSkillConfig
from .kit_todo import KitTodo, KitTodoConfig
from .kit_compact import KitCompact, KitCompactConfig

if TYPE_CHECKING:
    # Avoid runtime circular imports; these are lazily imported in __getattr__.
    from .kit_agent import KitAgent, KitAgentConfig

__all__ = [
    # base
    "KitManager",

    # bash
    "KitBash",
    "KitBashConfig",

    # files
    "KitFiles",
    "KitFilesConfig",

    # skill
    "KitSkill",
    "KitSkillConfig",

    # todo
    "KitTodo",
    "KitTodoConfig",

    # compact
    "KitCompact",
    "KitCompactConfig",

    # agent
    "KitAgent",
    "KitAgentConfig",
]


def __getattr__(name: str) -> Any:
    if name in ("KitAgent", "KitAgentConfig"):
        from .kit_agent import KitAgent, KitAgentConfig
        return {"KitAgent": KitAgent, "KitAgentConfig": KitAgentConfig}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
