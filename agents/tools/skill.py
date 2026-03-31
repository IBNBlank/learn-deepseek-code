#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-03-31
################################################################

import os
import re
from pathlib import Path

from agents.utils import SKILLS_DIR

from .common import ToolBase


class SkillTool(ToolBase):
    """Loads markdown skills (YAML frontmatter + body), matching agents/s05_skill_loading.py."""

    def __init__(self, skills_dir: str | None = None):
        sd = skills_dir if skills_dir is not None else SKILLS_DIR
        self.skills_dir = os.path.normpath(os.path.join(os.getcwd(), sd))
        self.skills: dict = {}
        self._load_all()

    def _register_skill(self, full_path: Path) -> None:
        text = full_path.read_text(encoding="utf-8")
        meta, body = self._parse_frontmatter(text)
        if full_path.name == "SKILL.md":
            default_name = full_path.parent.name
        else:
            default_name = full_path.stem
        name = meta.get("name", default_name)
        self.skills[name] = {
            "meta": meta,
            "body": body,
            "path": str(full_path),
        }

    def _load_all(self) -> None:
        root = Path(self.skills_dir)
        if not root.is_dir():
            return
        # s05: top-level *.md in skills_dir
        for f in sorted(root.glob("*.md")):
            self._register_skill(f)
        # nested SKILL.md (e.g. skills/foo/SKILL.md)
        for f in sorted(root.rglob("SKILL.md")):
            if f.parent == root:
                continue
            self._register_skill(f)

    def _parse_frontmatter(self, text: str) -> tuple:
        """Parse YAML frontmatter between --- delimiters."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        meta = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta, match.group(2).strip()

    @property
    def name(self) -> str:
        return "load_skill"

    @property
    def description(self) -> str:
        return "Load specialized knowledge by name."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name to load",
                }
            },
            "required": ["name"],
        }

    def get_system(self) -> str:
        """Layer 1: short descriptions for the system prompt."""
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
        """Layer 2: full skill body returned in tool_result."""
        skill = self.skills.get(name)
        if not skill:
            return (
                f"Error: Unknown skill '{name}'. "
                f"Available: {', '.join(self.skills.keys())}"
            )
        return f'<skill name="{name}">\n{skill["body"]}\n</skill>'

    def run(self, tool_input: dict, cur_work_dir: str) -> str:
        return self.get_content(tool_input["name"])
