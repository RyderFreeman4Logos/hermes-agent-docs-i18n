---
title: "Oss Forensics — GitHub supply-chain forensics: recovery, IOCs, reporting"
sidebar_label: "Oss Forensics"
description: "GitHub supply-chain forensics: recovery, IOCs, reporting"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# OSS 安全取证

GitHub 供应链取证：数据恢复、威胁指标提取与报告生成。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/security/oss-forensics` 命令安装 |
| 路径 | `optional-skills/security\oss-forensics` |
| 版本 | `1.0.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `安全`、`取证`、`GitHub`、`供应链` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，Agent 就会依据这些内容执行操作。
:::

# OSS 安全取证技能

一种用于调查开源软件供应链攻击的七阶段多 Agent 调查框架。
该框架借鉴了 RAPTOR 的取证系统，涵盖 GitHub 存档、Wayback Machine、GitHub API、本地 Git 数据分析、威胁指标提取、基于证据的假设形成与验证，以及最终取证报告的生成。

---

## ⚠️ 反幻觉防护准则

在执行每一步调查之前，请先阅读这些准则。违反这些准则将导致报告无效。

1. **证据优先原则**：所有报告、假设或总结中的陈述都必须至少引用一个证据编号（`EV-XXXX`）。严禁出现无依据的断言。  
2. **各司其职**：每个子代理（调查员）仅负责单一数据源，不得混用不同来源的数据。例如，GH Archive调查员不得查询GitHub API，反之亦然。角色职责边界必须严格遵循。  
3. **事实与假设区分**：所有未经验证的推论都需标注为`[HYPOTHESIS]`。只有经过原始来源核实的陈述才能被视为事实。  
4. **禁止伪造证据**：假设验证器在接受某个假设之前，必须通过自动化方式确认所引用的每个证据编号确实存在于证据库中。  
5. **否定假设需提供证据**：若要推翻某个假设，必须提出具体且有证据支持的反对论据。“未找到相关证据”不足以构成否定——这只意味着该假设尚无定论。  
6. **SHA/URL双重验证**：作为证据引用的任何提交SHA值、URL或外部标识符，都必须在至少两个独立来源得到确认后，才能被标记为已验证。  
7. **可疑代码处理规则**：绝不可在本地运行从被调查仓库中找到的代码。应仅进行静态分析，或是在隔离环境中使用`execute_code`功能。  
8. **机密信息遮蔽**：在调查过程中发现的任何API密钥、令牌或凭证，都必须在最终报告中予以遮蔽，仅可在内部日志中记录。  

---

## 示例场景

- **场景 A：依赖关系混淆**：有恶意的包 `internal-lib-v2` 以高于内部版本号的格式上传到 NPM。调查人员需要追踪该包首次出现的时间，以及目标仓库中的任何 PushEvent 是否曾将 `package.json` 更新为该版本。
- **场景 B：维护者权限被窃取**：有长期贡献记录的用户账户被用来推送带有后门的 `.github/workflows/build.yml` 文件。调查人员会查找该用户在长时间未活跃之后，或从新 IP/位置（若能通过 BigQuery 检测到）发起的 PushEvent。
- **场景 C：强制推送掩盖痕迹**：开发人员意外将生产环境机密信息提交后，又通过强制推送试图“修正”错误。调查人员会使用 `git fsck` 和 GH Archive 恢复原始提交记录的 SHA 值，从而确认究竟泄露了什么内容。

---

> **路径约定**：在本技能文档中，`SKILL_DIR` 指的是该技能安装目录的根目录（即包含此 `SKILL.md` 文件的文件夹）。当加载该技能时，需将 `SKILL_DIR` 替换为实际路径——例如 `~/.hermes/skills/security/oss-forensics/`，或是 `optional-skills/` 目录下的对应路径。所有脚本和模板文件的引用均以此路径为基准。

## 第 0 阶段：初始化

1. 创建调查工作目录：
   ```bash
   mkdir investigation_$(echo "REPO_NAME" | tr '/' '_')
   cd investigation_$(echo "REPO_NAME" | tr '/' '_')
   ```
2. 初始化证据存储库：
   ```bash
   python SKILL_DIR/scripts/evidence-store.py --store evidence.json list
   ```
