---
title: "Darwinian Evolver — Evolve prompts/regex/SQL/code with Imbue's evolution loop"
sidebar_label: "Darwinian Evolver"
description: "Evolve prompts/regex/SQL/code with Imbue's evolution loop"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 达尔文进化器

利用 Imbue 的进化循环功能，对提示词、正则表达式、SQL 语句或代码片段进行优化。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/research/darwinian-evolver` 安装 |
| 路径 | `optional-skills/research\darwinian-evolver` |
| 版本 | `0.1.0` |
| 开发者 | Bihruze (Asahi0x)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos |
| 标签 | `进化`、`优化`、`提示词工程`、`研究` |
| 相关技能 | [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv)、[`jupyter-notebook`](/docs/user-guide/skills/optional/data-science/data-science-jupyter-notebook) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为内容。
:::

# 达尔文进化器

运行 Imbue 提供的 [darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) —— 一种由大语言模型驱动的进化搜索循环 —— 根据适应度函数对**提示词、正则表达式、SQL 查询或小型代码片段**进行优化。

状态：该技能仅为上游工具的简化封装。它负责安装相关工具，引导智能体编写“问题”定义（包括目标对象、评估机制及变异规则），并通过上游命令行工具或自定义的简单 Python 驱动程序来控制进化循环的运行。

**许可证：** 该上游工具采用 **AGPL-3.0** 许可协议。该智能体仅通过上游 CLI 或 `subprocess`/`uv run` 方式调用该工具（属于简单整合），严禁将上游工具的类直接导入到 Hermes 中。

## 适用场景

- 用户提出“优化此提示词”、“为 X 优化正则表达式”、“自动改进此代码/SQL”或“寻找更优的指令”等需求。
- 您已拥有评分机制（精确匹配、正则匹配率、单元测试、LLM 评估工具或运行时指标）以及初始候选方案。若没有评分机制，请先设计一个——这是最关键的部分。
- 成本可接受：一次典型运行需要调用 50–500 次 LLM。在 gpt-4o-mini 上成本仅为几美分；而在 Claude Sonnet 上则可能需要几美元。

**以下情况请勿使用此功能：**
- 优化目标具有可微性（应使用梯度下降/DSPy 方法）。
- 只需要尝试 2–3 种方案——可直接手动编写即可。
- 适配度指标完全依赖主观判断，且无量化标准。

## 先决条件

- Python ≥3.11
- `git`、`uv`（或 `pip`）
- 下列任一 API 密钥：`OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY`

该智能体附带了一个名为 `parrot_openrouter.py` 的小型驱动程序，它通过 OpenAI SDK 使用 `OPENROUTER_API_KEY`，因此任何在 OpenRouter 上的模型均可使用。而上游 CLI 本身则预置了 Anthropic 相关配置，需要 `ANTHROPIC_API_KEY`。

## 安装（一次性操作）

通过 `terminal` 工具运行即可：

```bash
mkdir -p ~/.hermes/cache/darwinian-evolver && cd ~/.hermes/cache/darwinian-evolver
[ -d darwinian_evolver ] || git clone --depth 1 https://github.com/imbue-ai/darwinian_evolver.git
cd darwinian_evolver && uv sync
```

验证：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver \
  && uv run darwinian_evolver --help | head -5
```

## 快速入门——内置的 Parrot 示例

简易功能测试（需要 `ANTHROPIC_API_KEY`）：

```bash
cd ~/.hermes/cache/darwinian-evolver/darwinian_evolver
uv run darwinian_evolver parrot \
  --num_iterations 2 \
  --num_parents_per_iteration 2 \
  --mutator_concurrency 2 --evaluator_concurrency 2 \
  --output_dir /tmp/parrot_demo
```

输出结果：
- `/tmp/parrot_demo/snapshots/iteration_N.pkl` — 每次迭代后的种群数据（已序列化）
- `/tmp/parrot_demo/<jsonl>` — 每次迭代的 JSON 日志文件（路径会在执行结束时显示）

请在浏览器中打开 `~/.hermes/cache/darwinian-evolver/darwinian_evolver/darwinian_evolver/lineage_visualizer.html`，并加载该 JSON 日志以查看进化树。

## 快速入门 — OpenRouter 驱动（无需 Anthropic 密钥）

该技能附带了 `scripts/parrot_openrouter.py` 脚本——问题设置与 Parrot 相同，但会通过 OpenRouter 调用大型语言模型，因此任何提供商均可使用。

```bash
# From wherever the skill is installed:
SKILL_DIR=~/.hermes/skills/research/darwinian-evolver
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver

cd "$DE_DIR" && \
  EVOLVER_MODEL='openai/gpt-4o-mini' \
  uv run --with openai python "$SKILL_DIR/scripts/parrot_openrouter.py" \
    --num_iterations 3 --num_parents_per_iteration 2 \
    --output_dir /tmp/parrot_or
```

使用 `scripts/show_snapshot.py` 查看结果：

```bash
uv run --with openai python "$SKILL_DIR/scripts/show_snapshot.py" \
  /tmp/parrot_or/snapshots/iteration_3.pkl
```

预期输出：按得分从高到低排序的7个经过优化的提示模板，其中最优版本的得分应在0.6至0.8之间（初始模板`Say {{ phrase }}`的得分为0.000）。

## 定义自定义问题

该技能提供了`templates/custom_problem_template.py`文件——可直接复制、编辑并运行。需定义以下三个要素：

