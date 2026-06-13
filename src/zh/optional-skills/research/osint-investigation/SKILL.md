---
name: osint-investigation
description: Public-records OSINT investigation framework — SEC EDGAR filings, USAspending contracts, Senate lobbying, OFAC sanctions, ICIJ offshore leaks, NYC property records (ACRIS), OpenCorporates registries, CourtListener court records, Wayback Machine archives, Wikipedia + Wikidata, GDELT news monitoring. Entity resolution across sources, cross-link analysis, timing correlation, evidence chains. Python stdlib only.
version: 0.1.0
platforms: [linux, macos, windows]
author: Hermes Agent (adapted from ShinMegamiBoson/OpenPlanter, MIT)
metadata:
  hermes:
    tags: [osint, investigation, public-records, sec, sanctions, corporate-registry, property, courts, due-diligence, journalism]
    category: research
    related_skills: [domain-intel, arxiv]
---

# OSINT调查——公共记录交叉验证

针对公共记录类OSINT的调查框架，涵盖政府合同、企业备案信息、游说活动、制裁措施、海外数据泄露事件、房产记录、法庭记录、网页存档、知识库以及全球新闻等内容。该工具能够跨不同来源识别实体，以明确的置信度建立关联链接，执行统计时间分析，并生成结构化的证据链。

**仅依赖Python标准库，无需任何安装，可在Linux、macOS和Windows系统上运行。大多数数据源无需API密钥即可使用（OpenCorporates提供可选的免费令牌，但会限制调用频率）。**

该功能基于采用MIT许可协议的ShinMegamiBoson/OpenPlanter项目开发，并对其进行了扩展，新增了原项目未涉及的身份信息、房产信息、诉讼记录、档案资料及新闻来源等查询功能。

## 何时使用此功能

当用户提出以下需求时可使用该功能：

- “追踪资金流向”——从政府合同、游说活动到立法进程及制裁措施
- 企业尽职调查——了解谁控制着某家公司、其注册地址位于何处、董事会成员是谁、以及该公司提交了哪些备案文件
- 制裁筛查——查询某实体是否被列入OFAC SDN名单或ICIJ的海外数据泄露名单中
- “付费寻租”行为调查——调查与海外有关联的承包商，以及通过游说获得项目的客户
- 房产所有权查询——根据姓名或地址查找已登记的房产契约/抵押贷款信息（适用于纽约市；其他地区的用户可被引导至相应的登记机构）
- 诉讼历史查询——检索联邦及州级法院的判决文书及PACER系统中的案件档案
- 处理名称表述不一致的多源实体识别问题（如LLC后缀、缩写等）
- 以明确置信度构建证据链
- “关于X有哪些报道”——整合国际新闻（GDELT数据库）、维基百科内容以及Wayback Machine工具以找回已失效的网页链接

**以下场景请勿使用此功能：**

- 常规网络搜索 → 使用`web_search`/`web_extract`功能
- 域名/基础设施类OSINT调查 → 使用`domain-intel`功能
- 学术文献检索 → 使用`arxiv`功能
- 社交媒体账号查找 → 可选使用`sherlock`功能
- 美国**联邦**层面竞选财务信息查询——此处故意未涵盖FEC相关数据（免费DEMO_KEY版本的API在针对特定捐款人名称进行查询时可靠性较低）。如需查询联邦层面的捐款信息，请引导用户直接访问https://www.fec.gov/data/。

## 工作流程

该智能体通过`terminal`工具执行脚本，`SKILL_DIR`目录则存放着此SKILL.md文件。

### 1. 确定适用的数据来源

首先阅读各数据源的Wiki说明，以此规划后续的调查方案：

```
ls SKILL_DIR/references/sources/

# Federal financial / regulatory
cat SKILL_DIR/references/sources/sec-edgar.md       # corporate filings
cat SKILL_DIR/references/sources/usaspending.md     # federal contracts
cat SKILL_DIR/references/sources/senate-ld.md       # lobbying
cat SKILL_DIR/references/sources/ofac-sdn.md        # sanctions
cat SKILL_DIR/references/sources/icij-offshore.md   # offshore leaks

# Identity / property / litigation / archives / news
cat SKILL_DIR/references/sources/nyc-acris.md       # NYC property records
cat SKILL_DIR/references/sources/opencorporates.md  # global corporate registry
cat SKILL_DIR/references/sources/courtlistener.md   # court records (federal + state)
cat SKILL_DIR/references/sources/wayback.md         # Wayback Machine archives
cat SKILL_DIR/references/sources/wikipedia.md       # Wikipedia + Wikidata
cat SKILL_DIR/references/sources/gdelt.md           # global news monitoring
```

