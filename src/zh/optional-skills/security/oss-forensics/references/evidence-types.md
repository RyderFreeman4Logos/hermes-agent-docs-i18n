# 证据类型参考

涵盖在开源安全取证调查中使用的所有证据类型、威胁指标类型、GitHub事件类型以及观察结果的分类体系。

---

## 证据来源类型

| 类型 | 描述 | 典型来源示例 |
|------|------|--------------|
| `git` | 来自本地Git仓库分析的数据 | `git log`、`git fsck`、`git reflog`、`git blame` |
| `gh_api` | 来自GitHub REST API响应的数据 | `/repos/.../commits`、`/repos/.../pulls`、`/repos/.../events` |
| `gh_archive` | 来自GitHub归档数据（BigQuery存储）的数据 | `githubarchive.month.*`系列BigQuery表 |
| `web_archive` | 来自网页缓存器（Wayback Machine）的已存档网页 | CDX API查询结果、`web.archive.org/web/...`格式的快照 |
| `ioc` | 来自各类来源的威胁指标 | 从供应商报告、Git历史记录、网络流量中提取的指标 |
| `analysis` | 通过多源数据交叉关联得出的分析结论 | “归档数据中存在该SHA值，但API查询结果中未出现” |
| `vendor_report` | 来自外部安全厂商或研究人员的报告 | CVE预警信息、博客文章、NVD数据库记录 |
| `manual` | 由调查人员手动记录的观察结果 | 关于行为模式、时间线缺失等的笔记 |

---

## 威胁指标类型

| 类型 | 描述 | 示例 |
|------|------|---------|
| `COMMIT_SHA` | 与恶意活动相关的Git提交哈希值 | `abc123def456...` |
| `FILE_PATH` | 仓库内的可疑文件路径 | `src/utils/crypto.js`、`dist/index.min.js` |
| `API_KEY` | 被意外提交到代码库的API密钥 | `AKIA...`（AWS密钥）、`ghp_...`（GitHub个人访问令牌） |
| `SECRET` | 通用类型的机密信息/凭证 | 数据库密码、私钥文件 |
| `IP_ADDRESS` | C2服务器或攻击者的IP地址 | `192.0.2.1` |
| `DOMAIN` | 恶意或可疑域名 | `evil-cdn.io`、被篡改的包注册表域名 |
| `PACKAGE_NAME` | 恶意或被篡改的软件包名称 | `colo-rs`（对`color`一词的恶意篡改）、`lodash-utils` |
| `ACTOR_USERNAME` | 与攻击相关的GitHub用户名 | `malicious-bot-account` |
| `MALICIOUS_URL` | 指向恶意资源的URL地址 | `https://evil.example.com/payload.sh` |
| `WORKFLOW_FILE` | 可疑的CI/CD工作流文件 | `.github/workflows/release.yml` |
| `BRANCH_NAME` | 可疑的分支名称 | `refs/heads/temp-fix-do-not-merge` |
| `TAG_NAME` | 可疑的Git标签名称 | `v1.0.0-security-patch` |
| `RELEASE_NAME` | 可疑的版本发布记录 | 无对应标签或更新日志的版本发布 |
| `OTHER` | 未分类威胁指标的统称 | — |

---

## GitHub归档事件类型（共12种）

| 事件类型 | 取证意义 |
|----------|----------|
| `PushEvent` | 核心特征：当`payload.distinct_size=0`且`payload.size>0`时，表明存在强制推送行为；`payload.before`/`payload.head`字段可显示被篡改的历史记录。 |
| `PullRequestEvent` | 能检测到被删除的拉取请求、频繁的“创建→关闭”操作模式，以及来自新账户的拉取请求。 |
| `IssueEvent` | 可识别被删除的议题、协同标记行为，以及漏洞报告被快速关闭的情况。 |
| `IssueCommentEvent` | 能发现被删除的评论，以及短时间内异常密集的活动记录。 |
| `WatchEvent` | 用于检测批量加星活动（即新账户协同对仓库加星的行为）。 |
| `ForkEvent` | 能发现恶意提交之前的异常 fork 行为模式。 |
| `CreateEvent` | 分支或标签的创建事件，可能预示着新的版本发布或代码注入点出现。 |
| `DeleteEvent` | 分支或标签的删除事件，属于重要线索——攻击者常以此来隐藏操作痕迹。 |
| `ReleaseEvent` | 用于检测未经授权的版本发布，以及发布后代码制品被篡改的情况。 |
| `MemberEvent` | 合作人员的添加或移除事件，可能是维护者账号被攻破的迹象。 |
| `PublicEvent` | 仓库被设为公开状态的事件（有时用于暂时上传恶意代码）。 |
| `WorkflowRunEvent` | CI/CD流水线执行事件，可用于检测工作流注入或机密信息泄露行为。 |

---

## 证据验证状态

| 状态 | 含义 |
|------|------|
| `unverified` | 仅从单一来源收集到的证据，尚未进行交叉验证 |
| `single_source` | 主要来源已得到直接确认（例如在GitHub上可查到对应SHA值），但缺乏第二来源验证 |
| `multi_source_verified` | 已通过2个及以上独立来源交叉验证（例如GitHub归档数据与GitHub API均显示相同事件） |

只有处于`multi_source_verified`状态的证据，才能在经过验证的假设中被作为事实引用。属于`unverified`和`single_source`状态的证据必须标注为`[UNVERIFIED]`或`[SINGLE-SOURCE]`。

---

## 观察结果类型（参考RAPTOR框架设计）

| 类型 | 描述 |
|------|------|
| `CommitObservation` | 包含具体提交哈希值及元数据（作者、日期、被修改文件）的观察结果 |
| `ForceWashObservation` | 表明有人员试图强制清除分支中提交记录的证据 |
| `DanglingCommitObservation` | 该SHA值存在于Git对象存储中，但无法通过任何引用路径访问的观察结果 |
| `IssueObservation` | 包含标题、内容及时间戳的GitHub议题信息（无论是当前活跃的还是已归档的） |
| `PRObservation` | 包含差异对比摘要及审核人信息的GitHub拉取请求信息（当前活跃或已归档） |
| `IOC` | 带有上下文信息的单个威胁指标 |
| `TimelineGap` | 出现预期活动却异常缺失的时段 |
| `ActorAnomalyObservation` | 某特定GitHub用户账号的行为异常记录 |
| `WorkflowAnomalyObservation` | 可疑的CI/CD工作流更改或意外执行的观察结果 |
| `CrossSourceDiscrepancy` | 某项内容在某一来源存在，但在另一来源中缺失的记录（属于强烈的删除迹象） |
