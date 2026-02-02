# 0-调研 TASKS

> **Note:** 本阶段任务以 "足够支撑后续验证与写作" 为准，不设硬性数量要求。把下面的 `<...>` 换成你的课题内容即可。

## R001-R003 Baseline / 数据 / 评估

- [ ] R001: Baseline 盘点 (paper -> 可复现要点)  
  - [ ] 明确 baseline 的输入/输出/假设/限制，并写进对应的 `0-调研/notes/<paper_id>.md`.  
  - [ ] 记录 baseline 的训练配方 (数据处理、loss、优化器、关键超参、训练/推理差异).  
  - [ ] 列出复现缺失信息与 open questions (明确需要回到论文/附录/代码核对).  
  - Deep research prompt:  
    ```text
    以 <BASELINE> 为锚点，提取所有复现关键细节，整理成 implementation checklist。
    输出要点：输入输出、数据处理/normalization、loss、训练策略、推理/rollout、关键超参、硬件/成本、未写清的 open questions。
    ```

- [ ] R002: 数据集/benchmarks 与评估协议盘点  
  - [ ] 列出候选 datasets/benchmarks：来源、许可、获取方式、版本、数据形态、预处理要点.  
  - [ ] 把评估协议收敛到 `.codex/EVAL.md` (split unit、指标、统计方式、报告格式).  
  - Deep research prompt:  
    ```text
    请盘点 <DOMAIN> 方向常用 datasets/benchmarks 与评估设置，并与本项目需求对齐。
    输出：数据来源与许可、数据形态(输入/输出/长度/分辨率)、默认划分方式、主指标/辅助指标、常见坑(泄漏/对齐/归一化)。
    ```

- [ ] R003: 相关工作地图 (model lineage + 对照方法)  
  - [ ] 建立 "强相关/对照/可借鉴" 三类清单，并标注每篇的可迁移点.  
  - [ ] 形成 1 页 summary：我们的方法可能赢在哪里/可能输在哪里/代价是什么.  
  - Deep research prompt:  
    ```text
    围绕 <PROBLEM_STATEMENT>，整理相关工作地图：baseline、直接竞争方法、可借鉴机制。
    重点收敛到：后续验证阶段应该做哪些对照/消融，才能支撑 decision 与写作动机。
    ```

## R004-R006 Hypothesis -> 验证任务候选

- [ ] R004: 形成可证伪 hypothesis 列表  
  - [ ] 每条 hypothesis 都写清: 变量 / baseline / 指标 / 预期方向 / 反证条件 / 成本预算.  
  - [ ] 每条都指向最合适的数据集与对照 (不确定就写 open questions).  

- [ ] R005: 失败模式与风险清单  
  - [ ] 记录常见 failure modes：训练不收敛、rollout 崩溃、指标泄漏、数据对齐错误、过拟合/分布外等.  
  - [ ] 为每个 failure mode 给出最小排查步骤 (先检查数据与评估，再检查实现).  

- [ ] R006: 移交到 1-验证 的任务拆解  
  - [ ] 把每条 hypothesis 映射成 1-2 个 `1-验证` 任务候选 (task_id, design, pass/fail, budget).  
  - [ ] 更新 `1-验证/.codex/TASKS.md` 的候选队列，并在 `session/` 记录本次移交的决策与理由.  
