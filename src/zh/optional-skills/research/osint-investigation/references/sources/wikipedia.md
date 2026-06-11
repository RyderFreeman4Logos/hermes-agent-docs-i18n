# 维基百科 + 维基数据

## 1. 概述

维基百科是记录知名人物、地点及组织的权威叙事型资料来源。而维基数据则是其结构化数据的对应版本：包含约1.1亿条数据项，每条数据项都配有各种属性值、日期、标识符，以及指向外部权威数据库（如VIAF、ISNI、ORCID、GRID等）的交叉引用。

二者共同构成了高精度的实体识别层——只有符合特定标准的内容才会被收录，而所有被收录的实体都拥有完善的交叉引用关系。

## 2. 访问方式

- **维基百科 OpenSearch：** `https://en.wikipedia.org/w/api.php?action=opensearch`
- **维基百科 REST摘要接口：** `https://en.wikipedia.org/api/rest_v1/page/summary/<title>`
- **维基数据操作API：** `https://www.wikidata.org/w/api.php?action=wbgetentities`
- **维基数据SPARQL查询接口：** `https://query.wikidata.org/sparql`（功能更强大，但限流较为严格）
- **认证要求：** 无需认证，但**必须使用具有明确标识意义的User-Agent**

建议将 `HERMES_OSINT_UA` 设置为能体现来源信息的值，例如 `your-app/1.0 (you@example.com)`。对于通用型User-Agent，维基媒体基金会会返回HTTP 429限流响应。

## 3. 数据结构

`fetch_wikipedia.py`脚本生成的字段如下：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `source` | str | `wikipedia` 或 `wikipedia+wikidata` |
| `label` | str | 维基百科文章标题 |
| `description` | str | 维基数据中的简短描述 |
| `qid` | str | 维基数据QID（例如微软的QID为Q2283） |
| `wikipedia_title`、`wikipedia_url` | str | 文章标识符及对应URL |
| `wikidata_url` | str | 维基数据实体页面的URL |
| `instance_of` | str | 实体所属类别（基于P31标准） |
| `country` | str | 国家信息（组织/地点用P17，人物用P27） |
| `occupation` | str | 职业信息（基于P106标准） |
| `employer` | str | 所属机构信息（基于P108标准） |
| `date_of_birth` | str | 出生日期，格式为YYYY-MM-DD |
| `place_of_birth` | str | 出生地信息（基于P19标准） |
| `summary` | str | 从维基百科REST接口提取的摘要内容，长度约1000字符 |

该获取脚本使用维基数据的操作API（而非SPARQL）来获取结构化事实数据，因此限流限制相对宽松。

## 4. 覆盖范围

- 维基百科英文版：约700万篇文章
- 维基数据：约1.1亿条数据项，约15亿条属性描述
- 数据持续更新，同时有滥用过滤机制和自动化脚本实时监控
- 入选标准较为严格，大多数普通个人并未在维基百科上有相关条目

## 5. 交叉引用潜力

- **所有数据源** ↔ `label`（用于实体身份识别）
- **美国证券交易委员会EDGAR数据库** ↔ `label`（用于查找上市公司信息）
- **CourtListener网站** ↔ `label`（用于查找重大诉讼的涉事方）
- **维基数据的外部标识符**（当前该获取脚本暂不输出）：可链接到VIAF、ISNI、ORCID、GRID、GitHub、Twitter、IMDb等数据库

关联键规则：维基数据QID为标准唯一标识。大多数文章的维基百科标题保持稳定，但也可能存在重命名情况。

## 6. 数据质量

- **知名度过滤**：仅收录具有较高知名度的实体（不同主题的入选标准有所差异）
- **更新延迟**：时事内容可能需要数天到数周才能被收录
- **视角偏差/恶意篡改**：内容会经过审核，但在两次审核间隔期间可能仍存在问题
- **在世人物传记**有更严格的资料来源要求
- 维基数据中的属性值通常带有限定条件及参考链接，但当前该获取脚本暂不导出这些信息

## 7. 数据获取脚本

路径：`scripts/fetch_wikipedia.py`

```bash
# Look up a notable entity
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Microsoft" --out data/wp.csv

# A specific person
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Bill Gates" --out data/wp_bg.csv

# Skip the Wikidata enrichment for speed
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Microsoft" --no-wikidata \
    --limit 5 --out data/wp.csv
```

OpenSearch 的匹配机制属于模糊匹配类型——使用 `--limit 5` 参数即可获取与维基百科文章最相似的前 5 个结果。除非指定了 `--no-wikidata` 参数，否则每个匹配结果都会附带 QID 以及结构化事实信息。

## 8. 法律与许可条款

- 维基百科文本：CC-BY-SA-3.0 / GFDL 许可协议
- Wikidata 数据：CC0（公共领域）许可
- API 服务条款：需遵守速率限制要求，并明确标注您的代理信息
- 允许在注明出处的情况下进行商业用途使用

## 9. 参考资料

- 维基百科 OpenSearch 接口：https://www.mediawiki.org/wiki/API:Opensearch
- 维基百科 REST 接口：https://en.wikipedia.org/api/rest_v1/
- Wikidata 操作 API：https://www.wikidata.org/wiki/Wikidata:Data_access
- Wikidata SPARQL 查询接口：https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
- 用户代理政策：https://meta.wikimedia.org/wiki/User-Agent_policy
