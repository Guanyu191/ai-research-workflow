#!/usr/bin/env python3
from __future__ import annotations

"""Generates task.md from task.json (json2md).

This script syncs files inside a task directory:
  1-验证/tasks/<task_id>/task.json
  1-验证/tasks/<task_id>/task.md

It follows `.codex/templates/task.md` (key:value fields under each section).

Usage:
  python .codex/scripts/task_json2md.py --task-dir 1-验证/tasks/260101-task-001 \\
    --overwrite
  python .codex/scripts/task_json2md.py --tasks-root 1-验证/tasks --create-missing
"""

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"missing file: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid json: {path} ({e})") from e


def _dump_json_inline(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _get_str(x: Any, default: str = "...") -> str:
    s = str(x or "").strip()
    return s if s else default


def _get_dict(x: Any) -> dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _get_list(x: Any) -> list[Any]:
    return x if isinstance(x, list) else []


def render_task_md(task: dict[str, Any]) -> str:
    """Renders a task.json dict into task.md content.

    Args:
        task: Loaded JSON dict from `.../task.json`.

    Returns:
        A markdown document for `.../task.md`.

    Raises:
        ValueError: If `task_id` is missing.
    """
    task_id = _get_str(task.get("task_id", ""), default="")
    if not task_id:
        raise ValueError("task.json missing `task_id`")

    stage_raw = str(task.get("stage", "") or "").strip()
    stage = stage_raw if stage_raw else "1-验证"

    created_at_raw = str(task.get("created_at", "") or "").strip()
    created_at = created_at_raw if created_at_raw else "YYYY-MM-DD"

    source = _get_dict(task.get("source", {}))
    paper_id = _get_str(source.get("paper_id", ""))
    url = _get_str(source.get("url", ""))
    source_desc = _get_str(source.get("desc", ""))

    background = _get_dict(task.get("background", {}))
    why_now = _get_str(background.get("why_now", ""))

    hypothesis = _get_str(task.get("hypothesis", ""))

    design = _get_dict(task.get("design", {}))
    variables = _get_str(design.get("variables", ""))
    baseline = _get_str(design.get("baseline", ""))
    data_split_raw = str(design.get("data_split", "") or "").strip()
    data_split = data_split_raw if data_split_raw else "遵循 `.codex/EVAL.md`."
    metrics = _get_str(design.get("metrics", ""))
    budget = _get_str(design.get("budget", ""))

    acceptance = _get_dict(task.get("acceptance", {}))
    passed = _get_str(acceptance.get("pass", ""))
    fail_but_useful = _get_str(acceptance.get("fail_but_useful", ""))

    changes = _get_list(task.get("changes", []))
    inputs = _get_list(task.get("inputs", []))
    outputs = _get_list(task.get("outputs", []))

    result_summary = _get_str(task.get("result_summary", ""))
    decision = _get_str(task.get("decision", ""))
    next_tasks = _get_list(task.get("next_tasks", []))

    md: list[str] = []
    md.append(f"# Task: {task_id}.")
    md.append("")

    md.append("## 0. Meta.")
    md.append(f"- [ ] task_id: {task_id}  ")
    md.append(f"- [ ] stage: {stage}  ")
    md.append(f"- [ ] created_at: {created_at}  ")
    md.append(f"- [ ] paper_id: `{paper_id}`  ")
    md.append(f"- [ ] url: `{url}`  ")
    md.append("")

    md.append("## 1. 背景与来源.")
    md.append(f"- [ ] 来源补充：{source_desc} (例如：论文 issue，对话，直觉)  ")
    md.append(f"- [ ] 为什么现在做：{why_now}  ")
    md.append("")

    md.append("## 2. 假设 (Hypothesis).")
    md.append(f"- [ ] hypothesis：{hypothesis}  ")
    md.append("")

    md.append("## 3. 实验设计 (Design).")
    md.append(f"- [ ] variables：{variables}  ")
    md.append(f"- [ ] baseline：{baseline}  ")
    md.append(f"- [ ] data_split：{data_split}  ")
    md.append(f"- [ ] metrics：{metrics}  ")
    md.append(f"- [ ] budget：{budget} (时间/算力)  ")
    md.append("")

    md.append("## 4. 验收标准 (Acceptance).")
    md.append(f"- [ ] pass：{passed}  ")
    md.append(f"- [ ] fail_but_useful：{fail_but_useful} (能指导 next step 的信息)  ")
    md.append("")

    md.append("## 5. 产物 (Artifacts).")
    md.append(f"- [ ] changes: `{_dump_json_inline(changes)}`  ")
    md.append(f"- [ ] inputs: `{_dump_json_inline(inputs)}`  ")
    md.append(f"- [ ] outputs: `{_dump_json_inline(outputs)}`  ")
    md.append("")

    md.append("## 6. 写回 (Write-back).")
    md.append(f"- [ ] result_summary：{result_summary}  ")
    md.append(f"- [ ] decision：{decision}  ")
    md.append(f"- [ ] next_tasks: `{_dump_json_inline(next_tasks)}`  ")
    md.append("")

    return "\n".join(md)


def _iter_task_dirs(tasks_root: Path) -> list[Path]:
    if not tasks_root.exists():
        return []
    out: list[Path] = []
    for p in sorted(tasks_root.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_dir():
            continue
        if (p / "task.json").exists():
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
        "--create-missing",
        action="store_true",
        help="Create task.md if it does not exist.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing task.md.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; only print what would change.",
    )
    args = p.parse_args()

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
        task_json = task_dir / "task.json"
        task_md = task_dir / "task.md"
        if not task_json.exists():
            skipped += 1
            continue

        task = _load_json(task_json)
        task_id = str(task.get("task_id", "")).strip()
        if wanted and task_id not in wanted:
            skipped += 1
            continue

        exists = task_md.exists()
        if exists and not args.overwrite:
            skipped += 1
            continue
        if (not exists) and (not args.create_missing) and (not args.overwrite):
            skipped += 1
            continue

        content = render_task_md(task)
        if args.dry_run:
            action = "overwrite" if exists else "create"
            print(f"{action}: {task_md}")
            continue

        task_md.write_text(content, encoding="utf-8")
        if exists:
            updated += 1
        else:
            created += 1

    print(f"done: created={created}, updated={updated}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
