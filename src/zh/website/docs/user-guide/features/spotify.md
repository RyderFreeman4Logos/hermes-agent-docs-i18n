# Spotify

Hermes 能够通过 Spotify 的官方 Web API 及 PKCE OAuth 方式直接控制 Spotify 的各项功能——包括播放、队列管理、搜索、播放列表、已保存的歌曲/专辑以及收听历史记录。访问令牌会存储在 `~/.hermes/auth.json` 文件中，一旦出现 401 错误便会自动刷新；每台设备只需登录一次即可。

与 Hermes 内置的 OAuth 集成（如 Google、GitHub Copilot、Codex）不同，Spotify 要求每位用户都必须注册自己的轻量级开发者应用。Spotify 不允许第三方发布可供任何人使用的公共 OAuth 应用。整个注册过程大约需要两分钟，`hermes auth spotify` 命令会为你提供详细指导。

## 先决条件

- 一个 Spotify 账户。**免费账户**即可用于搜索、播放列表、音乐库及活动查看功能；而播放控制功能（播放、暂停、跳过、拖动进度条、调节音量、添加到队列、传输歌曲）则需要**高级账户**。
- 已安装并正在运行的 Hermes Agent。
- 对于播放功能而言：需要有一台**处于活跃状态的 Spotify Connect 设备**——至少有一台设备（手机、电脑、网页播放器或音箱）上需打开 Spotify 应用，这样 Web API 才有对象可控制。如果没有任何活跃设备，系统会返回包含“无活跃设备”提示的 `403 Forbidden` 错误；请在任意设备上打开 Spotify 后再试。

## 设置步骤

### 一次性设置：使用 `hermes tools` 命令或首次运行时设置

这是最快的设置方式。只需运行以下命令：

```bash
hermes tools
```

向下滚动至 `🎵 Spotify`，按空格键将其开启，随后按 `s` 键进行保存。在首次运行 `hermes setup` / `hermes setup tools` 时也可通过相同操作来切换。Spotify 采用主动授权模式，因此在此处开启该功能后会执行与 `hermes tools` 相同的、基于提供程序的配置流程。

Hermes 会直接引导您进入 OAuth 授权流程——如果您还没有 Spotify 应用，它会实时指导您创建一个。完成这些步骤后，工具集便能一次性完成启用与身份验证。

如果您希望分步操作（或之后需要重新授权），可使用以下两步流程。

### 两步流程

#### 1. 启用工具集

```bash
hermes tools
```

打开 `🎵 Spotify` 功能并保存设置，当内联向导出现时直接关闭它（按 Ctrl+C）。工具集会保持开启状态，仅将身份验证步骤暂缓执行。

#### 2. 运行登录向导

```bash
hermes auth spotify
```

在完成第一步之后，这7个Spotify工具才会出现在智能体的工具集中——它们默认是关闭状态的，因此不想使用这些工具的用户无需在每次API调用时都上传额外的工具配置文件。

如果未设置`HERMES_SPOTIFY_CLIENT_ID`，Hermes会引导用户在线完成应用注册流程：

1. 在浏览器中打开`https://developer.spotify.com/dashboard`
2. 打印出需要填写到Spotify“创建应用”表单中的具体数值
3. 提示用户输入获取到的客户端ID
4. 将该ID保存到`~/.hermes/.env`文件中，以便后续运行时跳过此步骤
5. 直接进入OAuth授权流程

获得用户授权后，令牌会被存储在`~/.hermes/auth.json`文件中的`providers.spotify`字段下。当前激活的推理提供方不会因此改变——Spotify认证机制与您的LLM提供方是相互独立的。

### 创建Spotify应用（向导要求的填写内容）

打开控制面板后，点击**创建应用**并填写以下信息：

| 字段 | 值 |
|-------|------|
| 应用名称 | 任意名称（例如`hermes-agent`） |
| 应用描述 | 任意描述（例如`个人Hermes集成工具`） |
| 网站地址 | 保持空白 |
| 重定向URI | `http://127.0.0.1:43827/spotify/callback` |
| 使用哪种API/SDK？ | 勾选**Web API** |

同意条款后点击**保存**。在下一页面点击**设置**，复制**客户端ID**并将其粘贴到Hermes的提示语中。这就是Hermes唯一需要的值——PKCE机制无需使用客户端密钥。

### 通过SSH或在无界面环境中运行

