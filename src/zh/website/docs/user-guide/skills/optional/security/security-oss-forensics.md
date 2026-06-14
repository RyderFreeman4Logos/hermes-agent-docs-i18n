---
title: "Oss Forensics — Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories"
sidebar_label: "Oss Forensics"
description: "Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# OSS取证分析

针对GitHub仓库提供的供应链调查、证据恢复及法医分析功能。
支持已删除提交的恢复、强制推送检测、威胁指标提取、多源证据收集、假设形成/验证以及结构化的法医报告生成。
该功能灵感来源于RAPTOR拥有1800多行代码的OSS取证系统。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/security/oss-forensics` 安装 |
| 路径 | `optional-skills/security/oss-forensics` |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时Hermes所加载的完整技能定义。技能运行时，代理将依据此内容作为操作指南。
:::

# OSS安全取证分析技能

一种用于调查开源供应链攻击的7阶段多代理调查框架。
该框架基于RAPTOR的取证系统优化而来，涵盖GitHub归档、Wayback Machine、GitHub API、本地git分析、威胁指标提取、基于证据的假设形成与验证，以及最终法医报告的生成。

---

## ⚠️ 反幻觉准则

在每个调查步骤开始前请仔细阅读这些准则。违反准则将导致报告无效。

1. **证据优先原则**：任何报告、假设或总结中的所有陈述都必须引用至少一个证据编号（`EV-XXXX`）。禁止出现无证据支撑的断言。
2. **各司其职**：每个子代理（调查员）仅负责单一数据源，不得混用不同来源的数据。负责GitHub归档的调查员不得查询GitHub API，反之亦然。角色边界必须严格遵循。
3. **事实与假设区分**：所有未经验证的推论均需标注 `[HYPOTHESIS]`。只有经过原始来源验证的陈述才能被视为事实。
4. **禁止伪造证据**：假设验证器在接受某个假设之前，必须通过自动化方式确认所有引用的证据编号确实存在于证据库中。
5. **需证据支持的否定**：若无具体的、有证据支撑的反论，不得直接否定某个假设。“未找到相关证据”不足以构成否定依据——这仅意味着该假设尚无定论。
6. **SHA/URL双重验证**：任何作为证据引用的提交SHA值、URL或外部标识符，都必须通过至少两个独立来源的确认后，才能被视为已验证。
7. **可疑代码处理规则**：绝不可在本地运行从被调查仓库中找到的代码。仅可进行静态分析，或在使用沙箱环境中的 `execute_code` 功能进行处理。
8. **机密信息遮蔽**：调查过程中发现的任何API密钥、令牌或凭证，都必须在最终报告中予以遮蔽，仅可在内部日志中记录。

---

## 实例场景

- **场景A：依赖项混淆**：有恶意包 `internal-lib-v2` 以高于内部版本号的格式上传到NPM。调查员需追踪该包首次出现的时间，以及目标仓库中的PushEvent是否曾将 `package.json` 更新为该版本。
- **场景B：维护者权限被窃取**：有长期贡献者的账户被用于推送经过后处理的 `.github/workflows/build.yml` 文件。调查员会查找该用户在长时间未活跃之后，或从新IP/位置（若可通过BigQuery检测到）发起的PushEvent。
- **场景C：强制推送掩盖行为**：有开发者意外将生产环境机密信息提交到代码库，随后又通过强制推送试图“修复”问题。调查员会使用 `git fsck` 和GitHub归档功能来恢复原始提交SHA值，并确认究竟泄露了哪些信息。

---

> **路径约定**：在本技能中，`SKILL_DIR` 指的是该技能安装目录的根目录（即包含此 `SKILL.md` 文件的文件夹）。当加载该技能时，需将 `SKILL_DIR` 替换为实际路径——例如 `~/.hermes/skills/security/oss-forensics/` 或 `optional-skills/` 目录下的对应路径。所有脚本和模板引用均以此路径为基准。

## 第0阶段：初始化

1. 创建调查工作目录：
   ```bash
   mkdir investigation_$(echo "REPO_NAME" | tr '/' '_')
   cd investigation_$(echo "REPO_NAME" | tr '/' '_')
   ```
2. 初始化证据存储库：
   ```bash
   python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list
   ```
3. 复制取证报告模板：
   ```bash
   cp SKILL_DIR/templates/forensic-report.md ./investigation-report.md
   ```
4. 创建一个 `iocs.md` 文件，用于记录所发现的威胁指标。  
5. 记录调查开始时间、目标仓库以及明确的调查目标。

---

## 第一阶段：提示解析与威胁指标提取

**目标**：从用户请求中提取所有结构化的调查目标。

**操作步骤**：
- 解析用户输入的提示语，并提取以下信息：
  - 目标仓库（`owner/repo` 格式）
  - 目标主体（GitHub 账户名、电子邮件地址）
  - 关注的时间范围（提交日期区间、PR 时间戳）
  - 已提供的威胁指标：提交 SHA 值、文件路径、软件包名称、IP 地址、域名、API 密钥/令牌、恶意网址
  - 任何相关的供应商安全报告或博客文章

**工具**：仅可使用推理功能；若需从大量文本块中提取信息，可使用 `execute_code` 功能配合正则表达式。

**输出**：将提取到的威胁指标填入 `iocs.md` 文件中。每个威胁指标必须包含以下信息：
- 类型（来源：COMMIT_SHA、FILE_PATH、API_KEY、SECRET、IP_ADDRESS、DOMAIN、PACKAGE_NAME、ACTOR_USERNAME、MALICIOUS_URL、OTHER）
- 具体值
- 来源（用户提供或推断得出）

**参考**：关于威胁指标的分类标准，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md)。

---

## 第二阶段：并行证据收集

使用 `delegate_task` 功能启动最多 5 个专门的调查子代理（批量模式，最多同时运行 3 个）。每个调查子代理仅负责**一个数据源**，且不得混用不同来源的数据。

> **协调器注意事项**：需在每个被委托任务的 `context` 字段中传递第一阶段获取的威胁指标列表以及调查的时间范围。

---

### 调查子代理 1：本地 Git 调查器

**职责范围**：仅可查询本地的 Git 仓库，不得调用任何外部 API。

**操作步骤**：
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

**需收集的证据**（可通过 `python3 SKILL_DIR/scripts/evidence-store.py add` 命令添加）：
- 每个悬空提交的 SHA 值 → 类型：`git`
- 强制推送产生的证据（显示历史记录被重写的 reflog）→ 类型：`git`
- 来自已验证贡献者的未签名提交 → 类型：`git`
- 可疑的二进制文件添加记录 → 类型：`git`

**参考资料**：如需了解如何获取通过强制推送提交的记录，请参阅 [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)。

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
- 归档中存在 Pull Request 但 API 中缺失 → 证明该 PR 已被删除
- 归档事件中列有贡献者，但贡献者列表中无此人 → 证明其权限已被撤销
- 归档的 PushEvents 中有提交记录，但 API 的提交列表中不存在 → 证明存在强制推送或删除行为

**参考**：有关 GitHub 事件类型的详细信息，请参阅 [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md)。

---

### 调查员 3：Wayback Machine 调查员

**职责范围**：仅可查询 WAYBACK MACHINE CDX API，不得使用 GitHub API。

**目标**：恢复已被删除的 GitHub 页面（README、问题记录、Pull Request、版本发布信息及维基页面）。

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
- 已删除问题/拉取请求的存档快照及其内容
- 显示变更历史的README版本记录
- 证明某些内容存在于存档中但当前GitHub状态中已缺失的证据

**参考资料**：关于CDX API参数的详细信息，请参阅 [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md)。

---

### 调查员4：GH存档/BigQuery调查员

**职责范围**：您仅能通过BigQuery来查询GITHUB ARCHIVE。该平台保存着所有公开GitHub事件的不可篡改记录。

> **前置条件**：需要具备具有BigQuery访问权限的Google Cloud凭证（需执行 `gcloud auth application-default login` 操作）。若无法满足此条件，请跳过该调查员，并在报告中予以说明。

**成本优化规则**（必须遵守）：
1. 每次执行查询前务必先运行 `--dry_run` 选项以估算成本。
2. 使用 `_TABLE_SUFFIX` 根据时间范围进行筛选，从而减少需要扫描的数据量。
3. 仅选择所需的列。
4. 除非正在执行聚合操作，否则请添加 LIMIT 限制。

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
- 强制推送事件（payload.size > 0，且payload.distinct_size = 0）
- 分支/标签的DeleteEvents事件
- 可疑CI/CD自动化流程的WorkflowRunEvents事件
- 出现在git日志“间隙”之前的PushEvents事件（属于代码重写行为的证据）

**参考资料**：有关全部12种事件类型及查询模式的信息，请参阅[github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md)。

---

### 调查员5：IOC信息丰富化调查员

**职责范围**：仅能利用公开的被动数据源，对第一阶段已有的IOC信息进行进一步丰富，严禁执行目标代码库中的任何代码。

**操作步骤**：
- 对每个提交SHA值：尝试通过直接的GitHub链接进行恢复（格式为`github.com/OWNER/REPO/commit/SHA.patch`）
- 对每个域名/IP地址：查询被动DNS记录及WHOIS信息（通过公共WHOIS服务上的`web_extract`功能）
- 对每个软件包名称：在npm/PyPI平台上查找是否存在相关的恶意软件包报告
- 对每个操作者用户名：核查其GitHub个人主页、代码贡献历史以及账户创建时间
- 使用三种方法恢复被强制推送的提交记录（详情参见[recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md)）

---

## 第3阶段：证据整合

所有调查员完成工作后，请执行以下操作：

1. 运行命令 `python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list`，查看所有已收集的证据。
2. 对每份证据，核实其`content_sha256`哈希值是否与原始来源一致。
3. 按以下维度对证据进行分类：
   - **时间线**：按时间顺序排列所有带有时间戳的证据
   - **操作者**：按GitHub用户名或邮箱地址分组
   - **IOC**：将证据与其关联的IOC信息对应起来
4. 识别**差异点**：即某些证据在某个来源存在，但在另一个来源中缺失（这往往是数据被删除的迹象）。
5. 为证据标记状态：若来自2个以上独立来源则标记为`[VERIFIED]`（已验证），否则标记为`[UNVERIFIED]`（仅来自单一来源）。

---

## 第4阶段：假设形成

一个有效的假设必须满足以下条件：
- 明确阐述具体主张（例如：“操作者X在DATE日期向BRANCH分支强制推送代码，旨在删除SHA编号为XX的提交”）
- 至少引用2个支持该主张的证据编号（格式为`EV-XXXX`、`EV-YYYY`）
- 指明哪些证据可以推翻该假设
- 在得到验证之前，该假设需标注为`[HYPOTHESIS]`

**常见的假设模板**（详见[investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md)）：
- 维护者账号被攻破：攻击者接管合法账户后注入恶意代码
- 依赖项混淆：通过占用相似名称的软件包来拦截安装请求
- CI/CD流程注入：恶意修改工作流，使代码在构建过程中执行
- 拼写混淆攻击：利用几乎相同的软件包名称针对输入错误的用户
- 凭据泄露：令牌或密钥被意外提交后又被强制推送以掩盖痕迹

对于每个假设，应启动一个`delegate_task`子代理，在最终确认之前尝试查找能够推翻该假设的证据。

---

## 第5阶段：假设验证

验证子代理必须严格执行以下检查步骤：

1. 提取每个假设所引用的所有证据编号。
2. 核实每个编号是否存在于`evidence.json`文件中（若有任何编号缺失，则视为严重错误，该假设将被判定为可能是伪造的）。
3. 确认每份标记为`[VERIFIED]`的证据确实来自2个以上独立来源。
4. 检查逻辑一致性：证据所呈现的时间线是否与该假设相符？
5. 探索其他可能的解释：同样的证据特征是否也可能由良性原因导致？

**输出结果**：
- `VALIDATED`：所有引用的证据均已核实，逻辑一致，且不存在合理的替代性解释。
- `INCONCLUSIVE`：现有证据虽支持该假设，但存在其他可能性或证据不足。
- `REJECTED`：存在缺失的证据编号，有未经验证的证据被当作事实引用，或发现逻辑矛盾。

被否决的假设将反馈回第4阶段以便进一步优化（最多可迭代3次）。

---

## 第6阶段：最终报告生成

根据[forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md)中的模板，填写`investigation-report.md`文件。

**必填内容**：
- 执行摘要：用一段话总结调查结果（已遭入侵/安全正常/无法确定），并说明置信度
- 时间线：按时间顺序列出所有重要事件，并标注相关证据
- 已验证的假设：列出每个假设的状态及对应的支持证据编号
- 证据清单：以表格形式展示所有`EV-XXXX`格式的证据条目，包括来源、类型及验证状态
- IOC列表：列出所有已提取并经过丰富处理的威胁指标
- 证据收集流程记录：详细说明证据的收集方式、来源以及对应的时间戳
- 建议措施：若发现安全漏洞，应采取的即时缓解措施；以及监控方面的建议

**报告撰写规则**：
- 所有事实性陈述都必须至少引用一个`[EV-XXXX]`格式的证据
- 执行摘要中必须明确说明置信度等级（高/中/低）
- 所有的敏感信息或凭据都需替换为`[REDACTED]`格式

---

## 第7阶段：任务完成

1. 运行命令统计最终证据数量：`python3 SKILL_DIR/scripts/evidence-store.py --store evidence.json list`
2. 将整个调查目录进行归档。
3. 若确认存在安全入侵：
   - 列出应立即采取的缓解措施（如更换凭据、锁定依赖项版本、通知受影响用户等）
   - 确定受影响的软件版本或软件包
   - 明确相关的信息披露义务（如果是公开发布的软件包，需与对应软件包仓库协调处理）
4. 将最终的`investigation-report.md`报告呈现给用户。

---

## 伦理使用指南

该功能专为**防御性安全调查**设计，旨在保护开源软件免受供应链攻击。严禁将其用于以下用途：
- 骚扰或跟踪代码贡献者或维护者
- 进行人肉搜索——将GitHub上的活动与真实身份关联起来用于恶意目的
- 获取竞争情报——未经授权调查专有或内部代码库
- 无端诬告——在缺乏有效证据的情况下发布调查结果（需遵守反幻觉机制的相关规定）

进行调查时应遵循**最小侵入原则**：仅收集足以验证或推翻假设的证据。在发布调查结果时，应遵循负责任的披露流程，在公开披露前与受影响的维护者进行沟通。

如果调查确实发现了安全入侵，应按照规范的漏洞披露流程操作：
1. 首先私下通知代码库的维护者
2. 给予合理的修复时间（通常为90天）
3. 若涉及已发布的软件包，需与npm、PyPI等软件包仓库进行协调
4. 在适当情况下提交CVE漏洞报告

---

## API调用速率限制

GitHub REST API设有速率限制，若不加以管理，可能会中断大规模的调查工作。

**已认证请求**：每小时5,000次（需要设置`GITHUB_TOKEN`环境变量或通过`gh` CLI工具进行身份认证）
**未认证请求**：每小时60次（无法用于调查任务）

**最佳实践建议**：
- 始终进行身份认证：可通过`export GITHUB_TOKEN=ghp_...`命令设置，或直接使用会自动完成认证的`gh` CLI工具
- 使用条件请求（如`If-None-Match`/`If-Modified-Since`请求头），避免对未发生变化的数据消耗调用配额
- 对于分页式的接口，需按顺序获取所有页面的内容，切勿同时对同一接口发起多个并行请求
- 查看`X-RateLimit-Remaining`响应头；若该数值低于100，应在`X-RateLimit-Reset`指示的时间之前暂停操作
- BigQuery平台也有自身的调用配额（免费套餐为每天10 TiB），务必先进行测试运行
- Wayback Machine CDX API没有明确的速率限制，但建议也控制请求频率，保持在每秒1-2次的范围内

如果在调查过程中遇到速率限制，应将已收集的部分结果存储到证据库中，并在报告中说明该限制情况。

---

## 参考资料

- [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md) —— 关于BigQuery查询、CDX API以及12种事件类型的说明
- [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md) —— IOC分类体系、证据来源类型及观察类型的相关说明
- [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md) —— 恢复被删除的提交记录、Pull Request及问题记录的方法
- [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md) —— 针对不同攻击类型的预置假设模板
- [evidence-store.py](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/scripts/evidence-store.py) —— 用于管理证据JSON存储的CLI工具
- [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) —— 结构化的报告模板
