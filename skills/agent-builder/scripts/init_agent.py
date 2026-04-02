#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Hex Claw Agent Scaffold - 生成基于hex_claw框架的代理脚本。

Usage:
    python init_agent.py <agent-name> [--level 1-6|full] [--path <output-dir>]

Examples:
    python init_agent.py my_bot                    # Level 2 (bash + files)
    python init_agent.py my_bot --level 1          # Level 1 (bash only)
    python init_agent.py my_bot --level 4          # Level 4 (+ subagent)
    python init_agent.py my_bot --level full       # All features
    python init_agent.py my_bot --path ./agents    # Custom output directory
"""

import argparse
import sys
import textwrap
from pathlib import Path

HEADER = '''\
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_DIR not in sys.path:
    sys.path.append(REPO_DIR)

from hex_claw.common import LOG_DIR
from hex_claw.common import print_answer
'''

LEVEL_CONFIGS = {
    1: {
        "desc": "L1 - Agent Loop (bash only)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
        ],
        "kits": [
            "KitBash(KitBashConfig(work_dir=cur_work_dir)),",
        ],
        "system_prompt": (
            'f"You are a coding agent at {cur_work_dir}. "\n'
            '                           "Use bash to solve tasks. Act, don\'t explain."'
        ),
        "extra_setup": "",
    },
    2: {
        "desc": "L2 - Tool Use (bash + files)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
        ],
        "kits": [
            "KitBash(KitBashConfig(work_dir=cur_work_dir)),",
            "KitFiles(KitFilesConfig(work_dir=cur_work_dir)),",
        ],
        "system_prompt": (
            'f"You are a coding agent at {cur_work_dir}. "\n'
            '                           "Use tools to solve tasks. Act, don\'t explain."'
        ),
        "extra_setup": "",
    },
    3: {
        "desc": "L3 - Todo Write (bash + files + todo)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
            "from hex_claw.kit import KitTodo, KitTodoConfig",
        ],
        "kits": [
            "KitBash(KitBashConfig(work_dir=cur_work_dir)),",
            "KitFiles(KitFilesConfig(work_dir=cur_work_dir)),",
            "KitTodo(KitTodoConfig()),",
        ],
        "system_prompt": (
            'f"""You are a coding agent at {cur_work_dir}.\n'
            'Use the todo tool to plan multi-step tasks. '
            'Mark in_progress before starting, completed when done.\n'
            'Prefer tools over prose."""'
        ),
        "extra_setup": "",
    },
    4: {
        "desc": "L4 - Subagent (bash + files + subagent)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "from hex_claw.agent import AgentSubConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
            "from hex_claw.kit import KitAgent, KitAgentConfig",
        ],
        "kits": None,  # special handling
        "system_prompt": (
            'f"You are a coding agent at {cur_work_dir}. "\n'
            '                           "Use the task tool to delegate exploration or subtasks."'
        ),
        "extra_setup": "subagent",
    },
    5: {
        "desc": "L5 - Skill Loading (bash + files + skill)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
            "from hex_claw.kit import KitSkill, KitSkillConfig",
        ],
        "kits": [
            "KitBash(KitBashConfig(work_dir=cur_work_dir)),",
            "KitFiles(KitFilesConfig(work_dir=cur_work_dir)),",
            "KitSkill(KitSkillConfig()),",
        ],
        "system_prompt": "skill",  # special handling
        "extra_setup": "",
    },
    6: {
        "desc": "L6 - Context Compact (bash + files + compact)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
            "from hex_claw.kit import KitCompact, KitCompactConfig",
        ],
        "kits": [
            "KitBash(KitBashConfig(work_dir=cur_work_dir)),",
            "KitFiles(KitFilesConfig(work_dir=cur_work_dir)),",
            "KitCompact(KitCompactConfig()),",
        ],
        "system_prompt": (
            'f"You are a coding agent at {cur_work_dir}. '
            'Use tools to solve tasks."'
        ),
        "extra_setup": "",
    },
    "full": {
        "desc": "Full Agent (all features)",
        "imports": [
            "from hex_claw.agent import AgentMain, AgentMainConfig",
            "from hex_claw.agent import AgentSubConfig",
            "",
            "from hex_claw.kit import KitManager",
            "from hex_claw.kit import KitBash, KitBashConfig",
            "from hex_claw.kit import KitFiles, KitFilesConfig",
            "from hex_claw.kit import KitTodo, KitTodoConfig",
            "from hex_claw.kit import KitSkill, KitSkillConfig",
            "from hex_claw.kit import KitAgent, KitAgentConfig",
            "from hex_claw.kit import KitCompact, KitCompactConfig",
        ],
        "kits": None,  # special handling
        "system_prompt": (
            'f"You are a coding agent at {cur_work_dir}. "\n'
            '                           "Use the task tool to delegate exploration or subtasks."'
        ),
        "extra_setup": "full",
    },
}


