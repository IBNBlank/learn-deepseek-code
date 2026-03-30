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

TOOLS = [
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
    {
        "name": "todo",
        "description": "Update task list. Track progress on multi-step tasks.",
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
                                "type": "string",
                                "enum":
                                ["pending", "in_progress", "completed"]
                            }
                        },
                        "required": ["id", "text", "status"]
                    }
                }
            },
            "required": ["items"]
        }
    },
]


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


class TodoManager:

    def __init__(self):
        self.items = []

    def update(self, items: list) -> str:
        if len(items) > 20:
            raise ValueError("Max 20 todos allowed")
        validated = []
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
        self.items = validated
        return self.render()

    def render(self) -> str:
        if not self.items:
            return "No todos."
        lines = []
        for item in self.items:
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]"
            }[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['text']}")
        done = sum(1 for t in self.items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(self.items)} completed)")
        return "\n".join(lines)


def agent_loop(
    client: Anthropic,
    messages: list,
    log_path: str,
    agent_config: dict,
):
    todo_manager = agent_config["todo_manager"]
    rounds_since_todo = 0
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
        used_todo = False
        wd = agent_config["cur_work_dir"]
        for block in response.content:
            if block.type == "tool_use":
                print(
                    f"\033[33m> {block.name}\033[0m \033[34m{block.input}\033[0m"
                )
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
                    elif block.name == "todo":
                        output = todo_manager.update(block.input["items"])
                        used_todo = True
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
        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
        if rounds_since_todo >= 3:
            results.append({
                "type": "text",
                "text": "<reminder>Update your todos.</reminder>"
            })
        append_msg(messages, {"role": "user", "content": results}, log_path)

        divide_log(log_path)


if __name__ == "__main__":
    cur_work_dir = os.getcwd()
    agent_config = {
        "model": MODEL,
        "tools": TOOLS,
        "max_tokens": 16000,
        "cur_work_dir": cur_work_dir,
        "system_prompt": f"""You are a coding agent at {cur_work_dir}.
Use the todo tool to plan multi-step tasks. Mark in_progress before starting, completed when done.
Prefer tools over prose.""",
        "todo_manager": TodoManager(),
    }
    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
    history = []

    log_path = os.path.join(LOG_DIR, "s03_history.md")
    init_log(log_path)
    try:
        while True:
            try:
                query = input("\033[36ms03 >> \033[0m")
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
