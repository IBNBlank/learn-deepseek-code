#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os, sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_DIR not in sys.path:
    sys.path.append(REPO_DIR)

from hex_claw.common import LOG_DIR
from hex_claw.common import print_answer

from hex_claw.agent import AgentMain, AgentMainConfig

from hex_claw.kit import KitManager
from hex_claw.kit import KitBash, KitBashConfig
from hex_claw.kit import KitFiles, KitFilesConfig


def main() -> int:
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
    ])
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=(f"You are a coding agent at {cur_work_dir}. "
                           "Use tools to solve tasks. Act, don't explain."),
            kit_manager=kit_manager,
            log_path=os.path.join(LOG_DIR, "s02_history.md"),
            cur_work_dir=cur_work_dir,
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
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
