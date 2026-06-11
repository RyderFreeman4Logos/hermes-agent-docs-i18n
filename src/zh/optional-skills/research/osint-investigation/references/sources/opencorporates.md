# OpenCorporates — 全球企业注册信息平台

## 1. 简介

OpenCorporates汇集了全球130多个司法管辖区的企业注册数据（涵盖约2亿家公司）。其数据来源包括美国各州的注册信息（如纽约州商业登记处、特拉华州公司登记处、加利福尼亚州商业登记处等）、英国公司注册局、欧盟各国的企业注册系统，以及大多数普通法司法管辖区的注册数据。

## 2. 访问方式

- **REST API：** `https://api.opencorporates.com/v0.4/`
- **HTML备用接口：** `https://opencorporates.com/companies?q=...`
- **认证要求：** 需要API令牌（免费套餐每月允许500次调用，也可选择付费方案）
- **速率限制：** 由令牌数量决定；未使用令牌的请求会返回401错误

请设置`OPENCORPORATES_API_TOKEN`环境变量。可通过https://opencorporates.com/api_accounts/new获取免费令牌。

## 3. 数据结构

`fetch_opencorporates.py`脚本返回的关键字段如下：

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| `name` | str | 公司法定名称 |
| `company_number` | str | 注册机构分配的编号 |
| `jurisdiction_code` | str | 例如`us_ny`、`us_de`、`gb` |
| `jurisdiction_name` | str | 易于理解的司法管辖区名称 |
| `incorporation_date` | str | 成立日期，格式为YYYY-MM-DD |
| `dissolution_date` | str | 注销日期，格式为YYYY-MM-DD；若公司仍在运营则为空 |
| `company_type` | str | 国内有限责任公司/外国公司等类型 |
| `status` | str | 运营中/已停业/已注销 |
| `registered_address` | str | 注册地址 |
| `opencorporates_url` | str | 对应OpenCorporates平台上的企业页面链接 |
| `officers_count` | str | 已记录的董事总数 |
| `source` | str | 数据来源，值为`api`、`html`或`html-fallback` |

## 4. 覆盖范围

- **美国：** 所有50个州以及华盛顿特区，涵盖有限责任公司、公司制企业及有限合伙企业等类型
- **国际地区：** 英国、欧盟各国、加拿大、澳大利亚、新西兰，以及许多亚太和拉丁美洲司法管辖区
- 累计包含约2亿条公司记录
- 不同司法管辖区的数据更新频率有所差异（英国公司注册局的数据近乎实时；部分州级注册系统的更新则可能滞后数月）

## 5. 交叉引用可能性

以下平台的数据可通过标准化公司名称实现关联查询：
- **NYC ACRIS** ↔ `name`（纽约市房产的有限责任公司/公司所有者信息）
- **USAspending** ↔ `name`（联邦政府采购中的企业信息）
- **SEC EDGAR** ↔ `name`（上市公司及其子公司信息）
- **ICIJ Offshore** ↔ `name`（国际企业结构信息）

部分记录还包含`previous_names`数组，记录历史名称变更情况，但当前该字段未被`fetch_opencorporates.py`脚本导出，如需查询请直接访问OpenCorporates平台。

## 6. 数据质量说明

- 由于公司多次重组或更名，其名称拼写可能有所不同
- 董事信息相比公司整体信息的完整性较低（许多司法管辖区并不要求公开董事信息）
- 一般不包含实益所有权数据——因为大多数司法管辖区并未强制要求披露此类信息。英国公司注册局虽提供PSC（具有重大控制权的人士）信息，但并非所有地区都实行此项制度
- 司法管辖区间的关联关系（如母公司/子公司关系）仅基于注册机构提交的文件，因此企业结构图往往不够完整

## 7. 数据获取脚本

脚本路径：`scripts/fetch_opencorporates.py`

```bash
# Search globally by name
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --out data/oc.csv

# Restrict to a jurisdiction
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --jurisdiction us_ny --out data/oc_ny.csv

# Set token via env or flag
OPENCORPORATES_API_TOKEN=xxx python3 SKILL_DIR/scripts/fetch_opencorporates.py \
    --query "Microsoft" --out data/oc.csv
```

若未提供令牌，脚本将回退至抓取 HTML 搜索页面的方式。但这种替代方案稳定性较差，仅能获取 `name`、`jurisdiction_code` 和 `opencorporates_url` 等字段——如需进行正式操作，请务必设置令牌。

## 8. 法律与许可说明

- OpenCorporates 整合的是公开记录，其底层数据属于公共领域。
- OpenCorporates 自有的数据库采用 CC-BY-SA-4.0 许可协议，使用时必须注明出处。
- API 服务条款禁止重新分发完整数据集，但单独引用每条记录则是允许的。

## 9. 参考资料

- API 文档：https://api.opencorporates.com/documentation/API-Reference
- 管辖区域代码：https://api.opencorporates.com/v0.4/jurisdictions.json
- 数据结构规范：https://opencorporates.com/info/our_data
