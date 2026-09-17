# 事后分析工具：结合取证功能与实时A/B测试，助力修复1,393个Agent运行中的问题  

这些脚本用于生成跟踪问题#103563中的各项数据，以及该问题对应的13个PR中“独立评审（第二轮）”部分的内容。该工具分为两个模块：  

- **`forensics/`** 模块会读取Hermes `state.db`的副本（以及轮换后的`agent.log*`文件和git日志），并重新计算每次运行中的实际数据，包括资金流向、每次调用的缓存行为、嵌套委托超时情况、批量合并交付延迟、工具使用中的问题、`/goal`循环的行为，以及任务开启后的返工情况。该模块无需调用模型，也不依赖网络。  
- **`live_ab/`** 和 **`review_probes/`** 模块则通过本地模拟的提供者，测试实际代码路径（包括真实的`AIAgent`、调度器、评估器、扫描器及SDK），以此展示每项修复措施的实际效果。`run.py`脚本会针对一两个实际场景运行这些测试，并同步输出“通过”或“失败”的结果。`review_probes/`中的测试用例是由独立评审团队设计的，用于重现PR初始版本中的缺陷，而经过修复的代码版本必须能够通过这些测试。  

所有数据都会被标记为**观测值**（来自实际使用记录、日志或git数据）或**模拟值**（通过重建或回放得到的数据）。请勿将模拟值与观测值混为一谈；关于两者为何会出现重叠，可参考问题#103563的第5节说明。  

## 需求条件

- 包含虚拟环境（`.venv/bin/python`）的 Hermes 检查点。进行取证分析时无需使用 NeMo Relay，因为 `live_ab/cache_prefix_wire.py` 中的抓包操作本身就是由该运行环境完成的。
- 用于取证分析：需提供 `~/.hermes/state.db` 的**副本**（绝不能直接使用原始文件；可通过 `sqlite3 state.db ".backup copy.db"` 或在 Hermes 未运行时使用 `cp` 命令创建副本），可选地还需提供已轮换的 `~/.hermes/logs/agent.log*` 文件。
- 对于 `--live` 模式下的探测：需在 `HERMES_HOME` 中配置真实凭证（此类运行模式每次执行都会产生费用）。

## 取证分析：重新计算您所执行运行任务的各项指标数值

```bash
cd <hermes-checkout>
P=.venv/bin/python
# 1. cost buckets, depth/duration shares, context-size reconstruction, excess-cache-write proxy, cap replay
$P -m evals.postmortem.forensics.tokens     --db state_copy.db [--root <session_id>] [--cap 200000 --floor 65000]
# 2. per-call cache behaviour from the logs (coverage fraction is printed first; quote nothing without it)
$P -m evals.postmortem.forensics.logcalls   --db state_copy.db --logs "$HOME/.hermes/logs/agent.log*"
# 3. delegation: timeouts, orphaned children, polling, batch-join delay, truncated summaries
$P -m evals.postmortem.forensics.delegation --db state_copy.db
# 4. tool friction: hardline false blocks, foreground refusals, whole-file rewrites, output volume
$P -m evals.postmortem.forensics.tools      --db state_copy.db
# 5. /goal loop: nudges, parked barrier, notification counts
$P -m evals.postmortem.forensics.goal_loop  --db state_copy.db
# 6. rework inventory for a large PR (git only)
$P -m evals.postmortem.forensics.rework     --repo . --base <merge-base> --open <sha-at-open> --head <merged-sha>
```

每个组件都会生成 `postmortem_out/<lane>.json` 文件并输出摘要信息。`--root` 参数的默认值为拥有最多子节点的顶层会话；为确保成本分桶的独立性，经过压缩迭代的子节点不会被纳入统计范围。定价依据是 `estimated_cost_usd` 中的数值，因此显示的美元金额与 Hermes 记录的数据一致（该数值仅为估算值，并非正式账单）。

### 参考输出（运行编号 #102117，2026-09-04 的 `state_copy.db` 文件）

