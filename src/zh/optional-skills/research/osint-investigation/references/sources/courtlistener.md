# CourtListener — 免费法律项目

## 1. 简介

CourtListener（免费法律项目）汇集了法院判决、案件清单、口头辩论记录以及法官相关数据。其收录的内容涵盖自殖民地时期以来的约1000万份联邦及州级法院判决，同时还包含通过RECAP系统上传的PACER案件清单数据。

## 2. 访问方式

- **REST API v4**：`https://www.courtlistener.com/api/rest/v4/`
- **认证**：大多数接口允许匿名访问；使用令牌可提升请求频率上限，并支持批量数据导出
- **请求频率限制**：未认证用户搜索时的请求频率约为每小时5,000次；使用令牌后可进一步提升频率

请设置 `COURTLISTENER_TOKEN` 环境变量。您可访问 https://www.courtlistener.com/sign-in/ 获取免费令牌，随后创建API密钥。

## 3. 数据结构

`fetch_courtlistener.py` 函数返回的关键字段如下：

| 字段名 | 类型 | 描述 |
|--------|------|-------------|
| `case_name` | str | 案件名称 |
| `court` | str | 法院名称 |
| `court_id` | str | 法院编号（例如 `nysd`、`scotus`、`ca9`） |
| `date_filed` | str | 提出诉讼的日期，格式为YYYY-MM-DD |
| `docket_number` | str | 法院案件编号 |
| `judge` | str | 法官姓名 |
| `citation` | str | 法律文献引用信息 |
| `result_type` | str | 数据类型，包括判决、案件清单、口头辩论记录及人员信息 |
| `snippet` | str | 搜索匹配的摘要内容（最多500个字符） |
| `absolute_url` | str | CourtListener平台的直接链接地址 |

## 4. 覆盖范围

- **联邦法院**：所有巡回法院和地区法院以及最高法院
- **州级法院**：50个州的最高法院及上诉法院，以及众多初审法院
- **判决记录**：可追溯至17世纪（殖民地时期）的约1000万份判决记录，1950年至今的判决则实现全覆盖
- **案件清单**：通过RECAP系统收录的来自用户上传的PACER PDF文件的超过300万条记录
- 数据持续更新中

## 5. 跨系统关联潜力

- **OpenCorporates** ↔ `case_name`（企业诉讼相关数据）
- **SEC EDGAR** ↔ `case_name`（证券集体诉讼相关数据）
- **OFAC SDN** ↔ `case_name`（制裁相关的民事/刑事案件数据）

关联键为 `case_name` 中的当事人名称。需要注意的是，`case_name` 通常采用缩写形式（如“Smith v. Jones”而非完整的当事人名称）——如需获取所有当事人信息，请使用该案件的完整URL。

## 6. 数据质量说明

- 较早的判决记录（1990年之前）往往缺少案件编号和法官信息
- 州级法院的覆盖范围相比联邦法院更为不均衡
- PACER案件清单的完整性取决于RECAP系统的用户上传情况，因此并非全部涵盖
- 保密文件不会被收录
- 案件描述中的当事人名称有时与起诉时的名称并不完全一致

## 7. 数据获取脚本

脚本路径：`scripts/fetch_courtlistener.py`

```bash
# Search opinions for a party / keyword
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Example Corp" \
    --out data/cl.csv

# PACER dockets (best for recent litigation)
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Example Corp" \
    --type dockets --out data/cl_dockets.csv

# Restrict to a court
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Microsoft" \
    --court ca9 --out data/cl_9th.csv

# Date range
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Example Corp" \
    --date-from 2020-01-01 --date-to 2024-12-31 --out data/cl.csv
```

请传递 `--token` 参数或设置 `COURTLISTENER_TOKEN`。

## 8. 法律与许可说明

- 法院判决文本属于公共领域
- Free Law Project依据CC0协议/公共领域授权提供相关数据
- 判决文本及元数据均无商业使用限制
- 部分PACER系统的PDF文件其排版（而非文本内容）受版权保护——可适用合理使用原则

## 9. 参考资料

- API文档：https://www.courtlistener.com/help/api/rest/
- 法院代码查询：https://www.courtlistener.com/api/jurisdictions/
- RECAP档案库：https://www.courtlistener.com/recap/
- 批量数据接口：https://www.courtlistener.com/help/api/bulk-data/
