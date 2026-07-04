---
name: unbroker
description: Autonomously remove your info from data-broker sites.
version: 1.0.0
author: SHL0MS (github.com/SHL0MS)
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3]
metadata:
  hermes:
    tags: [privacy, data-broker, opt-out, ccpa, gdpr, security, doxxing]
    category: security
    related_skills: [google-workspace, agentmail, himalaya, scrapling, osint-investigation]
    homepage: https://github.com/NousResearch/hermes-agent
---

# unbroker

该工具可帮您查找个人信息（姓名、地址、电话、邮箱、亲属关系等）在数据经纪商及人物搜索网站上的暴露位置，进而将其删除——尽可能自动完成，仅在网站要求输入验证码、政府身份证明、接听电话或传真时才由人工指导操作。它能够独立处理多个人的信息。需要注意的是，该工具**无法绕过反机器人系统**，**不会在未经明确记录的同意情况下对任何人采取行动**，也不会删除公开记录（如选民信息、财产记录、法庭记录）或该人自己管理的账户。

Python命令行界面（`scripts/pdd.py`）负责管理所有核心状态——包括配置设置、个人档案与同意记录、经纪商数据库、分级处理计划、账本、草稿文件、报告，以及**邮件发送（SMTP）、验证链接轮询（IMAP）和自动操作队列（`next`）**。而您（即智能体）则可使用内置工具执行扫描和表单填写操作：`web_extract`和`browser_navigate`用于搜索和填写网页表单，`cronjob`则用于定期重新扫描。

## 自动化运行机制