每条数据条目均遵循包含9个部分的模板结构：摘要、访问方式、数据架构、覆盖范围、交叉引用键、数据质量、数据获取方式、法律相关事项以及参考资料。

**交叉引用潜力**部分用于标识不同数据源之间的关联键——请先阅读该部分，以便选择合适的配对组合。

### 2. 数据获取

每个数据源在 `SKILL_DIR/scripts/` 目录下都配有仅依赖标准库的获取脚本：

**联邦金融/监管领域**

```bash
# SEC EDGAR filings (corporate disclosures)
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --cik 0000320193 \
    --types 10-K,10-Q --out data/edgar_filings.csv

# USAspending federal contracts
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --out data/contracts.csv

# Senate LD-1 / LD-2 lobbying disclosures
python3 SKILL_DIR/scripts/fetch_senate_ld.py --client "EXAMPLE CORP" \
    --year 2024 --out data/lobbying.csv

# OFAC SDN sanctions list (full snapshot)
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --out data/ofac_sdn.csv

# ICIJ Offshore Leaks — downloads ~70 MB bulk CSV on first use,
# then searches it locally. Cached for 30 days under
# $HERMES_OSINT_CACHE/icij/ (default: ~/.cache/hermes-osint/icij/).
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --out data/icij.csv
```

**身份信息/财产状况/诉讼案件/档案记录/新闻资讯**

```bash
# NYC property records (deeds, mortgages, liens) — ACRIS via Socrata
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "SMITH, JOHN" \
    --out data/acris.csv
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --address "571 HUDSON" \
    --out data/acris_addr.csv

# OpenCorporates — 130+ jurisdiction corporate registry
# (free token required; set OPENCORPORATES_API_TOKEN or pass --token)
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --jurisdiction us_ny --out data/opencorporates.csv

# CourtListener — federal + state court opinions, PACER dockets
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Smith v. Example Corp" \
    --type opinions --out data/courts.csv

# Wayback Machine — historical web captures
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --collapse digest --out data/wayback.csv

# Wikipedia + Wikidata — narrative bio + structured facts
# Set HERMES_OSINT_UA=your-app/1.0 (your@email) to identify yourself
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Bill Gates" \
    --out data/wp.csv

# GDELT — global news in 100+ languages, ~2015→present
python3 SKILL_DIR/scripts/fetch_gdelt.py --query '"Example Corp"' \
    --timespan 1y --out data/gdelt.csv
```

所有输出均为带有表头行的标准化 CSV 格式。脚本可重复运行且具备幂等性。

当查询对象并非来自特定数据源中的机构时（例如非上市公司的相关信息来自 SEC EDGAR，非联邦承包商的信息来自 USAspending，非游说客户的信息来自 Senate LDA），脚本会返回 0 行数据并给出明确警告，而不会悄悄生成空 CSV 文件。EDGAR 还会特别标明：当公司名称解析结果对应的是个人提交的 3/4/5 号表格，而非企业注册主体时。

各数据源的文档中均有关于速率限制的说明。默认的获取工具会在分页请求之间适当等待。对于支持 API 密钥的数据源（如 `SEC_USER_AGENT`、`SENATE_LDA_TOKEN`、`OPENCORPORATES_API_TOKEN`、`COURTLISTENER_TOKEN`），使用这些密钥会提升对应数据源的速率限制。所有脚本都会立即返回 429 错误响应，并附带上游服务端的限额提示，以便用户知晓需要降低请求频率或提供相应的 API 密钥。

### 3. 跨数据源解析实体

对名称进行标准化处理，并在两个 CSV 文件之间查找匹配项：

```bash
# Match lobbying clients (Senate LDA) against contract recipients (USAspending)
python3 SKILL_DIR/scripts/entity_resolution.py \
    --left  data/lobbying.csv   --left-name-col  client_name \
    --right data/contracts.csv  --right-name-col recipient_name \
    --out data/cross_links.csv
```

三种具有明确置信度的匹配等级：

