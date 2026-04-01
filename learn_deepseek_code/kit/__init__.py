#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from __future__ import annotations

from .base import KitManager
from .kit_bash import KitBash, KitBashConfig
from .kit_files import KitFiles, KitFilesConfig
from .kit_todo import KitTodo, KitTodoConfig
from .kit_agent import KitAgent, KitAgentConfig
from .kit_skill import KitSkill, KitSkillConfig
from .kit_compact import KitCompact, KitCompactConfig

__all__ = [
    # base
    "KitManager",

    # bash
    "KitBash",
    "KitBashConfig",

    # files
    "KitFiles",
    "KitFilesConfig",

    # todo
    "KitTodo",
    "KitTodoConfig",

    # agent
    "KitAgent",
    "KitAgentConfig",

    # skill
    "KitSkill",
    "KitSkillConfig",

    # compact
    "KitCompact",
    "KitCompactConfig",
]
