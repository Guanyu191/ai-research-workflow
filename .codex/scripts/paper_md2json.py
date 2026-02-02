#!/usr/bin/env python3
from __future__ import annotations

"""Parses paper notes (md) and writes back to research.json (md2json).

This script assumes each note follows (roughly) the template:
  .codex/templates/paper_note.md

It parses:
- Meta block (title, year, authors, tags, pdf_path, url, code_url, used_in_tasks).
- Key content sections (problem, method, key_claims, limitations, open_questions,
  what_we_can_reuse, hypotheses).

Usage:
  python .codex/scripts/paper_md2json.py --update-existing
  python .codex/scripts/paper_md2json.py --create-missing

Notes:
  - Existing entries are matched by `paper_id`, including nested entries under
    `followed`.
  - When creating missing entries, this script appends to the top-level
    `research` list.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


META_LINE_RE = re.compile(r"^- \*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$")


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
    if not x:
        return True
    if x in {"…", "...", "...", "......"}:
        return True
    if x.lower() in {"tbd", "todo"}:
        return True
    if "<paper_id>" in x or "<file>" in x:
        return True
    # Also treat any "..." / "…" suffix as placeholder, e.g. "claim-1: ...".
    if x.endswith(("...", "......", "…", "...")):
        return True
    return "…" in x


def _parse_json_list(value: str) -> list[Any] | None:
    v = _strip_backticks(value).strip()
    if not v.startswith("["):
        return None
    try:
        out = json.loads(v)
    except json.JSONDecodeError:
        return None
    return out if isinstance(out, list) else None


def _default_entry(paper_id: str) -> dict[str, Any]:
    return {
        "paper_id": paper_id,
        "title": "",
        "year": 0,
        "authors": [],
        "tags": [],
        "pdf_path": "",
        "url": "",
        "code_url": "",
        "problem": "",
        "method": "",
        "key_claims": [],
        "limitations": [],
        "open_questions": [],
        "what_we_can_reuse": [],
        "hypotheses": [],
        "used_in_tasks": [],
        "followed": [],
    }


def _iter_paper_entries(entries: list[Any] | Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(entries, list):
        return out
    for e in entries:
        if not isinstance(e, dict):
            continue
        out.append(e)
        out.extend(_iter_paper_entries(e.get("followed", [])))
    return out


def parse_paper_note(path: Path) -> dict[str, Any]:
    """Parses one paper note markdown into a research.json entry.

    Args:
        path: Note file path like `0-调研/notes/<paper_id>.md`.

    Returns:
        A dict that follows `.codex/templates/paper_entry.json` (extended fields).
    """
    paper_id = path.stem.strip()
    entry: dict[str, Any] = _default_entry(paper_id)

    lines = path.read_text(encoding="utf-8").splitlines()

    in_meta = False
    current_label: str | None = None

    buckets: dict[str, list[str]] = {
        "Problem": [],
        "Method": [],
        "Key claims": [],
        "Limitations": [],
        "Open questions": [],
        "What we can reuse": [],
        "Hypotheses we can test": [],
    }

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            heading = line[3:].strip()
            heading = re.sub(r"^\d+\.\s+", "", heading).strip()
            label = heading.split("(", 1)[0].strip()

            in_meta = label == "Meta"
            current_label = label if label in buckets else None
            continue

        if in_meta:
            m = META_LINE_RE.match(line.strip())
            if not m:
                continue
            key = m.group("key").strip()
            value = m.group("value").strip()
            if _is_placeholder(value):
                continue

            if key in {"authors", "tags", "used_in_tasks"}:
                parsed = _parse_json_list(value)
                if parsed is not None:
                    entry[key] = parsed
                else:
                    # Fallback: comma-separated string.
                    entry[key] = [
                        x.strip()
                        for x in _strip_backticks(value).split(",")
                        if x.strip()
                    ]
                continue

            if key == "year":
                try:
                    entry["year"] = int(_strip_backticks(value))
                except ValueError:
                    pass
                continue

            if key in {"pdf_path"}:
                entry["pdf_path"] = _strip_backticks(value)
                continue

            if key in {"paper_id", "title", "url", "code_url"}:
                entry[key] = _strip_backticks(value)
                continue

            # Unknown meta keys are ignored on purpose.
            continue

        if current_label and line.lstrip().startswith("- "):
            item = line.lstrip()[2:].strip()
            if _is_placeholder(item):
                continue
            if current_label in buckets:
                buckets[current_label].append(item)

    if buckets["Problem"]:
        entry["problem"] = "\n".join(buckets["Problem"])
    if buckets["Method"]:
        entry["method"] = "\n".join(buckets["Method"])

    entry["key_claims"] = buckets["Key claims"]
    entry["limitations"] = buckets["Limitations"]
    entry["open_questions"] = buckets["Open questions"]
    entry["what_we_can_reuse"] = buckets["What we can reuse"]
    entry["hypotheses"] = buckets["Hypotheses we can test"]

    return entry


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--research-json",
        type=Path,
        default=ROOT / "0-调研" / "research.json",
        help="Path to 0-调研/research.json.",
    )
    p.add_argument(
        "--notes-dir",
        type=Path,
        default=ROOT / "0-调研" / "notes",
        help="Directory for notes/<paper_id>.md.",
    )
    p.add_argument(
        "--paper_id",
        action="append",
        default=None,
        help="Only parse this paper_id (repeatable).",
    )
    p.add_argument(
        "--update-existing",
        action="store_true",
        help="Update existing entries in research.json.",
    )
    p.add_argument(
        "--create-missing",
        action="store_true",
        help="Create entries in research.json if missing.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write research.json; only print planned changes.",
    )
    args = p.parse_args()

    if not args.update_existing and not args.create_missing:
        raise ValueError("need at least one of: --update-existing, --create-missing")

    data = _load_json(args.research_json)
    research_entries = data.get("research", [])
    if not isinstance(research_entries, list):
        raise ValueError(f"`research` must be a list in {args.research_json}")

    by_paper_id: dict[str, dict[str, Any]] = {}
    for e in _iter_paper_entries(research_entries):
        pid = str(e.get("paper_id", "")).strip()
        if pid:
            by_paper_id[pid] = e

    wanted = set(args.paper_id or [])
    note_paths = sorted(args.notes_dir.glob("*.md"), key=lambda x: x.name.lower())

    planned_updates: list[str] = []
    planned_creates: list[str] = []

    for path in note_paths:
        if path.name == ".gitkeep":
            continue
        paper_id = path.stem.strip()
        if wanted and paper_id not in wanted:
            continue

        parsed = parse_paper_note(path)
        if paper_id in by_paper_id:
            if not args.update_existing:
                continue
            dst = by_paper_id[paper_id]
            # Update only known fields, keep any extra keys.
            for k, v in parsed.items():
                if k == "paper_id":
                    continue
                dst[k] = v
            planned_updates.append(paper_id)
        else:
            if not args.create_missing:
                continue
            research_entries.append(parsed)
            by_paper_id[paper_id] = parsed
            planned_creates.append(paper_id)

    if args.dry_run:
        if planned_creates:
            print("create:")
            for pid in planned_creates:
                print(f"- {pid}")
        if planned_updates:
            print("update:")
            for pid in planned_updates:
                print(f"- {pid}")
        print("dry-run: no files written.")
        return 0

    data["research"] = research_entries
    _write_json(args.research_json, data)
    print(f"done: created={len(planned_creates)}, updated={len(planned_updates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
