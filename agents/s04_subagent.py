#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import os, sys, subprocess
from anthropic import Anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.utils import API_KEY, BASE_URL, MODEL
from agents.utils import LOG_DIR, init_log, append_msg, divide_log


def safe_path(p: str, root: str) -> str:
    full = os.path.realpath(os.path.join(root, p))
    root = os.path.realpath(root)
    try:
        under = os.path.commonpath([full, root]) == root
    except ValueError:
        under = False
    if not under:
        raise ValueError(f"Path escapes workspace: {p}")
    return full


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


def run_read(path: str, cur_work_dir: str, limit: int = None) -> str:
    try:
        with open(safe_path(path, cur_work_dir), encoding="utf-8") as f:
            text = f.read()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str, cur_work_dir: str) -> str:
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


def run_edit(path: str, old_text: str, new_text: str,
             cur_work_dir: str) -> str:
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


CHILD_TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read file contents.",
        "input_schema": {
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
    },
    {
        "name": "write_file",
        "description": "Write content to file.",
        "input_schema": {
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
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file.",
        "input_schema": {
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
    },
]
PARENT_TOOLS = CHILD_TOOLS + [
    {
        "name": "task",
        "description":
        "Spawn a subagent with fresh context. It shares the filesystem but not conversation history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string"
                },
                "description": {
                    "type": "string",
                    "description": "Short description of the task"
                }
            },
            "required": ["prompt"]
        }
    },
]


def run_subagent(
    client: Anthropic,
    prompt: str,
    log_path: str,
    agent_config: dict,
) -> str:
    sub_messages = []  # fresh context
    append_msg(
        sub_messages,
        {
            "role": "user",
            "content": prompt
        },
        log_path,
        sub_agent=True,
    )

    wd = agent_config["cur_work_dir"]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=agent_config["model"],
            system=agent_config["subagent_system_prompt"],
            messages=sub_messages,
            tools=agent_config["child_tools"],
            max_tokens=agent_config["max_tokens"],
        )
        append_msg(
            sub_messages,
            {
                "role": "assistant",
                "content": response.content,
            },
            log_path,
            sub_agent=True,
        )
        if response.stop_reason != "tool_use":
            break

        results = []
        for block in response.content:
            if block.type == "tool_use":
                try:
                    if block.name == "bash":
                        output = run_bash(block.input["command"], wd)
                    elif block.name == "read_file":
                        output = run_read(
                            block.input["path"],
                            wd,
                            block.input.get("limit"),
                        )
                    elif block.name == "write_file":
                        output = run_write(
                            block.input["path"],
                            block.input["content"],
                            wd,
                        )
                    elif block.name == "edit_file":
                        output = run_edit(
                            block.input["path"],
                            block.input["old_text"],
                            block.input["new_text"],
                            wd,
                        )
                    else:
                        output = f"Unknown tool: {block.name}"
                except Exception as e:
                    output = f"Error: {e}"
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)
                })
        append_msg(sub_messages, {
            "role": "user",
            "content": results
        },
                   log_path,
                   sub_agent=True)

    return "".join(b.text for b in response.content
                   if hasattr(b, "text")) or "(no summary)"


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
        append_msg(messages, {
            "role": "assistant",
            "content": response.content
        }, log_path)
        if response.stop_reason != "tool_use":
            return

        results = []
        wd = agent_config["cur_work_dir"]
        for block in response.content:
            if block.type == "tool_use":
                print(
                    f"\033[33m> {block.name}\033[0m \033[34m{block.input}\033[0m"
                )
                try:
                    if block.name == "task":
                        desc = block.input.get("description", "subtask")
                        print(
                            f"\033[35m> task ({desc}): {block.input['prompt']}\033[0m"
                        )
                        output = run_subagent(
                            client,
                            block.input["prompt"],
                            log_path,
                            agent_config,
                        )
                    elif block.name == "bash":
                        output = run_bash(block.input["command"], wd)
                    elif block.name == "read_file":
                        output = run_read(
                            block.input["path"],
                            wd,
                            block.input.get("limit"),
                        )
                    elif block.name == "write_file":
                        output = run_write(
                            block.input["path"],
                            block.input["content"],
                            wd,
                        )
                    elif block.name == "edit_file":
                        output = run_edit(
                            block.input["path"],
                            block.input["old_text"],
                            block.input["new_text"],
                            wd,
                        )
                    else:
                        output = f"Unknown tool: {block.name}"
                except Exception as e:
                    output = f"Error: {e}"
                print(output)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)
                })
        append_msg(messages, {"role": "user", "content": results}, log_path)
        divide_log(log_path)


if __name__ == "__main__":
    cur_work_dir = os.getcwd()
    agent_config = {
        "model":
        MODEL,
        "tools":
        PARENT_TOOLS,
        "child_tools":
        CHILD_TOOLS,
        "max_tokens":
        16000,
        "cur_work_dir":
        cur_work_dir,
        "system_prompt":
        f"You are a coding agent at {cur_work_dir}. Use the task tool to delegate exploration or subtasks.",
        "subagent_system_prompt":
        f"You are a coding subagent at {cur_work_dir}. Complete the given task, then summarize your findings."
    }
    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
    history = []

    log_path = os.path.join(LOG_DIR, "s04_history.md")
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
