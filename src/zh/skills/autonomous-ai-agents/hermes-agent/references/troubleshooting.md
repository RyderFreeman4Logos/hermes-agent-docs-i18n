# 故障排除

### 语音功能无法使用
1. 检查 `config.yaml` 文件中是否设置了 `stt.enabled: true`。
2. 确认服务提供商已正确配置：可通过 `pip install faster-whisper` 安装相应库，或设置 API 密钥。
3. 在网关端执行 `/restart` 命令；在 CLI 环境中则需退出程序后重新启动。

### 某些工具不可用
1. 运行 `hermes tools` 命令，检查当前平台是否已启用对应工具集。
2. 部分工具需要环境变量（请检查 `.env` 文件）。
3. 启用工具后执行 `/reset` 命令重置配置。

### 模型/服务提供商相关问题
1. 运行 `hermes doctor` 命令，检查配置文件及依赖项状态。
2. 使用 `hermes auth` 命令重新验证 OAuth 服务提供商的授权信息（或执行 `hermes auth add <provider>` 添加新提供商）。
3. 确认 `.env` 文件中包含正确的 API 密钥。
4. **Copilot 403 错误**：`gh auth login` 生成的令牌无法用于 Copilot API。必须通过 `hermes model` → GitHub Copilot 的专用 OAuth 设备码流程进行授权。

### 修改未生效
- **工具/技能**：执行 `/reset` 命令可启动包含更新后工具集的新会话。
- **配置更改**：在网关端执行 `/restart` 命令；在 CLI 环境中则需退出程序后重新启动。
- **代码更改**：重启 CLI 或网关进程。

### web_extract 显示过时页面（结果缓存问题）
`web_search`/`web_extract` 功能会对搜索结果进行 20 分钟的缓存处理（参见 PR #94618）。在缓存有效期内重复请求同一网址时，系统会直接从缓存中返回结果，这可能导致“网站更新内容未显示”的错觉。

以下内容会始终从实时源获取，不会被缓存：
- localhost / 127.0.0.1 / `*.local` / `*.localhost` / 单标签局域网主机名 / 私有IP地址段及链路本地IP地址段（开发服务器、热重载构建环境、Chat-GUI界面中的文件预览功能）
- 被`security.website_blocklist`规则匹配的URL地址
- 返回失败响应以及通过无密钥救援机制处理的响应

若需在公共互联网上测试网站（如Vercel/Netlify预览版、ngrok/cloudflared隧道连接、测试环境域名），则无需自动排除公共DNS解析——需在config.yaml文件中手动列出相关主机地址：

```yaml
web:
  cache_exempt_hosts:      # always fetched live; effective immediately
    - mysite.vercel.app
    - "*.ngrok-free.app"
    - mysite.dev           # suffix match: also covers preview.mysite.dev
```

普通工具：设置 `web.cache_ttl_minutes: 1`（单位：分钟）或 `web.cache_enabled: false` 即可完全禁用两种缓存机制。

### 技能未显示的原因
1. 运行 `hermes skills list` 命令——确认相关技能已安装；
2. 运行 `hermes skills config` 命令——检查平台是否已启用该技能；
3. 直接加载技能：使用 `hermes -s name` 命令（或该技能本身的 `/<name>` 斜杠命令）。

### 网关相关问题
请先查看日志以排查问题：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见网关问题：
- **通过 SSH 登出后网关关闭**：启用 linger 功能：`sudo loginctl enable-linger $USER`
- **关闭 WSL2 后网关关闭**：WSL2 需要在 `/etc/wsl.conf` 中设置 `systemd=true`，才能让 systemd 服务正常运行。若未设置此参数，网关将回退到 `nohup` 模式（会随会话关闭而终止）。
- **网关陷入崩溃循环**：重置故障状态：`systemctl --user reset-failed hermes-gateway`

### 各平台特定问题
- **Discord 机器人无响应**：必须在机器人的“特权网关意图”设置中开启**消息内容意图**。
- **Slack 机器人仅在私信中可用**：需订阅 `message.channels` 事件。若未订阅，机器人将忽略公共频道。
- **Windows 特有问题**（如 `Alt+Enter` 换行、WinError 10106 错误、UTF-8 BOM 配置及行尾格式问题），请参阅 `references/windows-quirks.md` 文档。

### 辅助模型无法正常工作
如果视觉处理、压缩、会话搜索等**辅助任务**静默失败，`auto` 提供商将无法找到对应的后端服务。此时需设置 `OPENROUTER_API_KEY` 或 `GOOGLE_API_KEY`，或为每个辅助任务单独配置对应的提供商：
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### “重置权限”/自动批准所有请求
请参阅 `references/security-privacy.md` 文档——清除“始终允许”的设置，无需调整 yolo 模式。

