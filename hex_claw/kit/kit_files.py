#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from dataclasses import dataclass
import os
from typing import Callable

from .base import KitBase


@dataclass
class KitFilesConfig:
    work_dir: str = os.getcwd()


class KitFiles(KitBase):

    def __init__(self, config: KitFilesConfig):
        self._config = config

    def specs(self) -> list[dict]:
        return [
            {
                "name": "read_file",
                "description": "Read file contents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "limit": {
                            "type": "integer"
                        }
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "write_file",
                "description": "Write content to file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        }
                    },
                    "required": ["path", "content"],
                },
            },
            {
                "name": "edit_file",
                "description": "Replace exact text in file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "old_text": {
                            "type": "string"
                        },
                        "new_text": {
                            "type": "string"
                        },
                    },
                    "required": ["path", "old_text", "new_text"],
                },
            },
        ]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {
            "read_file": self.read_tool,
            "write_file": self.write_tool,
            "edit_file": self.edit_tool,
        }

    def read_tool(self, tool_input: dict) -> str:
        path = tool_input["path"]
        limit = tool_input.get("limit")
        try:
            with open(self.__safe_path(path, self._config.work_dir),
                      encoding="utf-8") as f:
                text = f.read()
            lines = text.splitlines()
            total = len(lines)
            if limit and limit < total:
                lines = lines[:limit] + [f"... ({total - limit} more lines)"]
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    def write_tool(self, tool_input: dict) -> str:
        path = tool_input["path"]
        content = tool_input["content"]
        try:
            fp = self.__safe_path(path, self._config.work_dir)
            parent = os.path.dirname(fp)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error: {e}"

    def edit_tool(self, tool_input: dict) -> str:
        path = tool_input["path"]
        old_text = tool_input["old_text"]
        new_text = tool_input["new_text"]
        try:
            fp = self.__safe_path(path, self._config.work_dir)
            with open(fp, encoding="utf-8") as f:
                content = f.read()
            if old_text not in content:
                return f"Error: Text not found in {path}"
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content.replace(old_text, new_text, 1))
            return f"Edited {path}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def __safe_path(path: str, root: str) -> str:
        full = os.path.realpath(os.path.join(root, path))
        root = os.path.realpath(root)
        try:
            under = os.path.commonpath([full, root]) == root
        except ValueError:
            under = False
        if not under:
            raise ValueError(f"Path escapes workspace: {path}")
        return full
