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
from ..agent.agent_sub import AgentSub, AgentSubConfig


@dataclass
class KitAgentConfig:
    sub_agent: AgentSubConfig


class KitAgent(KitBase):
    """Sub-agent delegation.

    The spawned sub-agent starts with fresh messages (no shared history) but can
    operate on the same filesystem via its kits.
    """

    def __init__(self, config: KitAgentConfig):
        self.__config = config
        self.__client = None

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

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        return {"task_set_client": self.__set_client}

    def run(self, tool_input: dict) -> str:
        prompt = tool_input["prompt"]
        sub_agent = AgentSub(self.__config.sub_agent, client=self.__client)

        # Fresh context for the child: no shared conversation history.
        sub_messages = [{"role": "user", "content": prompt}]
        response = sub_agent.agent_loop(sub_messages)

        result = "".join(b.text for b in response.content
                         if hasattr(b, "text")) or "(no summary)"
        return result

    def __set_client(self, helper_input: dict):
        """
        Helper hook (not a model tool): inject the parent's Anthropic client.
        Called via KitManager.run_helper("task_set_client", {"client": client}).
        """
        client = helper_input.get("client")
        self.__client = client