3. 复制取证报告模板：
   ```bash
   cp SKILL_DIR/templates/forensic-report.md ./investigation-report.md
   ```
4. 创建一个 `iocs.md` 文件，用于记录所发现的威胁指标。  
5. 记录调查开始时间、目标仓库以及明确的调查目标。

---

## 第一阶段：提示语解析与威胁指标提取

**目标**：从用户输入的请求中提取所有结构化的调查目标。

**操作步骤**：
- 解析用户提示语并提取以下信息：
  - 目标仓库（`owner/repo` 格式）
  - 目标主体（GitHub 账户名、电子邮件地址）
  - 关注的时间范围（提交日期区间、PR 时间戳）
  - 已提供的威胁指标：提交 SHA 值、文件路径、软件包名称、IP 地址、域名、API 密钥/令牌、恶意网址
  - 任何关联的供应商安全报告或博客文章

**工具**：仅可使用推理功能；如需从大量文本块中提取信息，可使用 `execute_code` 功能配合正则表达式。

**输出结果**：将提取到的威胁指标填入 `iocs.md` 文件中。每个威胁指标都必须包含以下字段：
- 类型（可选值包括：COMMIT_SHA、FILE_PATH、API_KEY、SECRET、IP_ADDRESS、DOMAIN、PACKAGE_NAME、ACTOR_USERNAME、MALICIOUS_URL、OTHER）
- 具体值
- 来源（用户提供或推断得出）

**参考**：关于威胁指标的分类标准，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/evidence-types.md) 文档。

---

## 第二阶段：并行证据收集

使用 `delegate_task` 功能启动最多 5 个专门的调查子代理（批量模式，最多同时运行 3 个）。每个调查子代理仅负责**一个数据源**，且不得混用不同来源的数据。

> **协调器提示**：请将第一阶段的IOC列表以及调查时间窗口传递到每个派生任务中的`context`字段中。
```bash
# Clone repository
git clone https://github.com/OWNER/REPO.git target_repo && cd target_repo

# Full commit log with stats
git log --all --full-history --stat --format="%H|%ae|%an|%ai|%s" > ../git_log.txt

# Detect force-push evidence (orphaned/dangling commits)
git fsck --lost-found --unreachable 2>&1 | grep commit > ../dangling_commits.txt

# Check reflog for rewritten history
git reflog --all > ../reflog.txt

# List ALL branches including deleted remote refs
git branch -a -v > ../branches.txt

# Find suspicious large binary additions
git log --all --diff-filter=A --name-only --format="%H %ai" -- "*.so" "*.dll" "*.exe" "*.bin" > ../binary_additions.txt

# Check for GPG signature anomalies
git log --show-signature --format="%H %ai %aN" > ../signature_check.txt 2>&1
```

**需收集的证据**（通过 `python SKILL_DIR/scripts/evidence-store.py add` 命令添加）：
- 每个悬空提交的 SHA 值 → 类型：`git`
- 强制推送产生的证据（显示历史记录被重写的 reflog）→ 类型：`git`
- 来自已验证贡献者的未签名提交 → 类型：`git`
- 可疑的二进制文件添加记录 → 类型：`git`

**参考资料**：如需了解如何获取被强制推送的提交记录，请参阅 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/recovery-techniques.md)。

---

### 调查员 2：GitHub API 调查员

**职责范围**：仅可查询 GITHUB REST API，不得在本地运行 git 命令。

**操作内容**：
```bash
# Commits (paginated)
curl -s "https://api.github.com/repos/OWNER/REPO/commits?per_page=100" > api_commits.json

# Pull Requests including closed/deleted
curl -s "https://api.github.com/repos/OWNER/REPO/pulls?state=all&per_page=100" > api_prs.json

# Issues
curl -s "https://api.github.com/repos/OWNER/REPO/issues?state=all&per_page=100" > api_issues.json

# Contributors and collaborator changes
curl -s "https://api.github.com/repos/OWNER/REPO/contributors" > api_contributors.json

# Repository events (last 300)
curl -s "https://api.github.com/repos/OWNER/REPO/events?per_page=100" > api_events.json

# Check specific suspicious commit SHA details
curl -s "https://api.github.com/repos/OWNER/REPO/git/commits/SHA" > commit_detail.json

# Releases
curl -s "https://api.github.com/repos/OWNER/REPO/releases?per_page=100" > api_releases.json

# Check if a specific commit exists (force-pushed commits may 404 on commits/ but succeed on git/commits/)
curl -s "https://api.github.com/repos/OWNER/REPO/commits/SHA" | jq .sha
```

