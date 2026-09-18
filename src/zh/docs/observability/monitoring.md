# 网关监控

针对Hermes网关守护进程，提供服务健康状态监控以及结构化的运行诊断功能，这些数据会通过OTLP/HTTP格式导出至操作员配置的端点（如OpenTelemetry Collector、DataDog或任何OTLP接收器）。

该层面在设计上不包含具体内容。它仅输出网关及cron任务的生命周期状态、平台连接器的健康状况，以及无具体内容的警告/错误诊断信息。它绝不会导出提示语、消息、工具参数或结果、任务名称、目标地址、调度时间表、原始错误信息、会话历史记录、使用分析数据、审计日志或详细的执行追踪信息。而任务/模型/工具的执行轨迹捕获功能则由Hermes内置的NeMo Relay SDK集成以及明确配置的Relay订阅器或导出器来处理，属于独立的监控层面。

## 会导出哪些内容

| 信号类型 | OTLP 路由 | 内容说明 |
| --- | --- | --- |
| 网关指标 | `/v1/metrics` | 包含 `hermes.gateway.up/state/busy/drainable/active_agents/background_work/background_delegations/restart_requested`，以及带有限定 `error_code` 属性的 `hermes.platform.up/degraded` 指标 |
| 健康状态/生命周期事件 | `/v1/traces` | 网关的生命周期状态转换（`starting -> running -> draining -> stopped`、`startup_failed`、退出状态），`gateway.health_snapshot` 数据，以及平台状态变化信息 |
| 诊断信息 | `/v1/logs` | 包含警告/错误类型网关事件的日志，这些日志具有固定内容，并且其子系统类型、严重程度、错误类别及错误代码等属性均受到限制；经过处理的日志消息不会被导出 |
| Cron 定时器指标 | `/v1/metrics` | 包含定时器的心跳信号与上次成功执行的时间间隔（若无法获取则不显示），来自定时器过时窗口机制的单调递增事件计数，正在运行中的任务数量，以及根据已保存的 `next_run_at` 值结合定时器的容错规则计算得出的逾期任务数量 |
| Cron 任务执行生命周期 | `/v1/traces` | 任务的持久状态（`claimed/running/completed/failed/unknown`），限定的来源类型与错误类别，经过哈希处理的任务密钥，若有时间戳则显示任务执行时长，而在定时器知晓任务结果时还会显示交付结果；处于终止状态的任务会触发“失败即刷新”机制，这可能导致任务完成时间延迟最多一秒 |
信号中会包含 `service.name`、版本号、监控模式以及安装 ID 的稳定单向哈希值，这样操作员便无需导出账户/配置文件信息或原始安装标识符，即可区分不同的实例。

`hermes.gateway.active_agents`、`hermes.gateway.background_work` 和 `hermes.gateway.background_delegations` 三者相互补充。`active_agents` 统计的是前台消息处理量、正在运行的定时任务以及 API 调用次数——即网关在关闭前仍需处理的任务量。而 `background_work` 则统计那些未被 `active_agents` 计入的离线任务，包括后台运行的 `delegate_task` 子代理、`terminal(background=true)` 进程以及看板工作进程；它的统计粒度为**任务级**——一组由 N 个子代理组成的并行任务会被视为 N 个独立任务，因此能够真实反映当前的并发子代理负载。`background_delegations` 仅统计异步委托的**单元数**（每个 `delegate_task` 的调度计为一个单元，一组并行任务也计为一个单元），用于与异步处理池的容量统计相匹配；若需了解资源占用压力，可将其与 `delegation.max_concurrent_children` 的值进行对比。若需获取每个实例的总活跃任务量，可将 `active_agents` 与 `background_work` 的数值相加；若要判断处理池是否已达到饱和状态，则应使用 `background_delegations`。

## 启用方式

```yaml
# config.yaml
monitoring:
  gateway_health_export:
    enabled: true
  export:
    otlp:
      enabled: true
      endpoint: http://collector-host:4318/v1/traces   # metrics/logs derive
      headers_env: {}   # header name -> ENV VAR NAME (values never stored)
```

随时查看代理的运行状态：

```bash
hermes monitoring status
```

