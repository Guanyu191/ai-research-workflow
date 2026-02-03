# 0-调研 AGENTS-TEACHER

本文件用于将 `0-调研/references/` 中的论文 PDF 翻译为高质量学习笔记 `0-调研/notes/<paper_id>.md`，遵循 "先翻译后讨论，再回写" 的工作流.

> **Note:** references 同步与登记规则见 `0-调研/.codex/AGENTS.md`，此处不重复.

## 1. 输入与输出

- **输入**: `0-调研/references/*.pdf`
- **输出**: `0-调研/notes/<paper_id>.md`
- **模板**: `.codex/templates/paper_note.md`
- **命名**: `paper_id` 用 `YYMMDD-NN` (例如 `260202-01`)

## 2. 硬规则 (必须遵守)

- **不要猜 (NO GUESSING)**: paper 没写清的条件/设置/结论边界，一律写入 `Open questions (reading)`，并说明需要回到 PDF/附录/代码核对.
- **疑似笔误先不改**: 如果发现 paper 内部出现明显自相矛盾或疑似排版/符号笔误 (例如定义式与后文数值不一致)，先按原文把公式/句子原样翻译出来，再用 `> **Note:**` 指出不一致点与推断风险，并把核对动作写入 `Open questions (reading)`. 不要静默修正为 "常见写法".
- **不扩写结论**: 不添加 paper 没有的 claim，不擅自补全实验设置或推断因果链.
- **遵从结构**: 默认逐段翻译，遵从论文原有组织方式与顺序，不为了 "更清晰" 擅自重排.
- **背景不省略**: 只要原论文在 Methodology/Background 里先讲 standard method / baseline (例如 standard Transformer 的 attention 定义)，就必须先完整翻译这一段，再进入 kernel viewpoint / 改进模块. 不要因为 "大家都懂" 就直接跳过.
- **关键术语**: 统一写成 `English term (中文术语)`，全文一致.
- **note block**: 统一使用 `> **Note:** ...`，前缀必须加粗，且冒号包含在加粗内. 仅用于术语对齐、符号解释、实现细节注释、常见误读点与需要核对的问题.
- **Note/例子必须可核实**: 你写的每一个 `> **Note:**` 与每一个 **例子:** 都必须能被核实 (paper 原文 / appendix / 官方代码 / 被引用论文的原文). 如果不能核实，就必须明确标注为 "需要核对" 并写入 `Open questions (reading)`，不要把它写成确定结论.
- **格式规范**: `0-调研/notes/*.md` 必须对齐 `.codex/文档编写规范-light-V1.1.2.md`，尤其是数学公式与标点. 重点如下:  
  - 行内公式只用 `$...$`，块级公式只用 `$$...$$`，禁止 `\(...\)` / `\[...\]`.  
  - 标点统一: 中文逗号 "，"，英文句号 "."，英文冒号 ": "，英文引号 `"`，英文括号 `()`.  
  - 数学符号尽量进公式里写 LaTeX (例如 `\times`，`\in`，`\Delta`，`\to`)，避免把 Unicode 符号散落在正文里.
  - 变量记号: 涉及小写字母 l 时，一律写成 "ell". 在公式中用 `\ell` (例如写 $R_{\ell}$，不要写 $R_l$)，避免与数字 $1$ 混淆.

## 3. 翻译与写作原则

- **翻译优先**: 默认流程是先产出翻译稿，再围绕你提出的疑点讨论，最后回写到同一份 note.
- **符号与排版对齐**: 数学符号、记号约定、公式排版尽量对齐 paper，不用 "等价但风格不同" 的改写替换原文表达.
- **指代清晰**: 回指某处内容时写清楚是 paper 的哪个对象 (Section, Fig., Table, Eq.)，避免 "上面那个图" 这类不明确指代.
- **额外内容只进 Note**: 凡是为了降低阅读门槛而补充的解释、直觉、改写理由、实现细节，一律写成 `> **Note:** ...`，不要混入正文翻译.
- **Note 分层**: 概念较抽象时允许连续使用多个 `> **Note:** ...`，先写直觉层，再写形式化层，避免把两种层次混在同一段里.
- **先解释再使用 (Methodology 优先级最高)**: 只要 Method 里出现一个会影响实现/复现的名词或缩写，就必须在首次出现处补一个 `> **Note:**`，写清楚 "它是什么，用来干什么，和本文哪个模块对应".  
  - 如果 paper 自己没解释，但写了 "X is proposed in [k]"，必须把 [k] 对应的文章找出来: 先从 paper references 里定位到标题与作者，再联网搜索该文章的官方版本 (OpenReview / arXiv / 期刊 / 官方 repo).  
  - 你补充的解释必须带一个具体例子 (toy example / 小公式 / 伪代码 / 形状说明). 如果找不到可靠来源或仍不确定，写进 `Open questions (reading)`，不要猜.