def build_simple_main(name: str, cfg: dict) -> str:
    """Generate main() for simple agents (L1-L3, L5-L6)."""
    kit_lines = "\n        ".join(cfg["kits"])
    is_skill = cfg["system_prompt"] == "skill"

    lines = []
    lines.append("def main() -> int:")
    lines.append("    cur_work_dir = os.getcwd()")
    lines.append("    kit_manager = KitManager([")
    lines.append(f"        {kit_lines}")
    lines.append("    ])")

    if is_skill:
        lines.append('    agent = AgentMain(')
        lines.append('        AgentMainConfig(')
        lines.append('            system_prompt=f"""You are a coding agent at {cur_work_dir}.')
        lines.append('Use load_skill to access specialized knowledge before tackling unfamiliar topics.')
        lines.append('')
        lines.append('Skills available:')
        lines.append('{kit_manager.run_helper("skill_get_system", {})}""",')
    else:
        lines.append("    agent = AgentMain(")
        lines.append("        AgentMainConfig(")
        lines.append(f"            system_prompt=({cfg['system_prompt']}),")

    lines.append("            kit_manager=kit_manager,")
    lines.append(f'            log_path=os.path.join(LOG_DIR, "{name}_history.md"),')
    lines.append("            cur_work_dir=cur_work_dir,")
    lines.append("        ))")
    lines.append("")
    lines.append("    history: list = []")
    lines.append("    try:")
    lines.append("        while True:")
    lines.append("            try:")
    lines.append(f'                query = input("\\033[36m{name} >> \\033[0m")')
    lines.append("            except (EOFError, KeyboardInterrupt):")
    lines.append("                return 0")
    lines.append('            if query.strip().lower() in ("q", "exit", ""):')
    lines.append("                return 0")
    lines.append("")
    lines.append('            history.append({"role": "user", "content": query})')
    lines.append("            history = agent.agent_loop(history)")
    lines.append("            print_answer(history)")
    lines.append("    except KeyboardInterrupt:")
    lines.append("        return 0")
    return "\n".join(lines)


def build_subagent_main(name: str) -> str:
    """Generate main() for L4 (subagent pattern)."""
    return textwrap.dedent(f'''\
def main() -> int:
    cur_work_dir = os.getcwd()

    child_kits = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
    ])
    child_agent_cfg = AgentSubConfig(
        system_prompt=(
            f"You are a coding subagent at {{cur_work_dir}}. "
            "Complete the given task, then summarize your findings."),
        kit_manager=child_kits,
        log_path=os.path.join(LOG_DIR, "{name}_history.sub.md"),
        cur_work_dir=cur_work_dir,
    )

    parent_kits = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitAgent(KitAgentConfig(sub_agent=child_agent_cfg)),
    ])
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=(
                f"You are a coding agent at {{cur_work_dir}}. "
                "Use the task tool to delegate exploration or subtasks."),
            kit_manager=parent_kits,
            log_path=os.path.join(LOG_DIR, "{name}_history.md"),
            cur_work_dir=cur_work_dir,
        ))

    history: list = []
    try:
        while True:
            try:
                query = input("\\033[36m{name} >> \\033[0m")
            except (EOFError, KeyboardInterrupt):
                return 0
            if query.strip().lower() in ("q", "exit", ""):
                return 0

            history.append({{"role": "user", "content": query}})
            history = agent.agent_loop(history)
            print_answer(history)
    except KeyboardInterrupt:
        return 0''')


