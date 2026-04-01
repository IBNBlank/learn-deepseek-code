#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from dataclasses import dataclass
from typing import Callable

from .base import KitBase
from ..agents.base import AgentConfig, Agent


@dataclass
class AgentKitConfig:
    pass


class AgentKit(KitBase):
    """sub-agent delegation; `run_fn` must implement the actual spawn logic."""

    def __init__(self, config: AgentKitConfig):
        self._config = config

    def specs(self) -> list[dict]:
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
                        "prompt": {"type": "string"},
                        "description": {
                            "type": "string",
                            "description": "Short description of the task",
                        },
                    },
                    "required": ["prompt"],
                },
            }
        ]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"task": self.run}

    def run(self, tool_input: dict) -> str:
        return self._config.run_fn(tool_input)
