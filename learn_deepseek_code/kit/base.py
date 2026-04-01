#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Iterable


class KitBase(ABC):
    """
    A kit is a bundle of tools (tool_name -> callable) plus their tool_specs.
    One kit can expose multiple tools/methods (e.g. file: read/write/edit).
    """

    @abstractmethod
    def specs(self) -> list[dict]:
        """Return a list of tool specs (Anthropic-style schema dicts)."""
        raise NotImplementedError

    @abstractmethod
    def tools(self) -> dict[str, Callable[[dict], str]]:
        """Return mapping: tool_name -> callable(tool_input)->str."""
        raise NotImplementedError

    # Backward-compatible aliases (old interface)
    def tool_specs(self) -> list[dict]:
        return self.specs()

    def tool_methods(self) -> dict[str, Callable[[dict], str]]:
        return self.tools()


class KitManager:
    """Compose multiple KitBase instances into one runnable tool-set."""

    def __init__(self, kits: Iterable[KitBase]):
        self._kits = list(kits)
        self._specs = self.merge_specs(self._kits)
        self._tools = self.merge_tools(self._kits)

    def specs(self) -> list[dict]:
        return self._specs

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return self._tools

    # Backward-compatible aliases (old interface)
    def tool_specs(self) -> list[dict]:
        return self.specs()

    def tool_methods(self) -> dict[str, Callable[[dict], str]]:
        return self.tools()

    def run_tool(self, tool_name: str, input: dict) -> str:
        fn = self._tools.get(tool_name)
        if fn is None:
            return f"Unknown tool: {tool_name}"
        return fn(input)

    @staticmethod
    def merge_specs(kits: Iterable[KitBase]) -> list[dict]:
        specs: list[dict] = []
        for k in kits:
            specs.extend(k.specs())
        return specs

    @staticmethod
    def merge_tools(
            kits: Iterable[KitBase]) -> dict[str, Callable[[dict], str]]:
        methods: dict[str, Callable[[dict], str]] = {}
        for k in kits:
            for name, fn in k.tools().items():
                if name in methods:
                    raise ValueError(f"Duplicate tool method name: {name}")
                methods[name] = fn
        return methods
