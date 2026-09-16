# 核心工具集 A/B 测试框架

该框架用于 2026 年 8 月开展的核心工具集性能测试批次（跟踪器编号：[#77056](https://github.com/NousResearch/hermes-agent/issues/77056)）。它通过一系列**旨在引发错误的任务**来衡量工具层的变更是否真正能够减少模型资源浪费——包括 LLM 调用次数、工具调用频率、工具错误率、重试次数、结果数据大小以及处理时间等指标，而这些任务均源自实际生产环境中的各类资源浪费场景。

## 设计思路

- **双臂结构，单一变量。** `baseline` 模式与 `fixes` 模式的唯一区别在于 `PYTHONPATH` 的设置（即使用 `origin/main` 分支还是自定义的集成分支）。两者共享相同的 Hermes 配置环境、模型、任务以及执行实例。
- **任务即陷阱。** 这9个任务均经过精心设计，旨在触发特定的故障类型：`python` 与 `python3`/venv 的混淆、已应用过的补丁、模糊的多匹配编辑、大小写敏感的搜索、隐藏目录的查找、过长的截断输出、频繁切换目录的多级目录操作、被列入黑名单的内联脚本，以及分页读取的大文件问题。任何声称能解决某类故障的修改，都必须能够有效避开对应的陷阱。
- **评分依据是实际运行轨迹，而非自我报告。** 指标来源于运行过程中由 NeMo Relay ATOF 生成的轨迹数据（`llm`/`tool` 层级的事件），同时还会考虑墙钟计时以及针对每个任务的程序化成功检查（标记字符串与磁盘验证）。
- **支持断点续传。** `meta.jsonl` 文件中已完成的 `run_id` 会被跳过，因此电池耗尽后仍可从上次中断处继续运行。启动失败（非零退出码且无输出）不会被记录——系统会自动尝试重新启动，而不会污染数据记录（这一点在2026年8月的第一次测试中得到了验证）。

## 设置步骤

1. 创建一个专用的 Hermes 配置环境，并配置待测试模型的相关凭证：

   ```bash
   export ABEVAL_HOME=/tmp/abeval-home
   mkdir -p "$ABEVAL_HOME"
   # minimal config.yaml + provider key, e.g. OpenRouter:
   cat > "$ABEVAL_HOME/config.yaml" <<'YAML'
   model:
     provider: openrouter
   YAML
   printf 'OPENROUTER_API_KEY=%s\n' "$KEY" > "$ABEVAL_HOME/.env"
   ```

运行时工具会为每次运行生成一个专属的 Relay `plugins.toml` 文件，并将原生 SDK 集成指向该文件；无需启用任何 Hermes 可观测性插件。

2. 准备这两个配置树：

   ```bash
   git worktree add /tmp/abeval-baseline origin/main
   # fixes tree = your integration branch checkout
   ```

## 运行

```bash
cd scripts/toolperf_abeval
export ABEVAL_ROOT=/tmp/abeval-workspace   # results + sandboxes land here
export ABEVAL_HOME=/tmp/abeval-home
./run_all.sh /tmp/abeval-baseline /path/to/fixes-tree 3 \
  "anthropic/claude-sonnet-4.5" "qwen/qwen3-coder-30b-a3b-instruct"
```

在原始电池供电的情况下，执行108次运行（2个模型 × 2种实验组设计 × 9项任务 × 3次重复）大约耗时2.5小时。可随时重新生成表格：

```bash
python3 ab_eval.py report --models "anthropic/claude-sonnet-4.5,qwen/qwen3-coder-30b-a3b-instruct"
```

## 查看结果

- 性能较弱的模型会表现出明显差异。而性能较强的模型通常能够在单轮内纠正大多数人为引入的错误，因此两者表现应基本相当；改进效果则体现为性能较弱模型的处理轮数、工具调用次数及错误数量有所减少。在2026年8月的测试批次中，qwen3-coder-30b模型的处理轮数减少了21%，工具调用次数减少了29%，错误数为0，推理时间也缩短了23%，而sonnet-4.5模型的表现则与前者基本持平。
- 当迭代次数n为3时，成功率的变化往往属于随机波动。在判定出现性能退化之前，应逐次检查所有成功率低于100%的测试案例（可通过查看`meta.jsonl`文件中的尾部数据来实现）。
- 评估机制能够揭示两种模型方案各自存在的缺陷——例如，最初的测试发现“隐藏文件搜索”功能仅在完全无匹配结果时才会被触发，该问题此后已在主版本中得到修复。

## 扩展功能

若需添加新任务，只需在`TASKS`（提示词）、`make_sandbox`（测试环境构建脚本）以及`SUCCESS`（自动化验证逻辑）这些文件中相应添加内容即可。验证规则应保持严格且标准化——仅依据预设的标记字符串及磁盘上的状态数据进行判断，切勿凭主观感觉行事。
