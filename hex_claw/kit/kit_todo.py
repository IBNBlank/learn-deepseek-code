#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

from dataclasses import dataclass
from typing import Callable, Optional

from .base import KitBase


@dataclass
class KitTodoConfig:
    pass


class KitTodo(KitBase):

    def __init__(self, config: Optional[KitTodoConfig] = None):
        self.__config = config or KitTodoConfig()
        self.__items: list[dict[str, str]] = []

    def specs(self) -> list[dict]:
        return [{
            "name": "todo",
            "description":
            "Update task list. Track progress on multi-step tasks.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "text": {
                                    "type": "string"
                                },
                                "status": {
                                    "type":
                                    "string",
                                    "enum":
                                    ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["id", "text", "status"],
                        },
                    }
                },
                "required": ["items"],
            },
        }]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"todo": self.run}

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        return {
            "todo_reminder": self.__reminder,
        }

    def run(self, tool_input: dict) -> str:
        return self.__update(tool_input["items"])

    def __update(self, items: list) -> str:
        if len(items) > 20:
            raise ValueError("Max 20 todos allowed")
        validated: list[dict[str, str]] = []
        in_progress_count = 0
        for i, item in enumerate(items):
            text = str(item.get("text", "")).strip()
            status = str(item.get("status", "pending")).lower()
            item_id = str(item.get("id", str(i + 1)))
            if not text:
                raise ValueError(f"Item {item_id}: text required")
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Item {item_id}: invalid status '{status}'")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({"id": item_id, "text": text, "status": status})
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress at a time")
        self.__items = validated
        return self.__render()

    def __render(self) -> str:
        if not self.__items:
            return "No todos."
        lines: list[str] = []
        for item in self.__items:
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]"
            }[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['text']}")
        done = sum(1 for t in self.__items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(self.__items)} completed)")
        return "\n".join(lines)

    def __reminder(self, input: dict) -> str:
        return {
            "type": "text",
            "text": "<reminder>Update your todos.</reminder>"
        }
