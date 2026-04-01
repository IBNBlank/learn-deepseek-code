#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

"""
Backward-compatible exports.

The new naming uses `learn_deepseek_code.kit` (a "kit" bundles multiple tools).
This `kits` package remains as a thin alias layer.
"""

from __future__ import annotations

from ..kit import (  # noqa: F401
    KitBase as ToolBase,
    KitManager as ToolManager,
    BashKit as BashTool,
    BashKitConfig as BashToolConfig,
    CompactKit as CompactTool,
    FileKit as FileTool,
    FileKitConfig as FileToolConfig,
    SkillKit as SkillTool,
    SkillKitConfig as SkillToolConfig,
    TaskKit as TaskTool,
    TaskKitConfig as TaskToolConfig,
    TodoKit as TodoTool,
    TodoKitConfig as TodoToolConfig,
)

__all__ = [
    "ToolBase",
    "ToolManager",
    "BashTool",
    "BashToolConfig",
    "CompactTool",
    "FileTool",
    "FileToolConfig",
    "SkillTool",
    "SkillToolConfig",
    "TaskTool",
    "TaskToolConfig",
    "TodoTool",
    "TodoToolConfig",
]
