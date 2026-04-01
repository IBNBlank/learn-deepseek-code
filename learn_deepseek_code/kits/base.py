#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from abc import ABC, abstractmethod
from typing import Callable, Iterable


# each tool could have multiple methods
# For example, the tool "file" could have the methods "read", "write", "edit"
# It's specs should be a list of dicts, each dict is a tool spec
# The tool methods should be a dict of method name and method function
class ToolBase(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def tool_specs(self) -> list[dict]:
        """Return a list of tool specs (Anthropic-style schema dicts)."""
        raise NotImplementedError

    @abstractmethod
    def tool_methods(self) -> dict[str, Callable[[dict], str]]:
        """Return mapping: tool_name -> callable(tool_input)->str."""
        raise NotImplementedError


