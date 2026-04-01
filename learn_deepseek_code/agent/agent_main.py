#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

import os
from anthropic import Anthropic
from anthropic.types import Message
from dataclasses import dataclass

from ..constants import API_KEY, BASE_URL, MODEL
from ..kit.base import KitManager
from .log_util import LogUtil


@dataclass
class AgentMainConfig:
    system_prompt: str
    kit_manager: KitManager
    log_path: str

    api_key: str = API_KEY
    base_url: str = BASE_URL
    model: str = MODEL
    max_tokens: int = 16000
    cur_work_dir: str = os.getcwd()


class AgentMain:

    def __init__(self, config: AgentMainConfig):
        self.config = config
        self.client = Anthropic(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        self.__log_util = LogUtil(self.config.log_path)
        self.__history = []

        self.__kit_manager = self.config.kit_manager
        self.__tool_names = self.__kit_manager.tool_names()

        # todo tool
        self.__todo_flag = "todo" in self.__tool_names
        self.__rounds_since_todo = 0

        # task tool
        self.__task_flag = "task" in self.__tool_names
        self.__kit_manager.run_helper("task_set_client",
                                      {"client": self.client})

    def agent_loop(self, messages: list) -> list:
        while True:
            # get agent response
            response, messages = self.agent_response(messages)
            if response.stop_reason != "tool_use":
                self.__log_util.divide_log()
                return messages

            # call tools
            results = []
            used_todo = False
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "todo":
                        used_todo = True
                    results.append({
                        "type":
                        "tool_result",
                        "tool_use_id":
                        block.id,
                        "content":
                        self.call_tool(block.name, block.input),
                    })

            # todo tool: remind the agent to update the todos
            if self.__todo_flag:
                self.__rounds_since_todo = 0 if used_todo else self.__rounds_since_todo + 1
                if self.__rounds_since_todo >= 3:
                    results.append(
                        self.__kit_manager.run_helper("todo_reminder", {}))

            # append the results to the messages
            self.__log_util.append_msg(messages, {
                "role": "user",
                "content": results,
            })

    def agent_response(self, messages: list) -> tuple[Message, list]:
        response = self.client.messages.create(
            model=self.config.model,
            system=self.config.system_prompt,
            messages=messages,
            tools=self.config.kit_manager.specs(),
            max_tokens=self.config.max_tokens,
        )
        self.__log_util.append_msg(messages, {
            "role": "assistant",
            "content": response.content
        })
        return response, messages

    def call_tool(self, tool_name: str, tool_input: dict) -> str:
        print(f"\033[33m< {tool_name}\033[0m \033[34m{tool_input}\033[0m")
        try:
            output = self.__kit_manager.run_tool(tool_name, tool_input)
        except Exception as e:
            output = f"Error: {e}"
        print(f"{output}")
        return output
