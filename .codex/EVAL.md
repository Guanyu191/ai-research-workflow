# EVAL (评估协议)

## 1. 数据划分 (Data split)
- Train/Test: 默认用 80% 训练集，20% 测试集 (可改). 按 `<SPLIT_UNIT>` 划分 (例如: subject / sequence / scene / patient / trajectory)，避免泄漏.  
- Val: 默认不单独设置 val. 如果需要调参或早停，再从训练侧划出.  
- 泄漏风险与避免: 主要关注时间泄漏/同源样本泄漏/重复样本. 通过按 `<SPLIT_UNIT>` 划分避免. 例如:
  - 若共有 `N=5` 个 split unit，可用前 `4` 个训练，最后 `1` 个测试.  
  - 若 `N=10`，可用前 `8` 个训练，最后 `2` 个测试.  

## 2. 指标 (Metrics)
- 主指标: `<PRIMARY_METRIC>` (把公式/实现说清楚，避免口头缩写).  
- 辅助指标 (可选): `<SECONDARY_METRICS>` (例如分段/逐时刻曲线、稳定性指标、代价指标).  
- 统计方式: `<AGGREGATION_AND_SEEDS>` (例如 mean/std，是否多 seed，如何汇总多个 split unit).  

## 3. 报告格式 (Reporting)
- 每次对比必须包含:
  - 配置名 (task_id / case_id).  
  - 训练成本 (steps，walltime，GPU/CPU).  
  - 指标与统计.  
  - 关键可视化 (必要时).  

## 4. 注意事项
- 指标描述一旦变更必须写 ADR，并更新所有 leaderboard 的解释.  