OpenTelemetry SDK属于可选组件（可通过`pip install 'hermes-agent[otlp]'`安装），会在首次使用时延迟加载。即便缺少该SDK或端点不可用，网关仍能正常运行：指标收集与常规事件导出功能不会被启用，而终端触发的定时事件会触发最多持续一秒的有限失败开放式刷新尝试，从而降低最终数据丢失的风险。

无论是在systemd/launchd/s6监控环境下、容器中、tmux会话中，还是直接运行`hermes gateway run`命令时，其工作方式都完全一致：由于导出功能集成在网关进程内，主机上无需额外配置sidecar、代理或收集器。

## 导出至DataDog

运行客户自有的OpenTelemetry Collector并实现数据转发：

```yaml
# otel-collector config
receivers:
  otlp:
    protocols:
      http:
exporters:
  datadog:
    api:
      key: ${env:DD_API_KEY}
service:
  pipelines:
    metrics:   {receivers: [otlp], exporters: [datadog]}
    traces:    {receivers: [otlp], exporters: [datadog]}
    logs:      {receivers: [otlp], exporters: [datadog]}
```

将 `monitoring.export.otlp.endpoint` 指向收集器。警报应发送至 `hermes.gateway.up`、`hermes.platform.up` 以及 `hermes.platform.degraded` 这些主题。

## 泛型集群查询与警报

具体的语法取决于客户所使用的可观测性后端。以下示例采用了 PromQL 风格的表达式，并刻意避免了使用特定于厂商的路由规则、目标地址或客户资产信息。

建议根据不可见的 `service.instance.id` 资源属性对集群视图进行分组。已终止运行的进程无法生成自身的零值，因此每项部署都需要同时具备显式状态检测与缺失序列检测功能。

```promql
# Explicit gateway failure.
hermes_gateway_up == 0

# Box disappeared or stopped exporting. Choose a window longer than the
# configured export interval and collector retry allowance.
absent_over_time(hermes_gateway_up[5m])

# Locally owned bridge is explicitly down.
hermes_platform_up == 0

# Scheduler thread is stale even though the gateway may still be alive.
hermes_cron_scheduler_heartbeat_age_seconds > 180

# Ticker loops but has not completed a successful tick recently.
hermes_cron_scheduler_last_success_age_seconds > 300

# One or more jobs are beyond their existing scheduler grace window.
hermes_cron_jobs_overdue > 0

# Catch-up counter increased, proving at least one stale occurrence was
# collapsed and run once after a delay.
increase(hermes_cron_scheduler_catch_up_occurrences[15m]) > 0
```

定时任务执行生命周期的相关记录会以 `hermes.cron_execution` span 的形式呈现。此外，还可以基于诸如特定边界属性之类的条件来触发警报或生成事件。

```text
hermes.status = failed|unknown
hermes.delivery_outcome = failed|not_configured
hermes.error_class = auth_failed|rate_limited|timeout|network_error|
                     dispatch_failed|interrupted|empty_response|
                     invalid_config|unknown
```

推荐的运营商视图包括：

1. 每个 `service.instance.id` 显示一行数据，展示网关状态及已配置的本地平台状态；
2. 调度器心跳信息、上次成功时间间隔、正在运行任务数、逾期任务数以及需要补发的任务数量；
3. 仅以不可见的 `hermes.job_key` 作为键值的定时任务生命周期数据流；
4. 针对设备缺失、本地桥接器故障、调度器数据过时、定时任务执行失败/状态未知、投递失败以及逾期/需补发任务等不同情况分别设置警报。

警报阈值与路由规则应存储在部署专用的配置文件中。切勿仅仅为了提升仪表板的可读性，而添加任务名称、提示信息、输出内容、调度时间、目标地址、原始错误信息、配置文件名称或账户标识等信息。

## 发布验证场景

在正式接受某个部署版本之前，需通过实际的数据收集器和后端系统，对以下五种场景进行逐一测试与验证：