| 等级 | 方法 | 置信度 |
|------|------|--------|
| `exact` | 去除后缀/标点符号后字符串完全一致 | 高 |
| `fuzzy` | 排序后的词元相等性（词袋匹配） | 中 |
| `token_overlap` | 词元重叠率≥60%，共有词元≥2个，且每个词元长度≥4字符 | 低 |

`cross_links.csv` 的输出列包括：`match_type, confidence, left_name, right_name, left_normalized, right_normalized, left_row, right_row`。

### 4. 统计时间相关性分析（可选）

通过排列检验来判断两个时间序列是否异常地紧密聚集在一起——例如在合同授予前后出现的游说活动记录——以此识别潜在的关联。

```bash
python3 SKILL_DIR/scripts/timing_analysis.py \
    --donations data/lobbying.csv --donation-date-col filing_date \
        --donation-amount-col income --donation-donor-col client_name \
        --donation-recipient-col registrant_name \
    --contracts data/contracts.csv --contract-date-col award_date \
        --contract-vendor-col recipient_name \
    --cross-links data/cross_links.csv \
    --permutations 1000 \
    --out data/timing.json
```

该脚本所使用的列标记被刻意设计为通用格式——虽然该工具最初是为处理捐赠与奖励相关的数据而开发的，但只要通过交叉链接将任意（活动、收款方）时间序列关联起来，它同样适用。其零假设为：活动发生时间与奖励发放日期相互独立。单尾p值表示在所有排列组合中，平均最近奖励距离小于或等于观测值的占比。每对（付款方、供应商）至少需要3个数据点才能运行此测试。

### 5. 生成结果JSON文件（证据链）

```bash
python3 SKILL_DIR/scripts/build_findings.py \
    --cross-links data/cross_links.csv \
    --timing data/timing.json \
    --out data/findings.json
```

每个检测结果均包含 `id、title、severity、confidence、summary、evidence[]、sources[]` 这些字段。  
每条证据项都会指向源 CSV 文件中的特定行，用户（或后续处理的智能体）可据此验证每一项结论的来源。

## 置信度与证据的规范

这是该智能体功能的核心准则。需向用户明确说明：  
- 每一项结论都必须有对应的记录依据，不得出现无根据的断言。  
- 置信度等级会随结论一同呈现。`match_type=fuzzy` 表示“可能”，而非“已确认”。  
- 实体识别仅能生成候选项，而非最终结论。“ACME LLC”与“Acme Holdings Group”之间的“模糊”匹配仅属于线索，而非事实。  
- 统计显著性并不等同于违规行为。p < 0.05 仅表示在零假设前提下该时间模式出现的可能性较低，但并不能证明存在舞弊行为。  
- 此处所有数据来源均为公开记录，但仍可能存在不准确之处、过时信息或被屏蔽的内容（如受 GDPR 规范保护的记录或密封文件）。

## 添加新的数据来源

请使用以下模板：

```bash
cp SKILL_DIR/templates/source-template.md \
    SKILL_DIR/references/sources/<your-source>.md
```

请填写全部9个字段。在`scripts/`目录下编写一个`fetch_<source>.py`脚本，该脚本仅能使用标准库功能，并生成格式规范的CSV文件。同时，请更新上方“适用场景”部分中的数据源列表。

## 工具及其限制

- `entity_resolution.py`不依赖任何外部模糊匹配库（如rapidfuzz或jellyfish），其最大匹配精度为词袋匹配。若需要Levenshtein算法、转写功能或语音匹配功能，需单独通过pip安装相关库。
- `timing_analysis.py`在生成排列组合时使用了Python的`random`模块。为确保结果可复现，请通过`--seed N`参数指定随机种子值。
- `fetch_*.py`脚本使用`urllib.request`进行请求，并会遵守服务器返回的`Retry-After`重试指示。尽管如此，大规模批量调用仍可能违反服务条款——请先仔细阅读每个数据源的相关法律说明。

## 法律声明

所有第一阶段的数据源均为公开记录，根据各自的访问规定（如《信息自由法》、公共记录法、国际刑事调查合作组织的公开发布规则以及美国外国资产控制委员会的公开数据政策），允许进行批量获取。但需注意以下几点：

- 部分数据源会设置严格的访问频率限制，请务必遵守其服务器返回的头部信息。
- 部分数据源会对注册人信息进行匿名处理（如WHOIS数据中的GDPR保护措施，以及被封存的备案文件）。
- 将公开记录相互关联以识别个人身份可能涉及伦理问题。该工具仅用于生成证据链，而非用于提出指控。