| 工作通道 | 输出内容 |
|---|---|
| 令牌使用情况 | `1394个会话，总费用为19,302.59美元`；缓存写入操作耗资11,159.76美元，缓存读取操作耗资3,587.17美元，输出操作耗资4,555.48美元；深度为2的节点占比65%，深度超过60分钟的节点占比61%；经过模型优化的过度缓存写入代理功能约需9,100美元；针对实际数据量设置锯齿形上限为20万，计算公式为：提示词数量 × 0.76（重建后的数据大小） |
| 日志调用情况 | 覆盖率为22,489/93,284，即24.1%；提示词的中位数值为229,648，第90百分位数值为408,794，超过20万次的提示词占比59%；命中率为93.9%；在未缓存输入数据中，有22.5%处于严格稳定状态，74.8%无进展；针对实际数据量设置锯齿形上限为20万，计算系数为0.498 |
| 任务委派情况 | 共有266个调度器；在234个嵌套会话中发生了332次任务委派超时现象；最终传递出了93个结果；首次超时后进入睡眠状态的时间为242.6小时；这些会话的总处理费用为4,034.69美元（包含实际处理工作所需费用）；220条摘要中有123条被截断；在批量合并过程中，根层级保留的子任务时长为233小时，深度为1的层级为300小时，深度为2的层级为52小时 |
| 工具调用情况 | 共进行了96,855次工具调用；其中579次属于硬限制拦截，归类为“格式错误”类型；有475次因前台超时而被拒绝调用（其中303次是因为请求处理时间超过900秒）；使用`&`符号启动的任务有185个，使用nohup命令启动的任务有24个；执行写文件操作的调用次数为8,188次，涉及数据量为9280万字符；在本会话中，有661次是对已读取的文件进行重写操作，且重写次数超过2万次；执行补丁应用的调用次数为4,623次 |
| 目标循环处理情况 | 共进行了5次提醒操作（其中2次发生在“等待”状态后的180秒内）；发出了34条批量处理通知；发出了48条后台进程处理通知；最终因`waiting_on_session=proc_…`这一条件，相关任务被暂停了201分钟 |
| 代码返工情况 | 在代码打开后，共发现1,703个标识符/341个模块，951个方法/156个类，126个测试定义/52个文件存在问题；在代码打开后共进行了125次提交操作，其中包括55次简化处理，39次审查修正，19次缺陷修复等操作 |
这两个锯齿状图表的设计意图有所不同：`tokens` 模型展示的是所有 93,000 次调用的*重建后*的单次调用数据量（系数为 0.76）；而 `logcalls` 模型则呈现日志中 24% 调用（即并发峰值时段，系数为 0.50）的*真实*单次调用数据量。相关问题报告也明确指出了这一点，并采用了第二种图表形式。

## 实时 A/B 测试：各修复方案的作用

```bash
# offline probes (fake providers, temp HERMES_HOME), main vs a branch or integration checkout:
.venv/bin/python -m evals.postmortem.run --repo /path/to/main --compare /path/to/branch
# add the probes that make real provider calls (cents):
.venv/bin/python -m evals.postmortem.run --repo /path/to/branch --live
# one PR only:
.venv/bin/python -m evals.postmortem.run --repo . --only 103492
```

| probe | PR | expects on the fixed head |
|---|---|---|
| `live_ab/hardline_scanner_matrix.py` | #103492 | 11-case matrix `ALL OK` (546-block class allowed; newline/`;`/`&&`/`|` hidden `reboot` blocked as itself) |
| `review_probes/scanner_bypass_probe.py` | #103492 | public guard `approved: False`, 0 callbacks, harmless Bash witness not executed |
| `live_ab/subagent_context_cap.py` | #103513 | child trigger `200,000` on a 1M model; parent untouched |
| `review_probes/context_cap_probe.py` | #103513 | cap holds through repeated compression + persistence; config validation |
| `live_ab/nested_delegate_deadline.py` | #103486 | 40 s deadline + 75 s leaf: result delivered (main: lost) |
| `review_probes/deadline_probe.py` | #103486 | same through actual dispatch |
| `live_ab/auth_stampede.py <repo> 40` | #103526 | `401s=0` (main: 40) |
| `review_probes/credential_identity_probe.py <repo> pr` | #103526 | explicit account-A key stays A (v1: became B) |
| `live_ab/batch_failure_notice.py` | #103549 | `TASK_FAILURE_NOTICE` at t+0.3 s, `BATCH_FINAL` after |
| `review_probes/notice_delivery_probe.py` | #103549 | gateway receives notice, notice, final; busy-parent final claim succeeds |
| `review_probes/cache_estimator_probe.py` | #103476 | preflight ≈ wire estimate; `should_compress` agrees |
| `live_ab/cache_prefix_wire.py <repo> B` (live) | #103476 | 0 mutated prefixes across 6 calls |
| `live_ab/goal_judge_wait.py <repo> 3` (live) | #103534 | `wait` ×3 on the run's "waiting on workers" response (main: `continue` ×3) |
| `review_probes/goal_scope_probe.py` | #103496/#103534 | judge sees own processes; delegation WAIT lifts on batch return |
| `review_probes/goal_repaste_probe.py` | #103553 | near-whole re-paste → pointer; `ship the API` ≠ `ship the UI` |
| `review_probes/rewrite_hint_probe.py` | #103551 | remote backend: no host-derived hint; FIFO: returns; 460 KB repeated-line file: skipped, not 22 s |
| `review_probes/finalizer_schedule_probe.py` | #103507 | pytest plugin: `-p evals.postmortem.review_probes.finalizer_schedule_probe --finalizer-probe=consumer-first` on `tests/e2e/test_relay_native_openai_stream.py` → 2 passed |

