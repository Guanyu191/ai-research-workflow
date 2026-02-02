# 2-实验和写作 阶段 AGENTS

本阶段目标: 构建论文级证据链 (消融，敏感性，统计)，并同步写作.

## 强制产物
- 每次系统化实验一个 case: `2-实验和写作/runs/<case_id>/`.  
- 每个 case 必须有: `case.json`，并将主指标写入 `results/leaderboard.csv`.  
- 图表统一汇总到 `results/figures/`，表格汇总到 `results/tables/`.

## 写作要求
- 先产图与表，再产文字.  
- 每个关键结论必须对应: 对照实验 + 消融 + 统计说明.  
