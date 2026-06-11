# ICIJ离岸信息泄露数据库

## 1. 概述

国际调查记者联盟（ICIJ）整合了“巴拿马文件”“天堂文件”“潘多拉文件”“巴哈马泄露事件”以及“其他离岸信息泄露案例”中的离岸实体数据，形成了一个综合数据库。该数据库包含约80万多个离岸实体及其相关负责人、中间人信息与地址。

## 2. 访问方式

- **批量下载（主要方式）：** `https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip`（约70 MB的ZIP文件，会定期更新）
- **搜索界面（人工操作）：** `https://offshoreleaks.icij.org/`
- **认证要求：** 无需认证
- **注意：** 之前用于数据对齐的Open Refine接口 `/reconcile`现已返回404错误，ICIJ已将其移除。目前仅剩的稳定访问方式仍是批量ZIP文件。该技能中的 `fetch_icij_offshore.py` 脚本会将ZIP文件缓存在本地（默认路径为 `~/.cache/hermes-osint/icij/`，每30天更新一次），从而实现离线查询。

## 3. 数据结构

`fetch_icij_offshore.py` 脚本生成的字段如下：

| 字段名 | 类型 | 描述 |
|--------|------|-------------|
| `node_id` | int | ICIJ标准的节点编号 |
| `name` | str | 实体/负责人/中间人的名称 |
| `node_type` | str | 实体/负责人/中间人/地址的类型 |
| `country_codes` | str | 用分号分隔的ISO国家代码 |
| `countries` | str | 国家名称 |
| `jurisdiction` | str | 离岸司法管辖区（如英属维尔京群岛、巴拿马等） |
| `incorporation_date` | str | 注册日期，格式为YYYY-MM-DD |
| `inactivation_date` | str | 停用日期，格式为YYYY-MM-DD（如该实体已被标记则填写此值） |
| `source` | str | 数据来源，如“巴拿马文件”“天堂文件”等 |
| `entity_url` | str | 对应ICIJ页面的链接 |
| `connections` | str | 用分号分隔的相关实体的节点编号 |

## 4. 数据覆盖范围

- 全球范围内的离岸实体记录
- 最早的记录可追溯至20世纪70年代的“巴哈马泄露事件”；大部分数据为1990年至2018年间的记录
- 该数据库并非实时更新——只有当ICIJ公布新的泄露信息时才会补充进来
- 数据总量约为：81万多个离岸实体，75万多名相关负责人，15万多个中间人

## 5. 跨数据源关联潜力

- **SEC EDGAR** ↔ `name`（拥有离岸分支的上市公司）
- **USAspending** ↔ `name`（具有离岸结构的联邦承包商）
- **OFAC SDN** ↔ `name`（使用离岸结构被列入制裁名单的实体）

关联键为标准化后的实体/负责人名称。在ICIJ内部进行跨数据源关联时，`node_id`是标准引用标识。关系图遍历功能通过脚本实现（基于`connections`字段采用广度优先搜索算法）。

## 6. 数据质量说明

- 同一离岸实体的名称在不同泄露事件中可能会出现细微差异
- 部分负责人可能是名义持有人或代持人，并非实际受益人
- 有些记录的信息非常有限，仅包含名称和所在司法管辖区
- 关系图并不完整——部分关联关系仅在原始资料中有记载，但未纳入结构化数据库中
- 已停用或被标记的实体仍会收录在数据库中，并标注有`inactivation_date`字段

## 7. 数据获取脚本

路径：`scripts/fetch_icij_offshore.py`

```bash
# Search by entity name (case-insensitive substring across the bulk DB)
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --out data/icij.csv

# Search by officer (individual person)
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --officer "SMITH JOHN" \
    --out data/icij.csv

# Search by jurisdiction (filter on cached results)
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --officer "SMITH" \
    --jurisdiction "BRITISH VIRGIN ISLANDS" --out data/icij_bvi.csv

# Force a fresh download (default refresh window is 30 days)
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --force-refresh --out data/icij.csv
```

首次调用时，约70 MB大小的ZIP文件会被下载到`~/.cache/hermes-osint/icij/`（或`$
