#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os

########################################################
# path
########################################################
BASE_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/.."
AGENT_DIR = f"{BASE_DIR}/agents"
SKILLS_DIR = f"{BASE_DIR}/skills"
LOG_DIR = f"{BASE_DIR}/logs"
os.makedirs(LOG_DIR, exist_ok=True)

########################################################
# api
########################################################
API_KEY_FILE = f"{BASE_DIR}/api_key"
with open(API_KEY_FILE, "r") as f:
    API_KEY = f.read().strip()
BASE_URL = "https://api.deepseek.com/anthropic"
MODEL = "deepseek-chat"

########################################################
# log
########################################################
_THINKING_HDR = '\n\n<font color="cyan">[thinking]</font>\n'
_ANSWER_HDR = '\n\n<b><font color="green">[answer]</font></b>\n'


def _assistant_other_hdr(block_type: str) -> str:
    t = block_type or "unknown"
    return f"\n<font color='yellow'>[assistant/{t}]</font>\n"


def _format_block_body_dict(block: dict) -> str:
    t = block.get("type")
    if t == "tool_use":
        name = block.get("name") or "unknown"
        parts = [f"name: {name}"]
        if block.get("input") is not None:
            parts.append(f"input: {block['input']}")
        return "\n".join(parts)
    if block.get("text") is not None:
        return str(block["text"])
    if block.get("thinking") is not None:
        return str(block["thinking"])
    if block.get("input") is not None:
        return str(block["input"])
    return str(block)


def _format_block_body_obj(block) -> str:
    t = getattr(block, "type", None)
    if t == "tool_use":
        name = getattr(block, "name", None) or "unknown"
        parts = [f"name: {name}"]
        inp = getattr(block, "input", None)
        if inp is not None:
            parts.append(f"input: {inp}")
        return "\n".join(parts)
    if getattr(block, "text", None) is not None:
        return str(block.text)
    if getattr(block, "thinking", None) is not None:
        return str(block.thinking)
    inp = getattr(block, "input", None)
    if inp is not None:
        return str(inp)
    return str(block)


def _format_content_for_log(content) -> str:
    if isinstance(content, str):
        return content.rstrip()
    lines = []
    for block in content:
        if isinstance(block, dict):
            t = block.get("type") or ""
            if t == "tool_result":
                tid = block.get("tool_use_id")
                lines.append(
                    f"\n<font color='yellow'>[tool_result tool_use_id={tid}]</font>\n"
                )
                lines.append(str(block.get("content", "")))
            elif t == "thinking":
                lines.append(_THINKING_HDR + str(block.get("thinking", "")))
            elif t == "text":
                lines.append(_ANSWER_HDR + str(block.get("text", "")))
            elif t not in ("text", "thinking"):
                lines.append(
                    _assistant_other_hdr(t) + _format_block_body_dict(block))
        else:
            t = getattr(block, "type", None) or ""
            if t == "thinking":
                lines.append(_THINKING_HDR +
                             str(getattr(block, "thinking", "")))
            elif t == "text":
                lines.append(_ANSWER_HDR + str(getattr(block, "text", "")))
            elif t not in ("text", "thinking"):
                lines.append(
                    _assistant_other_hdr(t) + _format_block_body_obj(block))
    return "\n".join(lines).rstrip()


def append_log(message: dict, log_path: str, sub_agent: bool = False) -> None:
    chunks = []
    body = _format_content_for_log(message["content"])
    if sub_agent:
        chunks.append(f"## SUBAGENT {message['role'].upper()}\n{body}\n")
    else:
        chunks.append(f"## {message['role'].upper()}\n{body}\n")
    block = "\n".join(chunks)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(block)


def append_msg(messages: list,
               msg: dict,
               log_path: str,
               sub_agent: bool = False) -> None:
    messages.append(msg)
    append_log(msg, log_path, sub_agent)


def divide_log(log_path: str) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n" + "---" + "\n\n")


def init_log(log_path: str) -> None:
    if os.path.exists(log_path):
        os.remove(log_path)

    name = os.path.basename(log_path)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"# {name}\n")
        f.write("\n" + "---" + "\n\n")