**交叉引用目标**（将差异标记为证据）：
- 归档中存在 PR，但 API 中不存在 → 说明该 PR 已被删除
- 归档事件中列有贡献者，但贡献者列表中无此人 → 说明其权限已被撤销
- 归档的 PushEvents 中有提交记录，但 API 的提交列表中不存在 → 说明存在强制推送或删除操作

**参考**：关于 GitHub 事件类型的详细信息，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/evidence-types.md)。

---

### 调查员 3：Wayback Machine 调查员

**职责范围**：仅可查询 WAYBACK MACHINE CDX API，不得使用 GitHub API。

**目标**：恢复已被删除的 GitHub 页面（README、问题记录、PR、版本发布信息、Wiki 页面）。

**操作步骤**：
```bash
# Search for archived snapshots of the repo main page
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO&output=json&limit=100&from=YYYYMMDD&to=YYYYMMDD" > wayback_main.json

# Search for a specific deleted issue
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/issues/NUM&output=json&limit=50" > wayback_issue_NUM.json

# Search for a specific deleted PR
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/pull/NUM&output=json&limit=50" > wayback_pr_NUM.json

# Fetch the best snapshot of a page
# Use the Wayback Machine URL: https://web.archive.org/web/TIMESTAMP/ORIGINAL_URL
# Example: https://web.archive.org/web/20240101000000*/github.com/OWNER/REPO

# Advanced: Search for deleted releases/tags
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/releases/tag/*&output=json" > wayback_tags.json

# Advanced: Search for historical wiki changes
curl -s "https://web.archive.org/cdx/search/cdx?url=github.com/OWNER/REPO/wiki/*&output=json" > wayback_wiki.json
```

**需收集的证据**：
- 已删除问题/PR的存档快照及其内容
- 显示版本变更的历史README文件
- 证明某些内容存在于存档中但当前GitHub状态中却缺失的证据

**参考**：有关CDX API参数的详细信息，请参阅 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/github-archive-guide.md)。

---

### 调查员4：GH存档/BigQuery调查员

**职责范围**：您仅能通过BIGQUERY来查询GITHUB ARCHIVE。该平台保存着所有公开GitHub事件的不可篡改记录。

> **前置条件**：需要具备具有BigQuery访问权限的Google Cloud账号（需执行`gcloud auth application-default login`操作）。若无法满足此条件，请跳过该调查员，并在报告中予以说明。

**成本优化规则**（必须遵守）：
1. 每次执行查询前务必先运行`--dry_run`以预估成本。
2. 使用 `_TABLE_SUFFIX` 根据时间范围进行过滤，从而减少需要扫描的数据量。
3. 仅选择所需的列。
4. 除非需要进行聚合操作，否则请使用LIMIT限制查询结果数量。

```bash
# Template: safe BigQuery query for PushEvents to OWNER/REPO
bq query --use_legacy_sql=false --dry_run "
SELECT created_at, actor.login, payload.commits, payload.before, payload.head,
       payload.size, payload.distinct_size
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'PushEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 1000
"
# If cost is acceptable, re-run without --dry_run

# Detect force-pushes: zero-distinct_size PushEvents mean commits were force-erased
# payload.distinct_size = 0 AND payload.size > 0 → force push indicator

# Check for deleted branch events
bq query --use_legacy_sql=false "
SELECT created_at, actor.login, payload.ref, payload.ref_type
FROM \`githubarchive.month.*\`
WHERE _TABLE_SUFFIX BETWEEN 'YYYYMM' AND 'YYYYMM'
  AND type = 'DeleteEvent'
  AND repo.name = 'OWNER/REPO'
LIMIT 200
"
```

**需收集的证据**：
- 强制推送事件（payload.size > 0，payload.distinct_size = 0）
- 分支/标签的DeleteEvents事件
- 存在可疑CI/CD自动化行为的WorkflowRunEvents事件
- 出现在git日志“间隔期”之前的PushEvents事件（属于代码重写的证据）

