---
title: "Parallel Cli"
sidebar_label: "Parallel Cli"
description: "Optional vendor skill for Parallel CLI — agent-native web search, extraction, deep research, enrichment, FindAll, and monitoring"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Parallel Cli

Parallel CLI 的可选第三方技能——具备原生代理支持的网络搜索、信息提取、深度研究、数据增强、FindAll 检索以及任务监控功能。推荐使用 JSON 格式输出，并适用于非交互式工作流。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/research/parallel-cli` 安装 |
| 路径 | `optional-skills/research/parallel-cli` |
| 版本 | `1.1.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Research`、`Web`、`Search`、`Deep-Research`、`Enrichment`、`CLI` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search)、[`mcporter`](/docs/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。当技能处于激活状态时，代理将依据此内容执行相应操作。
:::

# Parallel CLI

当用户明确要求使用 Parallel 功能，或终端原生工作流需要借助 Parallel 提供的专用技术栈来实现网络搜索、信息提取、深度研究、数据增强、实体识别或任务监控功能时，可使用 `parallel-cli`。

这属于可选的第三方工作流，并非 Hermes 的核心功能。

重要注意事项：
- Parallel 是一项付费服务，虽提供免费套餐，但并非完全免费的本地工具。
- 它与 Hermes 自带的 `web_search` / `web_extract` 功能存在重叠，因此对于常规查询无需默认优先使用它。
- 仅当用户明确提及 Parallel，或需要其数据增强、FindAll 检索或任务监控等功能时，才建议使用此技能。

`parallel-cli` 是为代理设计的，具备以下特性：
- 通过 `--json` 参数输出 JSON 格式数据
- 支持非交互式命令执行
- 可借助 `--no-wait`、`status` 和 `poll` 参数实现异步长任务处理
- 通过 `--previous-interaction-id` 参数实现上下文串联
- 在单个 CLI 命令中完成搜索、提取、研究、数据增强、实体识别及监控操作

## 适用场景

在以下情况下建议使用此技能：
- 用户明确提到 Parallel 或 `parallel-cli`
- 任务需求高于简单的单次搜索/提取操作，需要更复杂的工作流
- 需要可启动后延迟查询状态的异步深度研究任务
- 需要结构化数据增强、FindAll 实体识别或任务监控功能

若用户未明确要求使用 Parallel，对于快速的一次性查询，建议优先使用 Hermes 自带的 `web_search` / `web_extract` 功能。

## 安装方式

请根据当前环境选择侵入性最低的安装方式。

### Homebrew

```bash
brew install parallel-web/tap/parallel-cli
```

### npm

```bash
npm install -g parallel-web-cli
```

### Python 包

```bash
pip install "parallel-web-tools[cli]"
```

### 独立安装程序

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

如果您需要一个独立的 Python 安装环境，`pipx` 也是一个不错的选择：

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

## 认证

交互式登录：

```bash
parallel-cli login
```

无头模式 / SSH / 持续集成：

```bash
parallel-cli login --device
```

API密钥环境变量：

```bash
export PARALLEL_API_KEY="***"
```

验证当前认证状态：

```bash
parallel-cli auth
```

如果身份验证需要浏览器交互，请使用 `pty=true` 参数运行。

## 核心规则集

1. 当需要机器可读的输出时，始终优先选择 `--json` 参数。
2. 尽量使用显式参数以及非交互式流程。
3. 对于长时间运行的任务，请使用 `--no-wait` 参数，随后通过 `status` 或 `poll` 命令查看进度。
4. 仅引用 CLI 输出中提供的网址。
5. 如果后续可能需要查询结果，应将较大的 JSON 输出保存到临时文件中。
6. 仅在实际需要长时间运行的工作流时才使用后台进程；否则应在前台运行。
7. 除非用户明确要求使用 Parallel 功能或需要仅基于 Parallel 的工作流，否则优先使用 Hermes 自带工具。

## 快速参考指南

<!-- ascii-guard-ignore -->
```text
parallel-cli
├── auth
├── login
├── logout
├── search
├── extract / fetch
├── research run|status|poll|processors
├── enrich run|status|poll|plan|suggest|deploy
├── findall run|ingest|status|poll|result|enrich|extend|schema|cancel
└── monitor create|list|get|update|delete|events|event-group|simulate
```
## 常用标志与参数模式

常用的实用标志：
- `--json`：用于生成结构化输出
- `--no-wait`：用于异步任务
- `--previous-interaction-id <id>`：用于需要复用先前上下文的后续任务
- `--max-results <n>`：用于指定搜索结果的数量
- `--mode one-shot|agentic`：用于控制搜索模式
- `--include-domains domain1.com,domain2.com`：用于指定要包含的域名
- `--exclude-domains domain1.com,domain2.com`：用于指定要排除的域名
- `--after-date YYYY-MM-DD`：用于设置时间筛选条件

在方便的情况下，可从标准输入读取数据：

```bash
echo "What is the latest funding for Anthropic?" | parallel-cli search - --json
echo "Research question" | parallel-cli research run - --json
```

## 搜索功能

用于对当前网页进行查询，并返回结构化的搜索结果。

```bash
parallel-cli search "What is Anthropic's latest AI model?" --json
parallel-cli search "SEC filings for Apple" --include-domains sec.gov --json
parallel-cli search "bitcoin price" --after-date 2026-01-01 --max-results 10 --json
parallel-cli search "latest browser benchmarks" --mode one-shot --json
parallel-cli search "AI coding agent enterprise reviews" --mode agentic --json
```

实用约束选项：
- 使用 `--include-domains` 可筛选可信来源
- 使用 `--exclude-domains` 可排除干扰性域名
- 使用 `--after-date` 可按时间最新度进行过滤
- 若需更广泛的覆盖范围，则可使用 `--max-results`

```bash
parallel-cli search "latest React 19 changes" --json -o /tmp/react-19-search.json
```

在总结结果时：
- 首先给出答案；
- 包含日期、姓名及具体事实；
- 仅引用已提供的来源；
- 避免编造网址或来源标题。

## 提取功能

用于从网址中获取纯净的内容或 Markdown 格式。

```bash
parallel-cli extract https://example.com --json
parallel-cli extract https://company.com --objective "Find pricing info" --json
parallel-cli extract https://example.com --full-content --json
parallel-cli fetch https://example.com --json
```

当页面内容过于庞杂而您只需获取其中某部分信息时，请使用 `--objective` 参数。

## 深度研究

适用于需要多步骤处理且可能耗时的深入研究任务。

常见的处理器等级：
- `lite` / `base`：适用于追求更快、更低成本的查询；
- `core` / `pro`：适用于更全面的综合分析；
- `ultra`：适用于最复杂的科研任务。

### 同步模式

```bash
parallel-cli research run \
  "Compare the leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor core \
  --json
