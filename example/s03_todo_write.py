#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_DIR not in sys.path:
    sys.path.append(REPO_DIR)

from learn_deepseek_code.agent import AgentMain, AgentMainConfig
from learn_deepseek_code.constants import LOG_DIR
from learn_deepseek_code.kit import KitBash, KitBashConfig, KitFiles, KitFilesConfig, KitManager, KitTodo, KitTodoConfig


def print_answer(history: list) -> None:
    response_content = history[-1].get("content")
    if isinstance(response_content, list):
        for block in response_content:
            if hasattr(block, "text"):
                print(f"\n\033[32m[Answer]\033[0m")
                print(block.text)
        print()


def main() -> int:
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitTodo(KitTodoConfig()),
    ])
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=f"""You are a coding agent at {cur_work_dir}.
Use the todo tool to plan multi-step tasks. Mark in_progress before starting, completed when done.
Prefer tools over prose.""",
            kit_manager=kit_manager,
            log_path=os.path.join(LOG_DIR, "s03_history.md"),
            cur_work_dir=cur_work_dir,
        ))

    history: list = []
    try:
        while True:
            try:
                query = input("\033[36ms03 >> \033[0m")
            except (EOFError, KeyboardInterrupt):
                return 0
            if query.strip().lower() in ("q", "exit", ""):
                return 0

            history.append({"role": "user", "content": query})
            history = agent.agent_loop(history)
            print_answer(history)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
