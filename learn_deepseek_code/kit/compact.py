#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from typing import Callable

from .base import KitBase


class CompactKit(KitBase):
    """
    Layer 3 (manual): model requests compression.
    ``run`` only returns an acknowledgement; the agent loop must append tool
    results, then replace ``messages`` with the actual compaction result.
    """

    def specs(self) -> list[dict]:
        return [
            {
                "name": "compact",
                "description": "Trigger manual conversation compression (summarize and shrink history).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "focus": {
                            "type": "string",
                            "description": "What to preserve or emphasize in the summary",
                        }
                    },
                },
            }
        ]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"compact": self.run}

    def run(self, tool_input: dict) -> str:
        focus = tool_input.get("focus") or ""
        focus = str(focus).strip()
        if focus:
            return f"Compressing (focus: {focus})..."
        return "Compressing..."
