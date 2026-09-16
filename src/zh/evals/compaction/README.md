# 情境压缩评估工具

该工具衡量情境压缩对*信息检索能力*的实际影响，而不仅仅是Token数量的变化。

## 功能说明

1. 接收一段真实的较长对话记录（JSON格式：`{"messages": [...]}`，采用聊天格式）。
2. 从即将被压缩删减的内容中生成一系列事实性检索问题
   （为保证结果可复现，这些问题会针对每段对话记录单独缓存）。
3. 使用矩阵中的每种压缩策略（当前默认策略、激进尾部策略、代码库风格策略等）
   对对话记录执行`ContextCompressor.compress()`压缩操作。
4. 对于每种策略，仅使用压缩后的情境向新的大语言模型提出检索问题，
   并将模型的回答与标准答案进行比对。
5. 生成评分报告：列出每种策略下的信息检索准确率与保留Token数量。

## 使用方法

```bash
# from repo root, venv active
python evals/compaction/runner.py \
    --transcript /path/to/lineage.json \
    --policies current,aggressive,floor10k \
    --questions 15 \
    --out evals/compaction/results/run1
python evals/compaction/report.py evals/compaction/results/run1
```

会话记录不会被持久化存储（因为其中包含真实的会话数据）。请将`--transcript`参数指向本地文件。有关期望的文件格式以及CI冒烟测试中使用的合成会话记录生成工具，可参考`fixtures.py`文件。

## 从真实会话生成会话记录（位于`scripts/`目录）

由于采用了压缩轮转机制，单个活跃会话的token数量通常不会超过约300K，但*调用链*（即父节点到子节点的链条）会保留完整的未压缩历史数据。这些脚本会将该历史数据重构为可用于评估的会话记录：

```bash
# 1. ALWAYS copy the DB first — never point at the live state.db
cp ~/.hermes/state.db /tmp/state_copy.db

# 2. Find big lineages (sessions with parent_session_id form chains), then:
python evals/compaction/scripts/reconstruct_lineage.py \
    /tmp/state_copy.db <root_session_id> /tmp/lineage.json

# 3. (optional) Replay a 500K prefix through one checkout's compressor and
#    dump before/after for the HTML viewer:
python evals/compaction/scripts/replay_lineage.py <checkout> /tmp/lineage.json out.json 500000
python evals/compaction/scripts/build_html_report.py <runs_dir> report.html
```

`reconstruct_lineage.py`会按时间顺序遍历整个后代树，通过内容哈希值去除重复的旋转复制行，剔除合成压缩产生的伪影（如摘要、待办事项快照），并通过`system_prompts`去重表来确定系统提示词（会话仅存储哈希值）。该工具生成的HTML报告会将前后文本对照显示，并用不同颜色标注压缩伪影。

## 区域范围检测

`test_region_scoping.py`会在文本的开头、中间和结尾部分设置检测点，验证在传统模式和精简模式下，摘要生成器接收的序列化轮次输入仅包含中间（已压缩）区域。可直接运行该脚本，也可通过pytest来执行。

## 策略配置

策略定义在`policies.py`中。每项策略对应`ContextCompressor`构造函数中的参数，以及构造后可设置的可选属性覆盖值（例如`tail_token_budget`）。新策略可添加至此文件——运行程序会根据名称自动加载这些策略。

## 备注

- 问题生成与评判均使用`agent.auxiliary_client.call_llm`功能（与压缩器使用的传输方式相同），因此相关工具需要配置好对应的提供者。这会消耗真实Token：约为（策略数量×问题数量）次回答调用，再加上一次生成和一次评判。
- 准确性评分采用2/1/0的规则（正确/部分正确/错误）；得分表会显示标准化后的百分比。评判者可以查看标准答案，而答题者则无法查看。
- `--also-uncompacted`参数可添加一个对照组，该组会基于完整的原始文本进行回答——以此作为召回率的参考上限。