该功能设计为**全程无人干预式运行**。在信息收集并获取明确记录的同意后，整个流程中仅有两个必要的人工介入环节：（1）信息收集时的对话环节，以及（2）运行结束后生成的汇总任务清单（`$

```bash
PDD="python3 scripts/pdd.py"
```

该引擎将数据存储在 `$PDD_DATA_DIR` 目录下（默认为 `$HERMES_HOME/unbroker`），权限设置为 `0600`。应通过 `terminal` 命令运行，**严禁使用 `execute_code`**——因为后者会创建沙箱环境并屏蔽输出，从而导致无法读取相关数据档案。

## 快速参考

| 命令 | 用途 |
|---|---|
| `$PDD setup --auto` | **自动配置**：自动检测系统能力，并自动选择最合适的完整配置方案（无需人工询问） |
| `$PDD doctor` | 准备状态检查：验证配置、代理数量以及哪些升级已应用或可用 |
| `$PDD cdp [--check] [--print] [--port N]` | 通过 CDP 启动/检测操作员的 Chrome 浏览器，用于处理第二阶段的浏览器及网页邮件相关任务（使用专用调试配置文件；这是发送网页邮件及清除会话绑定限制的可靠方式） |
| `$PDD intake --full-name "..." [--alias ...] [--email ... --phone ...] [--city --state] [--prior-location "City,ST"] --consent` | 创建已同意处理的对象记录；可收集别名、多个邮箱/电话号码以及之前的居住地信息，并输出 `subject_id` |
| `$PDD next <subject>` | **自动循环驱动器**：安排当前需执行的代理操作顺序、生成人工处理摘要，以及设置下一次唤醒时间 |
| `$PDD brokers [--priority crucial]` | 列出人员搜索代理数据库中的记录（包括已筛选和实时更新的条目） |
| `$PDD refresh-brokers` | 获取最新的 BADBOOL 人员搜索列表以及 CA 数据代理注册表信息（当缓存过期时，`next` 命令会自动重新获取这些数据） |
| `$PDD registry [--search NAME]` | 显示注册表覆盖情况（目前 CA 地区约有 545 个记录已被收录；VT/OR/TX 地区的端口也已接入）；此功能仅涵盖 DROP/邮件处理流程，不包含扫描结果 |
| `$PDD drop <subject> [--filed]` | **一次性法律操作工具**：通过一次 CA DROP 请求即可从所有已注册的代理处删除该对象记录；使用 `--filed` 参数可对此次操作进行记录 |
| `$PDD plan <subject> [--priority crucial]` | 显示每个代理的处理层级、方法、搜索向量以及需要公开的具体字段信息 |
| `$PDD plan <subject> --batch` | **简化视图模式**：显示账本状态，按下一步操作类型对代理进行分组（未扫描/已找到/间接关联/被阻止/处理中/已完成），合并归属关系集群，**优先展示“已找到”集群的父节点，并生成定制化的 `parent_playbook` 指南**，同时列出后续操作步骤 |
| `$PDD fanout <subject> [--priority crucial] [--size 5]` | 将多个代理批量分配给并行运行的 `delegate_task` 子代理（大规模处理时自动采用此模式；每组 5 到 8 个代理以上时会导致超时） |
| `$PDD record <subject> <broker> <state> [--found true] [--evidence JSON] [--disclosed F --channel C] [--reason "..."]` | 更新账本记录（基于经过验证的状态机机制）；**自动设置 `next_recheck_at` 时间** |
| `$PDD show <subject> <broker>` | 读取某个案例的已记录状态、相关证据及公开日志，便于上级在无需重新获取列表地址的情况下核实子代理的“已找到”结果 |
| `$PDD send-email <subject> <broker> --listing <url> [--kind ccpa_indirect ...]` | 生成并记录邮件请求（收件人地址固定为该代理自身的邮箱）。**浏览器模式**会返回一个可用于通过网页邮件发送的 `compose` 格式内容，无需输入密码；**程序化模式**则通过 SMTP 发送邮件 |
| `$PDD verify-link <subject> <broker> --text '<body>'` | **浏览器模式**：从您读取的网页邮件文本中提取代理的验证链接，并对其进行反钓鱼评分 |
| `$PDD poll-verification <subject> [--broker <id>]` | **程序化模式**：通过 IMAP 定期轮询验证链接，并进行反钓鱼评分；系统会自动将状态从“已提交”更新为“等待验证” |
| `$PDD render-email <subject> <broker> --listing <url>` | 仅生成邮件草稿（在未配置邮件发送功能时作为备用方案） |
| `$PDD due <subject>` | 显示那些已到达重新检查时间点的案例（即纳入定时扫描队列的案例） |
| `$PDD tasks <subject>` | 提供一份整合后的人工处理摘要（在任务运行结束后生成） |
| `$PDD status <subject>` | 以 Markdown 格式输出状态报告 |
| `$PDD report <subject> --sheets` | 为 Google Sheets 跟踪工具生成数据行 |

## 批量操作（两阶段：全面扫描，然后删除）

当需要处理的代理数量超过少数几个时，应采用 **map → reduce → act** 的流程，而非逐个处理代理：

- **第一阶段——发现（仅读取数据，并行执行，可重复执行）**。首先全面扫描所有代理，并为每个代理记录一个结果状态（`found`/`not_found`/`indirect_exposure`/`blocked`）。由于扫描操作不会产生任何副作用，因此可以安全地并行执行并重复尝试。在采取进一步行动之前先获取完整的暴露情况图谱，这是实现后续的集群去重和优先级排序的基础。**默认情况下，父代理会直接驱动 `web_extract` 探针进行扫描**——大多数人员搜索网站会将姓名、电话、地址等信息以静态 HTML 的形式呈现，`web_extract` 可在几秒钟内读取完毕。仅针对那些完全依赖 JavaScript 的少数网站才使用 `browser_*` 类型的探针，而对于那些真正需要复杂逻辑处理的任务（如大规模同名或亲属关系辨识），则使用 `delegate_task` 子代理。**切勿将大量代理列表交给浏览器工具类子代理去扫描**——在实际操作中，这种方式会因浏览器导航速度较慢而频繁超时（每次约 600 秒，最多处理 5-6 个代理，且无法生成汇总结果）；最终成功写入账本的数据所需时间往往是父代理 `web_extract` 操作的 10 倍。对于被阻止访问的网站（如 DataDome、Cloudflare 或带有反爬机制的网站），同样不应交给子代理处理：只需记录为 `blocked` 状态，然后重新安排任务，使用隐身浏览器或 Browserbase 工具进行再次尝试。子代理会自动生成报告，父代理则需要重新获取关键网址，确认确实找到目标后再予以信任（这种机制具有双向验证作用：既能避免将真实信息误判为误报，也能防止误删合法数据）。
- **归约阶段——`$

   ```
   while true:
     q = $PDD next <subject>
     if q.actions is empty: break
     execute EVERY action in order; record each outcome via $PDD record
   ```

`next`会按顺序触发以下操作：`refresh_brokers`（刷新过期缓存）、`fanout_scan`/`scan_inline`（第一阶段爬取——参见第4步）、`poll_verification`（处理正在发送中的邮件确认）、`verify_removal`（进行定期复查）、`optout_web_form`/`optout_email_send`（第二阶段，优先处理父母相关记录，并按照剧本步骤执行）、`indirect_email_send`以及`stealth_rescan`。仅由人工完成的工作不会以独立操作的形式出现，而是会被汇总到`q.human_digest`中。在`autonomy=full`模式下，系统会不间断地执行各项操作；而在`assisted`模式下，则需遵循`confirm_first`原则。

4. **扫描操作（在`next`指示时执行）。**对于`fanout_scan`：运行命令`$
