# Hermes 成就系统

> **随 Hermes Agent 一同提供。** 该功能最初由 [@PCinkusz](https://github.com/PCinkusz) 在 https://github.com/PCinkusz/hermes-achievements 中开发，后被整合至 `plugins/hermes-achievements/` 目录中，因此仪表板可直接自带此功能，并能同步更新以适配 Hermes 的新功能变化。上游仓库仍用于新徽章的开发和界面迭代。

当通过安装脚本安装或从源代码克隆 Hermes 后，首次启动 `hermes dashboard` 时，该插件会自动注册为仪表板的一个标签页，无需额外安装步骤。更多详情请参阅主文档中的[内置插件 → hermes-achievements](../../website/docs/user-guide/features/built-in-plugins.md)。

Hermes 仪表板的成就系统：基于真实的本地 Hermes 会话历史记录，生成可收集的、分等级的徽章。

![Hermes 成就系统仪表板](docs/assets/achievements-dashboard-hd.png)

截图中使用的是临时演示数据，用于展示完整的视觉效果。该插件默认会读取真实的本地 Hermes 会话历史记录。

> **更新通知（2026-04-29）：** 如果您是在今天之前安装的此插件，请升级到最新版本。成就扫描路径已经过重构，可显著加快加载速度（采用快照缓存和增量检查点扫描技术）。

> **分享卡片功能（2026-05-04，随 hermes-agent v0.4.0 同步发布）：** 已解锁的成就卡片现在配有“分享”按钮，可生成尺寸为 1200×630 像素的 PNG 分享卡片（基于客户端 Canvas 技术，无需后端支持，也不涉及网络传输），并提供下载和复制到剪贴板的功能。该卡片尺寸适用于 X/Twitter、Discord、LinkedIn 和 Bluesky 的链接预览框。

## 功能说明

Hermes 成就系统会扫描本地 Hermes 会话，并根据智能体的实际行为来解锁相应徽章，这些行为包括：

- 自主工具链使用
- 调试与恢复操作模式
- vibe-coding 文件编辑能力
- Hermes 原生技能、内存管理、定时任务及插件使用情况
- 网络研究与浏览器自动化操作
- 模型/提供者工作流程
- 周末或夜间使用等习惯模式

成就系统共有三种可见状态：

- **已解锁** — 已获得至少一个等级的徽章
- **已发现** — 已知存在该成就，可查看进度，但尚未获得
- **隐藏中** — 在 Hermes 检测到相关信号之前保持隐藏状态

大多数成就都是通过逐步完成特定行为来提升等级的：

```text
Copper → Silver → Gold → Diamond → Olympian
```

每张卡片都设有一个可折叠的**统计项**部分，当用户需要详细信息时，即可查看具体的监控指标或要求。

在版本 `0.2.x` 中，成就列表已扩展至60多项，其中包括各类模型/提供者徽章，例如**五模飞行家**、**多语言提供者**、**Claude密友**、**Gemini制图师**以及**开放权重探索者**。

## 示例

- 让他来做饭
- 工具链大师
- 红色文本鉴赏家
- 3000端口已被占用
- 这本应很快完成
- 再做一点小修改
- 技能工匠
- 记忆守护者
- 上下文巨龙
- 插件小妖精
- 洞穴认证者

## 安装

将代码克隆到您的Hermes插件目录中：

```bash
git clone https://github.com/PCinkusz/hermes-achievements ~/.hermes/plugins/hermes-achievements
```

在本地开发时，建议将代码仓库存储在其他位置，并通过符号链接的方式关联它：

```bash
git clone https://github.com/PCinkusz/hermes-achievements ~/hermes-achievements
ln -s ~/hermes-achievements ~/.hermes/plugins/hermes-achievements
```

接着重新扫描控制台插件：

```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

当作为用户插件安装时，虽然仪表板界面可以正常加载，但 Python 后端 API 路由不会被自动导入。只有将该插件与 Hermes 一起打包时，后端路由才会可用。

## 更新

如果您是通过 git 安装的：

```bash
cd ~/.hermes/plugins/hermes-achievements
git pull --ff-only
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

对于安装在 `~/.hermes/plugins/hermes-achievements` 目录下的用户自定义插件，只需重新扫描插件即可，因为 Python 后端路由不会被自动导入。如果您通过拉取 hermes-agent 仓库中的更新来升级内置插件，且该更新改变了后端路由或 `plugin_api.py` 文件，那么在拉取更新后需要重启 `hermes dashboard`。

截至 2026 年 4 月 29 日，强烈建议进行更新，因为扫描性能有了显著提升：去除了重复的 `/overview` 扫描路径；增加了 `/achievements` 的缓存快照；并对未发生变化的会话实现了增量检查点复用功能。

成就解锁状态存储在本地的 `state.json` 文件中，不会被 git 更新所覆盖。新成就会根据您现有的 Hermes 会话历史进行评估。成就 ID 是稳定的，不应随意更改，因为它们是用于标识解锁状态的键值。

Git 仓库中的版本发布会带有标签，例如：

```bash
git fetch --tags
git checkout v0.2.0
```

## 文件

```text
dashboard/
├── manifest.json
├── plugin_api.py
└── dist/
    ├── index.js
    └── style.css
```

## API

这些后端路由是为内置插件准备的。用户自行安装的版本虽然会加载其控制台界面，但不会自动导入 Python 后端路由。

相关路由位于以下路径下：

```text
/api/plugins/hermes-achievements/
```

端点：

```text
GET  /achievements
GET  /scan-status
GET  /recent-unlocks
GET  /sessions/{session_id}/badges
POST /rescan
POST /reset-state
```

## 开发

运行检查：

```bash
node --check dashboard/dist/index.js
python3 -m py_compile dashboard/plugin_api.py
python3 -m unittest tests/test_achievement_engine.py -v
```

## 许可证

MIT许可证
