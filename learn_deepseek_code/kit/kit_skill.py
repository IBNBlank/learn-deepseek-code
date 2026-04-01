#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from dataclasses import dataclass
import glob
import os
import re
from typing import Callable, Optional

from ..constants import SKILLS_DIR
from .base import KitBase


@dataclass
class KitSkillConfig:
    skills_dir: str = SKILLS_DIR


class KitSkill(KitBase):
    """Loads markdown skills (YAML frontmatter + body)."""

    def __init__(self, config: Optional[KitSkillConfig] = None):
        self.__config = config or KitSkillConfig()
        self.skills: dict = {}
        self.__load_all()

    def specs(self) -> list[dict]:
        return [{
            "name": "load_skill",
            "description": "Load specialized knowledge by name.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Skill name to load"
                    }
                },
                "required": ["name"],
            },
        }]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"load_skill": self.run}

    def helpers(self) -> dict[str, Callable[[dict], str]]:
        return {"skill_get_system": self.__get_system}

    def run(self, tool_input: dict) -> str:
        name = tool_input["name"]
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self.skills.keys())}"
        return f'<skill name="{name}">\n{skill["body"]}\n</skill>'

    def __register_skill(self, full_path: str) -> None:
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()
        meta, body = self.__parse_frontmatter(text)
        base = os.path.basename(full_path)
        default_name = os.path.basename(os.path.dirname(
            full_path)) if base == "SKILL.md" else os.path.splitext(base)[0]
        name = meta.get("name", default_name)
        self.skills[name] = {
            "meta": meta,
            "body": body,
            "path": str(full_path),
        }

    def __load_all(self) -> None:
        root = self.__config.skills_dir
        if not os.path.isdir(root):
            return
        for full_path in sorted(glob.glob(os.path.join(root, "*.md"))):
            self.__register_skill(full_path)

        for dirpath, _dirnames, filenames in os.walk(root):
            if os.path.abspath(dirpath) == os.path.abspath(root):
                continue
            if "SKILL.md" in filenames:
                self.__register_skill(os.path.join(dirpath, "SKILL.md"))

    def __parse_frontmatter(self, text: str) -> tuple[dict, str]:
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        meta: dict[str, str] = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta, match.group(2).strip()

    def __get_system(self, helper_input: dict) -> str:
        if not self.skills:
            return "(no skills available)"
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "No description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return "\n".join(lines)
