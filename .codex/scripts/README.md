# .codex/scripts

这里放的是 workspace 内部脚本. 目标是把 "0-调研 -> 1-验证 -> 2-实验和写作" 的数据与文档保持一致，避免手工同步出错.

## 1) 检查 references 是否已被登记

用途: 扫描 `0-调研/references/` 里的 pdf，检查是否都已经在 `0-调研/research.json` 里登记，并且对应的 `0-调研/notes/<paper_id>.md` 是否存在.

用法:

```bash
python .codex/scripts/check_unrecognized_references.py
```

## 2) research.json -> notes/*.md (json2md)

用途: 用 `0-调研/research.json` 生成或覆盖 `0-调研/notes/<paper_id>.md`，用于批量初始化或同步 paper notes.

用法:

```bash
python .codex/scripts/paper_json2md.py --create-missing
python .codex/scripts/paper_json2md.py --paper_id 260123-01 --overwrite
```

## 3) notes/*.md -> research.json (md2json)

用途: 从 `0-调研/notes/<paper_id>.md` 解析出 meta 与正文要点，回写到 `0-调研/research.json` (适合我先写笔记，再补全登记册的流程).

用法:

```bash
python .codex/scripts/paper_md2json.py --update-existing
python .codex/scripts/paper_md2json.py --create-missing
```

## 4) task.json <-> task.md (任务同步)

用途: 把 `1-验证/tasks/<task_id>/task.json` 与 `task.md` 双向同步，避免 "写了 md 忘记回写 json" (或反过来).

约定: `task.md` 需要按 `.codex/templates/task.md` 的 key:value 写法来填.

用法:

```bash
python .codex/scripts/task_json2md.py --task-dir 1-验证/tasks/260101-task-001 --overwrite
python .codex/scripts/task_md2json.py --task-dir 1-验证/tasks/260101-task-001 --update-existing
```

## 5) 0-调研 审查模式 (md/json 对齐 + 模板一致性)

用途: 不看 pdf 内容，只做一致性审查:
- `0-调研/research.json` 的结构是否符合 `.codex/templates/paper_entry.json`.  
- `0-调研/notes/<paper_id>.md` 是否齐全，且与 `research.json` 的内容一致 (按 `.codex/templates/paper_note.md` 解析).  
- `session/` 里 `YYMMDD-session.md` 与 `YYMMDD-session.json` 是否成对存在，且结构符合 `.codex/templates/session.*` (session 统一放在 workspace 根目录).  

用法:

```bash
python .codex/scripts/audit_stage0.py --strict
```

## 6) 1-验证 fail case 反思文档 (rethinks)

用途: 在 `1-验证/rethinks/` 下创建一份新的反思文档骨架，文件名按 `YYMMDD-rethink-NN.md` 自动编号，避免手工命名出错.

用法:

```bash
python .codex/scripts/new_rethink.py
python .codex/scripts/new_rethink.py --source-task PV1-S001
python .codex/scripts/new_rethink.py --date 260202 --dry-run
```
