# SEC EDGAR — 公司备案文件

## 1. 概述

EDGAR（电子数据收集、分析与检索系统）是美国证券交易委员会用于公司信息披露备案的官方系统，涵盖以下文件类型：10-K（年度报告）、10-Q（季度报告）、8-K（重大事件报告）、DEF 14A（代理人委托书）、Form 4（内幕交易报告）以及13F（机构持仓报告）。

## 2. 访问方式

- **API接口**：`https://data.sec.gov/submissions/CIK<补足为10位数的编号>.json`（无需身份验证）
- **备案文件索引页面**：`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=...`
- **全文搜索功能**：`https://efts.sec.gov/LATEST/search-index?q=...`
- **身份验证要求**：根据SEC规定，无需身份验证，但需在请求头中添加包含联系信息的`User-Agent`字段
- **速率限制**：每个IP地址每秒最多可发送10次请求（该限制会严格执行）

## 3. 数据结构

`fetch_sec_edgar.py`工具生成的备案文件索引中的关键字段如下：

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| `cik` | 字符串 | 中央索引键（需补足为10位数字） |
| `company_name` | 字符串 | 公司注册名称 |
| `form_type` | 字符串 | 文件类型，如10-K、10-Q、8-K等 |
| `filing_date` | 字符串 | 文件提交日期，格式为YYYY-MM-DD |
| `accession_number` | 字符串 | 备案文件编号，例如0000320193-24-000123 |
| `primary_document` | 字符串 | 主文件的名称 |
| `filing_url` | 字符串 | 备案文件在索引页面上的直接链接 |
| `reporting_period` | 字符串 | 报告所涵盖的周期（如适用） |

## 4. 覆盖范围

- 涵盖1993年至今所有在美国注册的上市公司
- 1993年至2000年的部分早期备案文件可能因系统从纸质转向电子化而存在缺失
- 累计收录的备案文件数量约1200万份
- 文件一旦被接受，相关数据会在几分钟内更新完毕

## 5. 跨系统关联参考

以下系统可通过`company_name`与EDGAR数据实现关联：
- **USAspending**：用于查询作为联邦承包商的上市公司信息
- **Senate LD**：用于查询聘请说客的上市公司信息
- **OFAC SDN**：用于对上市企业进行制裁筛查

关联键为公司名称，如有中央索引键（CIK）则也可使用；其中CIK是标准且稳定的标识符。

## 6. 数据质量说明

- 子公司通常会使用其母公司的CIK进行备案，因此在通过名称进行匹配时需格外谨慎
- 公司名称可能会因品牌调整或并购而发生变化，但CIK保持不变
- 10-K报告中的第1A项“风险因素”为自由文本格式，适合用于类似`web_extract`的文本解析方式，但不适用于结构化查询
- 外国私人发行机构会提交20-F表格而非10-K表格

## 7. 数据获取脚本

脚本路径：`scripts/fetch_sec_edgar.py`

```bash
# By CIK
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --cik 0000320193 \
    --types 10-K,10-Q --out data/edgar_filings.csv

# By company name (resolves to CIK first via name search)
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --company "APPLE INC" \
    --types 8-K --since 2024-01-01 --out data/edgar_filings.csv
```

请将您的联系邮箱设置到 `SEC_USER_AGENT` 环境变量中（这是美国证券交易委员会的要求）。  
示例：`SEC_USER_AGENT="Research example@example.com"`。

## 8. 法律与许可条款

- 需遵守美国证券交易委员会规则 24b-2 / 17 CFR § 230.401 的公开记录规定  
- 提交的内容无需遵守任何商业用途限制  
- 美国证券交易委员会要求所有批量用户必须在请求中包含包含联系信息的 `User-Agent`，并遵守每秒 10 次请求的限制——未能遵守此规定可能会导致 IP 被封禁

## 9. 参考资料

- 开发者文档：https://www.sec.gov/edgar/sec-api-documentation  
- EDGAR 全文检索功能：https://efts.sec.gov/LATEST/search-index  
- 公平访问政策：https://www.sec.gov/os/accessing-edgar-data
