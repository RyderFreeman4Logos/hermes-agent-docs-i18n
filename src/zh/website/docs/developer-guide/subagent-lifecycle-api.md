---
title: Public Subagent Lifecycle API
sidebar_label: Subagent lifecycle API
---

# 公共子代理生命周期 API

插件无需导入 `tools.delegate_tool`、网关内部组件、TUI 状态或 `AIAgent` 相关字段，即可启动并管理新的 Hermes 子会话。该服务会从当前代理的轮次中自动确定其父代理，因此可在 CLI、网关、非交互式会话以及看板工作会话中正常使用。若在当前代理轮次之外尝试启动子代理，则会因“没有活跃的 Hermes 父会话”而失败。

```python
from agent.subagent_lifecycle import SubagentLaunchRequest

def launch_review(ctx):
    # Call from a plugin tool or hook while an agent turn is active.
    service = ctx.subagent_lifecycle
    handle = service.launch(SubagentLaunchRequest(
        goal="Review this change for regressions.",
        context="Only inspect the supplied repository.",
        role="leaf",
        correlation_id="review-42",
        allowed_toolsets=("file",),
    ))
    # Persist handle.to_dict() if desired.
    if service.wait(handle, timeout_seconds=2).timed_out:
        return handle.to_dict()
    return service.result(handle)
```

`SubagentHandle` 是可序列化的对象，其中包含带版本标识的、不可直接查看的能力信息。该对象可被传递给 `status`、`wait`、`cancel`、`result` 或 `reconnect` 函数使用；格式错误或被伪造的句柄将返回 `UNKNOWN`/`UNKNOWN_HANDLE`，且无法访问对应的子代理。

其稳定状态包括 `PENDING`、`STARTING`、`RUNNING`、`SUCCEEDED`、`FAILED`、`INTERRUPTED`、`CANCEL_REQUESTED`、`CANCELLED` 以及 `UNKNOWN`。

`cancel(handle, reason=...)` 是一种协作式操作：它会请求子代理在下一个安全的时机中断执行，并返回 `CANCEL_REQUESTED` 状态；只有在 `wait` 或 `result` 函数检测到终止状态后，才会确认任务已完成。终止状态下的结果具有不可变性、幂等性，长度限制为 32k 字符，不包含对话记录和内部推理过程，同时会附带一个稳定的结果哈希值。

该 API 实现了对异步执行过程的生命周期管理。子代理的创建与终止会使用与 `delegate_task` 相同的宿主管理路径，包括父工具的恢复、内存状态通知、序列化的 `subagent_stop` 回调处理、资源清理以及子代理相关成本的汇总。该 API 不会改变同步版的 `delegate_task` 工具、批量委托功能，也不会影响其网关或 TUI 显示界面。在初始实现中，元数据及终止状态结果会在内存中保留一小时。

当进程重新启动后，`reconnect` 函数将返回 `RECONNECT_UNAVAILABLE`，且不会启动新的子代理。此外，运行的 Python 线程也无法在进程退出后继续存活；调用方应将这些句柄视为因进程退出而中断的。

所有请求均会被强制拒绝：目标/上下文/元数据的大小存在上限，未知的工具集或范围过宽的工具集也会被直接驳回；此外，针对单个工具的限制、工作目录的覆盖设置以及单次启动的超时时间，在Hermes无法在不削弱隔离机制的前提下实现支持之前，同样会遭到明确拒绝。如需缩小允许使用的工具范围，可使用`allowed_toolsets`参数；同时，Hermes现有的“不安全工具”拦截机制仍会继续生效。