如果已设置`SSH_CLIENT`或`SSH_TTY`，Hermes会在向导引导和OAuth授权阶段自动跳过浏览器打开步骤。只需复制控制面板地址以及Hermes输出的授权链接，在本地机器的浏览器中打开它们即可正常操作——远程主机上的HTTP监听端口仍为`43827`。若不通过SSH本地转发，笔记本电脑的浏览器将无法访问远程回环地址。

```bash
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

关于跳板机/堡垒机配置以及其他潜在问题（如 mosh、tmux 工具使用及端口冲突等），请参阅[通过 SSH 的 OAuth/远程主机配置](../../guides/oauth-over-ssh.md)。

## 验证

```bash
hermes auth status spotify
```

该功能会显示令牌是否存在以及访问令牌的过期时间。令牌刷新是自动进行的：每当任何 Spotify API 调用返回 401 错误时，客户端会立即更换刷新令牌并重试一次。由于刷新令牌会在 Hermes 重启后依然有效，因此只有当您在 Spotify 账户设置中撤销该应用的授权，或执行 `hermes auth logout spotify` 命令时，才需要重新进行身份验证。

## 使用方法

登录成功后，该智能体即可使用 7 种 Spotify 工具。您可以像平常一样与智能体交流，它会自动选择合适的工具和操作。为获得最佳使用体验，智能体会加载一个辅助技能，指导标准的操作方式（如先搜索再播放、何时无需预先调用 `get_state` 等）。

```
> play some miles davis
> what am I listening to
> add this track to my Late Night Jazz playlist
> skip to the next song
> make a new playlist called "Focus 2026" and add the last three songs I played
> which of my saved albums are by Radiohead
> search for acoustic covers of Blackbird
> transfer playback to my kitchen speaker
```

### 工具参考

所有用于控制播放内容的操作都支持可选的 `device_id` 参数，以便指定目标设备。如果未提供该参数，Spotify 将使用当前活跃的设备。

#### `spotify_playback`
用于控制及查看播放状态，同时可获取近期播放历史记录。

| 操作 | 功能 | 是否需要高级版？ |
|------|------|----------------|
| `get_state` | 获取完整的播放状态（歌曲、设备、播放进度、随机播放/循环模式） | 否 |
| `get_currently_playing` | 仅返回当前正在播放的歌曲（返回 204 状态码时为空，详见下文） | 否 |
| `play` | 开始或继续播放。可选参数：`context_uri`、`uris`、`offset`、`position_ms` | 是 |
| `pause` | 暂停播放 | 是 |
| `next` / `previous` | 跳过当前歌曲 | 是 |
| `seek` | 跳转至指定毫秒位置的播放点 | 是 |
| `set_repeat` | 设置循环模式，可选值：`state` = `track` / `context` / `off` | 是 |
| `set_shuffle` | 设置随机播放模式，可选值：`state` = `true` / `false` | 是 |
| `set_volume` | 设置音量，范围为 0-100 的百分比 | 是 |
| `recently_played` | 获取最近播放过的歌曲。可选参数：`limit`、`before`、`after`（以 Unix 毫秒为单位） | 否 |

#### `spotify_devices`
| 操作 | 功能 |
|------|------|
| `list` | 列出账户下所有可连接的 Spotify Connect 设备 |
| `transfer` | 将播放内容转移到指定的 `device_id` 设备。可选参数：`play: true` 表示在转移过程中立即开始播放 |

### 由 Home Assistant 管理的音箱

如果 Home Assistant 管理着已支持 Spotify Connect 的音箱（例如 Sonos、Echo、Nest 或其他具备连接功能的音箱），只要 Spotify 能检测到这些设备，它们就会自动出现在 `spotify_devices list` 的列表中。对于这类场景，Hermes 不需要额外的 Home Assistant ↔ Spotify 中转组件——Spotify 本身即可完成设备路由。

可以通过音箱的显示名称来指令 Hermes 转移播放内容（例如“将播放内容转移到厨房的音箱”），或者在编写脚本时调用 `spotify_devices list` 并将具体的 `device_id` 传递给 `spotify_devices transfer` 函数。如果某个音箱未出现在列表中，只需打开 Spotify 应用或该音箱的 Spotify 集成一次，让 Spotify 将其注册为活跃的连接目标即可。

#### `spotify_queue`
| 操作 | 功能 | 是否需要高级版？ |
|------|------|----------------|
| `get` | 获取当前队列中的歌曲 | 否 |
| `add` | 将指定的 `uri` 添加到队列中 | 是 |

#### `spotify_search`
用于在音乐库中搜索内容。必须提供 `query` 参数。可选参数包括：`types`（歌曲/专辑/艺术家/播放列表/节目/剧集的数组）、`limit`、`offset`、`market`。

#### `spotify_playlists`
| 操作 | 功能 | 必需参数 |
|------|------|----------|
| `list` | 获取用户的播放列表 | — |
| `get` | 获取某个播放列表及其包含的歌曲 | `playlist_id` |
| `create` | 创建新播放列表 | `name`（可选参数：`description`、`public`、`collaborative`） |
| `add_items` | 向播放列表中添加歌曲 | `playlist_id`、`uris`（可选参数：`position`） |
| `remove_items` | 从播放列表中删除歌曲 | `playlist_id`、`uris`（可选参数：`snapshot_id`） |
| `update_details` | 重命名或修改播放列表信息 | `playlist_id` 及 `name`、`description`、`public`、`collaborative` 中的任意一个参数 |

#### `spotify_albums`
| 操作 | 功能 | 必需参数 |
|------|------|----------|
| `get` | 获取专辑的元数据 | `album_id` |
| `tracks` | 获取专辑的歌曲列表 | `album_id` |

#### `spotify_library`
提供对已保存歌曲和已保存专辑的统一访问功能。可通过 `kind` 参数选择要操作的集合。

| 操作 | 功能 |
|------|------|
| `list` | 分页显示库中的内容 |
| `save` | 将指定的 `ids`/`uris` 添加到库中 |
| `remove` | 从库中删除指定的 `ids`/`uris` |

必需参数：`kind` = `tracks` 或 `albums`，以及 `action` 参数。

### 免费版与高级版的功能对比

仅读类工具在免费账户上即可使用。而任何会修改播放内容或队列顺序的操作都需要高级版权限。

| 免费账户可用 | 需要高级版 |
|--------------|------------|
| `spotify_search`（所有搜索功能） | `spotify_playback`——播放、暂停、下一首、上一首、跳转播放点、设置循环模式、设置随机播放模式、设置音量 |
| `spotify_playback`——获取播放状态、当前播放歌曲、近期播放历史 | `spotify_queue`——添加歌曲到队列 |
| `spotify_devices`——列出设备 | `spotify_devices`——转移播放内容到其他设备 |
| `spotify_queue`——获取队列内容 |  |
| `spotify_playlists`（所有操作） |  |
| `spotify_albums`（所有操作） |  |
| `spotify_library`（所有操作） |  |

## 定时播放：Spotify + cron

由于 Spotify 相关工具属于常规的 Hermes 工具，因此可以在 Hermes 会话中通过 cron 任务来设定任意时间点的播放计划，无需编写新代码。

### 早晨唤醒播放列表

```bash
hermes cron add \
  --name "morning-commute" \
  "0 7 * * 1-5" \
  "Transfer playback to my kitchen speaker and start my 'Morning Commute' playlist. Volume to 40. Shuffle on."
