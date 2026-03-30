#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os, sys
from anthropic import Anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import API_KEY, BASE_URL, MODEL
from agents.utils import LOG_DIR, init_log, append_msg, divide_log
from agents.tools import ToolManager


def agent_loop(
    client: Anthropic,
    messages: list,
    agent_config: dict,
):
    tool_manager = agent_config["tool_manager"]
    while True:
        response = client.messages.create(
            model=agent_config["model"],
            system=agent_config["system_prompt"],
            messages=messages,
            tools=tool_manager.tool_specs(),
            max_tokens=agent_config["max_tokens"],
        )
        append_msg(messages, {
            "role": "assistant",
            "content": response.content
        }, agent_config["log_path"])
        if response.stop_reason != "tool_use":
            divide_log(agent_config["log_path"])
            return

        results = []
        wd = agent_config["cur_work_dir"]
        for block in response.content:
            if block.type == "tool_use":
                print(
                    f"\033[33m {block.name}\033[0m \033[34m{block.input}\033[0m"
                )
                try:
                    output = tool_manager.run_tool(block.name, block.input, wd)
                except Exception as e:
                    output = f"Error: {e}"
                print(output)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })
        append_msg(messages, {
            "role": "user",
            "content": results
        }, agent_config["log_path"])


if __name__ == "__main__":
    cur_work_dir = os.getcwd()

    tool_names = ["bash", "read_file", "write_file", "edit_file"]
    tool_manager = ToolManager(tool_names)
    agent_config = {
        "model":
        MODEL,
        "max_tokens":
        16000,
        "cur_work_dir":
        cur_work_dir,
        "log_path":
        os.path.join(LOG_DIR, "s02_history.md"),
        "tool_manager":
        tool_manager,
        "system_prompt":
        f"You are a coding agent at {cur_work_dir}. Use tools to solve tasks. Act, don't explain.",
    }

    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
    history = []
    init_log(agent_config["log_path"])
    try:
        while True:
            try:
                query = input("\033[36ms02 >> \033[0m")
            except (EOFError, KeyboardInterrupt):
                break
            if query.strip().lower() in ("q", "exit", ""):
                break

            append_msg(history, {
                "role": "user",
                "content": query
            }, agent_config["log_path"])
            agent_loop(client, history, agent_config)

            response_content = history[-1]["content"]
            if isinstance(response_content, list):
                for block in response_content:
                    if hasattr(block, "text"):
                        print(f"\n\033[32m[Answer]\033[0m")
                        print(block.text)
            print()
    except KeyboardInterrupt:
        pass
