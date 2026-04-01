#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from dataclasses import dataclass
from typing import Callable

from .base import ToolBase


@dataclass
class TaskToolConfig:
    run_fn: Callable[[dict], str]


class TaskTool(ToolBase):
    """Subagent delegation; `run_fn` must implement the actual spawn logic."""

    def __init__(self, config: TaskToolConfig):
        self._config = config

    def tool_specs(self) -> list[dict]:
        return [
            {
                "name": "task",
                "description": (
                    "Spawn a subagent with fresh context. It shares the filesystem "
                    "but not conversation history."
                ),
                "input_schema": {
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
                },
            }
        ]

    def tool_methods(self) -> dict[str, Callable[[dict], str]]:
        return {"task": self.run}

    def run(self, tool_input: dict) -> str:
        return self._config.run_fn(tool_input)