def build_full_main(name: str) -> str:
    """Generate main() for full agent."""
    return textwrap.dedent(f'''\
def main() -> int:
    cur_work_dir = os.getcwd()

    child_kits = KitManager([
        KitBash(KitBashConfig(work_dir=cur_work_dir)),
        KitFiles(KitFilesConfig(work_dir=cur_work_dir)),
        KitTodo(KitTodoConfig()),
        KitSkill(KitSkillConfig()),
    ])
    child_agent_cfg = AgentSubConfig(
        system_prompt=(
            f"You are a coding subagent at {{cur_work_dir}}. "
            "Complete the given task, then summarize your findings."),
        kit_manager=child_kits,
        log_path=os.path.join(LOG_DIR, "{name}_history.sub.md"),
        cur_work_dir=cur_work_dir,
    )
    parent_kits = KitManager([
        KitAgent(KitAgentConfig(sub_agent=child_agent_cfg)),
        KitCompact(KitCompactConfig()),
    ])
    agent = AgentMain(
        AgentMainConfig(
            system_prompt=(
                f"You are a coding agent at {{cur_work_dir}}. "
                "Use the task tool to delegate exploration or subtasks."),
            kit_manager=parent_kits,
            log_path=os.path.join(LOG_DIR, "{name}_history.md"),
            cur_work_dir=cur_work_dir,
        ))

    history: list = []
    try:
        while True:
            try:
                query = input("\\033[36m{name} >> \\033[0m")
            except (EOFError, KeyboardInterrupt):
                return 0
            if query.strip().lower() in ("q", "exit", ""):
                return 0

            history.append({{"role": "user", "content": query}})
            history = agent.agent_loop(history)
            print_answer(history)
    except KeyboardInterrupt:
        return 0''')


ENTRY = '''

if __name__ == "__main__":
    raise SystemExit(main())
'''


def create_agent(name: str, level, output_dir: Path):
    """Create a new hex_claw agent script."""
    cfg = LEVEL_CONFIGS.get(level)
    if cfg is None:
        print(f"Error: Unknown level '{level}'.")
        print(f"Available: {', '.join(str(k) for k in LEVEL_CONFIGS)}")
        sys.exit(1)

    agent_file = output_dir / f"{name}.py"
    output_dir.mkdir(parents=True, exist_ok=True)

    imports = "\n".join(cfg["imports"])

    if cfg["extra_setup"] == "subagent":
        main_body = build_subagent_main(name)
    elif cfg["extra_setup"] == "full":
        main_body = build_full_main(name)
    else:
        main_body = build_simple_main(name, cfg)

    content = f"{HEADER}\n{imports}\n\n\n{main_body}\n{ENTRY}"
    agent_file.write_text(content)
    print(f"Created: {agent_file}")
    print(f"  Level: {cfg['desc']}")
    print(f"\nUsage:")
    print(f"  cd {output_dir.resolve().parent}")
    print(f"  python {output_dir.name}/{name}.py")


def main():
    parser = argparse.ArgumentParser(
        description="生成基于hex_claw框架的AI代理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
Levels:
  1     L1 - Agent Loop    (bash only)              ~ s01_agent_loop.py
  2     L2 - Tool Use      (bash + files)           ~ s02_tool_use.py
  3     L3 - Todo Write    (bash + files + todo)     ~ s03_todo_write.py
  4     L4 - Subagent      (bash + files + subagent) ~ s04_subagent.py
  5     L5 - Skill Loading (bash + files + skill)    ~ s05_skill_loading.py
  6     L6 - Compact       (bash + files + compact)  ~ s06_context_compact.py
  full  Full Agent         (all features)            ~ s_full.py
        """),
    )
    parser.add_argument("name", help="Name of the agent to create")
    parser.add_argument(
        "--level",
        default="2",
        help="Complexity level: 1-6 or 'full' (default: 2)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Output directory (default: example/)",
    )

    args = parser.parse_args()

    level = args.level
    if level != "full":
        try:
            level = int(level)
        except ValueError:
            print(f"Error: level must be 1-6 or 'full', got '{level}'")
            sys.exit(1)

    if args.path is None:
        repo_dir = Path(__file__).resolve().parent.parent.parent
        output_dir = repo_dir / "example"
    else:
        output_dir = args.path.resolve()

    create_agent(args.name, level, output_dir)


if __name__ == "__main__":
    main()
