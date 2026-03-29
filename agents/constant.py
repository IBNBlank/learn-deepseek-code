#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-29
################################################################

import os

BASE_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/../"

API_KEY_FILE = f"{BASE_DIR}/api_key"
with open(API_KEY_FILE, "r") as f:
    API_KEY = f.read().strip()

BASE_URL = "https://api.deepseek.com/anthropic"

MODEL = "deepseek-chat"
