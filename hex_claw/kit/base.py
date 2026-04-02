#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

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

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        """Return mapping: code_tool_name -> callable(code_input)->str."""
        return {}


class KitManager:
    """Compose multiple KitBase instances into one runnable tool-set."""

    def __init__(self, kits: Iterable[KitBase]):
        self.__kits = list(kits)
        self.__specs = self.__merge_specs(self.__kits)
        self.__tools = self.__merge_tools(self.__kits)
        self.__helpers = self.__merge_helpers(self.__kits)

    def specs(self) -> list[dict]:
        return self.__specs

    def tool_names(self) -> list[str]:
        return list(self.__tools.keys())

    def helper_names(self) -> list[str]:
        return list(self.__helpers.keys())

    def run_helper(self, helper_name: str, input: dict) -> str:
        fn = self.__helpers.get(helper_name)
        if fn is None:
            return f"Unknown helper: {helper_name}"
        return fn(input)

    def run_tool(self, tool_name: str, input: dict) -> str:
        fn = self.__tools.get(tool_name)
        if fn is None:
            return f"Unknown tool: {tool_name}"
        return fn(input)

    @staticmethod
    def __merge_specs(kits: Iterable[KitBase]) -> list[dict]:
        specs: list[dict] = []
        for k in kits:
            specs.extend(k.specs())
        return specs

    @staticmethod
    def __merge_tools(
            kits: Iterable[KitBase]) -> dict[str, Callable[[dict], str]]:
        methods: dict[str, Callable[[dict], str]] = {}
        for k in kits:
            for name, fn in k.tools().items():
                if name in methods:
                    raise ValueError(f"Duplicate tool method name: {name}")
                methods[name] = fn
        return methods

    @staticmethod
    def __merge_helpers(
            kits: Iterable[KitBase]) -> dict[str, Callable[[dict], str]]:
        methods: dict[str, Callable[[dict], str]] = {}
        for k in kits:
            for name, fn in k.helpers().items():
                if name in methods:
                    raise ValueError(f"Duplicate helper method name: {name}")
                methods[name] = fn
        return methods
