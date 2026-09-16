# 异步报告渲染探针

用于桌面端异步完成报告的离线集成验证。该探针会首先生成模拟输出，再将其传递给真实的cron手动完成格式化器、进程通知格式化器、持久化传输模块以及SQLite数据库，随后读取实际数据行。浏览器则会加载生产环境下的水合脚本、运行时资源、SystemMessage功能以及桌面端CSS样式。整个过程无需使用任何模型、定时任务或用户配置。

操作方法：在已安装常规Python和npm依赖的仓库根目录下执行即可。

```sh
export HOME=$(mktemp -d)
export HERMES_HOME="$HOME/.hermes"
export ASYNC_REPORT_ARTIFACT_DIR=$(mktemp -d)
# If Chromium is installed outside the temporary HOME, set
# PLAYWRIGHT_BROWSERS_PATH to that installation's browser cache.
.venv/bin/python evals/desktop_bug_campaign/async-report-producer.py "$ASYNC_REPORT_ARTIFACT_DIR/producer.json"
node evals/desktop_bug_campaign/async-report-vite.mjs
# In another shell with the same environment:
node evals/desktop_bug_campaign/async-report-live.mjs before
node evals/desktop_bug_campaign/async-report-live.mjs after
```

Vite探针会绑定回环端口18164，验证完成后请将其停止。固定的基准水合状态源自提交记录`a688e7d5ff9aeaaa9c97d28c316467f89ab8c943`，其余所有渲染模块则采用当前检出版本。可通过对比生成的JSON数据与截图来确认差异：在验证前，cron/delegation/batch/legacy目录下的Markdown标题和表格均不存在，而在验证后则会出现；纯文本格式的结果依然保留，格式错误的邮件内容仍保持紧凑结构，而任务目标、上下文及转录内容的页脚路径则无法正常显示。批量任务中会存在多行格式的内容，这是因为生成工具并未对它们进行扁平化处理。

该功能属于生成工具与存储系统的集成以及实时的Chromium渲染功能，**并不**涉及定时执行、基于完成状态轮询的HTTP/WebSocket端到端测试、机器人聊天路由功能，也不包含原生macOS环境下的质量检测。这里的“process”情形指的是通过进程通知格式化器触发的异步委托事件，而非终端进程的完成事件。所有测试用例均为模拟生成的。
