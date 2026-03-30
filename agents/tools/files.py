#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import os

from .common import ToolBase, safe_path


class ReadFileTool(ToolBase):

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read file contents."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "limit": {
                    "type": "integer"
                }
            },
            "required": ["path"]
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        path = tool_input["path"]
        limit = tool_input.get("limit")
        try:
            with open(safe_path(path, cur_work_dir), encoding="utf-8") as f:
                text = f.read()
            lines = text.splitlines()
            total = len(lines)
            if limit and limit < total:
                lines = lines[:limit] + [f"... ({total - limit} more lines)"]
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"


class WriteFileTool(ToolBase):

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to file."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "content": {
                    "type": "string"
                }
            },
            "required": ["path", "content"]
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        path = tool_input["path"]
        content = tool_input["content"]
        try:
            fp = safe_path(path, cur_work_dir)
            parent = os.path.dirname(fp)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error: {e}"


class EditFileTool(ToolBase):

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Replace exact text in file."

    @property
    def input_schema(self) -> dict:
        return {
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
                }
            },
            "required": ["path", "old_text", "new_text"]
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        path = tool_input["path"]
        old_text = tool_input["old_text"]
        new_text = tool_input["new_text"]
        try:
            fp = safe_path(path, cur_work_dir)
            with open(fp, encoding="utf-8") as f:
                content = f.read()
            if old_text not in content:
                return f"Error: Text not found in {path}"
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content.replace(old_text, new_text, 1))
            return f"Edited {path}"
        except Exception as e:
            return f"Error: {e}"
