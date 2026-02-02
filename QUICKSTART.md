# Quickstart

## 0) 任务命名
- 抽象任务: 写在 `.codex/TASKS.md`，只描述方向，不写具体实现细节 (例如 `PR1`，`PV1`，`PE1`).
- 具体任务: 写在各阶段的 `*/.codex/TASKS.md`，命名用 `<抽象任务>-S<NNN>` (例如 `PR1-S001`，`PV1-S001`，`PE1-S001`).
- 任务目录: 对于需要落盘代码与结果的任务 (例如 `1-验证/tasks/`)，我优先用具体任务 id 作为目录名.

## 0.5) 5 分钟启动清单 (把 `<...>` 换成你的课题)
- [ ] `.codex/AGENTS.md`: 项目名 / 问题 / 输入输出 / baseline / 边界.  
- [ ] `.codex/PLAN.md`: 里程碑、默认验证顺序、baseline 代码位置、demo 数据策略.  
- [ ] `.codex/EVAL.md`: 数据划分单位 (split unit) / 主指标 / 统计方式 / 报告格式.  
- [ ] `data/REGISTRY.json`: 数据来源、版本、路径(相对路径)、hash、生成命令、许可信息.  
- [ ] （可选但推荐）更新各阶段 `*/.codex/PLAN.md` 与 `*/.codex/TASKS.md`，把抽象任务落到可执行 checklist.  

## 环境要求
- Python 3.10+ (能运行 `python .codex/scripts/*.py`).  

## 1) 初始化
- 在 `.codex/AGENTS.md` 补齐研究问题与边界 (Problem).  
- 填写 `.codex/EVAL.md`.  
- 在 `data/REGISTRY.json` 登记数据来源与路径.  

## 2) 调研录入
- 把 pdf 放进 `0-调研/references/`.  
- 运行检查脚本，看看是否有未登记的 pdf: `python .codex/scripts/check_unrecognized_references.py --strict`.  
- 在 `0-调研/research.json` 里新增 paper block (字段参考 `.codex/templates/paper_entry.json`).  
- 生成或同步笔记:
  - `python .codex/scripts/paper_json2md.py --create-missing` (生成 `0-调研/notes/<paper_id>.md`).  
  - `python .codex/scripts/paper_md2json.py --update-existing` (把 notes 回写到 `research.json`).  

## 3) 新建验证任务
- 先在 `.codex/TASKS.md` 里选一个归属的抽象任务 (例如 `PV1`)，再在 `1-验证/.codex/TASKS.md` 里写一条对应的具体任务 (例如 `PV1-S001`).
- 在 `1-验证/tasks/` 新建目录 `<task_id>/` (推荐直接用 `PV1-S001` 这种具体任务 id).  
- 复制模板:
  - `.codex/templates/task.md` -> `<task_id>/task.md`  
  - `.codex/templates/task.json` -> `<task_id>/task.json`  
  - `.codex/templates/notes.md` -> `<task_id>/notes.md`  
- （可选）参考示例目录: `1-验证/tasks/PV1-S001-example/` (建议复制后改名).  
- 同步 `task.md` 与 `task.json` (可选，但推荐):  
  - `python .codex/scripts/task_json2md.py --task-dir 1-验证/tasks/<task_id> --overwrite`  
  - `python .codex/scripts/task_md2json.py --task-dir 1-验证/tasks/<task_id> --update-existing`  
- 跑实验后写回结论，并更新 `1-验证/leaderboard.csv`.

## 4) 新建 case (论文级实验)
- 在 `2-实验和写作/runs/<case_id>/` 放 `case.json`.  
- 将主结果写入 `2-实验和写作/results/leaderboard.csv`.  
- （可选）参考示例目录: `2-实验和写作/runs/PE1-S001-example/` (建议复制后改名).  

## 5) 模式 (我怎么让 Codex 干活)
> Note: 这里的 "模式" 不是脚本开关，而是一次对话的工作方式. 我可以直接说: 进入 <阶段> <模式>: <目标>.  

- **项目级: `.codex/AGENTS.md` 规划模式:**  
  - **适用:** 新项目启动，或研究问题/输入输出/边界还不稳定时.  
  - **用法:** 以 `.codex/AGENTS.md` 为 SSOT，把 Problem 写清楚 (问题、输入/输出、边界/基线).  
- **项目级: `.codex/AGENTS.md` 整理模式:**  
  - **适用:** 想快速看全局进展，发现 "没写回/没更新/不一致" 的地方，并生成一份可追溯的小报告.  
  - **用法:** 扫描 `.codex/PLAN.md`、`.codex/TASKS.md`、各任务目录与 leaderboard 的一致性，修正后把结论写进 `session/YYMMDD-session.md` + `session/YYMMDD-session.json`.  
- **0-调研: 规划模式:**  
  - **适用:** 从 "想法" 落到可操作 hypothesis，确定要读什么、记什么、产出什么.  
  - **用法:** 明确要补齐的 paper list / 速读卡片 / 结论抽取，并把当天推进写进 `session/`.  
- **0-调研: 审查模式:**  
  - **适用:** 调研阶段里程碑前/交接前，检查 registry、notes、references 是否一致 (不看 pdf 内容).  
  - **用法:** `python .codex/scripts/audit_stage0.py --strict`.  
- **1-验证: 粗规划模式:**  
  - **适用:** 先把一个验证任务变成 "最小可证伪单元" (0.5-1 天) 的骨架.  
  - **用法:** 新建 `1-验证/tasks/<task_id>/`，把 hypothesis / baseline / pass-fail / budget 先写满，再决定是否进入细规划或编程.  
- **1-验证: 细规划模式:**  
  - **适用:** 任务已确定要做，需要把变量、对照、数据切分、指标、记录方式写到可直接开工.  
  - **用法:** 完整填写 `task.md` / `task.json`，并明确 "产物要写回到哪里" (task 三件套 + `1-验证/leaderboard.csv`).  
- **1-验证: 编程模式:**  
  - **适用:** 已经有清晰的 task 设计，直接实现代码、跑通 pipeline、产出可复现结果.  
  - **用法:** 只做与 task 相关的最小改动，跑完后写回 `task.json` 的 result_summary/decision/next_tasks，并更新 `1-验证/leaderboard.csv`.  
- **1-验证: 审查模式:**  
  - **适用:** 跑完实验后复盘，检查证据链是否完整 (配置、指标、成本、结论、下一步).  
  - **用法:** 对照 `.codex/EVAL.md` 与 task 三件套，把缺的写回，并在 `session/` 记录这次审查结论.  
- **1-验证: 反思模式:**  
  - **适用:** 出现失败结论/异常现象/转向决策，需要把 fail cases 系统化沉淀，避免重复踩坑.  
  - **用法:** 在 `1-验证/rethinks/` 下新建 `YYMMDD-rethink-NN.md` (模板: `.codex/templates/rethink.md`，推荐脚本: `python .codex/scripts/new_rethink.py --source-task <task_id>`)，流程为 "人写初稿 -> agent 润色 -> 人终审".  
- **1-验证: 优化模式:**  
  - **适用:** baseline 已跑通，开始以指标为导向做有证据的迭代 (而不是盲试).  
  - **用法:** 每次只改一个变量或一组强相关变量，明确预期影响与风险，结果统一写回 task 三件套 + `1-验证/leaderboard.csv` + `session/`.  

> Note: 从现在开始只保留一个 session 目录: `./session/`. 请不要在 `0-调研/`、`1-验证/` 等子目录下新建 `session/`.  
