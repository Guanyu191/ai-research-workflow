#!/usr/bin/env python3
from __future__ import annotations

"""Checks whether PDFs in 0-调研/references are registered and have notes.

This script is for the "paper intake" loop:
- PDFs live in `0-调研/references/` (or `0-调研/reference/` for legacy).
- If a PDF is recognized/registered, there should be a matching entry in
  `0-调研/research.json` (either in the top-level `research` list, or nested
  under `followed`) with a `paper_id` (e.g. 260123-01) and `pdf_path`.
- Each registered paper should also have a note file:
  `0-调研/notes/<paper_id>.md`.

Usage:
  python .codex/scripts/check_unrecognized_references.py
  python .codex/scripts/check_unrecognized_references.py --strict
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AuditResult:
    unrecognized_pdfs: list[str]
    missing_pdfs: list[str]
    missing_notes: list[str]
    duplicate_pdf_refs: dict[str, list[str]]

    def has_issues(self) -> bool:
        return bool(
            self.unrecognized_pdfs
            or self.missing_pdfs
            or self.missing_notes
            or self.duplicate_pdf_refs
        )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"missing file: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid json: {path} ({e})") from e


def _relpath_str(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _find_reference_dirs(explicit: list[Path] | None) -> list[Path]:
    if explicit:
        return [p if p.is_absolute() else (ROOT / p) for p in explicit]

    candidates = [
        ROOT / "0-调研" / "references",
        ROOT / "0-调研" / "reference",
    ]
    return [p for p in candidates if p.exists()]


def _iter_pdfs(ref_dirs: list[Path]) -> list[Path]:
    pdfs: list[Path] = []
    for d in ref_dirs:
        if not d.exists():
            continue
        for p in d.rglob("*.pdf"):
            if p.is_file():
                pdfs.append(p)
        for p in d.rglob("*.PDF"):
            if p.is_file():
                pdfs.append(p)

    seen: set[Path] = set()
    out: list[Path] = []
    for p in sorted(pdfs, key=lambda x: x.as_posix().lower()):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _normalize_entry_pdf_path(pdf_path: str) -> Path | None:
    if not pdf_path:
        return None

    p = Path(pdf_path)
    if not p.is_absolute():
        p = ROOT / p
    # We do not require the file to exist.
    return p.resolve(strict=False)


def _iter_paper_entries(entries: list[Any] | Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(entries, list):
        return out
    for e in entries:
        if not isinstance(e, dict):
            continue
        out.append(e)
        followed = e.get("followed", [])
        out.extend(_iter_paper_entries(followed))
    return out


def audit(research_json: Path, notes_dir: Path, ref_dirs: list[Path]) -> AuditResult:
    """Audits PDF references vs research.json and notes/.

    Args:
        research_json: Path to `0-调研/research.json`.
        notes_dir: Path to `0-调研/notes/`.
        ref_dirs: One or more directories that contain PDFs.

    Returns:
        AuditResult containing unrecognized PDFs, missing PDFs/notes, and duplicates.
    """
    data = _load_json(research_json)
    research_entries = data.get("research", [])
    if not isinstance(research_entries, list):
        raise ValueError(f"`research` must be a list in {research_json}")
    entries = _iter_paper_entries(research_entries)

    pdf_to_paper_ids: dict[str, list[str]] = {}
    paper_id_to_pdf: dict[str, str] = {}

    for e in entries:
        if not isinstance(e, dict):
            continue
        paper_id = str(e.get("paper_id", "")).strip()
        pdf_path = str(e.get("pdf_path", "")).strip()
        if not paper_id:
            continue
        p = _normalize_entry_pdf_path(pdf_path)
        if p is None:
            continue
        rel = _relpath_str(p)
        pdf_to_paper_ids.setdefault(rel, []).append(paper_id)
        paper_id_to_pdf[paper_id] = rel

    duplicate_pdf_refs = {k: v for k, v in pdf_to_paper_ids.items() if len(v) > 1}

    pdfs = _iter_pdfs(ref_dirs)
    pdf_rels = [_relpath_str(p.resolve()) for p in pdfs]

    unrecognized_pdfs = [rel for rel in pdf_rels if rel not in pdf_to_paper_ids]
    missing_pdfs: list[str] = []
    for rel in pdf_to_paper_ids.keys():
        p = Path(rel)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            missing_pdfs.append(rel)

    missing_notes: list[str] = []
    for paper_id in sorted(paper_id_to_pdf.keys()):
        note_path = notes_dir / f"{paper_id}.md"
        if not note_path.exists():
            missing_notes.append(f"{paper_id} -> {_relpath_str(note_path)}")

    return AuditResult(
        unrecognized_pdfs=sorted(unrecognized_pdfs),
        missing_pdfs=sorted(missing_pdfs),
        missing_notes=missing_notes,
        duplicate_pdf_refs=duplicate_pdf_refs,
    )


def _print_report(result: AuditResult) -> None:
    if not result.has_issues():
        print("OK: no issues found.")
        return

    if result.unrecognized_pdfs:
        print("Unrecognized PDFs (exists in references/, missing in research.json):")
        for p in result.unrecognized_pdfs:
            print(f"- {p}")
        print()

    if result.missing_pdfs:
        print("Missing PDFs (referenced by research.json, but file not found):")
        for p in result.missing_pdfs:
            print(f"- {p}")
        print()

    if result.missing_notes:
        print("Missing notes (paper_id has no notes/<paper_id>.md):")
        for s in result.missing_notes:
            print(f"- {s}")
        print()

    if result.duplicate_pdf_refs:
        print("Duplicate PDF references (same pdf_path used by multiple paper_id):")
        for pdf_path, paper_ids in sorted(result.duplicate_pdf_refs.items()):
            joined = ", ".join(sorted(paper_ids))
            print(f"- {pdf_path}: {joined}")


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
        help="Path to 0-调研/notes/.",
    )
    p.add_argument(
        "--references-dir",
        type=Path,
        action="append",
        default=None,
        help="PDFs directory to scan (repeatable). Default: 0-调研/references/.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if any issue is found.",
    )
    args = p.parse_args()

    ref_dirs = _find_reference_dirs(args.references_dir)
    if not ref_dirs:
        print("No references directory found (expected 0-调研/references/).")
        return 2

    result = audit(
        research_json=args.research_json,
        notes_dir=args.notes_dir,
        ref_dirs=ref_dirs,
    )
    _print_report(result)
    if args.strict and result.has_issues():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