1. **`Organism`** — 一个基于Pydantic的`BaseModel`子类，用于存储需要优化的内容（如`prompt_template: str`、`regex_pattern: str`、`sql_query: str`、`code_block: str`等）。需为其添加一个`run(*args)`方法以执行相关操作。

2. **`Evaluator`** — 具备`.evaluate(organism) -> EvaluationResult(score=..., trainable_failure_cases=[...], holdout_failure_cases=[...], is_viable=True)`方法。
   - **`score`**的取值范围为[0, 1]，数值越高表示效果越好。
   - **`trainable_failure_cases`** — 即变异器所接收的输入数据，需包含足够的上下文信息（包括输入内容、预期结果与实际输出），以便大型语言模型进行故障诊断。
   - **`holdout_failure_cases`** — 不会传递给变异器，可用于检测过拟合现象。
   - 除非该`Organism`存在严重缺陷（如引发异常或返回None等），否则默认设置`is_viable=True`。得分为0但仍然可用的`Organism`也是可行的——只是在父代选择过程中会被降低权重。

3. **`Mutator`** — 具备`.mutate(organism, failure_cases, learning_log_entries) -> list[Organism]`方法。
   其典型工作流程为：构建一个包含当前`Organism`、相关故障案例以及修复建议请求的大型语言模型提示语；解析模型返回的响应；进而生成一个新的`Organism`。若解析失败，则返回`[]`，此时循环会自动处理该情况。
接着编写一个驱动脚本，将 `Problem(initial_organism, evaluator, [mutators])` 与 `EvolveProblemLoop` 相连接，并通过 `loop.run(num_iterations=N)` 进行迭代——随附的 `scripts/parrot_openrouter.py` 文件可作为参考。

## 真正重要的超参数

| 参数 | 默认值 | 何时调整 |
|---|---|---|
| `--num_iterations` | 5 | 当对评估器有足够信心后，可提升至 10–20 |
| `--num_parents_per_iteration` | 4 | 为降低计算成本，可降至 2 |
| `--mutator_concurrency` | 10 | 为避免速率限制，可降至 2–4 |
| `--evaluator_concurrency` | 10 | 同上；评估器也会对大语言模型造成负担 |
| `--batch_size` | 1 | 当突变操作能处理多次失败时，可提升至 3–5 |
| `--verify_mutations` | 关闭 | 当突变操作效率低下（每次 Imbue 运行中节省的成本不足 10 倍）时，可开启该选项 |
| `--midpoint_score` | `p75` | 除非得分呈现聚集趋势，否则无需调整 |
| `--sharpness` | 10 | 无需调整 |

## 常见陷阱

1. **“初始个体必须具有生存能力”**——即便种子个体的得分是0，也应在`EvaluationResult`中设置`is_viable=True`。因为无法从无生存能力的个体中进行进化，所以循环会直接拒绝它们。
2. **提供方的内容过滤机制会导致运行失败**。基于Azure的OpenRouter模型会对类似“忽略之前的指令”这样的语句返回HTTP 400错误。应将LLM调用包裹在`try/except`结构中，并返回`f"<LLM_ERROR: {e}>"`——这样进化器就会将该个体的得分定为0并继续下一轮。
3. **`loop.run()`是一个生成器**——在对其进行迭代之前，调用它并不会启动任何操作。应使用`for snap in loop.run(num_iterations=N):`的语法。
4. **快照为嵌套的pickle格式文件**。`iteration_N.pkl`文件中包含一个字典，该字典里存有`population_snapshot`（即更多经过pickle序列化的字节数据）。若要反序列化这些数据，必须确保在与序列化时相同的路径下能够导入`Organism`类。
5. **默认的并发级别过高**。设置为10/10会在大多数提供方那里触发速率限制。建议初始值设为2/2。
6. **CLI默认绑定Anthropic平台**。执行`uv run darwinian_evolver <problem>`命令时会自动查找`ANTHROPIC_API_KEY`并使用Claude Sonnet模型。若要使用其他提供方，需编写类似`parrot_openrouter.py`的驱动程序。
7. **受AGPL许可证约束**。严禁在Hermes核心代码中直接使用`from darwinian_evolver import ...`语句。而放在`~/.hermes/skills/...`目录下的自定义驱动脚本属于用户端代码，是允许的。
8. **没有PyPI包版本**。执行`pip install darwinian-evolver`命令会安装到错误的包。务必从GitHub仓库直接进行安装。

## 验证

完成安装并运行 Parrot 后，只要其退出码为 0 即可：

```bash
DE_DIR=~/.hermes/cache/darwinian-evolver/darwinian_evolver
ls "$DE_DIR/darwinian_evolver/lineage_visualizer.html" >/dev/null && \
cd "$DE_DIR" && uv run darwinian_evolver --help >/dev/null && \
echo "darwinian-evolver: OK"
```

## 参考资料

- [Imbue研究文章](https://imbue.com/research/2026-02-27-darwinian-evolver/)
- [ARC-AGI-2实验结果](https://imbue.com/research/2026-02-27-arc-agi-2-evolution/)
- [imbue-ai/darwinian_evolver项目](https://github.com/imbue-ai/darwinian_evolver)（AGPL-3.0许可证）
- [达尔文哥德尔机器](https://arxiv.org/abs/2505.22954)
- [PromptBreeder工具](https://arxiv.org/abs/2309.16797)