```

### 异步启动 + 轮询检测

```bash
parallel-cli research run \
  "Compare the leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor ultra \
  --no-wait \
  --json

parallel-cli research status trun_xxx --json
parallel-cli research poll trun_xxx --json
parallel-cli research processors --json
```

### 上下文串联/后续提问功能

```bash
parallel-cli research run "What are the top AI coding agents?" --json
parallel-cli research run \
  "What enterprise controls does the top-ranked one offer?" \
  --previous-interaction-id trun_xxx \
  --json
```

推荐的 Hermes 工作流程：
1. 使用 `--no-wait --json` 参数启动任务
2. 记录返回的运行/任务编号
3. 若用户需继续处理其他工作，可直接进行后续操作
4. 随后调用 `status` 或 `poll` 命令查询状态
5. 结合返回的来源信息，汇总生成最终报告

## 数据增强功能

当用户提供 CSV/JSON 或表格格式的输入数据，并希望从网络搜索中获取更多字段信息时，可使用此功能。

### 可建议添加的字段

```bash
parallel-cli enrich suggest "Find the CEO and annual revenue" --json
```

### 规划配置方案

```bash
parallel-cli enrich plan -o config.yaml
```

### 内联数据

```bash
parallel-cli enrich run \
  --data '[{"company": "Anthropic"}, {"company": "Mistral"}]' \
  --intent "Find headquarters and employee count" \
  --json
