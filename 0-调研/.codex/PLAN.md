# 0-调研 PLAN

## 0. 核心问题 (四问)
- 要解决什么问题？
- 为什么要解决这个问题？
- 能用/要用什么方案解决这个问题？
- 能用/要用什么算例来验证我们的方案能解决这个问题？

## 1. 本阶段产物
- `0-调研/research.json`: 记录论文条目，覆盖足够支撑问题与方案的文章.  
- `0-调研/notes/<paper_id>.md`: 每篇关键论文一页卡片，按模板回答四问并可复用.  
- Hypothesis: 以足够为准，且每条都可证伪、可落到后续验证算例与对比.  
- 移交到 `1-验证/`: 将 hypothesis -> 可执行的验证任务描述 (算例、数据切分、指标、对比项、预期现象、反证条件).  

## 2. 工作流 (建议)
- Pre-flight: 先运行 `.codex/scripts/check_unrecognized_references.py --strict`，确保 `references/` 与 `research.json` 同步.  
- 主题地图:
  - `<BASELINE>` 及强相关工作 (模型谱系/对比方法).  
  - `<METHOD_CANDIDATES>` 的关键机制与可复用设计点 (按你的课题替换).  
  - `<MOTIVATION>`: 为什么这个问题重要/为什么现在做.  
  - 评估协议与常见失败模式 (metrics、split、leakage、failure cases).  
- 阅读 -> 记录 -> 提炼:
  - 每读一篇，先补齐 `research.json`，再写 note，并在 note 中明确四问.  
  - 形成 hypothesis 时，写清变量、预期、反证条件，并标注最合适的验证算例.  
- 对接验证: 每次收敛一组 hypothesis，就同步更新 `1-验证/` 的任务候选 (只写描述与依赖，细节留到验证阶段的 TASKS).  
