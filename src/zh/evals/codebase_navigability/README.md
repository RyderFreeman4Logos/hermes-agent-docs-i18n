# 代码库可导航性评估

该评估用于衡量**LLM智能体**处理某个代码库所需的成本，而非CPU的处理成本。该功能是为2026年9月的分解方案（PR #102117）而设计，旨在确保后续重构后的数据仍保持一致。所有计算均在离线环境下进行且结果确定，不会调用任何模型。

## 它要回答的三个问题

1. **查看一个定义需要阅读多少代码？**（`bench.py`）
   计算逻辑为：统计`tests/`目录中所有`from <第一方模块> import <名称>`的导入语句，再通过重导引找到实际**定义该名称**的模块。这相当于约19,000次自动生成的“定位X”操作。针对每项任务，会计算定义文件的字符数、符号本身的字符数，以及文件大小与32k/128k上下文限制的匹配情况；还会统计该代码段跨越了多少个2,000行长度的读取窗口、同一文件中存在多少个无关的顶层元素，以及该符号的圈复杂度。字符计数基于真实的`tiktoken` `o200k_base`标准；若该工具不可用，则会退而使用字节/4的换算方式并明确标注。

2. **一个高效的智能体查询某个符号实际上需要付出多少成本？**（`lookup_sim.py`）
   该工具通过我们的工具模拟优秀模型所采用的查询策略：首先使用`grep -n`查找定义位置（1次调用），然后在找到的位置周围读取200行范围的代码（1次调用）；仅在仍在读取定义内容时，才以2,000行为单位逐页向前读取。评估会统计工具调用的次数以及返回的字符数。由于比较的是两种代码库中都存在的符号随机样本，因此属于配对对比分析。

3. **结构与运行时分析。**（`static_metrics.py`、`runtime_bench.py`）
包括代码/注释/文档字符串的行数分布、文件及函数大小分布、`elif`链长度、嵌套深度、Radon CC/MI指标、导入图结构（边、入度/出度、Tarjan强连通分量循环）；针对入口点的纯解释器导入时间/模块数量/RSS值、CLI命令的端到端执行情况、进程内的高频执行路径、通过pytest收集的测试数据，以及字节码占用空间。《runtime_bench.py`会将`PYTHONPATH`固定为指定的代码树，并确保不会加载来自其他版本的模块（否则，可编辑安装方式会导致隐蔽的交叉污染）。

## 使用方法

```bash
# deps: tiktoken + radon (bench venv or the project venv)
uv pip install tiktoken radon

# 1 + 2: pass two checkouts (git worktree add is the easy way to get the baseline)
git worktree add /tmp/base origin/main
python evals/codebase_navigability/bench.py /tmp/base base --out out/
python evals/codebase_navigability/bench.py .        head --out out/
python evals/codebase_navigability/lookup_sim.py /tmp/base . --sample 4000 --out out/

# 3
NAV_OUT=out/ python evals/codebase_navigability/static_metrics.py /tmp/base base
NAV_OUT=out/ python evals/codebase_navigability/static_metrics.py .        head
NAV_OUT=out/ python evals/codebase_navigability/runtime_bench.py  /tmp/base base 9
NAV_OUT=out/ python evals/codebase_navigability/runtime_bench.py  .        head 9
```

在包含100万行代码的测试树上，`bench.py`和`static_metrics.py`的运行时间各约为2分钟；`lookup_sim.py`处理4,000个符号时需要约10分钟（它会将“读取”的每个窗口都进行分词处理）；而`runtime_bench.py`在重复9次测试时，每棵树的运行时间约为4分钟。

## 如实解读测试结果

- `bench.py`衡量的是**简单读取**的成本（即完整读取整个定义文件）。当代码文件被拆分后，这一数值会下降约3倍，同时它也决定了某个文件是否能够放入上下文窗口中。
- `lookup_sim.py`衡量的是**智能处理**的成本。由于使用了grep工具加上200行的窗口大小限制，该成本在文件拆分后几乎不会发生变化，因为它已经能够规避文件大小带来的影响。真正会影响该成本的因素是：(a) 定义本身的长度缩短，以及(b) 周围代码的标记符密度。删除注释会提高每行的标记符密度，因此即使在代码量减少的情况下，经过删除注释优化后，使用固定的200行窗口处理时所需的标记符数量反而会增加。这两种效应确实存在且方向相反，应同时报告两个数值，而非只展示那个看似更优的结果。
- 在Python中，代码拆分会导致导入时间**增加**（因为每个模块都会产生额外的开销），同时导入图中的最大循环通常也会变大（文件内部的耦合关系会转变为模块间的连接）。这些工具都无法掩盖这些变化。

PR #102117的测试结果已在PR描述中给出，该次测试的原始JSON数据则保存在PR的讨论帖中。
