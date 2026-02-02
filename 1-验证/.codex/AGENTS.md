# 1-验证 阶段 AGENTS

本阶段目标: 用最小成本证伪/验证 hypothesis，并尽快做出继续/停止/转向决策.

## 模式 (只选一种)

- 每次进入 1-验证，我只进入一种模式，直到你说 "结束":  
  - "开启规划模式-粗": 阶段级规划，落盘到 `1-验证/.codex/PLAN.md` 与 `1-验证/.codex/TASKS.md`.  
  - "开启规划模式-细": 任务级规划，聚焦某个 `task_id`，落盘到对应 `1-验证/tasks/<task_id>/task.md` (例如 `1-验证/tasks/260101-task-001/task.md`).  
  - "开启编程模式": 只实现需求、逻辑正确即可；用最简单直观的写法，不追求可扩展性/工程化，也不刻意补全各种 `raise error`/异常体系.  
  - "开启审查模式": 只做逻辑与任务对齐审查；发现问题立即反馈，直到确认没问题才写入对应 `notes.md`.  
  - "开启反思模式": 针对 fail cases 的系统化复盘与沉淀，落盘到 `1-验证/rethinks/YYMMDD-rethink-NN.md` (人写初稿 -> agent 润色 -> 人终审).  
  - "开启优化模式": 在代码已跑通的前提下，按代码规范优化写法/结构；不改变行为与结论.  
- 若你未明确指定模式: 我会先问你要进入哪一种，不会默认开始做事.  

## 强制产物
- 每个任务一个目录: `1-验证/tasks/<task_id>/`.  
- 每个任务必须包含三件套: `task.md` + `task.json` + `notes.md`.  
- 任何可比较结果都必须更新 `1-验证/leaderboard.csv`.
- 每个明确的失败结论/转向决策，必须产出一份反思记录: `1-验证/rethinks/YYMMDD-rethink-NN.md` (来源 task / 结论 / 思考链).

## 任务质量要求
- 先跑强 baseline，确保评估脚本可信.  
- 一个任务尽量只改变一个关键因素 (便于归因).  

## 规划模式-粗 (Stage planning)

- 目标: 规划阶段主线与任务队列，不做实现与跑实验.  
- 我只会更新:  
  - `1-验证/.codex/PLAN.md`: 里程碑、关键 claim/hypothesis、验收标准.  
  - `1-验证/.codex/TASKS.md`: 任务 checklist (`- [ ] ...` / `- [x] ...`) 与优先级调整.  

## 规划模式-细 (Task planning)

- 目标: 把某一个任务写成可执行、可证伪的最小单元.  
- 我会先确认 `task_id`，并只更新该任务目录下的:  
  - `1-验证/tasks/<task_id>/task.md`: 补齐 hypothesis / design / acceptance / artifacts / write-back.  
- 若你希望 md/json 同步: 我会在同一任务内用脚本回写 `task.json`:  

```bash
python .codex/scripts/task_md2json.py --task-dir 1-验证/tasks/<task_id> --update-existing
```

## 编程模式 (Coding)

- 目标: 完成需求并能跑通，优先直观与最小实现.  
- 约束: 不做提前抽象；不为了 "健壮性" 引入复杂错误体系；能用简单条件分支解决就不要上框架.  
- 若产生可对比结果: 必须更新 `1-验证/leaderboard.csv`，并在 `task.json`/`notes.md` 写清楚证据与决策.  

## 审查模式 (Review)

- 目标: 审查当前代码/实验是否满足 `task.md` 描述与验收标准.  
- 约束: 不做实现改动；只给问题清单、定位建议、以及 "如何判定修复完成" 的标准.  
- 通过标准: 确认逻辑与任务一致、结果可复现、关键路径无明显漏洞后，才把审查结论写入: `1-验证/tasks/<task_id>/notes.md`.  

## 反思模式 (Rethink)

- 目标: 让 idea work 的过程中，把失败案例/转向点系统化沉淀，减少重复踩坑，并让后续迭代有可追溯的 "为什么".  
- 产物: `1-验证/rethinks/YYMMDD-rethink-NN.md` (模板: `.codex/templates/rethink.md`).  
- 命名: `YYMMDD-rethink-NN.md`，同一天从 `01` 开始递增，推荐用脚本自动生成骨架避免手工出错:  

```bash
python .codex/scripts/new_rethink.py --source-task <task_id>
```

- 工作流约束:  
  - 人写初稿: 你先把要点写成 "子弹点/半成品"，我不替你编造结论或理由.  
  - agent 润色: 我只做结构化、补齐表达、把证据链写清楚，并标注不确定处供你核对.  
  - 人终审: 你确认无误后再把 `status` 标为 `final`.  
- 写回: rethink 定稿后，把其路径写回到对应 `1-验证/tasks/<task_id>/notes.md`，并同步 `task.json` 的 `decision/next_tasks` (如适用).  

## 优化模式 (Optimize)

- 目标: 在 "已经跑通并通过审查" 的基础上做代码规范化与可读性优化.  
- 约束: 不改变外部行为、不改变结论；优化后需要能跑通同样的验证流程.  

## 结束 (Session)

- 当你说 "结束": 我必须把本次对话的关键信息沉淀为 session 记录 (追加写入，文件已存在则 append):  
  - `session/YYMMDD-session.md`  
  - `session/YYMMDD-session.json` (结构参考 `.codex/templates/session.json`，但 `stage` 写 `1-验证`，`mode` 写本次实际模式)  
