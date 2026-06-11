# 压力测试/极限测试套件

这类长时间运行的测试旨在在恶劣环境下对 Kanban 核心功能进行压力测试。由于每项测试的运行时间可能超过30秒，且会启动真实的子进程，因此**不会通过 `scripts/run_tests.sh` 脚本自动执行**。

需手动运行：

```bash
./venv/bin/python -m pytest tests/stress/ -v -s
# or individual files:
./venv/bin/python tests/stress/test_concurrency.py
./venv/bin/python tests/stress/test_subprocess_e2e.py
./venv/bin/python tests/stress/test_property_fuzzing.py
./venv/bin/python tests/stress/test_benchmarks.py
```

## 测试内容概述

- **test_concurrency.py** — 5个工作进程，100个任务，采用竞争获取机制。旨在验证不会发生重复获取任务、孤立运行任务的情况，且SQLite错误不会导致任务重试失败。
- **test_concurrency_mixed.py** — 10个工作进程 + 1个任务回收进程，共500个任务，包含随机操作（获取/完成/阻塞/解锁/归档）。即使在恶劣的调度环境下也能保持相同的不变性。
- **test_concurrency_reclaim_race.py** — 设置任务的有效时间小于其处理时长，使任务回收进程在任务处理过程中故意将其取走；验证工作进程的延迟完成请求能被正确拒绝（CAS保护机制有效）。
- **test_subprocess_e2e.py** — 调度器会启动真实的Python子进程工作进程，这些进程通过CLI发送心跳信号并完成任务处理；同时会对实际已终止的进程ID进行崩溃检测。
- **test_property_fuzzing.py** — 生成500组随机操作序列，总计约4万次操作，每执行一步后都会进行9项不变性检查。
- **test_atypical_scenarios.py** — 包含28种异常用户输入场景：Unicode/表情符号/从右到左文本、1MB大小的字符串、SQL注入尝试、循环结构、自引用关系、宽扇入/扇出结构、时钟偏移问题、包含空格/Unicode字符或符号链接的HERMES_HOME路径、单个任务的1000次重复运行、进程间的幂等性键竞争、终端状态恢复尝试，以及包含异常JSON格式的仪表板REST接口测试。
- **test_benchmarks.py** — 测试任务调度、重算就绪状态检测、任务列表查询、工作进程上下文构建等功能在100个/1000个/10000个任务条件下的响应延迟。测试结果以JSON格式保存，便于后续进行回归差异分析。
