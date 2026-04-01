#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

import json, time, os
import tiktoken
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from anthropic import Anthropic

from .base import KitBase
from ..constants import TRANSCRIPT_DIR


@dataclass
class KitCompactConfig:
    """
    Implements the 3-layer compaction pipeline (see `example/s06_context_compact.py`):
    - Layer 1: replace old tool_result content with placeholders (silent, every turn)
    - Layer 2: auto summarize when tokens exceed threshold (save transcript + summarize)
    - Layer 3: manual `compact` tool trigger (agent loop performs summarize)
    """

    keep_recent: int = 3
    preserve_result_tools: list[str] = field(default_factory=lambda: ["read_file"])
    token_threshold: int = 50_000
    summary_max_tokens: int = 2_000
    conversation_max_chars: int = 80_000
    transcript_dir: str = TRANSCRIPT_DIR


class KitCompact(KitBase):
    """
    Layer 3 (manual): model requests compression.
    ``run`` only returns an acknowledgement; the agent loop must append tool
    results, then replace ``messages`` with the actual compaction result.
    """

    def __init__(self, config: Optional[KitCompactConfig] = None):
        self._config = config or KitCompactConfig()
        self._enc = tiktoken.get_encoding("cl100k_base")

    def specs(self) -> list[dict]:
        return [{
            "name": "compact",
            "description":
            "Trigger manual conversation compression (summarize and shrink history).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "focus": {
                        "type":
                        "string",
                        "description":
                        "What to preserve or emphasize in the summary",
                    }
                },
            },
        }]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"compact": self.run}

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        return {
            "compact_tool_compact": self.tool_compact,
            "compact_auto_compact": self.auto_compact,
            "compact_manual_compact": self.manual_compact,
        }

    def run(self, tool_input: dict) -> str:
        return "Compressing..."

    # -- Layer 1: micro_compact (tool_compact) --
    def tool_compact(self, messages: list) -> list:
        # Collect (msg_index, part_index, tool_result_dict) for all tool_result entries
        tool_results = []
        for msg_idx, msg in enumerate(messages):
            if msg["role"] == "user" and isinstance(msg.get("content"), list):
                for part_idx, part in enumerate(msg["content"]):
                    if isinstance(part,
                                  dict) and part.get("type") == "tool_result":
                        tool_results.append((msg_idx, part_idx, part))
        if len(tool_results) <= self._config.keep_recent:
            return messages
        # Find tool_name for each result by matching tool_use_id in prior assistant messages
        tool_name_map = {}
        for msg in messages:
            if msg["role"] == "assistant":
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, "type") and block.type == "tool_use":
                            tool_name_map[block.id] = block.name
        # Clear old results (keep last KEEP_RECENT). Preserve read_file outputs because
        # they are reference material; compacting them forces the agent to re-read files.
        to_clear = tool_results[:-self._config.keep_recent]
        for _, _, result in to_clear:
            if not isinstance(result.get("content"), str) or len(
                    result["content"]) <= 100:
                continue
            tool_id = result.get("tool_use_id", "")
            tool_name = tool_name_map.get(tool_id, "unknown")
            if tool_name in self._config.preserve_result_tools:
                continue
            result["content"] = f"[Previous: used {tool_name}]"
        return messages

    # -- Layer 2: auto_compact (token check + agent_compact) --
    def auto_compact(self, client: Anthropic, model: str,
                     messages: list) -> list:
        if self.__estimate_tokens(messages) > self._config.token_threshold:
            return self.manual_compact(client, model, messages)
        return messages

    # -- Layer 3: manual_compact (angent call + agent tool) --
    def manual_compact(self, client: Anthropic, model: str,
                       messages: list) -> list:
        # Save full transcript to disk
        os.makedirs(self._config.transcript_dir, exist_ok=True)
        transcript_path = os.path.join(self._config.transcript_dir,
                                       f"transcript_{int(time.time())}.jsonl")
        with open(transcript_path, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg, default=str) + "\n")
        print(f"[transcript saved: {transcript_path}]")
        # Ask LLM to summarize
        conversation_text = json.dumps(
            messages, default=str)[-self._config.conversation_max_chars:]
        response = client.messages.create(
            model=model,
            messages=[{
                "role":
                "user",
                "content":
                "Summarize this conversation for continuity. Include: "
                "1) What was accomplished, 2) Current state, 3) Key decisions made. "
                "Be concise but preserve critical details.\n\n" +
                conversation_text
            }],
            max_tokens=self._config.summary_max_tokens,
        )
        summary = response.content[0].text
        # Replace all messages with compressed summary
        return [
            {
                "role":
                "user",
                "content":
                f"[Conversation compressed. Transcript: {transcript_path}]\n\n{summary}"
            },
        ]

    def __estimate_tokens(self, messages: list[dict[str, Any]]) -> int:
        """
        Prefer `tiktoken` when available; otherwise use a rough heuristic.
        """
        if self._enc is None:
            return len(str(messages)) // 4
        total = 0
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, str):
                total += len(self._enc.encode(content))
            else:
                total += len(self._enc.encode(str(content)))
        return total
