#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

import os

_THINKING_HDR = '\n\n<font color="cyan">[thinking]</font>\n'
_ANSWER_HDR = '\n\n<b><font color="green">[answer]</font></b>\n'


class LogUtil:

    def __init__(self, log_path: str | None = None):
        self.log_path = log_path

        if os.path.exists(log_path):
            os.remove(log_path)

        name = os.path.basename(log_path)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n")
            f.write("\n" + "---" + "\n\n")

    def append_log(self, message: dict, sub_agent: bool = False) -> None:
        body = LogUtil._format_content_for_log(message["content"])
        if sub_agent:
            block = f"## SUBAGENT {message['role'].upper()}\n{body}\n"
        else:
            block = f"## {message['role'].upper()}\n{body}\n"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(block)

    def append_msg(self,
                   messages: list,
                   msg: dict,
                   sub_agent: bool = False) -> None:
        messages.append(msg)
        self.append_log(msg, sub_agent=sub_agent)

    def divide_log(self) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "---" + "\n\n")

    @staticmethod
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
                    lines.append(_THINKING_HDR +
                                 str(block.get("thinking", "")))
                elif t == "text":
                    lines.append(_ANSWER_HDR + str(block.get("text", "")))
                elif t not in ("text", "thinking"):
                    lines.append(
                        LogUtil._assistant_other_hdr(t) +
                        LogUtil._format_block_body_dict(block))
            else:
                t = getattr(block, "type", None) or ""
                if t == "thinking":
                    lines.append(_THINKING_HDR +
                                 str(getattr(block, "thinking", "")))
                elif t == "text":
                    lines.append(_ANSWER_HDR + str(getattr(block, "text", "")))
                elif t not in ("text", "thinking"):
                    lines.append(
                        LogUtil._assistant_other_hdr(t) +
                        LogUtil._format_block_body_obj(block))
        return "\n".join(lines).rstrip()

    @staticmethod
    def _assistant_other_hdr(block_type: str) -> str:
        t = block_type or "unknown"
        return f"\n<font color='yellow'>[assistant/{t}]</font>\n"

    @staticmethod
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

    @staticmethod
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
