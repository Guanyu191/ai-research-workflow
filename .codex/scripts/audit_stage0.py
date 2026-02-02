#!/usr/bin/env python3
from __future__ import annotations

"""Audits 0-调研 for md/json consistency and template conformance (review mode).

This script checks:
1) `0-调研/research.json` structure vs `.codex/templates/paper_entry.json`.
2) `0-调研/notes/<paper_id>.md` existence and content consistency with research.json
   (using the same parser as `paper_md2json.py`).
3) `session/` session file pairs: `YYMMDD-session.md` <-> `.json`, and
   their basic structure vs `.codex/templates/session.md` and `session.json`.

Usage:
  python .codex/scripts/audit_stage0.py
  python .codex/scripts/audit_stage0.py --strict
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import check_unrecognized_references as ref_audit
import paper_md2json as paper_md


ROOT = Path(__file__).resolve().parents[2]

PAPER_ID_RE = re.compile(r"^\d{6}-\d{2}$")
SESSION_MD_RE = re.compile(r"^(?P<date>\d{6})-session\.md$")
SESSION_JSON_RE = re.compile(r"^(?P<date>\d{6})-session\.json$")


@dataclass(frozen=True)
class Issue:
    where: str
    message: str


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


def _is_placeholder_str(s: str) -> bool:
    x = (s or "").strip()
    return x in {"…", "...", "...", "......", ""} or "…" in x


def _normalize_value(v: Any) -> Any:
    if isinstance(v, str):
        return "" if _is_placeholder_str(v) else v.strip()
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return v
    if isinstance(v, list):
        out: list[Any] = []
        for it in v:
            if isinstance(it, str):
                s = it.strip()
                if _is_placeholder_str(s):
                    continue
                out.append(s)
            else:
                out.append(it)
        return out
    if isinstance(v, dict):
        return v
    if v is None:
        return None
    return v


def _iter_paper_entries(
    entries: list[Any] | Any,
    prefix: str = "research",
) -> list[tuple[dict[str, Any], str]]:
    out: list[tuple[dict[str, Any], str]] = []
    if not isinstance(entries, list):
        return out
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            continue
        loc = f"{prefix}[{i}]"
        out.append((e, loc))
        out.extend(_iter_paper_entries(e.get("followed", []), prefix=f"{loc}.followed"))
    return out


def _load_template_types(template_path: Path) -> dict[str, type]:
    tpl = _load_json(template_path)
    if not isinstance(tpl, dict):
        raise ValueError(f"paper template must be an object: {template_path}")
    return {k: type(v) for k, v in tpl.items()}


def _validate_paper_entry(
    entry: dict[str, Any],
    loc: str,
    template_types: dict[str, type],
) -> list[Issue]:
    issues: list[Issue] = []
    missing = [k for k in template_types.keys() if k not in entry]
    if missing:
        issues.append(Issue(where=loc, message=f"missing keys: {missing}"))

    extra = [k for k in entry.keys() if k not in template_types]
    if extra:
        issues.append(Issue(where=loc, message=f"extra keys (allowed but review): {extra}"))

    for k, want_t in template_types.items():
        if k not in entry:
            continue
        got = entry.get(k)
        if got is None:
            continue
        if want_t is list:
            if not isinstance(got, list):
                issues.append(
                    Issue(
                        where=loc,
                        message=f"type mismatch: {k} should be list, got {type(got).__name__}",
                    )
                )
            continue
        if want_t is int:
            if not isinstance(got, int):
                issues.append(
                    Issue(
                        where=loc,
                        message=f"type mismatch: {k} should be int, got {type(got).__name__}",
                    )
                )
            continue
        if want_t is str:
            if not isinstance(got, str):
                issues.append(
                    Issue(
                        where=loc,
                        message=f"type mismatch: {k} should be str, got {type(got).__name__}",
                    )
                )
            continue

    paper_id = str(entry.get("paper_id", "")).strip()
    if paper_id and not PAPER_ID_RE.match(paper_id):
        issues.append(
            Issue(
                where=loc,
                message=f"paper_id format unexpected: {paper_id} (expected YYMMDD-NN)",
            )
        )

    followed = entry.get("followed", [])
    if followed is not None and not isinstance(followed, list):
        issues.append(Issue(where=loc, message="followed should be a list"))

    return issues


def _load_expected_note_headings(template_path: Path) -> list[str]:
    text = template_path.read_text(encoding="utf-8")
    headings = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            headings.append(s)
    return headings


def _audit_paper_notes(
    research_entries: list[dict[str, Any]],
    notes_dir: Path,
    note_template_path: Path,
) -> list[Issue]:
    issues: list[Issue] = []
    expected_headings = _load_expected_note_headings(note_template_path)

    by_paper_id: dict[str, dict[str, Any]] = {}
    duplicates: dict[str, list[str]] = {}
    for e in research_entries:
        pid = str(e.get("paper_id", "")).strip()
        if not pid:
            continue
        if pid in by_paper_id:
            duplicates.setdefault(pid, []).append(_relpath_str(notes_dir / f"{pid}.md"))
        by_paper_id[pid] = e
    if duplicates:
        for pid in sorted(duplicates):
            issues.append(Issue(where=f"paper_id={pid}", message="duplicate paper_id in research.json"))

    # Notes referenced by research.json.
    for pid, entry in sorted(by_paper_id.items()):
        note_path = notes_dir / f"{pid}.md"
        loc = f"notes/{pid}.md"
        if not note_path.exists():
            issues.append(Issue(where=loc, message="missing note file for paper_id"))
            continue

        # Basic structural check vs template.
        lines = note_path.read_text(encoding="utf-8").splitlines()
        if not lines:
            issues.append(Issue(where=loc, message="empty note file"))
        else:
            want_header = f"# Paper Note: {pid}"
            if lines[0].strip() != want_header:
                issues.append(
                    Issue(
                        where=loc,
                        message=f"unexpected title line: got={lines[0].strip()!r}, want={want_header!r}",
                    )
                )
        content = note_path.read_text(encoding="utf-8")
        for h in expected_headings:
            if h not in content:
                issues.append(Issue(where=loc, message=f"missing heading: {h}"))

        # Consistency check: parse md -> dict and compare with research.json entry.
        parsed = paper_md.parse_paper_note(note_path)
        compare_keys = [k for k in parsed.keys() if k != "followed"]
        for k in compare_keys:
            a = _normalize_value(parsed.get(k))
            b = _normalize_value(entry.get(k))
            if a != b:
                issues.append(
                    Issue(
                        where=loc,
                        message=f"md/json mismatch: key={k}, md={a!r}, json={b!r}",
                    )
                )

    # Notes that do not exist in research.json.
    if notes_dir.exists():
        for p in sorted(notes_dir.glob("*.md"), key=lambda x: x.name.lower()):
            if p.name == ".gitkeep":
                continue
            pid = p.stem.strip()
            if pid and pid not in by_paper_id:
                issues.append(
                    Issue(
                        where=_relpath_str(p),
                        message="note exists but paper_id not found in research.json",
                    )
                )

    return issues


def _validate_session_json(session_json: Path, template_types: dict[str, type]) -> list[Issue]:
    issues: list[Issue] = []
    data = _load_json(session_json)
    if not isinstance(data, dict):
        return [Issue(where=_relpath_str(session_json), message="session json must be an object")]

    for k, want_t in template_types.items():
        if k not in data:
            issues.append(Issue(where=_relpath_str(session_json), message=f"missing key: {k}"))
            continue
        got = data.get(k)
        if got is None:
            continue
        if want_t is list:
            if not isinstance(got, list):
                issues.append(
                    Issue(
                        where=_relpath_str(session_json),
                        message=f"type mismatch: {k} should be list, got {type(got).__name__}",
                    )
                )
        elif want_t is str:
            if not isinstance(got, str):
                issues.append(
                    Issue(
                        where=_relpath_str(session_json),
                        message=f"type mismatch: {k} should be str, got {type(got).__name__}",
                    )
                )

    date = str(data.get("date", "")).strip()
    if date and not re.fullmatch(r"\d{6}", date):
        issues.append(Issue(where=_relpath_str(session_json), message=f"invalid date: {date}"))

    stage = str(data.get("stage", "")).strip()
    if stage:
        allowed_stages = {"project", "0-调研", "1-验证", "2-实验和写作"}
        if stage not in allowed_stages:
            want = ", ".join(sorted(allowed_stages))
            issues.append(
                Issue(
                    where=_relpath_str(session_json),
                    message=f"unexpected stage: {stage} (allowed: {want})",
                )
            )

    entries = data.get("entries", [])
    if isinstance(entries, list):
        for i, e in enumerate(entries):
            if not isinstance(e, dict):
                issues.append(
                    Issue(
                        where=_relpath_str(session_json),
                        message=f"entries[{i}] must be an object",
                    )
                )
                continue
            for required in [
                "timestamp",
                "mode",
                "context",
                "work_done",
                "decisions",
                "issues",
                "next_steps",
            ]:
                if required not in e:
                    issues.append(
                        Issue(
                            where=_relpath_str(session_json),
                            message=f"entries[{i}] missing key: {required}",
                        )
                    )
    return issues


def _audit_sessions(session_dir: Path) -> list[Issue]:
    issues: list[Issue] = []

    md_dates: dict[str, Path] = {}
    json_dates: dict[str, Path] = {}

    if not session_dir.exists():
        return [Issue(where=_relpath_str(session_dir), message="missing session directory")]

    for p in sorted(session_dir.iterdir(), key=lambda x: x.name.lower()):
        if p.name == ".gitkeep":
            continue
        if p.is_dir():
            continue
        m_md = SESSION_MD_RE.match(p.name)
        if m_md:
            md_dates[m_md.group("date")] = p
            continue
        m_js = SESSION_JSON_RE.match(p.name)
        if m_js:
            json_dates[m_js.group("date")] = p
            continue

    all_dates = sorted(set(md_dates) | set(json_dates))
    for d in all_dates:
        md_path = md_dates.get(d)
        js_path = json_dates.get(d)
        if md_path is None:
            issues.append(Issue(where=f"session/{d}", message="missing session md"))
        if js_path is None:
            issues.append(Issue(where=f"session/{d}", message="missing session json"))

        if md_path and md_path.exists():
            text = md_path.read_text(encoding="utf-8").strip()
            if not text:
                issues.append(Issue(where=_relpath_str(md_path), message="empty session md"))
            else:
                want = f"# Session: {d}."
                first = md_path.read_text(encoding="utf-8").splitlines()[0].strip()
                if first != want:
                    issues.append(
                        Issue(
                            where=_relpath_str(md_path),
                            message=f"unexpected title line: got={first!r}, want={want!r}",
                        )
                    )

        if js_path and js_path.exists():
            tpl_types = _load_template_types(ROOT / ".codex" / "templates" / "session.json")
            issues.extend(_validate_session_json(js_path, tpl_types))

    return issues


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
        "--session-dir",
        type=Path,
        default=ROOT / "session",
        help="Directory for session logs (workspace/session).",
    )
    p.add_argument(
        "--paper-template",
        type=Path,
        default=ROOT / ".codex" / "templates" / "paper_entry.json",
        help="Template for paper entry json structure.",
    )
    p.add_argument(
        "--paper-note-template",
        type=Path,
        default=ROOT / ".codex" / "templates" / "paper_note.md",
        help="Template for paper note markdown structure.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero code if any issue is found.",
    )
    args = p.parse_args()

    issues: list[Issue] = []

    # 0) Reference intake audit (pdf registry + missing notes + duplicates).
    ref_dirs = [
        d
        for d in [
            ROOT / "0-调研" / "references",
            ROOT / "0-调研" / "reference",
        ]
        if d.exists()
    ]
    if ref_dirs:
        res = ref_audit.audit(
            research_json=args.research_json,
            notes_dir=args.notes_dir,
            ref_dirs=ref_dirs,
        )
        if res.unrecognized_pdfs:
            for s in res.unrecognized_pdfs:
                issues.append(Issue(where="references", message=f"unrecognized pdf: {s}"))
        if res.missing_pdfs:
            for s in res.missing_pdfs:
                issues.append(Issue(where="research.json", message=f"missing pdf file: {s}"))
        if res.missing_notes:
            for s in res.missing_notes:
                issues.append(Issue(where="notes", message=f"missing note: {s}"))
        if res.duplicate_pdf_refs:
            for pdf_path, pids in sorted(res.duplicate_pdf_refs.items()):
                joined = ", ".join(sorted(pids))
                issues.append(
                    Issue(where="research.json", message=f"duplicate pdf_path: {pdf_path} -> {joined}")
                )
    else:
        issues.append(Issue(where="references", message="no references directory found"))

    # 1) research.json schema check.
    data = _load_json(args.research_json)
    research = data.get("research", [])
    if not isinstance(research, list):
        raise ValueError(f"`research` must be a list in {args.research_json}")

    template_types = _load_template_types(args.paper_template)
    entries_with_loc = _iter_paper_entries(research)
    flat_entries: list[dict[str, Any]] = []
    for e, loc in entries_with_loc:
        flat_entries.append(e)
        issues.extend(_validate_paper_entry(e, loc, template_types))

    # 2) notes consistency check.
    issues.extend(
        _audit_paper_notes(
            research_entries=flat_entries,
            notes_dir=args.notes_dir,
            note_template_path=args.paper_note_template,
        )
    )

    # 3) session files audit.
    issues.extend(_audit_sessions(args.session_dir))

    if not issues:
        print("OK: no issues found.")
        return 0

    print("Issues found:")
    for it in issues:
        print(f"- {it.where}: {it.message}")

    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
