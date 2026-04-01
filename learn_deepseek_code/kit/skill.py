#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

from dataclasses import dataclass
import os
import re
from pathlib import Path
from typing import Callable

from ..constants import SKILLS_DIR
from .base import KitBase


@dataclass
class SkillKitConfig:
    skills_dir: str | None = None


class SkillKit(KitBase):
    """Loads markdown skills (YAML frontmatter + body)."""

    def __init__(self, config: SkillKitConfig):
        self._config = config
        sd = config.skills_dir if config.skills_dir is not None else SKILLS_DIR
        self.skills_dir = os.path.normpath(os.path.join(os.getcwd(), sd))
        self.skills: dict = {}
        self._load_all()

    def _register_skill(self, full_path: Path) -> None:
        text = full_path.read_text(encoding="utf-8")
        meta, body = self._parse_frontmatter(text)
        default_name = full_path.parent.name if full_path.name == "SKILL.md" else full_path.stem
        name = meta.get("name", default_name)
        self.skills[name] = {"meta": meta, "body": body, "path": str(full_path)}

    def _load_all(self) -> None:
        root = Path(self.skills_dir)
        if not root.is_dir():
            return
        for f in sorted(root.glob("*.md")):
            self._register_skill(f)
        for f in sorted(root.rglob("SKILL.md")):
            if f.parent == root:
                continue
            self._register_skill(f)

    def _parse_frontmatter(self, text: str) -> tuple[dict, str]:
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        meta: dict[str, str] = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta, match.group(2).strip()

    def specs(self) -> list[dict]:
        return [
            {
                "name": "load_skill",
                "description": "Load specialized knowledge by name.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Skill name to load"}
                    },
                    "required": ["name"],
                },
            }
        ]

    def tools(self) -> dict[str, Callable[[dict], str]]:
        return {"load_skill": self.run}

    def get_system(self) -> str:
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

    def get_content(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self.skills.keys())}"
        return f'<skill name="{name}">\n{skill["body"]}\n</skill>'

    def run(self, tool_input: dict) -> str:
        return self.get_content(tool_input["name"])