```

### 非交互式文件运行

```bash
parallel-cli enrich run \
  --source-type csv \
  --source companies.csv \
  --target enriched.csv \
  --source-columns '[{"name": "company", "description": "Company name"}]' \
  --intent "Find the CEO and annual revenue"
```

### 通过 YAML 配置运行

```bash
parallel-cli enrich run config.yaml
```

### 状态/轮询

```bash
parallel-cli enrich status <task_group_id> --json
parallel-cli enrich poll <task_group_id> --json
```

在非交互式操作时，应使用明确的 JSON 数组来定义列结构。在报告成功之前，务必先验证输出文件的正确性。

## FindAll

当用户需要的是完整的发现数据集而非简短答案时，可使用该功能进行大规模实体识别。

```bash
parallel-cli findall run "Find AI coding agent startups with enterprise offerings" --json
parallel-cli findall run "AI startups in healthcare" -n 25 --json
parallel-cli findall status <run_id> --json
parallel-cli findall poll <run_id> --json
parallel-cli findall result <run_id> --json
parallel-cli findall schema <run_id> --json
```

当用户希望获取一组可被进一步审查、筛选或丰富处理的已发现实体时，此方法比普通搜索更为适用。

## 监控功能

用于实时检测随时间发生的变更。

```bash
parallel-cli monitor list --json
parallel-cli monitor get <monitor_id> --json
parallel-cli monitor events <monitor_id> --json
parallel-cli monitor delete <monitor_id> --json
```

创建过程通常是较为敏感的环节，因为节奏与交付质量至关重要：

```bash
parallel-cli monitor create --help
```

当用户需要对该页面或来源进行持续跟踪而非仅执行一次性获取操作时，请使用此方法。

## 推荐的 Hermes 使用模式

### 带引用的高效回复
1. 运行 `parallel-cli search ... --json`
2. 解析标题、URL、日期及内容摘录
3. 仅使用返回的 URL 中的引用信息对内容进行总结

### URL 深入分析
1. 运行 `parallel-cli extract URL --json`
2. 如有需要，可使用 `--objective` 或 `--full-content` 选项重新运行
3. 对提取出的 Markdown 内容进行引用或总结

### 长期研究工作流
1. 运行 `parallel-cli research run ... --no-wait --json`
2. 保存返回的 ID
3. 继续处理其他任务或定期轮询状态
4. 带有引用信息对最终报告进行总结

### 结构化数据增强工作流
1. 检查输入文件及其列结构
2. 使用 `enrich suggest` 功能或直接指定需要增强的列
3. 运行 `enrich run` 命令
4. 如有需要，可轮询以确认任务是否完成
5. 在确认成功之前先验证输出文件

## 错误处理与退出码

CLI 已定义了以下退出码含义：
- `0`：操作成功
- `2`：输入数据错误
- `3`：认证错误
- `4`：API 错误
- `5`：超时

如果遇到认证错误：
1. 检查 `parallel-cli auth` 的运行状态
2. 确认 `PARALLEL_API_KEY` 的设置，或运行 `parallel-cli login` / `parallel-cli login --device` 命令
3. 确认 `parallel-cli` 已添加到系统 `PATH` 环境变量中

## 维护指南

查看当前的认证状态及安装情况：

```bash
parallel-cli auth
parallel-cli --help
```

更新命令：

```bash
parallel-cli update
pip install --upgrade parallel-web-tools
parallel-cli config auto-update-check off
```

## 常见问题与注意事项

- 除非用户明确要求以人类可读的格式获取输出，否则切勿省略 `--json` 参数。
- 不得引用 CLI 输出中未出现的来源信息。
- 执行 `login` 操作时可能需要终端或浏览器的交互支持。
- 对于较短时间的任务，建议在前台运行；避免过度使用后台进程。
- 当处理大量结果集时，应将 JSON 文件保存到 `/tmp/*.json` 目录中，而非将其全部加载到上下文中。
- 若 Hermes 的内置工具已能满足需求，切勿擅自选择并行处理模式。
- 请记住，这属于供应商提供的工作流，通常需要账号认证，并且超出免费套餐后还需支付费用。
