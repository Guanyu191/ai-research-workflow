# 代码编写规范-light-V1.0.0

用途: 让 Codex 在撰写 Python 科研代码时，对齐我的代码风格 (可读性，可复现，可维护).  
读者: 我自己. 与我协作写代码或改代码的 AI 工具.  
适用: 小型 AI for Science 项目 (验证任务，小规模实验，论文复现脚本).  
来源: Python 之禅 + Google Python Style Guide (取其原则，不强制逐条一致).  
更新规则: 对该规范文件的版本号，人为更新则改第二位版本号，AI 更新则改第三位的版本号.

---

## 0. 全局原则

- 目标优先级: 正确性 > 可复现 > 可读性 > 可维护 > 性能.
- 显式优先: 参数，路径，seed，dtype，device 都不要靠默认值或全局变量.
- 报错要可行动: 消息里写清 "收到什么 -> 期望什么 -> 怎么修".
- 小函数，小模块: 优先写可测试的 pure function，再写脚本 glue code.
- 先写清楚再写快: 性能优化必须有 profile 或明确 bottleneck.

> Note: 对我这类 "小型科研代码"，最值钱的不是跑得快，而是 2 周后我还能复现并解释得清楚.

## 1. 目录与入口 (小项目默认)

- `src/<pkg>/`: 可复用的库代码.  
- `scripts/`: 一次性入口脚本 (解析参数 -> 调用 `src/`).  
- `configs/`: 实验配置 (json/yaml).  
- `runs/<case_id>/`: 产物目录 (config + metrics + checkpoints + figures).  
- `tests/`: 最小单测 (shape，数值 sanity，回归).  

示例: 一个最小项目结构长这样.

```text
.
├── src/pan_ai/
│   ├── __init__.py
│   ├── pde.py
│   └── metrics.py
├── scripts/
│   └── run_case.py
├── configs/
│   └── case_debug.json
└── tests/
    └── test_pde.py
```

## 2. 格式与命名 (PEP 8 + Google)

- 缩进 4 空格.  
- 行宽: 我默认用 black 的 88 (如果不用 formatter，也按这个习惯写).  
- 命名:
  - 模块/文件: `snake_case.py`.  
  - 函数/变量: `snake_case`.  
  - 类: `CamelCase`.  
  - 常量: `UPPER_SNAKE_CASE`.  
  - 私有: `_leading_underscore`.  
- 科研变量建议带语义后缀: `dt_s`，`dx_m`，`temp_k`，`rho_kg_m3` (避免单位混乱).  

示例: import 分三组写 (标准库 -> 第三方 -> 本地)，组与组之间空一行.

```python
from pathlib import Path

import numpy as np

from pan_ai.pde import laplacian_2d
```

工具 (可选): 我默认用 ruff + black + pytest 做最小质量门槛.

```bash
python -m pip install ruff black pytest
ruff check .
black .
pytest -q
```

## 3. 类型标注 + docstring (Google 风格)

- 对外函数/类必须写 type hints + docstring.  
- docstring 写 "做什么 + 输入输出 + 关键约束/单位/shape"，不要写大段推导.  
- 格式: summary 一行，以 "." 结尾；空一行；再写 `Args:` / `Returns:` / `Raises:`.  

示例: 下面展示一个带 shape 校验的数值函数写法.

```python
from __future__ import annotations

import numpy as np


def laplacian_2d(u: np.ndarray, dx: float) -> np.ndarray:
    """Computes the 2D Laplacian on a regular grid (2nd-order stencil).

    Args:
        u: Scalar field with shape (H, W).
        dx: Grid spacing in meters.

    Returns:
        Laplacian with shape (H, W).

    Raises:
        ValueError: If u is not 2D or dx is non-positive.
    """
    if u.ndim != 2:
        raise ValueError(f"u must be 2D, got shape={u.shape}")
    if dx <= 0:
        raise ValueError(f"dx must be positive, got dx={dx}")

    return (
        -4.0 * u
        + np.roll(u, 1, axis=0)
        + np.roll(u, -1, axis=0)
        + np.roll(u, 1, axis=1)
        + np.roll(u, -1, axis=1)
    ) / (dx * dx)
```

## 4. 注释与代码组织 (Python 之禅落地)

- 注释解释 "为什么" (why)，不要复述代码 "做了什么" (what).  
- 少嵌套: 能 `return` 就尽早 `return`，能拆函数就拆.  
- 明确优于隐式: 不要在函数里悄悄读全局路径，悄悄写文件，悄悄改随机种子.  

> Yes: `train(cfg) -> metrics` 返回结果，由 `main()` 决定写哪里.  
> No: `train()` 内部自己拼路径写一堆文件，外面也不知道发生了什么.  

## 5. 配置，日志，产物 (科研最小闭环)

- 每次 run 都有独立 `run_dir/`，里面至少包含:
  - `config.json`: 超参 + seed + 数据版本 + 代码版本 (能拿来复现).  
  - `metrics.jsonl` 或 `metrics.csv`: 每个 step/epoch 一行.  
- 库代码用 `logging`，脚本里才可以少量 `print` (但我更推荐也用 logging).  
- 文件路径用 `pathlib.Path`，不要手写字符串拼接.  

示例: 下面展示 "创建 run_dir + 写 config + 打 log" 的最小模板.

```python
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunConfig:
    case_id: str
    seed: int
    out_dir: Path


def parse_args() -> RunConfig:
    p = argparse.ArgumentParser()
    p.add_argument("--case_id", required=True)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out_dir", type=Path, default=Path("runs"))
    a = p.parse_args()
    return RunConfig(case_id=a.case_id, seed=a.seed, out_dir=a.out_dir)


def init_run(cfg: RunConfig) -> Path:
    run_dir = cfg.out_dir / cfg.case_id
    run_dir.mkdir(parents=True, exist_ok=False)

    cfg_json = {**asdict(cfg), "out_dir": str(cfg.out_dir)}
    (run_dir / "config.json").write_text(
        json.dumps(cfg_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    logger.info("run_dir=%s", run_dir)
    return run_dir


def main() -> None:
    cfg = parse_args()
    _run_dir = init_run(cfg)
    # 把核心逻辑放在 src/ 里，这里只做 "参数解析 -> 调用 -> 写回产物".


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
```

## 6. 随机性与可复现 (seed 只设一次)

- 随机种子集中在一个函数里设置，并写入 config.  
- 任何 nondeterministic 行为都要 "可选开关 + 文档说明".  
- 对结果敏感的实验: 默认跑多 seed，报告均值与方差/置信区间 (描述跟 `.codex/EVAL.md` 对齐).  

示例: 下面是一个最小的 seed 函数 (numpy + 标准库).

```python
import os
import random

import numpy as np


def seed_everything(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
```

## 7. 数值计算的基本防线 (AI for Science 常见坑)

- dtype 和单位要显式: `float32` / `float64`，m / s / kg.  
- 广播 (broadcast) 不要靠运气: 关键张量 shape 在入口处校验.  
- 浮点对比用容差，不要 `==`.  

示例: 下面用 `np.testing` 做数值回归断言.

```python
import numpy as np

np.testing.assert_allclose(y, y_ref, rtol=1e-5, atol=1e-8)
```

## 8. 自查清单

- 标准库/第三方 import 是否分组，且无未使用 import.  
- 对外函数是否有 type hints + docstring (Args/Returns/Raises).  
- 是否记录了 config + seed + metrics (能复现).  
- 路径是否都用 `Path`，且脚本参数显式传入.  
- 关键张量/数组是否在入口处校验 shape，dtype，单位.  
