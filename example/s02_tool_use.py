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

try:
    from learn_deepseek_code.agent.agent import Agent, AgentConfig
    from learn_deepseek_code.constants import LOG_DIR
    from learn_deepseek_code.kit import (
        KitBash,
        KitBashConfig,
        KitFiles,
        KitFilesConfig,
        KitManager,
    )
except ModuleNotFoundError as e:
    missing = getattr(e, "name", None) or str(e)
    print(f"[error] Missing dependency: {missing}")
    print("Install deps with: pip install -r requirements.txt")
    raise


def print_answer(history: list) -> None:
    response_content = history[-1].get("content")
    if isinstance(response_content, list):
        for block in response_content:
            if hasattr(block, "text"):
                print(f"\n\033[32m[Answer]\033[0m")
                print(block.text)
        print()


if __name__ == "__main__":
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
    ])
    agent = Agent(
        AgentConfig(
            system_prompt=(f"You are a coding agent at {cur_work_dir}. "
                           "Use tools to solve tasks. Act, don't explain."),
            kit_manager=kit_manager,
            log_path=os.path.join(LOG_DIR, "s02_history.md"),
        ))

    history: list = []
    try:
        while True:
            try:
                query = input("\033[36ms02 >> \033[0m")
            except (EOFError, KeyboardInterrupt):
                raise SystemExit(0)
            if query.strip().lower() in ("q", "exit", ""):
                raise SystemExit(0)

            history.append({"role": "user", "content": query})
            history = agent.agent_loop(history)
            print_answer(history)
    except KeyboardInterrupt:
        pass
