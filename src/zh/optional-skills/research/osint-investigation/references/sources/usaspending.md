# USAspending — 联邦政府合同与拨款信息

## 1. 概述

USAspending.gov 是联邦支出数据的官方来源。涵盖的内容包括：合同、拨款、贷款、直接支付以及子拨款。根据2014年《数据法案》的规定，所有联邦机构都必须按照统一的格式进行数据上报。

## 2. 访问方式

- **API v2**：`https://api.usaspending.gov/api/v2/`（无需认证，也无需密钥）
- **批量下载**：`https://files.usaspending.gov/`（按拨款类型提供CSV或Parquet格式文件）
- **认证要求**：无
- **速率限制**：虽未严格规定，但建议控制请求频率在每秒10次以内

## 3. 数据结构

`fetch_usaspending.py` 函数返回的主要字段（针对主级拨款）如下：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `award_id` | str | 联邦拨款编号（合同为PIID，拨款为FAIN） |
| `recipient_name` | str | 中标方的法定名称 |
| `recipient_uei` | str | 唯一实体标识符（2022年起取代DUNS编号） |
| `recipient_duns` | str | 旧版DUNS编号（仅用于历史查询） |
| `recipient_parent_name` | str | 最终上级机构名称 |
| `recipient_state` | str | 中标方所在州 |
| `awarding_agency` | str | 授款部门或机构名称 |
| `awarding_sub_agency` | str | 下属层级机构（例如国防部→陆军） |
| `award_type` | str | 授款类型：合同、拨款、贷款、直接支付 |
| `award_amount` | float | 当前的美元总负债金额 |
| `award_date` | str | 授款或签约日期，格式为YYYY-MM-DD |
| `period_of_performance_start` | str | 项目执行开始日期，格式为YYYY-MM-DD |
| `period_of_performance_end` | str | 项目执行结束日期，格式为YYYY-MM-DD |
| `naics_code` | str | 行业分类代码 |
| `psc_code` | str | 产品或服务代码 |
| `competition_extent` | str | 招标方式：公开招标、限制招标或单一来源招标 |
| `description` | str | 授款详情描述（文本形式） |

## 4. 覆盖范围

- 仅涵盖美国联邦级拨款（不包括州级及地方级拨款）
- 数据时间范围为2008财年至今（2017财年数据完整覆盖）
- 每两周根据各机构上报的数据进行更新
- 累计记录量超过1亿条

## 5. 跨数据源关联参考

- **SEC EDGAR** ↔ `recipient_name`（作为承包商的上市公司信息）
- **Senate LD** ↔ `recipient_name`（获得合同的游说团体信息）
- **OFAC SDN** ↔ `recipient_name`（对承包商的制裁筛查——虽应通过SAM.gov过滤，但仍需自行核实）
- **ICIJ Offshore** ↔ `recipient_name`（与海外机构有关联的承包商信息）

关联键为标准化的中标方名称；若存在UEI编号，则以该编号作为唯一标识。

## 6. 数据质量说明

- 2022年4月完成了从DUNS编号到UEI编号的转换——旧记录仍使用DUNS编号，新记录则使用UEI编号
- 部分子拨款项目不会被上报（FFATA项目的金额门槛为3万美元）
- 授款金额会随着后续的修改而变化——获取脚本会返回当前的总金额
- 早期记录中的`competition_extent`字段为文本形式——`fetch_usaspending.py`函数会将其标准化为统一值
- 中标方名称存在大量变体，如“ACME LLC”、“Acme L.L.C.”、“ACME, INC”等，均可能出现。建议使用`entity_resolution.py`工具进行名称标准化处理。

## 7. 数据获取脚本

脚本路径：`scripts/fetch_usaspending.py`

```bash
# By recipient name
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --out data/contracts.csv

# By awarding agency
python3 SKILL_DIR/scripts/fetch_usaspending.py --agency "Department of Defense" \
    --fy 2024 --out data/contracts.csv

# Filter to sole-source only
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --sole-source-only --out data/contracts.csv
```

## 8. 法律与许可条款

- 根据《联邦资金问责与透明度法案》（FFATA，2006年）及《数据法案》（2014年），相关数据属于公开记录。
- 这些数据不存在任何商业使用限制。
- 对于获奖者的个人信息（例如某些资助项目中的小型企业主地址），应按照相关资助机构的隐私政策进行处理。

## 9. 参考资料

- API文档：https://api.usaspending.gov/
- 数据字典：https://www.usaspending.gov/data-dictionary
- 资助数据结构说明：https://files.usaspending.gov/docs/Data_Dictionary_Crosswalk.xlsx
