# Wayback Machine — Internet Archive CDX

## 1. 概述

自1996年以来，Internet Archive的Wayback Machine已收录了约9000亿页网页。CDX服务器API通过URL、时间戳和内容哈希值对这些网页进行索引。该服务完全免费、匿名使用，无需身份验证。

## 2. 访问方式

- **CDX服务器：** `https://web.archive.org/cdx/search/cdx`
- **Wayback链接地址：** `https://web.archive.org/web/<时间戳>/<URL>`
- **立即保存页面（写入）：** `https://web.archive.org/save/<URL>`（使用不同的API）
- **身份验证：** 不需要
- **速率限制：** 宽松；建议以约1次请求/秒的频率访问

## 3. 数据结构

`fetch_wayback.py`脚本返回的关键字段如下：

| 字段名 | 类型 | 描述 |
|--------|------|-------------|
| `url` | str | 被收录的原始URL |
| `timestamp` | str | 时间戳，格式为YYYYMMDDHHMMSS（CDX标准格式） |
| `wayback_url` | str | 可直接用于查看该网页的链接地址 |
| `mimetype` | str | 网页被收录时的内容类型 |
| `status` | str | HTTP状态码（通常为200） |
| `digest` | str | 网页内容的SHA1哈希值，便于内容比对 |
| `length` | str | 网页内容的字节数 |

## 4. 收录范围

- 时间范围：1996年至今
- 已收录约7亿个域名的9000亿多页网页
- 通过自动爬虫和人工操作持续更新
- 部分域名（如新闻类网站）的收录较为全面，而部分私人域名则收录较少

## 5. 跨引用潜力

- **维基百科** ↔ 可反向查找那些后来已消失的参考页面
- **新闻类URL** ↔ 当当前网址无法访问时，可获取原文内容
- **企业网站** ↔ 可获取已被删除的历史“关于我们”页面及高管简介

当其他数据源指向已不存在的网址时，Wayback CDX可作为高效的**内容恢复**工具。

## 6. 数据质量

- 被robots.txt屏蔽的域名可能收录不完整或根本没有收录
- 不同网页的收录完整性存在差异（有时仅保存HTML，而未保存CSS/JS文件）
- 部分内容可能因域名所有者的要求而被排除（如遵循DMCA规定）
- 带查询字符串的“深层链接”的收录情况参差不齐
- 时间分辨率以单次收录为准，并非连续记录——因此经常会出现数据缺失的情况

## 7. 数据获取脚本

路径：`scripts/fetch_wayback.py`

```bash
# All captures of a specific URL
python3 SKILL_DIR/scripts/fetch_wayback.py --url "https://example.com/page" \
    --out data/wb.csv

# All captures of a host
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --out data/wb.csv

# All captures of a domain + subdomains
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match domain --out data/wb.csv

# Only unique-content captures within a date window
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --collapse digest \
    --from-date 2020-01-01 --to-date 2023-12-31 \
    --out data/wb.csv
```

## 8. 法律与许可条款

- Internet Archive的抓取行为遵循公平使用原则及相关研究规定。
- 重放URL属于稳定引用地址，建议在相关文献中予以标注。
- 内容管理遵循Internet Archive的非营利性使用条款。
- 部分内容受版权保护；即便CDX条目显示已进行抓取，也可能被限制重放。

## 9. 参考资料

- CDX服务器文档：https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md
- Wayback API文档：https://archive.org/help/wayback_api.php
- Internet Archive官网：https://archive.org/
