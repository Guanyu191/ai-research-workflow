# PLAN (项目里程碑)

本文件回答 3 件事: 我们要做什么、做到什么程度算完成、产物写回哪里 (证据链可追溯).

## 0) 目标与成功标准 (Problem -> Evidence -> Decision)

- **问题:** `<PROBLEM_STATEMENT>`
- **方案(候选):** `<BASELINE>` -> `<METHOD_VARIANT_1>` / `<METHOD_VARIANT_2>` / ...
- **评估协议:** 以 `.codex/EVAL.md` 为 SSOT.
- **成功标准 (可操作版本):**
  - 形成明确 decision: 继续 / 转向 / 停止，并能指向可追溯证据 (配置、日志、指标、对照说明).
  - 当形成明确决策时，写 ADR: `.codex/decisions/ADR-xxxx-*.md`.

## 1) 数据与基线定义 (SSOT)

- **数据登记:** `data/REGISTRY.json` (来源、版本、路径、hash、生成命令、许可信息).
- **默认验证顺序 (建议):**
  - `<DATASET_ID_1>`
  - `<DATASET_ID_2>`
  - `<DATASET_ID_3>`
- **从最小可跑开始 (demo 数据策略):**
  - 先从每个数据集中抽出一个最小子集 (例如 1 条序列 / 100 个样本 / 1 个场景)，存到 `data/processed/`，并登记到 `data/REGISTRY.json`.
  - demo 只用于: 跑通 pipeline / 检查指标与泄漏 / 验证可学习性；不用于最终对比结论.
- **baseline 定义 (进入验证前必须明确):**
  - baseline 代码位置: `<RELATIVE_PATH_TO_BASELINE_CODE>`
  - 关键配置: `<INPUT_WINDOW>` / `<PRED_HORIZON>` / loss / optimizer / batching / seeds
  - 报告格式: 指标 + 成本 + 关键可视化 (如需要)，并写回到 `1-验证/leaderboard.csv`.

## Milestone A (调研 -> 可操作假设)

- **产物:**
  - 我在 `0-调研/research.json` 找到并登记 "足够支撑问题与方案" 的关键文章 (允许在实验过程中边验证边补文献).
  - 我在 `0-调研/notes/` 为关键文章补齐速读卡片 (抽取: 问题、方法、证据、局限、可复用点).
  - 我更新 `0-调研/.codex/PLAN.md` 与 `0-调研/.codex/TASKS.md` (把 hypothesis 落到可验证任务).
- **出口条件:**
  - 形成 "足够的" 可证伪 hypothesis (每条写清: 变量/对照/指标/预期方向/失败也有用的信息).
  - "是否足够" 由你确认. 我在进入 Milestone B 前会向你询问一次.

## Milestone B (验证 -> 明确路线)

- **产物:**
  - 我跑通 baseline + 评估流程 (先 demo，再逐步扩大)，并形成可追溯的对照记录.
  - 我围绕 hypothesis 做 "足够的" 单因素改动验证 (每次只改一个变量或一组强相关变量).
- **出口条件:**
  - 形成明确 decision: 路线 A / 路线 B / 放弃.
  - 当形成明确决策时，写 ADR (`.codex/decisions/ADR-xxxx-*.md`).

## Milestone C (实验与写作 -> 论文证据链)

- **产物:**
  - `2-实验和写作/runs/<case_id>/case.json`: 我形成可复现实验 case 记录 (命令、配置、环境、指标齐全).
  - `2-实验和写作/results/leaderboard.csv`: 我维护完整对照表 (baseline + 主方法 + ablations).
  - `2-实验和写作/paper/main.tex` 可编译，且与 `2-实验和写作/paper/draft.json` 同步.
- **出口条件:**
  - 关键结论可追溯到: 对应 case + 日志/图表 + leaderboard 条目 (而不是口头描述).
  - "是否足够" 由你确认. 我在准备推进写作收敛前会向你询问一次.

## 当前已确定的规划选择 (如需变更，先讨论再更新本文件)

- 默认验证顺序: `<DATASET_ID_1> -> <DATASET_ID_2> -> ...`
- demo 策略: `<HOW_TO_BUILD_DEMO_DATASET>`
- 评估点位/报告方式 (可选): `<REPORTING_POINTS_OR_PROTOCOL>`
