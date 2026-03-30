#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from typing import Callable

from .common import ToolBase


class TaskTool(ToolBase):
    """Subagent delegation; `run_fn` must implement the actual spawn logic."""

    def __init__(self, run_fn: Callable[[dict, str], str]):
        self._run_fn = run_fn

    @property
    def name(self) -> str:
        return "task"

    @property
    def description(self) -> str:
        return (
            "Spawn a subagent with fresh context. It shares the filesystem "
            "but not conversation history."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string"
                },
                "description": {
                    "type": "string",
                    "description": "Short description of the task",
                },
            },
            "required": ["prompt"],
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        return self._run_fn(tool_input, cur_work_dir)
