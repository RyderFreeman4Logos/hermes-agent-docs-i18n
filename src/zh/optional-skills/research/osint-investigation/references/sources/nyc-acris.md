# NYC ACRIS — 纽约市房地产记录系统

## 1. 概述

自动城市登记信息系统（ACRIS）是纽约市对已登记的房地产相关文件建立的索引，这些文件包括地契、抵押贷款合同、清偿协议、留置权文件以及统一商法典相关申请。该系统覆盖曼哈顿、布朗克斯、布鲁克林、皇后区和史泰登岛地区。相关数据以4个相互关联的Socrata数据集形式发布在纽约市开放数据门户上。

## 2. 访问方式

- **Socrata API：** `https://data.cityofnewyork.us/resource/636b-3b5g.json`（用于获取相关主体信息）
- **其他数据集：** `bnx9-e6tj`（主数据集）、`8h5j-fqxa`（法律相关数据）、`uqqa-hym2`（参考资料数据集）
- **认证要求：** 仅读取数据无需认证（如需更高访问权限，可使用Socrata的`$

```bash
# By party name
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "ROLNICK" --out data/acris.csv

# By address (useful when you know the property but not the names)
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --address "571 HUDSON" --out data/acris.csv

# Restrict to grantees (buyers / mortgagees)
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "ROLNICK" --party-type 2 \
    --out data/acris_buyers.csv
```

该脚本会连接“当事方 → 主记录”数据源，以此填充文档类型、日期、行政区划以及金额等信息。如需跳过此连接步骤（从而提升速度并减少输出列数），可使用`--no-enrich`参数。

## 8. 法律与许可说明

- 依据纽约州《不动产法》及纽约市章程属于公开记录
- 该数据无任何商业使用限制
- 根据法规规定，所有ACRIS数据均为公开信息

## 9. 参考资料

- ACRIS门户网站：https://a836-acris.nyc.gov/CP/
- 纽约市开放数据平台：https://data.cityofnewyork.us/
- 当事方数据集：https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Parties/636b-3b5g
- 文档类型代码说明：https://www1.nyc.gov/site/finance/taxes/acris.page
