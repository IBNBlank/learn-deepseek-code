#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import subprocess

from .common import ToolBase


class BashTool(ToolBase):

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return "Run a shell command."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string"
                }
            },
            "required": ["command"]
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        command = tool_input["command"]
        dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
        if any(d in command for d in dangerous):
            return "Error: Dangerous command blocked"
        try:
            r = subprocess.run(
                command,
                shell=True,
                cwd=cur_work_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            out = (r.stdout + r.stderr).strip()
            return out if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (120s)"
