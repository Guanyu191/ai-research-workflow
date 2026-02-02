#!/usr/bin/env python3
from __future__ import annotations

"""Parses task.md and writes back to task.json (md2json).

This script syncs files inside a task directory:
  1-验证/tasks/<task_id>/task.md
  1-验证/tasks/<task_id>/task.json

It expects task.md to follow `.codex/templates/task.md` (key:value fields).

Usage:
  python .codex/scripts/task_md2json.py --task-dir 1-验证/tasks/260101-task-001 \\
    --update-existing
  python .codex/scripts/task_md2json.py --tasks-root 1-验证/tasks --update-existing
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


HEADER_RE = re.compile(r"^#\s+Task:\s+(?P<task_id>[^.]+)\.\s*$")
BULLET_RE = re.compile(r"^- \[(?P<state>[ xX])\]\s+(?P<rest>.*)$")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"missing file: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid json: {path} ({e})") from e


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _strip_backticks(s: str) -> str:
    x = s.strip()
    if len(x) >= 2 and x[0] == "`" and x[-1] == "`":
        return x[1:-1]
    return x


def _is_placeholder(s: str) -> bool:
    x = s.strip()
    return x in {"…", "...", "...", "......", ""} or "…" in x


def _parse_kv(rest: str) -> tuple[str, str] | None:
    # Supports both ":" and "：" as delimiter.
    if "：" in rest:
        k, v = rest.split("：", 1)
        return k.strip(), v.strip()
    if ":" in rest:
        k, v = rest.split(":", 1)
        return k.strip(), v.strip()
    return None


def _parse_json_list(value: str) -> list[Any] | None:
    v = _strip_backticks(value).strip()
    if not v.startswith("["):
        return None
    try:
        out = json.loads(v)
    except json.JSONDecodeError:
        return None
    return out if isinstance(out, list) else None


def _set_path(obj: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur: dict[str, Any] = obj
    for k in parts[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[parts[-1]] = value


KEY_MAP: dict[str, str] = {
    "task_id": "task_id",
    "stage": "stage",
    "created_at": "created_at",
    "paper_id": "source.paper_id",
    "url": "source.url",
    "来源补充": "source.desc",
    "为什么现在做": "background.why_now",
    "hypothesis": "hypothesis",
    "variables": "design.variables",
    "baseline": "design.baseline",
    "data_split": "design.data_split",
    "metrics": "design.metrics",
    "budget": "design.budget",
    "pass": "acceptance.pass",
    "fail_but_useful": "acceptance.fail_but_useful",
    "result_summary": "result_summary",
    "decision": "decision",
}

LIST_KEYS: dict[str, str] = {
    "changes": "changes",
    "inputs": "inputs",
    "outputs": "outputs",
    "next_tasks": "next_tasks",
}


def parse_task_md(path: Path) -> dict[str, Any]:
    """Parses one task markdown into a partial task.json dict.

    Args:
        path: Markdown file path like `.../task.md`.

    Returns:
        A partial dict containing only fields found in the markdown.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    out: dict[str, Any] = {}

    for raw in lines:
        line = raw.rstrip()
        m = HEADER_RE.match(line.strip())
        if m:
            out["task_id"] = m.group("task_id").strip()
            continue

        m = BULLET_RE.match(line.strip())
        if not m:
            continue

        rest = m.group("rest").strip()
        kv = _parse_kv(rest)
        if kv is None:
            continue
        key, value = kv
        if not key:
            continue

        if key in LIST_KEYS:
            parsed = _parse_json_list(value)
            if parsed is not None:
                _set_path(out, LIST_KEYS[key], parsed)
                continue
            # Allow comma-separated list as fallback.
            v = _strip_backticks(value).strip()
            if not v:
                _set_path(out, LIST_KEYS[key], [])
                continue
            if _is_placeholder(v):
                continue
            items = [x.strip() for x in v.split(",") if x.strip()]
            _set_path(out, LIST_KEYS[key], items)
            continue

        if key in KEY_MAP:
            v = _strip_backticks(value).strip()
            if _is_placeholder(v):
                continue
            _set_path(out, KEY_MAP[key], v)
            continue

    return out


def _iter_task_dirs(tasks_root: Path) -> list[Path]:
    if not tasks_root.exists():
        return []
    out: list[Path] = []
    for p in sorted(tasks_root.iterdir(), key=lambda x: x.name.lower()):
        if p.is_dir() and (p / "task.md").exists():
            out.append(p)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--tasks-root",
        type=Path,
        default=ROOT / "1-验证" / "tasks",
        help="Root folder that contains task directories.",
    )
    p.add_argument(
        "--task-dir",
        type=Path,
        action="append",
        default=None,
        help="Task directory to process (repeatable).",
    )
    p.add_argument(
        "--task-id",
        action="append",
        default=None,
        help="Only process these task_id under tasks-root (repeatable).",
    )
    p.add_argument(
        "--update-existing",
        action="store_true",
        help="Update task.json if it exists.",
    )
    p.add_argument(
        "--create-missing",
        action="store_true",
        help="Create task.json if missing.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; only print planned changes.",
    )
    args = p.parse_args()

    if not args.update_existing and not args.create_missing:
        raise ValueError("need at least one of: --update-existing, --create-missing")

    task_dirs: list[Path]
    if args.task_dir:
        task_dirs = [d if d.is_absolute() else (ROOT / d) for d in args.task_dir]
    else:
        tasks_root = args.tasks_root
        if not tasks_root.is_absolute():
            tasks_root = ROOT / tasks_root
        task_dirs = _iter_task_dirs(tasks_root)

    wanted = set(args.task_id or [])

    created = 0
    updated = 0
    skipped = 0
    for task_dir in task_dirs:
        task_md = task_dir / "task.md"
        task_json = task_dir / "task.json"
        if not task_md.exists():
            skipped += 1
            continue

        parsed = parse_task_md(task_md)
        task_id = str(parsed.get("task_id", "")).strip()
        if wanted and task_id not in wanted:
            skipped += 1
            continue

        had_json = task_json.exists()
        if had_json:
            if not args.update_existing:
                skipped += 1
                continue
            data = _load_json(task_json)
        else:
            if not args.create_missing:
                skipped += 1
                continue
            data = {}

        # Merge parsed fields into existing json (keep unknown keys/subkeys).
        if "task_id" in parsed:
            data["task_id"] = parsed["task_id"]

        for k in ["stage", "created_at", "hypothesis", "result_summary", "decision"]:
            if k in parsed:
                data[k] = parsed[k]

        for nested_key in ["source", "background", "design", "acceptance"]:
            if nested_key in parsed and isinstance(parsed[nested_key], dict):
                if nested_key not in data or not isinstance(data.get(nested_key), dict):
                    data[nested_key] = {}
                data[nested_key].update(parsed[nested_key])

        for list_key in ["changes", "inputs", "outputs", "next_tasks"]:
            if list_key in parsed:
                data[list_key] = parsed[list_key]

        if args.dry_run:
            action = "update" if had_json else "create"
            print(f"{action}: {task_json}")
            continue

        _write_json(task_json, data)
        if had_json:
            updated += 1
        else:
            created += 1

    print(f"done: created={created}, updated={updated}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
