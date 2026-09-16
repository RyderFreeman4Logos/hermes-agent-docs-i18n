# 浏览器使用模式基准测试

PR [#81958](https://github.com/NousResearch/hermes-agent/pull/81958) 中的 A/B 电池测试方案
（浏览器使用 CLI 3.0 模式，基于 @laithrw 对 #66476 的改进）：内置
`browser_*` 工具集与单一的 `browser_exec` 驱动程序进行对比，在实时多步骤网页任务中，以在相同准确率下完成的任务令牌数、工具调用次数以及实际耗时作为衡量标准。

## 设计思路

- **各测试组仅在工具树和配置上存在差异。** `base` 组从合并基准版本检出，运行内置的十二个 `browser_*` 工具；`pr` 组从目标分支检出，运行 `browser_exec`（`browser.backend: browser-use`）；`prns` 组则是去除了模式辅助函数摘要、仅保留标题信息的 `pr` 组（用于隔离摘要值）。每个测试组都会设置一个临时的 `HERMES_HOME` 环境变量；网页请求的凭证也会被移除，因此所有测试组都必须实际驱动浏览器运行。
- **任务通过预言机进行验证。** 针对 toscrape-family 类型的网站（内容稳定且无反爬机制），通过正则表达式预言机来验证最终结果。测试数据来自 `tasks/easy.json`（包含5种任务：价格查询、类别提取、计数/聚合、登录、分页处理）以及 `tasks/hard.json`（包含6种任务：全类别多页面爬取、五星评分聚合、JS动态渲染处理、登录序列操作、跨类别比较）。
- **支持任务续跑。** 在重新运行时，会跳过 `results/*.jsonl` 文件中已完成的测试单元（规则与 `scripts/toolperf_abeval` 相同）。
- **后端矩阵配置。** `orchestrate.py` 负责启动本地的无头 Chrome CDP；而 `orchestrate_cloud.py --backend nous-cloud|browserbase` 则会通过产品所使用的相同服务提供商，为每个测试单元配置真实的云浏览器环境。
## 运行

```bash
# arms are pinned checkouts — e.g. merge-base worktree vs your branch
export BUBENCH_BASE_TREE=/path/to/merge-base-tree
export BUBENCH_PR_TREE=/path/to/branch-tree
```

注意：自从 #81958 合并之后（同时 #85170 使得浏览器默认使用相应驱动程序），当前 main 分支在两个分支中都会使用 `browser_exec`。只有当 `BUBENCH_BASE_TREE` 被固定为 #81958 之前的版本树时，`base` 分支才会检测内置的 `browser_*` 工具集（最初的测试是使用该 PR 的合并基础工作树）。在今后针对新浏览器功能进行 A/B 测试时，请将 `base` 分支固定为正在测试的更改的合并基础版本——因为这两个分支本身是通用的。

```bash
google-chrome --headless=new --remote-debugging-port=9333 \
  --user-data-dir=/tmp/bubench-chrome --no-first-run --disable-gpu about:blank &

python3 orchestrate.py --tasks tasks/hard.json --reps 3     # 108 cells @ 2 models x 3 arms
python3 report.py results/results.jsonl
```

## 基准评分卡（2026年8月8日至10日，第#81958次运行——共204个单元格）

**困难任务电池测试，本地Chrome CDP**（每个单元格包含6项任务，每项任务执行3次；采用最终修正后的Oracle读取结果，无任何数据被排除）：

```
model      arm       ok  tok_mean  tok_med  calls  wall_s  vs base tok
opus4.8    base   18/18     64594    63776    4.1    25.2            —
opus4.8    pr     18/18     25934    25030    2.0    17.5         -60%
opus4.8    prns   18/18     25578    27934    3.2    23.7         -60%
kimi-k3    base   18/18     56464    53276    5.3    50.0            —
kimi-k3    pr     18/18     19230    16710    2.4    33.3         -66%
kimi-k3    prns   18/18     23099    21160    4.1    50.5         -59%
```

摘要裁剪：pr模式（搭配digest辅助工具）36/36次测试均通过，平均处理量为22,582个令牌；prns模式（仅头部信息）36/36次测试亦全部通过，平均处理量为24,339个令牌——3.4KB的固定摘要无需额外成本且还能稍作节省；而11KB的完整实时技能转储则不会带来任何优势。

**后端矩阵**（pr版本，相同任务）：

```
model      backend          ok  tok_mean  calls   wall
opus4.8    local-cdp     17/18     25934    2.0   17.5
opus4.8    nous-cloud    12/12     33330    2.8   33.8
opus4.8    browserbase    6/6      26712    2.2   23.2
kimi-k3    local-cdp     18/18     19230    2.4   33.3
kimi-k3    nous-cloud    12/12     22050    2.9   41.4
kimi-k3    browserbase    6/6      22121    2.8   35.2
```

**“轻松电池”第一轮测试**（共5项任务，每项重复3次，使用sonnet-5与qwen3-coder-30b模型；排除因provider噪声导致的无效运行后——即仅考虑原始聊天模板XML格式的数据，且无任何工具调用情况）：

```
model                     arm    ok     prompt  compl   total  calls  wall_s
claude-sonnet-5           base  15/15    39771    324   40095   2.7    16.5
claude-sonnet-5           pr    15/15    27482    509   27991   2.4    14.3
qwen3-coder-30b           base  13/14    59509    559   60068   5.7    21.5
qwen3-coder-30b           pr    10/11    57146   1616   58763   6.8    26.3
```

sonnet-5：在同等条件下可节省30%的Token消耗。qwen3-30b：效果一般——性能较弱的模型会因反复尝试执行代码而耗尽节省下来的资源。Token节省优势主要体现在多步骤任务中，且随着任务复杂度的增加而愈发显著；同时，性能更强的模型也能以更少的工具调用完成任务。

来自同一次运行的兼容性检测结果：Firecrawl的云浏览器支持精细的CDP WebSocket连接；而Camofox没有CDP接口——由于存在结构上的不兼容性，因此在#81958号版本中会自动回退到内置的工具集。

注意事项：仅适用于无反爬机制且无需处理复杂单页应用的toscrape系列网站；每个单元格内的任务数量n需≤3；在此数值范围内的成功率差异属于正常波动——在运行回归测试之前，应逐次检查成功率低于100%的单元格。

## 数据来源

最初的每次运行生成的`results*.jsonl`文件存储在 `/tmp/bu-bench/`（临时文件系统）中，却在2026年8月12日的主机重启时丢失。该目录中的测试框架、任务定义及汇总数据是从基准测试运行时的会话记录（会话编号`20260808_050008_5f615e`及工具调用历史）中完整恢复的；`single_run.py`/`orchestrate*.py`则是经过恢复后的脚本，其中已将原有的`/tmp/bu-bench`路径参数化。重新运行该测试套件即可生成新的每次运行数据。
