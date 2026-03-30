#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-30
################################################################

import os


class ToolBase:

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def input_schema(self) -> dict:
        raise NotImplementedError

    def to_spec(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        raise NotImplementedError


def safe_path(p: str, root: str) -> str:
    full = os.path.realpath(os.path.join(root, p))
    root = os.path.realpath(root)
    try:
        under = os.path.commonpath([full, root]) == root
    except ValueError:
        under = False
    if not under:
        raise ValueError(f"Path escapes workspace: {p}")
    return full
