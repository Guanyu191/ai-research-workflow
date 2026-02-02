# AI 科研工作流 Workspace 模板

本仓库模板面向: AI for Science 项目 + Codex 协作 (任务拆解，实验记录，证据链沉淀).  
目标: 让 "调研 -> 验证 -> 实验与写作" 形成闭环，且所有关键结论都可追溯，可复现，可检索.

## 目录总览
- `.codex/`: 项目级规则与模板 (SSOT: single source of truth).  
- `0-调研/`: 文献与想法输入侧 (论文登记 + 速读卡片 + 结论抽取).  
- `1-验证/`: 小成本验证 (最小原型，可证伪实验，快速决策).  
- `2-实验和写作/`: 系统化实验 + 论文证据链 (可复现 case + 总榜).  
- `data/`: 全局数据目录 (分层 + 登记册).  

## 我日常这样用 (最小闭环)
1. 调研: 在 `0-调研/` 用表单/脚本将论文写入 `research.json`，并生成一页速读卡片到 `0-调研/notes/`.  
2. 验证: 在 `1-验证/tasks/` 新建任务目录，复制 `.codex/templates/` 下的任务模板三件套: `task.md` + `task.json` + `notes.md`.  
3. 实验: 在 `2-实验和写作/runs/<case_id>/` 写 `case.json`，并把主指标同步到 `2-实验和写作/results/leaderboard.csv`.  
4. 决策: 发生关键取舍时，写 `.codex/decisions/ADR-xxxx-*.md`，并在对应 task notes 里引用.

## Codex 约定 (强制写回)
- 任何完成的任务都必须更新: `task.json` 的 `result_summary`，`decision`，`next_tasks`，以及 `notes.md` 的复盘.  
- 若产生可对比指标，必须更新 leaderboard (验证阶段或实验阶段).  
- 若改变评估描述/数据划分/核心结构，必须写 ADR.

## 初始化时我只需要改 3 个地方
- `.codex/AGENTS.md`: 研究问题与项目边界 (Problem).  
- `.codex/EVAL.md`: 评估协议 (数据划分，指标，统计).  
- `data/REGISTRY.json`: 数据来源，版本，hash，生成命令.  