```

每周工作日的上午7点，系统会自动执行以下操作：
1. Cron任务启动一个无界面的Hermes会话。
2. Agent读取指令后，首先调用`spotify_devices list`按名称查找“厨房音箱”，随后依次执行`spotify_devices transfer`、`spotify_playback set_volume`、`spotify_playback set_shuffle`、`spotify_search`以及`spotify_playback play`等操作。
3. 音乐便会在目标音箱中开始播放。整个流程仅需一个会话及几次工具调用，无需人工干预。

### 夜间关机流程

```bash
hermes cron add \
  --name "wind-down" \
  "30 22 * * *" \
  "Pause Spotify. Then set volume to 20 so it's quiet when I start it again tomorrow."
```

### 常见注意事项

- **Cron 任务触发时必须存在正在使用的设备。** 如果没有 Spotify 客户端正在运行（手机、电脑或 Connect 扬声器），播放操作将会返回 `403 no active device` 错误。对于用于早晨播放的播放列表，建议选择始终处于开机状态的设备（如 Sonos、Echo 或智能音箱），而非手机。
- **任何涉及修改播放状态的操作——包括播放、暂停、跳过、调整音量以及传输歌曲——都需要高级订阅权限。** 仅用于读取数据的 Cron 任务（例如定时发送“最近播放的歌曲列表”给邮箱）在免费版中即可正常使用。
- **Cron 代理会继承您当前启用的工具集。** 若要在 Cron 任务中使用 Spotify 相关功能，必须先在 `hermes tools` 中启用 Spotify 工具。
- **Cron 任务会以 `skip_memory=True` 的参数运行**，因此不会向您的记忆存储空间写入数据。

完整的 Cron 使用指南请参阅：[Cron 任务](./cron)。

## 登出

```bash
hermes auth logout spotify
```

该操作会从 `~/.hermes/auth.json` 中移除令牌。若同时要清除应用配置，请从 `~/.hermes/.env` 中删除 `HERMES_SPOTIFY_CLIENT_ID`（如果已设置 `HERMES_SPOTIFY_REDIRECT_URI`，也请一并删除），或再次运行向导。

若要在 Spotify 端撤销该应用权限，请访问 [与您账户关联的应用](https://www.spotify.com/account/apps/) 并点击 **REMOVE ACCESS**。

## 故障排除

**`403 Forbidden — Player command failed: No active device found`** — 您需要在至少一台设备上运行 Spotify。请在手机、桌面端或网页版 Spotify 应用中打开应用，播放任意歌曲约一秒以完成设备注册，然后再试。使用 `spotify_devices list` 可查看当前已检测到的设备。

**`403 Forbidden — Premium required`** — 您使用的是免费账户，却试图执行会改变播放内容的操作。请参考上文的功能列表。

**`get_currently_playing` 请求返回 `204 No Content`** — 表示当前所有设备上均无正在播放的内容。这是 Spotify 的正常响应，并非错误；Hermes 会以空结果的形式给出说明（`is_playing: false`）。

**`INVALID_CLIENT: Invalid redirect URI`** — 您在 Spotify 应用设置中填写的重定向地址与 Hermes 使用的地址不一致。默认值为 `http://127.0.0.1:43827/spotify/callback`。请将该地址添加到应用允许的重定向地址列表中，或是在 `~/.hermes/.env` 中将 `HERMES_SPOTIFY_REDIRECT_URI` 设置为实际注册的地址。