**参考资料**：关于全部12种事件类型及查询模式，请参阅[github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/github-archive-guide.md)。

---

### 调查员5：IOC信息补充调查员

**职责范围**：仅能利用公开的被动来源，对第一阶段已有的IOC信息进行补充完善。严禁执行目标代码库中的任何代码。

**操作步骤**：
- 对每个提交SHA值：尝试通过直接的GitHub链接进行恢复（格式为`github.com/OWNER/REPO/commit/SHA.patch`）
- 对每个域名/IP地址：查询被动DNS记录及WHOIS信息（通过公共WHOIS服务上的`web_extract`功能）
- 对每个软件包名称：在npm/PyPI平台上查找是否存在相关的恶意软件包报告
- 对每个操作者用户名：查看其GitHub个人主页、贡献历史以及账户创建时间
- 采用三种方法恢复被强制推送的提交记录（详见[recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/recovery-techniques.md)）

---

## 第三阶段：证据整合

在所有调查员完成工作后：

1. 运行命令 `python SKILL_DIR/scripts/evidence-store.py --store evidence.json list`，即可查看所有已收集的证据。
2. 对每条证据，需确认其 `content_sha256` 哈希值与原始来源一致。
3. 按以下方式对证据进行分类：
   - **时间线**：按时间顺序排列所有带有时间戳的证据；
   - **操作者**：按 GitHub 用户名或电子邮件地址进行分组；
   - **IOC**：将证据与其关联的 IOC 对应起来。
4. 识别**差异项**：即在一个来源中存在但在另一个来源中缺失的内容（这通常是数据被删除的迹象）。
5. 为证据标记状态：若来自2个以上独立来源则标记为 `[VERIFIED]`（已验证），否则标记为 `[UNVERIFIED]`（仅来自单一来源）。

---

## 第4阶段：假设形成

一个有效的假设需满足以下条件：
- 提出明确的断言（例如：“操作者X在DATE日期强制推送代码到BRANCH分支，旨在删除某个提交SHA”）；
- 引用至少2个支持该断言的证据编号（如 `EV-XXXX`、`EV-YYYY`）；
- 指明哪些证据可以推翻该假设；
- 在得到验证之前，该假设需标注为 `[HYPOTHESIS]`。

**常见的假设模板**（详见 [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/investigation-templates.md)）：
- 维护者被攻破：攻击者窃取合法账户后注入恶意代码；
- 依赖项混淆：通过占用相似名称的包来拦截安装请求；
- CI/CD注入：篡改构建流程，在编译过程中执行恶意代码；
- 拼写抢注：使用与合法包名极为相似的名称，针对输入错误的用户；
- 凭据泄露：令牌或密钥被意外提交后，又被强制推送以试图掩盖痕迹。
对于每个假设，都会生成一个 `delegate_task` 子代理，以便在确认之前尝试寻找能够反驳该假设的证据。

---

## 第 5 阶段：假设验证

验证子代理必须严格检查以下内容：

1. 对于每个假设，提取所有被引用的证据 ID。
2. 确认每个 ID 都存在于 `evidence.json` 中（若缺少任何 ID，则视为严重错误，该假设将被判定为可能是伪造的）。
3. 确认每条标记为 `[VERIFIED]` 的证据都来自两个及以上独立来源。
4. 检查逻辑一致性：证据所呈现的时间线是否支持该假设？
5. 查找其他可能的解释：同样的证据模式是否也可能由良性原因造成？

**输出结果**：
- `VALIDATED`：所有引用的证据均经过验证，逻辑一致，且不存在合理的替代解释。
- `INCONCLUSIVE`：现有证据虽支持该假设，但存在其他可能的解释或证据不足。
- `REJECTED`：缺少证据 ID，有未经验证的证据被当作事实使用，或检测到逻辑矛盾。

被否决的假设会反馈回第 4 阶段进行进一步优化（最多迭代 3 次）。

---

## 第 6 阶段：生成最终报告

根据 [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/templates/forensic-report.md) 中的模板，填写 `investigation-report.md` 文件。

