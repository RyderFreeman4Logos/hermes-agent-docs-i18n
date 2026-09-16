# Read-Tool 评估工具

这是一种 A/B 对比测试工具，用于衡量 `read_file` 相关设计决策对实际智能体运行性能的影响。该工具的灵感来源于 Command Code 在 2026 年 8 月发布的关于 read-tool 的分析文章——该文章对比了十种处理恶意文件的测试工具，但其中关于 Hermes 的描述存在多处错误（实际上我们早已实现了行级长度限制、意图猜测功能、笔记本/Docx/Xlsx 文件提取、PDF 转换以及设备路径黑名单等功能）。本次评估通过真实的 `AIAgent` 对实际运行场景进行测试，而非依赖任何第三方提供的能力列表。

## 评估内容

每个任务都会让完整的 Hermes 智能体（包含文件处理、终端操作及搜索工具集）在一个固定的恶意工作环境中执行任务：

| 测试用例 | 文件特征 | 测试任务 |
|---|---|---|
| `package-lock.json` | 共 80,000 行，大小 2.7MB——存在令牌陷阱 | `lockfile_version` |
| `src/app.min.js` | 包含一条 600KB 长度的正则匹配内容 | `minified_backoff` |
| `logs/server.log` | 共 150,000 行，文件末尾附近有一处 ERROR 日志 | `log_error_hunt` |
| `data/report.txt` | 共 412 行——用于测试 EOF 后的行为 | `past_eof` |
| `config/overrides.yaml` | 空文件 | `empty_config` |
| `notes/Meeting…PM.txt` | 文件名包含 NFD 编码、U+202F 及 U+2019 特殊字符 | `unicode_filename` |
| `AGENTS.md` 与 `AGENT.md` | 文件名仅存在细微差异 | `near_miss_filename` |
| `logs/live.pipe` | FIFO 队列结构——会阻塞简单的读取操作 | `fifo_hang` |
| `data/data.txt` | 文件名为 .txt，但实际上内容为 PNG 图片字节 | `lying_extension` |
每项任务的指标包括：**准确率**（基于预设真实值，通过子串/正则表达式评估器计算得出）、**API调用次数**、**工具调用次数**、**文件读取调用次数**、**总token数**以及**wall_s**。效率汇总值均为各项任务的平均值，而非总和。

## 运行方式

```bash
# Baseline (3 reps, both models)
python3 evals/readtool/runner.py --model anthropic/claude-opus-4.8 \
    --provider openrouter --reps 3 --label baseline
python3 evals/readtool/runner.py --model qwen/qwen3.8-max \
    --provider openrouter --reps 3 --label baseline

# After a feature change, re-run with a new label:
python3 evals/readtool/runner.py --model qwen/qwen3.8-max \
    --provider openrouter --reps 3 --label feat-stat-guard

# Compare
python3 evals/readtool/report.py --labels baseline feat-stat-guard
```

**评估规则（源自 hermesbench 的规范）：**

- 至少需进行 **3 次重复测试**；单次测试的误差在 ±3% 范围内属于正常波动，不能视为有效结果。
- 在测试运行过程中严禁修改 `tools/` 目录——测试工具会自动加载最新的模型结构。
- 有意使用两种模型：一种是为应对粗糙输入而设计的边界模型（opus），另一种则是能充分体现模型质量的优秀开源模型（qwen-max）。即便某项特性仅对 qwen 有效，也会被计入统计——因为强化训练正是针对这类模型群体而言的。
- 出现错误的测试任务将得分为 0，虽仍会计入准确率的分母，但不会被纳入效率指标的计算中。

## 结果展示格式

```
results/<label>/<model_slug>/rep<N>.json
```

除用于记录每个被评估功能的测试结果及对应数值的 `SUMMARY.md` 文件外，`results/` 目录均会被 Git 忽略。