- **例子优先**: `> **Note:**` 里默认要有 **例子:**，尤其是数值分析类词 (quadrature weight, kernel integral, Euler update) 与张量操作类词 (mode product, tensor-matrix product, Kronecker 结构).
- **例子记号统一**: **例子:** 应尽量复用前文已定义的符号与记号 (例如先用 $\mathbf{U},\mathbf{W}$ 解释 $\times_m$ 的定义). 如果需要切换到本文/论文的符号 (例如 $\mathbf{V},\mathbf{A}^{(m)}$)，必须显式写出映射关系，避免同一段里混用导致索引与维度混乱.
- **不要把线性核写成概率权重**: softmax-free / kernel matrix (例如 $\mathbf{A}^{(m)}$) 不保证非负或行和为 $1$. 因此文字表述优先用 "线性变换" / "线性组合"，不要写成 "加权平均" 或暗示概率意义 (除非原文明确是 softmax 权重).
- **vec/Kronecker 约定要写清**: 只要写到 $\operatorname{vec}(\cdot)$ 或 Kronecker product $\otimes$，就必须声明 $\operatorname{vec}$ 的展平约定 (列优先或行优先) 并确保公式与该约定一致. 不确定就不要写.
- **常见公式先核实**: 写 InstanceNorm / LayerNorm / BatchNorm 等标准化公式时，先做一次定义核对 (均值，方差，分母 $\sqrt{\cdot+\epsilon}$) 与维度核对. 不确定的部分写入 `Open questions (reading)`，不要猜.
- **可读性改写放在后面**: 初稿阶段优先覆盖与对齐，只有在正确性稳定后才做少量可读性改写，且不改变语义边界.
- **术语一致**: 关键术语固定译法并保持全文一致，避免同义词导致概念漂移; 术语首次出现或首次解释时允许加粗强调.
- **引号与字符**: 英文引号与撇号统一使用 ASCII 字符 `"` 与 `'`，避免智能引号.
- **来源标注策略**: note 中默认不写页码式溯源标注; 若需要溯源，在对话中单独给出 PDF 文件名与页码即可.

## 3.1 特别提醒: 翻译 FactFormer (Scalable Transformer for PDE Surrogate Modeling)

当你在翻译 `Scalable Transformer for PDE Surrogate Modeling` 的 Methodology 时，必须把 FactFormer 的实现链路讲到 "可直接照着写代码" 的粒度，并在关键名词处补 `> **Note:**` + **例子:**:

- **softmax-free attention**: 写清楚它的矩阵形式，与 "kernel integral viewpoint" 的对应关系 (离散积分 / quadrature weight 的直觉).
- **RoPE**: 写清 RoPE 的作用与核心性质 (相对位置)，并解释 "为什么能写成只依赖 $x_i-x_j$".
- **learnable projection**: 写清从 $n$ 维函数到每个轴的一维子函数的投影过程，强调其本质是 "pointwise transform + mean pooling + pointwise MLP" (在均匀网格情形).
- **factorized kernel integral**: 写清 $\mathbf{A}^{(m)}$ 的形状与构造，再写清最终如何用张量-矩阵乘积得到输出.
- **mode product / tensor-matrix product**: 必须给 2D toy example (例如 $4\times 4$)，让读者知道它到底在做什么求和.
- **Instance Normalization**: 说明它是按 sample + channel 做归一化，为什么对深堆叠/长 rollout 的数值尺度有帮助.
- **latent marching + pushforward**: 说明它们在训练时解决的具体问题 (compounding error / train-inference gap)，至少给一个最小可执行伪代码片段说明 pushforward 的 stop-gradient 做法.

## 4. 默认互动结构

1) **翻译准备**:
   - 你提供: `paper_id`、`pdf_path`、本次覆盖范围 (默认从 Abstract 开始逐段翻译).
   - 我确认: 翻译粒度 (默认逐段) 与输出路径 `0-调研/notes/<paper_id>.md`.
2) **产出翻译稿**:
   - 按 `.codex/templates/paper_note.md` 的 `Abstract / Introduction / Methodology / Experiments` 顺序逐段翻译.
   - 初稿阶段不展开大段讲解，只做必要的术语与符号注释 (写进 `> **Note:**`).
   - 同步填写模板中的结构化小节 `Problem / Method / Key claims / Limitations / Open questions`，只写 paper 明确支持的信息.
3) **你复核对照**:
   - 你对照 PDF 标出错译、漏译、歧义与需要进一步解释的点.
4) **讨论疑点**:
   - 我围绕疑点解释与修订，并明确哪些点必须回到 PDF 核对.
5) **回写 note**:
   - 将讨论收敛后的版本回写到同一份 note，保持结构与表述边界一致.

## 5. 翻译改稿工作流 (迭代)

这是强制流程，默认按顺序推进:

1) [ ] 覆盖优先: 不漏段、不乱序，先把目标范围完整翻译出来.
2) [ ] 正确性: 对照原文修正错译、漏译、符号、条件与结论边界.
3) [ ] 格式: 对齐 `.codex/文档编写规范-light-V1.1.2.md`.
4) [ ] 原则: 在不改语义的前提下提升可读性 (段落、强调、`> **Note:**` 策略).
5) [ ] 语义对照: 多轮改稿后再次对照原文，检查语义漂移风险 (尤其是条件、范围、因果关系).

## 6. 可选: note -> research.json

当你明确要求 "回写 research.json" 时，执行:

```bash
python .codex/scripts/paper_md2json.py --create-missing --update-existing --paper_id <paper_id>
```
