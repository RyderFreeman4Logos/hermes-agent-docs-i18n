# 安全与隐私相关开关

常见的一些“为何Hermes会对我的输出/工具调用/命令执行X操作？”类开关，以及用于切换它们的具体命令。由于这些设置仅在启动时读取一次，因此大多数情况下需要重新启动会话（在聊天中输入`/reset`，或重新调用`hermes`）才能生效。

### 工具输出中的机密信息遮蔽

机密信息遮蔽功能**默认处于开启状态**——在工具输出（终端标准输出、`read_file`读取的内容、网页内容、子代理的摘要等）被纳入对话上下文和日志之前，系统会自动扫描其中可能包含的API密钥、令牌及机密信息。在正常使用情况下建议保持该功能开启：

```bash
hermes config set security.redact_secrets true       # keep enabled globally
```

**需要重启。** `security.redact_secrets` 会在导入时被生成快照——因此即便在会话进行中通过某些工具命令（如 `export HERMES_REDACT_SECRETS=false`）尝试切换其状态，也不会对正在运行的进程产生任何影响。应告知用户通过终端在配置文件中修改该设置，然后再启动新的会话。这样做是有意为之，旨在防止大型语言模型在处理任务过程中自行改变该设置。

仅在确实需要原始的凭证类字符串用于调试或编辑器开发时，才应将其禁用：
```bash
hermes config set security.redact_secrets false
```

### 网关消息中的个人身份信息脱敏

此功能与机密信息脱敏相互独立。启用该功能后，网关会在会话上下文数据传递给模型之前，先对其用户 ID 进行哈希处理，并删除其中的电话号码：

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### 命令审批提示

默认情况下（`approvals.mode: smart`），Hermes 会请求辅助大语言模型来评估那些被标记为具有破坏性风险的shell命令（如 `rm -rf`、`git reset --hard` 等）。可选的模式如下：

- `smart` — 对低风险命令自动批准，拒绝高风险命令，在不确定时向用户发起提示（默认模式）
- `manual` — 始终向用户发起提示
- `off` — 跳过所有审批提示（相当于 `--yolo`）

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

无需修改配置即可实现单次调用绕过限制：
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

注意：YOLO模式或`approvals.mode: off`设置并不会关闭敏感信息掩蔽功能，二者是相互独立的。

### “重置权限”/“让Hermes再次询问”

用户通常希望清除已累积的“始终允许”状态——而非更改YOLO模式，也不是取消每次编辑时的确认提示（此类功能并不存在；只有Shell命令执行时才会触发确认提示）。相关设置存储在两个位置：

1. Shell命令允许列表：`hermes config set command_allowlist '[]'`
2. Shell钩子同意设置（仅存在时有效）：`rm -f ~/.hermes/shell-hooks-allowlist.json`

随后需检查`hermes config get approvals.mode`的数值（不应为`off`），并确认启动别名或systemd服务单元中未预置`--yolo`参数。

### Shell钩子允许列表

某些Shell钩子集成在触发前需要明确列出允许执行的命令。相关设置通过`~/.hermes/shell-hooks-allowlist.json`管理，首次运行需要相关钩子时会进行交互式提示。

### 禁用Web/浏览器/图像生成工具

若希望完全阻止模型使用网络或媒体相关工具，可打开`hermes tools`并针对不同平台进行开关设置。更改将在下次会话时生效（可使用`/reset`命令重置）。工具列表详见`references/configuration.md`文件。

