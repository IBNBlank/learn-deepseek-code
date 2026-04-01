#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

"""
Backward-compatible alias.

New naming is `kit`:
- A **kit** bundles multiple tools/methods (tool_name -> callable).
- `KitManager` composes multiple kits into one tool-set.
"""

from __future__ import annotations

try:
    # package import
    from .kit import KitBase as ToolBase
    from .kit import KitManager as ToolUtil
except Exception:  # pragma: no cover
    # script-style fallback
    from learn_deepseek_code.kit import KitBase as ToolBase  # type: ignore
    from learn_deepseek_code.kit import KitManager as ToolUtil  # type: ignore

__all__ = ["ToolBase", "ToolUtil"]
