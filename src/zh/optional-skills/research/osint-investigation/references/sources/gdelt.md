# GDELT — 全球新闻监测服务

## 1. 概述

GDELT（全球事件、语言与情感数据库）通过全文索引功能，以100多种语言对全球新闻进行监测。数据每15分钟更新一次。涵盖时间范围从2015年至今，已索引文章数量超过10亿篇，支持免费匿名访问。

相较于Google News，GDELT的覆盖范围更广（包含更多国际媒体及长尾信息源），并且还能根据情感倾向、主题（CAMEO编码）、人物及机构对新闻进行分类索引。

## 2. 访问方式

- **DOC 2.0 API**：`https://api.gdeltproject.org/api/v2/doc/doc`
- **Events / GKG 2.0**：`https://api.gdeltproject.org/api/v2/events/events`
- **认证要求**：无需认证
- **请求频率限制**：DOC API允许的请求频率为**每5秒1次**，且限制极为严格

当收到429错误响应时，获取数据脚本会自动等待6秒后再次尝试。

## 3. 数据结构

`fetch_gdelt.py`脚本返回的关键字段如下：

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| `title` | str | 文章标题 |
| `url` | str | 文章链接 |
| `seen_date` | str | GDELT首次获取到该文章的时间（协调世界时） |
| `domain` | str | 文章发布平台的域名 |
| `language` | str | 文章来源语言 |
| `source_country` | str | 2位字母的国家代码 |
| `tone` | str | 由GDELT计算得出的情感倾向分数（负值表示负面报道） |
| `social_image` | str | 如有开放图谱图片，则为其URL地址 |

## 4. 覆盖范围

- 支持100多种语言的全球新闻
- 数据时间范围从2015年至今（部分历史事件通过独立数据流可追溯至1979年）
- 更新频率：每15分钟一次
- 偏见性分析：虽然以英语媒体报道为主，但整体信息源覆盖极为广泛

## 5. 跨系统关联潜力

- **所有信息源** ↔ `title` / `url`（可用于查找任意主题的相关新闻）
- **维基百科** ↔ 重要实体对应的时间线信息
- **网页归档机** ↔ 用于恢复已失效链接的文章内容
- **OFAC SDN名单** ↔ 制裁相关新闻的上下文信息
- **SEC EDGAR数据库** ↔ 8-K格式重大事件的相关新闻

关联键为文章标题或正文中出现的实体名称。GDELT还会将所有命名实体提取到另一个独立数据流（GKG）中，该数据流无法通过当前获取脚本查询——如需进行实体级筛选，可直接向GDELT发起请求。

## 6. 数据质量说明

- 文章标题的提取为自动化处理，可能存在误差（有时会包含网站名称、分隔符及文章标题；有时则为通用页面标题）
- 情感倾向分析由GDELT自行计算，并非来自新闻源本身
- 部分域名被过度采样（如新闻专线和内容聚合平台）
- 文章来源国家是根据域名注册信息或顶级域名推断的，对于使用中性域名的国际新闻网站，此信息可能不准确
- 文章链接可能会失效，建议结合网页归档机来保存文章内容

## 7. 数据获取脚本

脚本路径：`scripts/fetch_gdelt.py`

```bash
# Recent news mentioning an entity
python3 SKILL_DIR/scripts/fetch_gdelt.py --query "Nous Research" \
    --timespan 6m --out data/gdelt.csv

# Phrase-exact (use double quotes inside single quotes for the shell)
python3 SKILL_DIR/scripts/fetch_gdelt.py --query '"Dillon Rolnick"' \
    --timespan 1y --out data/gdelt.csv

# Filter to a country / language
python3 SKILL_DIR/scripts/fetch_gdelt.py --query "Microsoft" \
    --source-country US --source-lang English --out data/gdelt.csv

# Date range
python3 SKILL_DIR/scripts/fetch_gdelt.py --query "Microsoft" \
    --start 2024-01-01 --end 2024-12-31 --out data/gdelt.csv
```

GDELT提供了专属的查询运算符：短语引用、AND/OR/NOT运算，以及`sourcecountry:US`、`theme:ECON_BANKRUPTCY`、`tone<-5`等表达方式。具体语法请参阅https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/。

## 8. 法律与许可条款

- GDELT数据可免费供学术研究与新闻报道使用。
- 文章链接指向原始发布方，版权仍归发布方所有。
- GDELT并非内容档案库，而是一个元数据索引系统。

## 9. 参考资料

- DOC 2.0 API文档：https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- 主题与查询语法说明：https://blog.gdeltproject.org/gkg-2-0-our-global-knowledge-graph-2-0-amazing-data-at-your-fingertips/
- 项目官网：https://www.gdeltproject.org/