## 缓存并发检测工具（`live_ab/cache_concurrency_probe.py`）

该工具是 #104284 / #104421 以及 NousResearch/api#227 后面的实现核心。N 个并行运行的真实 `AIAgent` 会针对同一路由执行相同的循环检测逻辑；每次调用中的缓存读取/创建操作、响应编号、上游服务提供商信息以及前缀哈希值都会被记录下来，随后会对连续的检测结果进行分类——判定为“理想状态”、“卡住状态”（之前的写入内容无法被识别：路由问题）或“崩溃状态”（整个上下文都需要重新生成）。

```bash
# ~$50 per 20x6 arm on Fable 5.1 at the 5m tier
python -m evals.postmortem.live_ab.cache_concurrency_probe --repo . --provider nous --workers 20 --calls 6 --out /tmp/p.jsonl
python -m evals.postmortem.live_ab.cache_concurrency_probe --repo . --provider nous --wire native --workers 20 --calls 6 --out /tmp/p.jsonl
python -m evals.postmortem.live_ab.cache_concurrency_probe --repo . --provider openrouter --pin anthropic --workers 20 --calls 6 --out /tmp/p.jsonl
```

参考结果（2026-09-05/06）：Nous原生连接方式的失败率为13.9%（在4次测试中该比例始终介于14%至20%之间，且无论是否设置端口提供商固定值或等待2秒稳定时间，该比例均无变化）；Nous聊天连接方式的失败率为0/320；OpenRouter固定连接方式的失败率为0/161；而OpenRouter非固定连接方式的失败率则上升了9.8%。在切换`agent/nous_wire.py::GMI_NATIVE_WIRE_CLEARED`之前，可利用这些数据来清除新的上游连接。使用`--ttl 1h`参数可重现2倍写入价格的问题（#104168）。`.summary.json`文件中记录了存在问题的交易对及其对应的两个响应ID，便于提供商进行日志分析。

## 未包含的内容及原因

- **路径轨迹数据本身**。测试过程中的`state.db`文件中存储了51,956条绝对路径、5,341个电子邮件地址、私有IP地址、聊天/用户ID，以及工具输出中的真实格式API密钥和JWT令牌。这些数据无法公开，而且该测试工具的设计也无需公开此类数据——可直接在用户自己的数据库上运行。
- **人工分类结果**。在最初的审计中，72次返工提交的根本原因类别（符号丢失、语义漂移或兼容性问题）是由人工标注的；`forensics/rework.py`脚本仅能复现用于标注的原始数据列表，无法进一步处理。
- **汇总统计数据**。这是出于设计考量——每条测试路径都会单独显示对应的数值及相应说明。

## 证据文件包

原始测试报告、独立审查结果，以及该测试工具基于测试数据库重新计算出的JSON数据，均保存在#103563链接中的保密Gist文档中（其中不包含路径轨迹数据，详见“未包含的内容”部分）。

## 数据来源说明

取证分析模块：由五个并行运行的Hermes子代理组成（2026年9月4日版本），在此版本中已改用`--db`/`--root`参数来指定路径，而非硬编码路径。`live_ab/`目录用于存储主代理针对每个PR进行的A/B测试结果。`review_probes/`目录则存放独立的 `/review`子代理所生成的检测结果（2026年9月5日版本），该版本同样支持通过命令行指定路径；这些检测结果及对应的修复方案会显示在每个PR的“独立审查（第二轮）”板块中。
