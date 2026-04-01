#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import os, sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_DIR not in sys.path:
    sys.path.append(REPO_DIR)

from learn_deepseek_code.common import LOG_DIR
from learn_deepseek_code.common import print_answer

from learn_deepseek_code.agent import AgentMain, AgentMainConfig

from learn_deepseek_code.kit import KitManager
from learn_deepseek_code.kit import KitBash, KitBashConfig
from learn_deepseek_code.kit import KitFiles, KitFilesConfig
from learn_deepseek_code.kit import KitSkill, KitSkillConfig


def main() -> int:
    cur_work_dir = os.getcwd()
    kit_manager = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitSkill(KitSkillConfig()),
    ])
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=f"""You are a coding agent at {cur_work_dir}.
Use load_skill to access specialized knowledge before tackling unfamiliar topics.

Skills available:
{kit_manager.run_helper("skill_get_system", {})}""",
            kit_manager=kit_manager,
            log_path=os.path.join(LOG_DIR, "s05_history.md"),
            cur_work_dir=cur_work_dir,
        ))

    history: list = []
    try:
        while True:
            try:
                query = input("\033[36ms05 >> \033[0m")
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