**必填部分**：
- **执行摘要**：用一段文字给出判定结果（已入侵/安全/无法确定），并说明置信度。  
- **时间线**：按时间顺序梳理所有重要事件，并标注相关证据来源。  
- **已验证假设**：列出每个假设的状态及对应的证据编号。  
- **证据登记表**：以表格形式展示所有`EV-XXXX`格式的证据，包括来源、类型及验证状态。  
- **威胁指标列表**：汇总所有提取并经过进一步分析的威胁指标。  
- **证据保管流程**：详细说明证据的收集方式、来源以及对应的时间戳。  
- **建议措施**：若检测到入侵，则提供即时应对方案；同时给出监控方面的建议。

**报告编写规则**：  
- 所有事实性陈述都必须引用至少一个`[EV-XXXX]`格式的证据。  
- 执行摘要中必须明确说明置信度等级（高/中/低）。  
- 所有的敏感信息或凭证都需替换为`[REDACTED]`。

---

## 第7阶段：报告完成

1. 运行最终证据统计命令：`python SKILL_DIR/scripts/evidence-store.py --store evidence.json list`  
2. 将整个调查目录归档。  
3. 若确认存在安全入侵：  
   - 列出即时应对措施（如更换凭证、锁定依赖项哈希值、通知受影响用户等）。  
   - 确定受影响的版本或软件包。  
   - 记录信息披露义务（如果是公开发布的软件包，则需与相关软件包注册平台协调处理）。  
4. 将最终的`investigation-report.md`报告呈现给用户。

---

## 伦理使用指南

该功能专为**防御性安全调查**设计，旨在保护开源软件免受供应链攻击。严禁将其用于以下用途：

- 对贡献者或维护者进行**骚扰或跟踪**  
- **泄露个人信息**——出于恶意目的将 GitHub 活动与真实身份关联起来  
- **竞争情报收集**——未经授权擅自调查专有或内部代码库  
- **虚假指控**——在缺乏有效证据的情况下发布调查结果（请参阅反幻觉规范）  

开展调查时应遵循**最小侵入原则**：仅收集足以验证或推翻假设的必要证据。在公布结果时，应遵循负责任的披露流程，并在公开之前与受影响的维护者进行沟通。  

如果调查发现确实存在安全漏洞，需按照规范的漏洞披露流程操作：  
1. 首先私下通知代码库的维护者  
2. 给予合理的修复时间（通常为 90 天）  
3. 若发布的软件包受到影响，则与包注册平台（如 npm、PyPI 等）进行协调  
4. 在适当情况下提交 CVE 报告  

---

## API 请求速率限制  

若不加以管理，GitHub REST API 的速率限制可能会中断大规模的调查工作。  

**已认证请求**：每小时 5,000 次（需使用 `GITHUB_TOKEN` 环境变量或 `gh` CLI 进行身份验证）  
**未认证请求**：每小时 60 次（无法用于调查）  

**最佳实践**：
- 始终进行身份验证：设置 `export GITHUB_TOKEN=ghp_...`，或使用可自动完成认证的 `gh` CLI 工具。  
- 使用条件请求（`If-None-Match` / `If-Modified-Since` 请求头），以避免因数据未发生变化而消耗配额。  
- 对于分页接口，请按顺序获取所有页面——切勿对同一接口同时发起并行请求。  
- 查看 `X-RateLimit-Remaining` 请求头；若该数值低于 100，需等待至 `X-RateLimit-Reset` 时间戳后再继续操作。  
- BigQuery 有独立的配额限制（免费套餐为每天 10 TiB），务必先进行试运行。  
- Wayback Machine CDX API 没有明确的速率限制，但建议仍保持礼貌，请求频率最高控制在每秒 1-2 次。  

如果在调查过程中遇到速率限制，请将已获取的部分结果保存到证据存储中，并在报告中注明该限制情况。  

---

## 参考资料

- [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/github-archive-guide.md) — BigQuery 查询、CDX API 以及 12 种事件类型  
- [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/evidence-types.md) — IOC 分类体系、证据来源类型及观测类型  
- [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/recovery-techniques.md) — 恢复已删除的提交记录、PR 以及问题记录  
- [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/references/investigation-templates.md) — 针对不同攻击类型的预构建假设模板  
- [evidence-store.py](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/scripts/evidence-store.py) — 用于管理证据 JSON 存储的 CLI 工具  
- [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security\oss-forensics/templates/forensic-report.md) — 结构化报告模板
