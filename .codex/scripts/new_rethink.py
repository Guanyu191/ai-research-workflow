#!/usr/bin/env python3
from __future__ import annotations

"""Create a new rethink note under 1-验证/rethinks with YYMMDD-rethink-NN.md naming.

This is intended for systematic fail-case management during stage 1-验证.
Workflow requirement (enforced by humans, not this script):
  - Human writes the first draft.
  - Agent polishes.
  - Human reviews the final version.

Usage:
  python .codex/scripts/new_rethink.py
  python .codex/scripts/new_rethink.py --source-task PV1-S001
  python .codex/scripts/new_rethink.py --date 260202 --dry-run
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FILENAME_RE = re.compile(r"^(?P<date>\d{6})-rethink-(?P<n>\d{2})\.md$")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--date",
        default=None,
        help="YYMMDD (default: local today). Example: 260202",
    )
    p.add_argument(
        "--source-task",
        default=None,
        help="Task id to link, e.g. PV1-S001 or 260126-task-001.",
    )
    p.add_argument(
        "--out-dir",
        default="1-验证/rethinks",
        help="Output directory (relative to workspace root).",
    )
    p.add_argument(
        "--template",
        default=".codex/templates/rethink.md",
        help="Template path (relative to workspace root).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the path and exit without writing files.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite if the target file already exists.",
    )
    return p.parse_args()


def _today_yymmdd() -> str:
    return datetime.now().strftime("%y%m%d")


def _to_created_at(yymmdd: str) -> str:
    return datetime.strptime(yymmdd, "%y%m%d").strftime("%Y-%m-%d")


def _next_index(out_dir: Path, yymmdd: str) -> int:
    max_n = 0
    if not out_dir.exists():
        return 1
    for p in out_dir.iterdir():
        if not p.is_file():
            continue
        m = FILENAME_RE.match(p.name)
        if not m:
            continue
        if m.group("date") != yymmdd:
            continue
        max_n = max(max_n, int(m.group("n")))
    return max_n + 1


def _fill_template(
    template_text: str,
    *,
    rethink_id: str,
    created_at: str,
    source_task: str | None,
) -> str:
    lines = template_text.splitlines()
    out: list[str] = []
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# Rethink:"):
            out.append(f"# Rethink: {rethink_id} - <一句话标题>")
            continue
        if line.startswith("- [ ] id:"):
            out.append(f"- [ ] id: {rethink_id}  ")
            continue
        if line.startswith("- [ ] created_at:"):
            out.append(f"- [ ] created_at: {created_at}  ")
            continue
        if line.startswith("- [ ] 润色:"):
            out.append("- [ ] 润色: GPT-5.2-xhigh @ YYYY-MM-DD  ")
            continue
        if source_task and line.startswith("- [ ] 来源 task:"):
            out.append(f"- [ ] 来源 task: `{source_task}`  ")
            continue
        out.append(line)
    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    args = _parse_args()

    yymmdd = args.date or _today_yymmdd()
    if not re.fullmatch(r"\d{6}", yymmdd):
        raise SystemExit("--date must be YYMMDD, e.g. 260202")

    out_dir = (ROOT / args.out_dir).resolve()
    template_path = (ROOT / args.template).resolve()

    n = _next_index(out_dir, yymmdd)
    if n > 99:
        raise SystemExit(f"too many rethinks for {yymmdd}: NN would exceed 99")

    rethink_id = f"{yymmdd}-rethink-{n:02d}"
    out_path = out_dir / f"{rethink_id}.md"

    if args.dry_run:
        print(out_path)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"file already exists: {out_path} (use --overwrite)")

    template_text = template_path.read_text(encoding="utf-8")
    created_at = _to_created_at(yymmdd)
    filled = _fill_template(
        template_text,
        rethink_id=rethink_id,
        created_at=created_at,
        source_task=args.source_task,
    )
    out_path.write_text(filled, encoding="utf-8")

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
