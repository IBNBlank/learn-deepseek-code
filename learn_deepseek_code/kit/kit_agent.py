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
from ..agent.agent import AgentConfig, Agent


@dataclass
class KitAgentConfig:
    sub_agent: AgentConfig


class KitAgent(KitBase):
    """sub-agent delegation; `run_fn` must implement the actual spawn logic."""

    def __init__(self, config: KitAgentConfig):
        self._config = config

    def specs(self) -> list[dict]:
        return [{
            "name":
            "task",
            "description":
            ("Spawn a subagent with fresh context. It shares the filesystem "
             "but not conversation history."),
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
        }]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"task": self.run}

    def run(self, tool_input: dict) -> str:
        prompt = tool_input["prompt"]
        sub_agent = Agent(self._config.sub_agent)
        
        sub_messages = [{"role": "user", "content": prompt}]  # fresh context
        for _ in range(30):  # safety limit
            response = sub_agent.agent_loop(sub_messages)
            if response.stop_reason != "tool_use":
                break
        
        # Only the final text returns to the parent -- child context is discarded
        return "".join(b.text for b in response.content if hasattr(b, "text")) or "(no summary)"
