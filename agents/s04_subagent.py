#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import os, sys
from anthropic import Anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import API_KEY, BASE_URL, MODEL
from agents.utils import LOG_DIR, init_log, append_msg, divide_log
from agents.tools import ToolManager, TaskTool


def run_subagent(
    client: Anthropic,
    prompt: str,
    agent_config: dict,
) -> str:
    tool_manager = agent_config["child_tool_manager"]
    sub_messages = []
    append_msg(
        sub_messages,
        {
            "role": "user",
            "content": prompt
        },
        agent_config["log_path"],
        sub_agent=True,
    )

    wd = agent_config["cur_work_dir"]
    response = None
    for _ in range(30):
        response = client.messages.create(
            model=agent_config["model"],
            system=agent_config["subagent_system_prompt"],
            messages=sub_messages,
            tools=tool_manager.tool_specs(),
            max_tokens=agent_config["max_tokens"],
        )
        append_msg(
            sub_messages,
            {
                "role": "assistant",
                "content": response.content,
            },
            agent_config["log_path"],
            sub_agent=True,
        )
        if response.stop_reason != "tool_use":
            break

        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(
                    f"\033[33m>> {block.name}\033[0m \033[34m{block.input}\033[0m"
                )
                try:
                    output = tool_manager.run_tool(block.name, block.input, wd)
                except Exception as e:
                    output = f"Error: {e}"
                print(f">> {output}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)
                })
        append_msg(sub_messages, {
            "role": "user",
            "content": results
        },
                   agent_config["log_path"],
                   sub_agent=True)

    if response is None:
        return "(no summary)"
    return "".join(b.text for b in response.content
                   if hasattr(b, "text")) or "(no summary)"


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
                if block.name == "task":
                    desc = block.input.get("description", "subtask")
                    print(
                        f"\033[35m> task ({desc}): {block.input['prompt']}\033[0m"
                    )
                try:
                    output = tool_manager.run_tool(block.name, block.input, wd)
                except Exception as e:
                    output = f"Error: {e}"
                print(output)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)
                })
        append_msg(messages, {
            "role": "user",
            "content": results
        }, agent_config["log_path"])


if __name__ == "__main__":
    cur_work_dir = os.getcwd()
    log_path = os.path.join(LOG_DIR, "s04_history.md")
    child_tool_names = ["bash", "read_file", "write_file", "edit_file"]
    child_tool_manager = ToolManager(child_tool_names)
    agent_config = {
        "model":
        MODEL,
        "max_tokens":
        16000,
        "cur_work_dir":
        cur_work_dir,
        "log_path":
        log_path,
        "child_tool_manager":
        child_tool_manager,
        "system_prompt":
        f"You are a coding agent at {cur_work_dir}. Use the task tool to delegate exploration or subtasks.",
        "subagent_system_prompt":
        f"You are a coding subagent at {cur_work_dir}. Complete the given task, then summarize your findings."
    }

    def _run_task(tool_input: dict, _wd: str) -> str:
        return run_subagent(
            client,
            tool_input["prompt"],
            agent_config,
        )

    task_tool = TaskTool(_run_task)
    parent_tool_manager = ToolManager(child_tool_names + [task_tool])
    agent_config["tool_manager"] = parent_tool_manager

    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
    history = []
    init_log(log_path)
    try:
        while True:
            try:
                query = input("\033[36ms04 >> \033[0m")
            except (EOFError, KeyboardInterrupt):
                break
            if query.strip().lower() in ("q", "exit", ""):
                break

            append_msg(history, {"role": "user", "content": query}, log_path)
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
