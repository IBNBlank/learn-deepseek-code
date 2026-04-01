#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import subprocess
from dataclasses import dataclass

from typing import Callable

from .base import ToolBase


@dataclass
class BashToolConfig:
    work_dir: str
    timeout_s: int = 120


class BashTool(ToolBase):

    def __init__(self, config: BashToolConfig):
        self._config = config

    def tool_specs(self) -> list[dict]:
        return [
            {
                "name": "bash",
                "description": "Run a shell command.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string"
                        }
                    },
                    "required": ["command"]
                },
            }
        ]

    def tool_methods(self) -> dict[str, Callable[[dict], str]]:
        return {"bash": self.run}

    def run(self, tool_input: dict) -> str:
        command = tool_input["command"]
        dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
        if any(d in command for d in dangerous):
            return "Error: Dangerous command blocked"
        try:
            r = subprocess.run(
                command,
                shell=True,
                cwd=self._config.work_dir,
                capture_output=True,
                text=True,
                timeout=self._config.timeout_s,
            )
            out = (r.stdout + r.stderr).strip()
            return out if out else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: Timeout ({self._config.timeout_s}s)"
