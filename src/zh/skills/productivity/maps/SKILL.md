---
name: maps
description: "Geocode, POIs, routes, timezones via OpenStreetMap/OSRM."
version: 1.2.0
author: Mibayy
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [maps, geocoding, places, routing, distance, directions, nearby, location, openstreetmap, nominatim, overpass, osrm]
    category: productivity
    requires_toolsets: [terminal]
    supersedes: [find-nearby]
---

# 地图技能

基于免费的开放数据源实现位置智能功能。提供8条命令、44类兴趣点分类，无任何依赖（仅使用Python标准库），也无需API密钥。

数据来源包括：OpenStreetMap/Nominatim、Overpass API、OSRM、TimeAPI.io。

该技能已取代旧版的`find-nearby`技能——所有原有功能均被下方的`nearby`命令所涵盖，同时保留了相同的`--near "<地点>"`快捷参数及多类别搜索功能。

## 适用场景

- 用户在Telegram中发送位置标记（消息中包含纬度/经度）→ 使用`nearby`命令
- 用户需要根据地点名称获取坐标 → 使用`search`命令
- 用户已知坐标但想要对应地址 → 使用`reverse`命令
- 用户询问附近的餐厅、医院、药店、酒店等场所 → 使用`nearby`命令
- 用户需要了解驾车/步行/骑行距离或行程时间 → 使用`distance`命令
- 用户需要获取两个地点之间的路线指引 → 使用`directions`命令
- 用户需要了解某地的时区信息 → 使用`timezone`命令
- 用户需要在特定地理区域内搜索兴趣点 → 使用`area`命令结合`bbox`参数

## 先决条件

Python 3.8及以上版本（仅需标准库，无需通过pip安装额外包）。

脚本路径：`~/.hermes/skills/maps/scripts/maps_client.py`

## 命令列表

```bash
MAPS=~/.hermes/skills/maps/scripts/maps_client.py
```

### search — 对地名进行地理编码

```bash
python3 $MAPS search "Eiffel Tower"
python3 $MAPS search "1600 Pennsylvania Ave, Washington DC"
```

返回值：纬度、经度、显示名称、类型、边界框以及重要性得分。

### reverse — 坐标转地址

```bash
python3 $MAPS reverse 48.8584 2.2945
```

返回结果：完整的地址明细（街道、城市、州/省、国家/地区及邮政编码）。

### nearby — 按类别查找地点

```bash
# By coordinates (from a Telegram location pin, for example)
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10
python3 $MAPS nearby 40.7128 -74.0060 hospital --radius 2000

# By address / city / zip / landmark — --near auto-geocodes
python3 $MAPS nearby --near "Times Square, New York" --category cafe
python3 $MAPS nearby --near "90210" --category pharmacy

# Multiple categories merged into one query
python3 $MAPS nearby --near "downtown austin" --category restaurant --category bar --limit 10
```

共涵盖46类场所：餐厅、咖啡馆、酒吧、医院、药店、酒店、民宿、露营地、超市、自动取款机、加油站、停车场、博物馆、公园、学校、大学、银行、警察局、消防站、图书馆、机场、火车站、公交站、教堂、清真寺、犹太教会堂、牙医诊所、医院、电影院、剧院、健身房、游泳池、邮局、便利店、面包店、书店、洗衣店、洗车店、汽车租赁店、自行车租赁店、出租车服务、兽医诊所、动物园、游乐场、体育场、夜总会。

每条搜索结果都会包含以下信息：`name`（名称）、`address`（地址）、`lat`/`lon`（纬度/经度）、`distance_m`（距离，单位为米）、`maps_url`（可点击的谷歌地图链接）、`directions_url`（从搜索点出发的谷歌地图路线指引），此外在适用的情况下还会显示推荐标签——如`cuisine`（菜系）、`hours`（营业时间）、`phone`（电话号码）、`website`（网站地址）。

### distance — 行程距离与耗时

```bash
python3 $MAPS distance "Paris" --to "Lyon"
python3 $MAPS distance "New York" --to "Boston" --mode driving
python3 $MAPS distance "Big Ben" --to "Tower Bridge" --mode walking
```

模式：驾驶（默认）、步行、骑行。会同时返回实际行驶距离、耗时以及用于对比的直线距离。

### directions — 分步导航

```bash
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking
python3 $MAPS directions "JFK Airport" --to "Times Square" --mode driving
```

会返回按序号排列的步骤信息，其中包含操作指令、距离、耗时、道路名称以及转向类型（转弯、出发、到达等）。

### timezone — 坐标所对应时区

```bash
python3 $MAPS timezone 48.8584 2.2945
python3 $MAPS timezone 35.6762 139.6503
```

返回时区名称、UTC偏移量以及当前的本地时间。

### area — 地点的边界框与区域范围

```bash
python3 $MAPS area "Manhattan, New York"
python3 $MAPS area "London"
```

返回边界框坐标、以公里为单位的宽高以及大致面积。
可作为 `bbox` 命令的输入数据使用。

### bbox — 在边界框范围内进行搜索

```bash
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

可在地理矩形区域内查找兴趣点。首先使用 `area` 命令获取指定地点的边界框坐标。

## 使用 Telegram 位置图钉

当用户发送位置图钉时，消息中会包含 `latitude:` 和 `longitude:` 字段。提取这些值后直接传递给 `nearby` 命令即可：

```bash
# User sent a pin at 36.17, -115.14 and asked "find cafes nearby"
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

请以编号列表的形式呈现结果，需包含名称、距离以及`maps_url`字段，这样用户便能在聊天界面中点击该链接直接打开地图。对于“现在就能去吗？”这类问题，请查看`hours`字段；若该字段缺失或信息不明确，则需通过`web_search`进行核实，因为OSM上的营业时间是由社区维护的，未必实时更新。

## 工作流程示例

**“查找斗兽场附近的意大利餐厅”：**
1. `nearby --near "Colosseum Rome" --category restaurant --radius 500`
   — 仅需一条命令即可自动完成地理编码

**“他们发送的这个位置标记附近有什么？”：**
1. 从Telegram消息中提取经纬度
2. `nearby LAT LON cafe --radius 1500`

**“如何从酒店步行到会议中心？”：**
1. `directions "Hotel Name" --to "Conference Center" --mode walking`

**“西雅图市中心有哪些餐厅？”：**
1. `area "Downtown Seattle"` → 获取边界框
2. `bbox S W N E restaurant --limit 30`

## 常见问题

- Nominatim服务条款规定：每秒最多仅可发送1次请求（脚本会自动处理此限制）
- `nearby`命令要求提供经纬度，或使用`--near "<地址>"`参数——两者中必须满足其一
- OSRM路线规划功能在欧洲和北美的覆盖效果最佳
- 在高峰时段，Overpass API的响应速度可能会变慢；脚本会自动在多个镜像服务器（overpass-api.de → overpass.kumi.systems）之间切换
- `distance`和`directions`命令需使用`--to`参数指定目的地，而非直接使用位置坐标
- 若仅提供邮政编码，则在全球范围内可能得到模糊的结果，建议同时注明国家/州信息

## 验证方法

```bash
python3 ~/.hermes/skills/maps/scripts/maps_client.py search "Statue of Liberty"
# Should return lat ~40.689, lon ~-74.044

python3 ~/.hermes/skills/maps/scripts/maps_client.py nearby --near "Times Square" --category restaurant --limit 3
# Should return a list of restaurants within ~500m of Times Square
```
