# 参议院游说披露信息 —— 游说披露法案（LD-1 / LD-2）

## 1. 概述

根据1995年《游说披露法案》（LDA，后经2007年HLOGA修订），参议院公共记录办公室负责公开相关游说披露信息。LD-1用于登记新的客户与游说者之间的合作关系；LD-2则用于提交季度活动报告。

## 2. 访问方式

- **API接口**：`https://lda.senate.gov/api/v1/`（仅读取操作无需身份认证）
- **批量下载**：`https://lda.senate.gov/api/v1/filings/?format=csv`（支持分页下载）
- **身份认证**：若每小时请求量超过120次，则需要使用令牌——请在 https://lda.senate.gov/api/auth/register/ 进行注册
- **速率限制**：未认证时每小时120次请求，已认证时每小时1,200次请求

## 3. 数据结构

`fetch_senate_ld.py`函数返回的关键字段如下：

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| `filing_uuid` | str | 唯一的文件编号 |
| `filing_type` | str | LD-1、LD-2、LD-203等类型标识 |
| `filing_year` | int | 文件对应的年份 |
| `filing_period` | str | 季度（Q1/Q2/Q3/Q4）或年度 |
| `registrant_name` | str | 游说公司或组织名称 |
| `registrant_id` | str | 参议院分配的注册机构编号 |
| `client_name` | str | 所代表的客户名称 |
| `client_id` | str | 参议院分配的客户编号 |
| `client_general_description` | str | 客户所在的行业或业务领域 |
| `income` | float | 本季度来自该客户的LD-2报告中的收入（单位：美元） |
| `expenses` | float | LD-2报告中的内部游说支出 |
| `lobbyists` | str | 以分号分隔的游说者姓名列表 |
| `issues` | str | 以分号分隔的关注议题领域 |
| `government_entities` | str | 曾联系过的政府机构或商会名称 |
| `filing_date` | str | 文件提交日期，格式为YYYY-MM-DD |

## 4. 覆盖范围

- 仅涵盖美国联邦层面的游说活动（各州的游说事务由相应州的伦理监管机构负责）
- 数据时间跨度为1999年至今（2008年起实现全电子化记录）
- LD-2数据按季度提交
- 累计收录的文件数量超过100万份

## 5. 数据关联潜力

- **USAspending** ↔ `client_name`（为获取合同而进行游说的客户）
- **SEC EDGAR** ↔ `client_name`（作为游说客户的上市公司）
- **OFAC SDN** ↔ `client_name`（对游说客户进行制裁筛查）

数据关联键为标准化的`client_name`。在关联参议院内部记录时，`registrant_id`和`client_id`具有唯一性。

## 6. 数据质量说明

- 随着时间推移，许多游说者会因工作变动而出现在不同的注册机构名下
- `issues`和`government_entities`字段为自由文本格式，存在大小写不一致的情况
- 外国代理需通过FARA（司法部）机制进行注册，而非通过本平台
- 部分较旧的文件中，收入/支出数据是以10,000美元为区间来标注的

## 7. 数据获取脚本

脚本路径：`scripts/fetch_senate_ld.py`

```bash
# By client
python3 SKILL_DIR/scripts/fetch_senate_ld.py --client "EXAMPLE CORP" \
    --year 2024 --out data/lobbying.csv

# By registrant (lobbying firm)
python3 SKILL_DIR/scripts/fetch_senate_ld.py --registrant "BIG K STREET LLP" \
    --year 2024 --out data/lobbying.csv
```

如果您拥有相关令牌，请设置 `SENATE_LDA_TOKEN` 环境变量（或使用 `--token` 参数指定）。默认情况下为匿名模式，允许每小时发送 120 次请求。

## 8. 法律与许可条款

- 属于《美国法典》第 2 篇第 1604 条规定的公开记录（LDA）
- 无商业使用限制
- 可无条件重复使用——详情请参阅参议院公共记录办公室的免责声明

## 9. 参考资料

- API 文档：https://lda.senate.gov/api/redoc/v1/
- LDA 指南：https://lobbyingdisclosure.house.gov/ld_guidance.pdf
- 参议院公共记录网站：https://lda.senate.gov/
