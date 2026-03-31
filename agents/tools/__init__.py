#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from .bash import BashTool
from .common import ToolBase
from .files import EditFileTool, ReadFileTool, WriteFileTool
from .task import TaskTool
from .todo import TodoTool
from .skill import SkillTool


_TOOL_CLASSES = {
    "bash": BashTool,
    "edit_file": EditFileTool,
    "read_file": ReadFileTool,
    "write_file": WriteFileTool,
    "todo": TodoTool,
    "load_skill": SkillTool,
}


class ToolManager:

    def __init__(self, tools: list):
        self.tool_dict = {}
        for item in tools:
            if isinstance(item, ToolBase):
                if item.name in self.tool_dict:
                    continue
                self.tool_dict[item.name] = item
                continue
            name = item if isinstance(item, str) else item.get("name")
            if not name or name in self.tool_dict:
                continue
            cls = _TOOL_CLASSES.get(name)
            if cls is None:
                print(f"Unknown tool: {item!r}")
                continue
            self.tool_dict[name] = cls()

    def tool_specs(self) -> list:
        return [tool.to_spec() for tool in self.tool_dict.values()]

    def run_tool(self, tool_name: str, tool_input: dict,
                 cur_work_dir: str) -> str:
        if tool_name not in self.tool_dict:
            return f"Unknown tool: {tool_name}"
        return self.tool_dict[tool_name].run(tool_input, cur_work_dir)


__all__ = [
    "ToolManager",
    "TaskTool",
    "SkillTool",
]
