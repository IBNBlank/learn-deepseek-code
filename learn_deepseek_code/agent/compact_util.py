#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import time, json
import tiktoken
from anthropic import Anthropic


class CompactUtils:

    def __init__(self,
                 keep_recent: int = 3,
                 token_threshold: int = 50000,
                 summary_max_tokens: int = 2000,
                 conversation_max_chars: int = 80000):
        self.keep_recent = keep_recent
        self.token_threshold = token_threshold
        self.summary_max_tokens = summary_max_tokens
        self.conversation_max_chars = conversation_max_chars
        self.enc = tiktoken.get_encoding("cl100k_base")

    def estimate_tokens(self, messages: list) -> int:
        return sum(
            len(self.enc.encode(m.get("content", ""))) for m in messages)

    # -- Layer 1: tool_compact - replace old tool results with placeholders --
    def tool_compact(self, messages: list, keep_recent: int = None) -> list:
        if keep_recent is None:
            keep_recent = self.keep_recent

        # Collect (msg_index, part_index, tool_result_dict) for all tool_result entries
        tool_results = []
        for msg_idx, msg in enumerate(messages):
            if msg["role"] == "user" and isinstance(msg.get("content"), list):
                for part_idx, part in enumerate(msg["content"]):
                    if isinstance(part,
                                  dict) and part.get("type") == "tool_result":
                        tool_results.append((msg_idx, part_idx, part))
        if len(tool_results) <= keep_recent:
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
        # Clear old results (keep last KEEP_RECENT)
        to_clear = tool_results[:-keep_recent]
        for _, _, result in to_clear:
            if isinstance(result.get("content"), str) and len(
                    result["content"]) > 100:
                tool_id = result.get("tool_use_id", "")
                tool_name = tool_name_map.get(tool_id, "unknown")
                result["content"] = f"[Previous: used {tool_name}]"
        return messages

    # -- Layer 2: agent_compact - save transcript, summarize, replace messages --
    def agent_compact(self, client: Anthropic, messages: list) -> list:
        # Save full transcript to disk
        TRANSCRIPT_DIR.mkdir(exist_ok=True)
        transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
        with open(transcript_path, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg, default=str) + "\n")
        print(f"[transcript saved: {transcript_path}]")
        # Ask LLM to summarize
        conversation_text = json.dumps(messages, default=str)[:80000]
        response = client.messages.create(
            model=MODEL,
            messages=[{
                "role":
                "user",
                "content":
                "Summarize this conversation for continuity. Include: "
                "1) What was accomplished, 2) Current state, 3) Key decisions made. "
                "Be concise but preserve critical details.\n\n" +
                conversation_text
            }],
            max_tokens=self.summary_max_tokens,
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
            {
                "role":
                "assistant",
                "content":
                "Understood. I have the context from the summary. Continuing."
            },
        ]
