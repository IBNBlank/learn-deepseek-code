#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os, sys, subprocess
from anthropic import Anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import API_KEY, BASE_URL, MODEL
from agents.utils import LOG_DIR, init_log, append_msg, divide_log

TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string"
            }
        },
        "required": ["command"],
    },
}]


def run_bash(command: str, cur_work_dir: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=cur_work_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def agent_loop(
    client: Anthropic,
    messages: list,
    log_path: str,
    agent_config: dict,
):
    while True:
        response = client.messages.create(
            model=agent_config["model"],
            system=agent_config["system_prompt"],
            messages=messages,
            tools=agent_config["tools"],
            max_tokens=agent_config["max_tokens"],
        )

        # Append assistant turn
        append_msg(messages, {
            "role": "assistant",
            "content": response.content
        }, log_path)

        # If the model didn't call a tool, we're done
        if response.stop_reason != "tool_use":
            return

        # Execute each tool call, collect results
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\033[33m$ {block.input['command']}\033[0m")
                if block.name == "bash":
                    output = run_bash(
                        block.input["command"],
                        agent_config["cur_work_dir"],
                    )
                else:
                    output = f"Unknown tool: {block.name}"
                print(output)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })
        append_msg(messages, {"role": "user", "content": results}, log_path)

        # Divide the log
        divide_log(log_path)


if __name__ == "__main__":
    cur_work_dir = os.getcwd()
    agent_config = {
        "model":
        MODEL,
        "tools":
        TOOLS,
        "max_tokens":
        16000,
        "cur_work_dir":
        cur_work_dir,
        "system_prompt":
        f"You are a coding agent at {cur_work_dir}. Use bash to solve tasks. Act, don't explain.",
    }
    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
    history = []

    log_path = os.path.join(LOG_DIR, "s01_history.md")
    init_log(log_path)
    try:
        while True:
            try:
                query = input("\033[36ms01 >> \033[0m")
            except (EOFError, KeyboardInterrupt):
                break
            if query.strip().lower() in ("q", "exit", ""):
                break

            append_msg(history, {"role": "user", "content": query}, log_path)
            agent_loop(client, history, log_path, agent_config)

            response_content = history[-1]["content"]
            if isinstance(response_content, list):
                for block in response_content:
                    if hasattr(block, "text"):
                        print(f"\n\033[32m[Answer]\033[0m")
                        print(block.text)
            print()
    except KeyboardInterrupt:
        pass
