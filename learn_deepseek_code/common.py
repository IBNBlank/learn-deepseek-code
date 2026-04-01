#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

import os

########################################################
# path
########################################################
REPO_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/.."

SKILLS_DIR = f"{REPO_DIR}/skills"
LOG_DIR = f"{REPO_DIR}/logs"
TRANSCRIPT_DIR = f"{REPO_DIR}/transcripts"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

########################################################
# api
########################################################
with open(f"{REPO_DIR}/api_key", "r") as f:
    API_KEY = f.read().strip()
BASE_URL = "https://api.deepseek.com/anthropic"
MODEL = "deepseek-chat"


########################################################
# utils
########################################################
def print_answer(history: list) -> None:
    response_content = history[-1].get("content")
    if isinstance(response_content, list):
        for block in response_content:
            if hasattr(block, "text"):
                print(f"\n\033[32m[Answer]\033[0m")
                print(block.text)
        print()
