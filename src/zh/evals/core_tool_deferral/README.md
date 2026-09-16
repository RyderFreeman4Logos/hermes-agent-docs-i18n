# core_tool_deferral — 用于处理工具可见性变化的实时 A/B 测试框架

该功能是为 PR #97979 中的维护者电池组件设计的（即 tool_search 桥接层之后的核心工具延迟处理机制）。它通过从两个固定的代码版本中启动真实的进程内 `AIAgent` 实例，针对任意模型组合以编程方式评估任务结果——包括准确率、API 调用次数、token 使用量、处理时间以及桥接层调用次数等指标。

原始评估结果及完整数据可见于 `results/SUMMARY.md` 文件以及 PR #97979 的内容中（共进行了 288 次测试，使用的模型包括 gpt-5.6-terra / glm-5.3-flash / qwen3.8-27b）。

## 结构布局

- `tasks.py` — 14项任务的测试组合：每个延迟工具对应一项任务，支持多步骤执行（待办事项处理、GUI流程链）、长流程执行（session_search → 备份 → cron → 待办事项处理），并包含用于消除歧义的机制、仅基于“急切性”进行的控制策略，以及用于干扰虚假检测结果的元素。每项任务均配有固定测试环境、程序化评分系统（0–1分的分值评定）以及预设的用户回复内容。
- `worker.py` — 在独立的子进程中运行一个由“臂组、模型、任务、重复次数”构成的单元：包含临时的HERMES_HOME目录与工作空间，封闭式的环境设置（仅保留OPENROUTER_API_KEY），预置的会话数据库（目标对象与干扰项），确定性的桌面界面模拟组件（desktop_ui发射器与智能体回调函数），而在计算机使用/图像生成相关功能则通过注册表处理程序进行模拟。终端、文件、cron任务、进程及会话数据库均为真实存在。退出码3表示基础设施或配置错误（此类任务不会被评分）。
- `orchestrator.py` — 测试组合运行管理器：具备安全恢复功能，为每项任务设置时间限制，支持并行执行各单元任务，可对出错记录进行重试处理，并设有三重基础设施故障中止保护机制。
- `report.py` — 为每项任务生成统计表格，展示两种测试臂组的各项指标（得分差异、轮次数、令牌使用量、时间限制情况以及桥接调用次数），同时计算任务平均值，并对噪声与错误进行统计分析。

## 运行方式

```bash
# 1. Two plain checkouts pinned to the SHAs under test (never pip install -e)
git worktree add /tmp/abdefer-base <baseline-sha>
git worktree add /tmp/abdefer-pr   <pr-sha>

export ABDEFER_BASE_TREE=/tmp/abdefer-base
export ABDEFER_PR_TREE=/tmp/abdefer-pr
export OPENROUTER_API_KEY=...   # the only key the worker keeps

# 2. Smoke one cheap cell first
python3 worker.py base openai/gpt-5.6-terra config_grep_distractor 1 /tmp/smoke.json

# 3. Battery (per model; start with the STRONGEST model to validate variance)
python3 orchestrator.py openai/gpt-5.6-terra 3 --parallel=5
python3 orchestrator.py z-ai/glm-5.3-flash 3 --parallel=5
python3 orchestrator.py qwen/qwen3.8-27b   3 --parallel=5

# 4. Readout
python3 report.py
```

`ABDEFER_PYTHON`用于指定工作进程的解释器（默认为调度器的解释器）；`ABDEFER_RESULTS`则用于指定结果存储的根目录。

## 规范要求（源自readtool/session_search框架）

- 在启动任务前，需根据实时更新的OpenRouter列表核对模型标识符是否有效。
- 交互公平性：若智能体以纯文本形式提出问题结束当前轮次，工作进程将发送预设回复（最多2条，计入`user_roundtrips`统计）；否则所有需要进一步澄清的任务都会被不公平地记为0分，进而影响整体评估结果——最初的Terra运行实验正是因为此问题而被舍弃的。
- 分母统一规则：出现错误的运行任务得分计为0，并仍计入准确率的分母中，但不会被纳入效率指标的计算范围。
- 在得出最终结论前，需将评分差异较大的任务样本的评估周期从n=3延长至n=6。
- 对于发现率回归问题，应首先检查相同任务在基础组中的使用情况——因为即使“可见性”并非延迟回归现象，某些工具模型仍可能产生偏差。
- 在发布数据前，需对`*.transcript.json`文件中的异常数据项进行审核。

`results/`目录会被git忽略，仅`SUMMARY.md`除外——因为结果JSON文件可以重新生成，而最终评估结论才是需要保留的实质内容。