**`429 Too Many Requests`** — 这是 Spotify 设置的请求频率限制。Hermes 会显示友好的错误提示，建议等待一分钟后再试。如果问题依旧存在，可能是您的脚本中存在循环逻辑过于频繁——Spotify 的配额大约每 30 秒重置一次。

**不断出现 `401 Unauthorized` 错误** — 您的刷新令牌已被撤销（通常是因为您从账户中移除了该应用，或该应用已被删除）。请再次运行 `hermes auth spotify` 命令。

**向导无法自动打开浏览器** — 如果您是通过 SSH 连接，或处于没有显示设备的容器环境中，Hermes 会检测到这种情况并跳过自动打开浏览器的步骤。请复制向导输出的仪表板地址，手动打开该页面。

## 高级用法：自定义权限范围

默认情况下，Hermes 会为所有已发布的工具请求所需的权限范围。如需限制访问权限，可进行自定义设置：

```bash
hermes auth spotify --scope "user-read-playback-state user-modify-playback-state playlist-read-private"
```

权限范围参考：[Spotify Web API 权限范围](https://developer.spotify.com/documentation/web-api/concepts/scopes)。如果申请的权限范围少于某个工具所需，该工具的请求将会因 403 错误而失败。

## 高级功能：自定义客户端 ID / 重定向 URI

```bash
hermes auth spotify --client-id <id> --redirect-uri http://localhost:3000/callback
```

或者将它们永久性地设置在 `~/.hermes/.env` 文件中：

```
HERMES_SPOTIFY_CLIENT_ID=<your_id>
HERMES_SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

在您的 Spotify 应用设置中，必须将重定向 URI 加入允许列表。默认设置几乎适用于所有情况——只有当端口 43827 被占用时才需要对其进行修改。

## 文件位置

| 文件 | 内容 |
|------|------|
| `~/.hermes/auth.json` → `providers.spotify` | 访问令牌、刷新令牌、有效期、权限范围以及重定向 URI |
| `~/.hermes/.env` | `HERMES_SPOTIFY_CLIENT_ID`，可选的 `HERMES_SPOTIFY_REDIRECT_URI` |
| Spotify 应用 | 由您在 [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) 上创建；其中包含客户端 ID 以及重定向 URI 的允许列表 |