1. **定时任务执行成功**：观察任务状态从“已领取”变为“正在运行”再变为“已完成”，同时记录任务耗时及真实的投递结果；
2. **定时任务执行失败**：确认任务状态显示为“失败”，并识别出具体的错误类型，同时在解码后的 OTLP 数据包中不应存在任何原始异常信息或内容；
3. **定时任务执行中断**：在任务运行过程中停止对应的网关，随后重新启动该网关，观察其状态是否恢复为“未知”；
4. **本地桥接器故障**：中断某个本地连接器的工作，观察其状态变为“已中断”、“正在重试”或“严重故障”，并确认其恢复后的状态，同时验证其他未受影响的设备仍能正常运行；
5. **网关被强制终止**：终止某个测试用的网关，验证系统是否能检测到相关数据序列的缺失，随后重新启动该网关，确认其会恢复为相同的不可见实例标识。
Hermes Agent 所管理的 Relay 传输状态仍在监控范围内。对于其自身管理的任何共享连接平台状态，相应的独立网关或连接器服务仍具有权威性，且应通过自身的遥测路径来输出这些状态信息。

在各种场景下，都需要确认系统在恢复后信号与警报能够正常清除，其他相关项不受影响，收集器故障仍会保持“故障开启”状态，同时解码后的指标、时间跨度、日志以及资源属性均不应包含任何异常内容。

## 本地冒烟测试（无需 Docker）

```bash
# terminal 1: capture collector on :4318
python scripts/observability/otel_capture_collector.py \
  --host 127.0.0.1 --port 4318 --log /tmp/hermes_otel_capture.jsonl

# terminal 2: drive the real exporter through lifecycle transitions,
# a fatal platform, and a structured warning event, then flush
python scripts/observability/gateway_health_export_probe.py \
  --endpoint http://127.0.0.1:4318/v1/traces \
  --log /tmp/hermes_otel_capture.jsonl --wait 8
# exit 0 prints: {"requests": 6, "paths": ["/v1/logs", "/v1/metrics", "/v1/traces"]}
```

## 维护与扩展该词汇表

按照设计，此词汇表属于**固定、枚举且不包含任何内容的词汇表**。添加信号并非简单的“发布新指标”——每一个新的名称和属性都必须在所有强制使用该受限词汇表的层中进行声明，否则它们将会被 silently 忽略。请根据您要进行的更改遵循相应的检查清单。核心原则是：**如果某个新信号虽然已被发布，但未在所有层中声明，它看起来像是代码错误，但实际上属于词汇表注册问题——系统不会报错，该信号只是永远无法传递到位。**

### 无内容约束原则（适用于所有更改）

在添加任何内容之前，务必确认其不包含任何实际信息。数字、布尔值、年龄、持续时间、单调计数以及单向哈希值都是安全的。**绝对不要**添加可能存储任务名称、提示语、输出结果、调度信息、目标地址、原始异常文本、文件路径、配置文件名、账户编号或自由格式字符串的属性。当需要将记录与某个任务/实体关联时，应对该记录进行哈希处理（如 `sha256(...)[:24]`，参见 `agent/monitoring/cron_health.py` 中的 `_job_key`），而绝不能直接发送原始 ID。所有可能涉及用户输入的字符串属性都必须经过 `redaction.redact_for_export` 处理并被截断（参见 `agent/monitoring/otlp_exporter.py` 中的 `_span_attrs`）。

### 添加新的度量指标/计数器

1. 在快照生成工具中输出该指标（位于 `agent/monitoring/gateway_health.py` 的 `build_gateway_health_snapshot` 函数、`cron_health.py` 中的 `build_cron_health_snapshot` 函数，或 `gateway_health_export.py` 中与 `_read_runtime_snapshot` 相连的相应读取器）。最佳实践是：绝不能让任何读取器引发异常并进入数据收集循环——应对其异常并记录一条**不包含具体内容的警告信息，仅标注异常类型名称**（这与定时任务及后台工作读取器的处理方式一致），这样一旦出现功能退化问题就能被及时发现，而不会导致信号被悄悄丢弃。

2. 在 `gateway_health_export.py` 中的 `_start_metric_provider` 函数所定义的 `observable-gauge` 结构的 `metric_names` 列表中注册该指标的完整名称。**那些在快照中被输出但未在此处注册的指标将永远无法被监控到。**

3. 在该文件中添加对应的导出表格行及警报示例。

