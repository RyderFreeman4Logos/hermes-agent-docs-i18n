# 故障排除

### 语音功能无法使用
1. 检查 `config.yaml` 文件中是否设置了 `stt.enabled: true`。
2. 确认服务提供商已正确配置：执行 `pip install faster-whisper` 或设置 API 密钥。
3. 在网关端执行 `/restart` 命令；在 CLI 环境下则需退出当前进程后重新启动。

### 某些工具不可用
1. 运行 `hermes tools` 命令，检查对应平台是否已启用该工具集。
2. 部分工具需要环境变量（请查看 `.env` 文件）。
3. 启用工具后执行 `/reset` 命令。

### 模型或服务提供商相关问题
1. 运行 `hermes doctor` 命令，检查配置及依赖项状态。
2. 使用 `hermes auth` 命令重新认证 OAuth 服务提供商（或执行 `hermes auth add <provider>`）。
3. 确认 `.env` 文件中包含正确的 API 密钥。
4. **Copilot 403 错误**：`gh auth login` 生成的令牌无法用于 Copilot API。必须通过 `hermes model` → GitHub Copilot 的专用 OAuth 设备码流程进行认证。

### 修改未生效
- **工具/技能问题**：执行 `/reset` 命令可启动包含更新后工具集的新会话。
- **配置更改问题**：在网关端执行 `/restart` 命令；在 CLI 环境下则需退出当前进程后重新启动。
- **代码更改问题**：重启 CLI 或网关进程。

### 技能未显示
1. 运行 `hermes skills list` 命令，确认相关技能已成功安装。
2. 使用 `hermes skills config` 命令，检查对应平台是否已启用该技能。
3. 可通过明确指定名称来加载技能：执行 `hermes -s name` 命令（或使用该技能自身的 `/<name>` 斜杠命令）。

### 网关相关问题
请先查看日志以获取故障线索：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见网关问题：
- **通过 SSH 登出后网关崩溃**：启用 linger 功能：`sudo loginctl enable-linger $USER`
- **关闭 WSL2 后网关崩溃**：WSL2 需要在 `/etc/wsl.conf` 中设置 `systemd=true`，才能让 systemd 服务正常运行。若未设置，网关将回退到 `nohup` 模式（会随着会话关闭而终止）。
- **网关陷入崩溃循环**：重置故障状态：`systemctl --user reset-failed hermes-gateway`

### 平台特定问题
- **Discord 机器人无响应**：需在机器人的“特权网关意图”设置中启用**消息内容意图**。
- **Slack 机器人仅在私信中可用**：必须订阅 `message.channels` 事件。否则，机器人将忽略公共频道。
- **Windows 特有问题**（如 `Alt+Enter` 换行、WinError 10106 错误、UTF-8 BOM 配置及行尾格式问题），请参阅 `references/windows-quirks.md` 文档。

### 辅助模型无法正常工作
如果视觉处理、压缩、会话搜索等**辅助任务**静默失败，`auto` 提供商将无法找到对应的后端服务。此时需设置 `OPENROUTER_API_KEY` 或 `GOOGLE_API_KEY`，或为每个辅助任务单独配置对应的提供商：
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### “重置权限”/自动批准所有请求
请参阅 `references/security-privacy.md` —— 清除“始终允许”的设置，无需调整“即拍即过”模式。

