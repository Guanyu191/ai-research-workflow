#!/usr/bin/env python3
from __future__ import annotations

"""Generates paper notes (md) from research.json (json2md).

This is a helper script for the 0-调研 intake loop:
- Source of truth for metadata lives in `0-调研/research.json`.
- Each paper should have a note file in `0-调研/notes/<paper_id>.md`.
- It also supports nested entries under `followed`.

Default behavior:
- Only creates missing notes.
- Does not overwrite existing notes unless `--overwrite` is set.

Usage:
  python .codex/scripts/paper_json2md.py --create-missing
  python .codex/scripts/paper_json2md.py --paper_id 260123-01 --overwrite
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
    return "…" in x


def _bullet_list_from_text(text: str) -> list[str]:
    t = (text or "").strip()
    if not t:
        return ["- ..."]
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    return [f"- {ln}" for ln in lines] if lines else ["- ..."]


def _bullet_list_from_items(
    items: list[Any] | Any,
    placeholder: list[str],
) -> list[str]:
    if isinstance(items, list) and items:
        out: list[str] = []
        for it in items:
            s = str(it).strip()
            if _is_placeholder(s):
                continue
            out.append(f"- {s}")
        return out or placeholder
    return placeholder


def render_paper_note(entry: dict[str, Any]) -> str:
    """Renders a single paper entry into a note markdown string.

    Args:
        entry: A dict that follows `.codex/templates/paper_entry.json`.

    Returns:
        A markdown document for `0-调研/notes/<paper_id>.md`.

    Raises:
        ValueError: If `paper_id` is missing.
    """
    paper_id = str(entry.get("paper_id", "")).strip()
    if not paper_id:
        raise ValueError("paper entry missing `paper_id`")

    title = str(entry.get("title", "")).strip() or "..."
    year = int(entry.get("year", 0) or 0)
    authors = entry.get("authors", [])
    if not isinstance(authors, list):
        authors = []
    tags = entry.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    used_in_tasks = (
        entry.get("used_in_tasks", [])
        if isinstance(entry.get("used_in_tasks", []), list)
        else []
    )

    pdf_path = str(entry.get("pdf_path", "")).strip() or "0-调研/references/<file>.pdf"
    url = str(entry.get("url", "")).strip() or "..."
    code_url = str(entry.get("code_url", "")).strip() or "..."

    problem_lines = _bullet_list_from_text(str(entry.get("problem", "") or ""))
    method_lines = _bullet_list_from_text(str(entry.get("method", "") or ""))

    key_claims_lines = _bullet_list_from_items(
        entry.get("key_claims", []),
        placeholder=["- claim-1: ... (evidence: ...)", "- claim-2: ..."],
    )
    limitations_lines = _bullet_list_from_items(
        entry.get("limitations", []),
        placeholder=["- ..."],
    )
    open_questions_lines = _bullet_list_from_items(
        entry.get("open_questions", []),
        placeholder=["- ..."],
    )
    what_we_can_reuse_lines = _bullet_list_from_items(
        entry.get("what_we_can_reuse", []),
        placeholder=["- ..."],
    )
    hypotheses_lines = _bullet_list_from_items(
        entry.get("hypotheses", []),
        placeholder=["- H1: ... (variable: ...; protocol: ...; metric: ...; falsify if: ...)"],
    )

    md = []
    md.append(f"# Paper Note: {paper_id}")
    md.append("")
    md.append("## 0. Meta")
    md.append(f"- **paper_id**: {paper_id}  ")
    md.append(f"- **title**: {title}  ")
    md.append(f"- **year**: {year}  ")
    md.append(f"- **authors**: `{_dump_json_inline(authors)}`  ")
    md.append(f"- **tags**: `{_dump_json_inline(tags)}`  ")
    md.append(f"- **pdf_path**: `{pdf_path}`  ")
    md.append(f"- **url**: {url}  ")
    md.append(f"- **code_url**: {code_url}  ")
    md.append(f"- **used_in_tasks**: `{_dump_json_inline(used_in_tasks)}`  ")
    md.append("")
    md.append("## 1. Abstract (摘要)")
    md.append("")
    md.append("逐段翻译，简洁清晰、口语化，但不能产生歧义或信息丢失.")
    md.append("")
    md.append("> **Note:** 关键术语统一使用 English term (中文术语). 数字、指标、对比对象与适用范围必须保留.")
    md.append("")
    md.append("## 2. Introduction (引言)")
    md.append("")
    md.append("逐段翻译，重点理清研究逻辑与相关工作之间的关系 (不引入 paper 没有的推断).")
    md.append("")
    md.append("## 3. Methodology (方法)")
    md.append("")
    md.append("逐段翻译，重点关注细节，必要时用 note block 把符号、shape、损失项、训练/推理流程与实现细节注释清楚.")
    md.append("")
    md.append("> **Note:** 对于每个关键符号，优先写清: 含义、shape、取值范围、单位/物理意义 (如果 paper 给了).")
    md.append("")
    md.append("## 4. Experiments (实验)")
    md.append("")
    md.append("逐段翻译，重点写清做了什么实验，以及为什么能支持结论 (claim -> evidence).")
    md.append("")
    md.append("## 5. Problem (paper)")
    md.extend(problem_lines)
    md.append("")
    md.append("## 6. Method (paper)")
    md.extend(method_lines)
    md.append("")
    md.append("## 7. Key claims (paper)")
    md.extend(key_claims_lines)
    md.append("")
    md.append("## 8. Limitations (paper)")
    md.extend(limitations_lines)
    md.append("")
    md.append("## 9. Open questions (reading)")
    md.extend(open_questions_lines)
    md.append("")
    md.append("## 10. What we can reuse (our project)")
    md.extend(what_we_can_reuse_lines)
    md.append("")
    md.append("## 11. Hypotheses we can test (our project)")
    md.extend(hypotheses_lines)
    md.append("")

    return "\n".join(md)


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
        help="Only generate notes for this paper_id (repeatable).",
    )
    p.add_argument(
        "--create-missing",
        action="store_true",
        help="Create notes that do not exist.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing notes (dangerous).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; only print what would change.",
    )
    args = p.parse_args()

    data = _load_json(args.research_json)
    research_entries = data.get("research", [])
    if not isinstance(research_entries, list):
        raise ValueError(f"`research` must be a list in {args.research_json}")
    entries = _iter_paper_entries(research_entries)

    wanted = set(args.paper_id or [])
    args.notes_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    updated = 0
    skipped = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        paper_id = str(e.get("paper_id", "")).strip()
        if not paper_id:
            continue
        if wanted and paper_id not in wanted:
            continue

        note_path = args.notes_dir / f"{paper_id}.md"
        exists = note_path.exists()
        if exists and not args.overwrite:
            skipped += 1
            continue
        if (not exists) and (not args.create_missing) and (not args.overwrite):
            skipped += 1
            continue

        content = render_paper_note(e)
        if args.dry_run:
            action = "overwrite" if exists else "create"
            print(f"{action}: {note_path}")
            continue

        note_path.write_text(content, encoding="utf-8")
        if exists:
            updated += 1
        else:
            created += 1

    print(f"done: created={created}, updated={updated}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