4. 如果部署环境在出口器之前使用了基于指标名称白名单的 OpenTelemetry Collector（即带有 `name != "..."` 规则的 `filter/...` 处理器），则需在该白名单中一并添加新指标的名称——否则该收集器会在数据传递到后端之前就将其丢弃。虽然这不属于代码仓库中的内容，但却是新指标虽已正确生成却始终无法显示的最常见原因；请在 Pull Request 中明确指出这一点，以便负责部署的人员及时更新其收集器配置。

### 添加新的子系统（即新的信号系列）

请按照cron模式进行结构设计（参考`cron_health.py`及其相关实现）：将读取/数据投影逻辑置于独立的模块中，提供一个`build_<subsystem>_health_snapshot()`函数，该函数返回限定范围内的`GatewayMetric`数据（以及可能存在的事件），并通过相同的尽力处理机制及try/except警告机制将其扩展为`_read_runtime_snapshot`函数。随后，针对每个新增的指标名称执行“添加指标”检查清单，针对每项新的事件属性执行“添加属性”检查清单。此外还需为该子系统的故障模式补充相应的发布验证场景。

### 扩展错误类型/状态/来源/状态值词汇表

这些是用于限定系统行为范围的封闭型枚举。应先扩展集合，再扩展分类规则，绝不能单独修改其中任意一项：

- **Cron任务**（位于`agent/monitoring/cron_health.py`）：包含 `_KNOWN_STATUSES`、_KNOWN_SOURCES`、_KNOWN_DELIVERY_OUTCOMES`以及`classify_cron_error`关键字分类桶。任何未列入该集合的值在输出时都会被强制标记为`unknown`，因此未被添加到集合中的新值将无法被识别。
- **网关/平台**（位于`agent/monitoring/gateway_health.py`）：包含 _KNOWN_GATEWAY_STATES`、_KNOWN_PLATFORM_STATES`以及`classify_gateway_error`。

相关规则如下：需保持词汇表规模较小且具有实际业务意义（错误类型应对应具体的操作动作，而非异常子类）；新的分类桶必须基于稳定的关键字进行匹配，而不能依赖可能变化的消息文本；需同时更新该文件警报部分中的`hermes.error_class = ...`列表以及对应的枚举单元测试，以确保契约得到验证，而非仅作为固定数值存在。

### 为现有事件/时间跨度添加无内容属性

需将该键添加到 `agent/monitoring/otlp_exporter.py::_span_attrs` 文件中，对应发射器针对各类数据的 `keep_by_kind` 允许列表中（未列出的键将被直接丢弃）；如果该键为字符串类型，则需先通过掩码处理功能。与指标处理方式类似，如果部署环境中的收集器拥有时间跨度属性的 `keep_keys(...)` 允许列表，也需将该键添加到其中，否则它在传输过程中会被移除。

### 需验证整个数据传输链，而不仅仅是发射环节

仅进行数据发射是必要的，但还不够。必须确认信号能够完整地传递到后端，因为枚举类型、`metric_names` 注册信息、发射器属性允许列表以及各类收集器允许列表都会在无错误的情况下自动丢弃未列出的值。

```bash
hermes monitoring status                 # posture
python scripts/observability/gateway_health_export_probe.py \
  --endpoint http://127.0.0.1:4318/v1/traces \
  --log /tmp/cap.jsonl --wait 8          # drive the real exporter
```

解码捕获到的 OTLP 数据包，确认新的名称/属性已正确添加，且不存在任何内容泄露。如果前面有真实的收集器存在，则需将其允许列表中的条目一并加入，再针对后端进行重新验证，而不仅仅依赖本地的捕获数据。

## 范围与发展路线

`hermes monitoring` CLI 故意仅暴露 `status` 状态信息。当前的首个版本仅涵盖由 Hermes Agent 管理的服务健康状况及运行诊断信号，包括 Hermes Agent 自身的中继传输健康状态。Team Gateway 的权威共享连接器/平台状态明确不在其覆盖范围内，产品分析、审计/质量报告以及详细的执行追踪功能也同样不在范围内。至于共享客户端使用指标和企业级追踪遥测数据，则将在获得相关方同意的前提下，通过 NeMo Relay 集成进行设计，同时会设定相应的策略和数据导出限制；这样的监控层面被严格限定，以便操作人员能够在不涉及任何包含业务内容的信号的情况下启用该功能。随着相关功能的完善，该遥测数据展示方式也可能会进行调整。
