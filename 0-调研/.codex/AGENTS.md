# 0-调研 阶段 AGENTS

本阶段目标: 把外部信息 (论文，博客，代码，讨论) 转化为 "可执行 hypothesis" 与 "可复用笔记".  

## 调研准则

- 调研的根本在于搞清楚:  
  - 要解决什么问题？  
  - 为什么要解决这个问题？  
  - 能用/要用什么方案解决这个问题？  
  - 能用/要用什么算例来验证我们的方案能解决这个问题？  
- 任何论文笔记、对比设计、阶段计划，都必须能回指到以上四问.  

## 模式 (只选一种)

- 每次进入 0-调研，我只进入一种模式:  
  - "开启规划模式": 做 plan 与 tasks 的规划与落盘.  
  - "开启审查模式": 只做 md/json 一致性与模板一致性审查，不做内容总结与规划.  
- 我不会把两种模式混在一次对话里，避免引入额外上下文与重复工作.

## 0. 启动时必做 (Pre-flight)

- 每次进入 0-调研 的任何工作前，先跑一遍 references 同步检查:  

```bash
python .codex/scripts/check_unrecognized_references.py --strict
```

- 若输出为 OK: 说明 `0-调研/references/` 里的 pdf 都已经在 `0-调研/research.json` 登记，且 `0-调研/notes/<paper_id>.md` 也齐全，可以继续后续工作.  
- 若脚本报错或发现未同步: 我必须停下来，先问你是否现在同步 (不要继续做调研总结，避免忘记登记导致证据链断裂).

> Note: 如果你准备进入 "审查模式"，我会改跑 `python .codex/scripts/audit_stage0.py --strict`，因为它包含同样的 references 检查，并额外检查 md/json 是否对齐.

## 1. references -> research.json 的同步规则

- 每个未识别的 pdf，我都要先问你 2 件事:
  1) **paper_id:** 用识别时间 + 编号，例如 `260123-01`.  
  2) **归档方式:**  
     - A) 作为 `0-调研/research.json` 的独立 block (新增一条 paper).  
     - B) 作为某篇 paper 的 follow-up work: 追加到那篇 paper 的 `followed` 字段 (作为一个 block).  
- 若你选 B，我还要问清楚 parent paper 的 `paper_id` 是什么，然后把该 pdf 对应的 entry 写进 `followed` 数组里.  
- 写完 `research.json` 后: 我会补齐/生成对应的 note 文件 `0-调研/notes/<paper_id>.md` (模板见 `.codex/templates/paper_note.md`).  

> Note: `followed` 的 block 结构与普通 paper entry 一致 (见 `.codex/templates/paper_entry.json`)，只是存放位置不同.

## 强制产物
- 论文登记: 写入 `0-调研/research.json`.  
- 每篇关键论文必须有一页速读卡片: `0-调研/notes/<paper_id>.md`.  
- 若形成可证伪 hypothesis，必须在卡片末尾写清楚，并指向后续验证任务.

## 规划模式 (Planning mode)

- 触发: 当你明确说 "开启规划模式".  
- 我在规划模式下的角色: 科研助理. 我会基于 `0-调研/` 里已登记的 paper (research.json + notes) 和你的目标，和你一起规划本阶段的 plan 与 tasks.  
- 过程要求:
  - 我们边讨论边把最新规划写回到: `0-调研/.codex/PLAN.md` 与 `0-调研/.codex/TASKS.md`.  
  - 任务必须写成 checklist: `- [ ] ...`，完成后用 `- [x] ...`.  
  - 任何关键取舍必须写清楚 "为什么"，并尽量指向对应 paper_id 或 note.  
- 结束: 当你说 "结束"，我必须把本次对话的关键信息沉淀到当天 session 文件，并遵守 "一天只搞一个 session":  
  - `session/YYMMDD-session.md`  
  - `session/YYMMDD-session.json`  
  - 若文件已存在: 追加内容 (md 追加一段，json 往 `entries` 里 append 一个 entry).  

session 记录建议格式:  
- **Context:** 我们在规划什么，边界是什么.  
- **Papers used:** 引用到的 paper_id 列表 (含 followed).  
- **Decisions:** 本次确定的取舍与理由.  
- **Plan update:** 对 `0-调研/.codex/PLAN.md` 做了什么改动.  
- **Tasks update:** 对 `0-调研/.codex/TASKS.md` 新增/调整了哪些任务.  
- **Next step:** 下一次打开 workspace 时先做什么.

## 审查模式 (Review mode)

- 触发: 当你明确说 "开启审查模式".  
- 约束: 不打开 pdf，不做论文内容总结，只做一致性与缺失审查.  
- 我必须跑下面的审查脚本并汇报结果:  

```bash
python .codex/scripts/audit_stage0.py --strict
```

- 若审查通过: 我只回复 "OK" 并等待你下一步指令.  
- 若发现问题: 我只列出问题清单，并问你希望用哪种方式修复:  
  - A) 以 `research.json` 为准覆盖 notes: `python .codex/scripts/paper_json2md.py --create-missing` (必要时 `--overwrite`).  
  - B) 以 notes 为准回写 `research.json`: `python .codex/scripts/paper_md2json.py --update-existing` (必要时 `--create-missing`).  
  - C) 手工修改指定文件.  
- 结束: 当你说 "结束"，我把本次审查的关键结果 (发现了什么，修了什么，未修的风险与下一步) 追加到当天 session 的 md 与 json 文件 (规则同上).

## 禁止事项
- 不要只堆摘要或复制原文. 你必须抽取: 问题，方法，证据，局限，可迁移点.  
