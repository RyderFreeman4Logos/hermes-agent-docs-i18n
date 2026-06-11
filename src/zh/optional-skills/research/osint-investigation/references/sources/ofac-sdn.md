# OFAC SDN——特别指定国民名单

## 1. 概述

美国外国资产控制办公室（OFAC）会发布特别指定国民及被封禁人员名单（SDN）。美国公民通常被禁止与该名单上的个人和实体进行任何交易。此外，该机构还会发布非SDN类的综合名单（如BIS拒绝入境人员名单、FSE名单等）。

## 2. 获取方式

- **完整XML格式：** `https://www.treasury.gov/ofac/downloads/sdn.xml`
- **分隔符格式：** `https://www.treasury.gov/ofac/downloads/sdn.csv`
- **综合列表格式：** `https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml`
- **认证要求：** 无
- **访问频率限制：** 无（为静态文件下载），数据会持续更新。

## 3. 数据结构

`fetch_ofac_sdn.py`脚本返回的关键字段如下：

| 字段名 | 数据类型 | 描述 |
|--------|----------|------|
| `entity_id` | int | OFAC分配的唯一标识码 |
| `name` | str | 主名称 |
| `entity_type` | str | 个人/实体/船舶/飞机 |
| `program_list` | str | 用分号分隔的制裁项目名称（例如SDGT；IRAN） |
| `title` | str | 适用于个人：头衔/职务 |
| `nationalities` | str | 用分号分隔的国籍代码 |
| `aka_list` | str | 用分号分隔的“别名” |
| `addresses` | str | 用分号分隔的已知地址 |
| `dob` | str | 出生日期（仅适用于个人） |
| `pob` | str | 出生地（仅适用于个人） |
| `remarks` | str | OFAC提供的自由文本备注 |
| `last_updated` | str | 更新日期，格式为YYYY-MM-DD |

## 4. 覆盖范围

- 全球范围——涵盖所有被美国财政部列入制裁名单的实体
- SDN名单约有10,000条记录，综合名单约有15,000条记录
- 数据持续更新（在执法行动频繁期间甚至每日更新）
- 名单包含别名信息（非常常见，单个实体可能有多个别名）

## 5. 跨系统关联潜力

- **SEC EDGAR** ↔ `name`（被制裁的上市公司）
- **USAspending** ↔ `name`（作为联邦承包商被制裁的实体——虽理论上不应存在此类关联，但仍需核实）
- **ICIJ Offshore** ↔ `name`（同样被制裁的离岸实体）

关联键为标准化后的名称。**重要提示**：必须同时与`aka_list`中的别名进行匹配，因为许多被制裁实体是通过其别名才被发现的。

## 6. 数据质量

- 名称来自多种文字系统，可能存在多种罗马化拼写
- 别名往往与主名称差异很大
- 部分记录的信息较为有限（个人字段可能缺少出生日期和地址）
- 自由文本备注中包含重要背景信息，务必仔细阅读
- “特别指定全球恐怖分子”（SDGT）和“网络相关”（CYBER2）制裁项目会频繁新增或移除名单中的条目

## 7. 数据获取脚本

路径：`scripts/fetch_ofac_sdn.py`

```bash
# Full snapshot
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --out data/ofac_sdn.csv

# Filter to specific program
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --program SDGT --out data/sdn_sdgt.csv

# Entities only (skip individuals, vessels, aircraft)
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --entity-type entity --out data/sdn_entities.csv
```

## 8. 法律与许可规定

- 根据行政命令授权及法定制裁计划形成的公开记录  
- 美国境内的相关主体必须对这些名单进行核查——该规定具有强制约束力  
- 对数据本身并无限制；限制仅适用于与名单中所列实体的交易  
- “过度匹配”行为不会导致任何处罚——虽然需对误报进行核实，但并不被禁止  

## 9. 参考资料

- 美国财政部海外资产控制办公室官网：https://ofac.treasury.gov/  
- 特别指定国民名单：https://ofac.treasury.gov/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists  
- 数据格式说明：https://ofac.treasury.gov/sdn-list/sanctions-list-search-tool  
- 合规指南：https://ofac.treasury.gov/recent-actions
