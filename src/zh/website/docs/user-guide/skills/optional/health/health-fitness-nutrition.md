---
title: "Fitness Nutrition — Workout planning, macros, and body metrics via wger/USDA"
sidebar_label: "Fitness Nutrition"
description: "Workout planning, macros, and body metrics via wger/USDA"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 健身营养

通过 wger/USDA 提供锻炼计划、宏量营养素计算及身体指标分析功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/health/fitness-nutrition` 安装 |
| 路径 | `optional-skills/health\fitness-nutrition` |
| 版本 | `1.0.0` |
| 开发者 | Hailey Marshall (haileymarshall)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `健康`、`健身`、`营养`、`健身房`、`锻炼`、`饮食`、`运动` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 健身与营养

由专业健身教练和运动营养师打造的技能。整合两大数据源及离线计算工具——为健身爱好者提供一站式服务。

**数据来源（全部免费，无需安装 pip 依赖）：**

- **wger** (https://wger.de/api/v2/) — 公开的锻炼数据库，涵盖690多种锻炼动作，包含相关肌肉群、所需器械及图片。公共接口无需任何认证。
- **USDA FoodData Central** (https://api.nal.usda.gov/fdc/v1/) — 美国政府推出的营养数据库，收录38万多种食品信息。使用 `DEMO_KEY` 即可立即使用；如需更高数据量限制，可免费注册。

**离线计算工具（纯标准库 Python 实现）：**

- 身体质量指数（BMI）、总每日能量消耗（TDEE，采用Mifflin-St Jeor公式计算）、一次最大力量（分别采用Epley/Brzycki/Lombardi公式计算）、宏量营养素分配比例、体脂率（美国海军测量法）

---

## 适用场景

当用户询问以下内容时，可触发此技能：
- 锻炼动作、训练计划、健身房训练流程、肌肉群分类及训练分组方式
- 食物中的宏量营养素含量、热量值、蛋白质含量、饮食规划及热量统计
- 身体成分：BMI、体脂率、TDEE、热量盈余/缺口
- 一次最大力量的估算值、训练强度百分比及渐进超负荷原则
- 减脂、增肌或维持体重的宏量营养素比例

---

## 操作步骤

### 锻炼动作查询（wger API）

所有wger公共接口均返回JSON格式数据，且无需身份验证。在查询锻炼动作时，请务必添加`format=json`和`language=2`（英语）参数。

**步骤1 — 确定用户需求：**
- 按肌肉群查询 → 使用 `/api/v2/exercise/?muscles={id}&language=2&status=2&format=json`
- 按类别查询 → 使用 `/api/v2/exercise/?category={id}&language=2&status=2&format=json`
- 按训练器械查询 → 使用 `/api/v2/exercise/?equipment={id}&language=2&status=2&format=json`
- 按名称查询 → 使用 `/api/v2/exercise/search/?term={query}&language=english&format=json`
- 查询完整信息 → 使用 `/api/v2/exerciseinfo/{exercise_id}/?format=json`

**步骤2 — 获取参考ID（避免多次调用API）：**

锻炼动作类别对应ID如下：

| ID | 类别     |
|----|----------|
| 8  | 手臂     |
| 9  | 腿部     |
| 10 | 腹部     |
| 11 | 胸部     |
| 12 | 背部     |
| 13 | 肩部     |
| 14 | 小腿     |
| 15 | 有氧运动 |

肌肉名称对应ID：

| ID | 肌肉名称                 | ID | 肌肉名称                 |
|----|--------------------------|----|-------------------------|
| 1  | 肱二头肌                 | 2  | 前三角肌                 |
| 3  | 前锯肌                   | 4  | 胸大肌                   |
| 5  | 外斜肌                   | 6  | 腓肠肌                   |
| 7  | 腹直肌                   | 8  | 臀大肌                   |
| 9  | 斜方肌                   | 10 | 股四头肌                 |
| 11 | 股二头肌                 | 12 | 背阔肌                   |
| 13 | 肱肌                     | 14 | 肱三头肌                 |
| 15 | 胫骨后肌                 |    |                         |

训练器械：

| ID | 训练器械               |
|----|------------------------|
| 1  | 杠铃                   |
| 3  | 哑铃                   |
| 4  | 健身垫                 |
| 5  | 瑞士球                 |
| 6  | 单杠                   |
| 7  | 无（自重训练）          |
| 8  | 长凳                   |
| 9  | 斜板长凳               |
| 10 | 铁壶铃                 |

**第3步 — 获取并展示结果：**

```bash
# Search exercises by name
QUERY="$1"
ENCODED=$(python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY")
curl -s "https://wger.de/api/v2/exercise/search/?term=${ENCODED}&language=english&format=json" \
  | python -c "
import json,sys
data=json.load(sys.stdin)
for s in data.get('suggestions',[])[:10]:
    d=s.get('data',{})
    print(f\"  ID {d.get('id','?'):>4} | {d.get('name','N/A'):<35} | Category: {d.get('category','N/A')}\")
"
```

```bash
# Get full details for a specific exercise
EXERCISE_ID="$1"
curl -s "https://wger.de/api/v2/exerciseinfo/${EXERCISE_ID}/?format=json" \
  | python -c "
import json,sys,html,re
data=json.load(sys.stdin)
trans=[t for t in data.get('translations',[]) if t.get('language')==2]
t=trans[0] if trans else data.get('translations',[{}])[0]
desc=re.sub('<[^>]+>','',html.unescape(t.get('description','N/A')))
print(f\"Exercise  : {t.get('name','N/A')}\")
print(f\"Category  : {data.get('category',{}).get('name','N/A')}\")
print(f\"Primary   : {', '.join(m.get('name_en','') for m in data.get('muscles',[])) or 'N/A'}\")
print(f\"Secondary : {', '.join(m.get('name_en','') for m in data.get('muscles_secondary',[])) or 'none'}\")
print(f\"Equipment : {', '.join(e.get('name','') for e in data.get('equipment',[])) or 'bodyweight'}\")
print(f\"How to    : {desc[:500]}\")
imgs=data.get('images',[])
if imgs: print(f\"Image     : {imgs[0].get('image','')}\")
"
```

```bash
# List exercises filtering by muscle, category, or equipment
# Combine filters as needed: ?muscles=4&equipment=1&language=2&status=2
FILTER="$1"  # e.g. "muscles=4" or "category=11" or "equipment=3"
curl -s "https://wger.de/api/v2/exercise/?${FILTER}&language=2&status=2&limit=20&format=json" \
  | python -c "
import json,sys
data=json.load(sys.stdin)
print(f'Found {data.get(\"count\",0)} exercises.')
for ex in data.get('results',[]):
    print(f\"  ID {ex['id']:>4} | muscles: {ex.get('muscles',[])} | equipment: {ex.get('equipment',[])}\")
"
```

### 营养成分查询（USDA FoodData Central）

若已设置 `USDA_API_KEY` 环境变量，则使用该密钥；否则将自动回退至 `DEMO_KEY`。
`DEMO_KEY` 每小时允许 30 次请求，而免费注册获得的密钥则每小时允许 1,000 次请求。

```bash
# Search foods by name
FOOD="$1"
API_KEY="${USDA_API_KEY:-DEMO_KEY}"
ENCODED=$(python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$FOOD")
curl -s "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=${API_KEY}&query=${ENCODED}&pageSize=5&dataType=Foundation,SR%20Legacy" \
  | python -c "
import json,sys
data=json.load(sys.stdin)
foods=data.get('foods',[])
if not foods: print('No foods found.'); sys.exit()
for f in foods:
    n={x['nutrientName']:x.get('value','?') for x in f.get('foodNutrients',[])}
    cal=n.get('Energy','?'); prot=n.get('Protein','?')
    fat=n.get('Total lipid (fat)','?'); carb=n.get('Carbohydrate, by difference','?')
    print(f\"{f.get('description','N/A')}\")
    print(f\"  Per 100g: {cal} kcal | {prot}g protein | {fat}g fat | {carb}g carbs\")
    print(f\"  FDC ID: {f.get('fdcId','N/A')}\")
    print()
"
```

```bash
# Detailed nutrient profile by FDC ID
FDC_ID="$1"
API_KEY="${USDA_API_KEY:-DEMO_KEY}"
curl -s "https://api.nal.usda.gov/fdc/v1/food/${FDC_ID}?api_key=${API_KEY}" \
  | python -c "
import json,sys
d=json.load(sys.stdin)
print(f\"Food: {d.get('description','N/A')}\")
print(f\"{'Nutrient':<40} {'Amount':>8} {'Unit'}\")
print('-'*56)
for x in sorted(d.get('foodNutrients',[]),key=lambda x:x.get('nutrient',{}).get('rank',9999)):
    nut=x.get('nutrient',{}); amt=x.get('amount',0)
    if amt and float(amt)>0:
        print(f\"  {nut.get('name',''):<38} {amt:>8} {nut.get('unitName','')}\")
"
```

### 离线计算工具

如需批量运算，可使用 `scripts/` 目录中的辅助脚本；
若仅需进行单次计算，则可直接运行以下命令：

- `python scripts/body_calc.py bmi <体重_kg> <身高_cm>`
- `python scripts/body_calc.py tdee <体重_kg> <身高_cm> <年龄> <男|女> <活动强度 1-5>`
- `python scripts/body_calc.py 1rm <重量> <重复次数>`
- `python scripts/body_calc.py macros <每日总能量消耗_kcal> <减脂|维持体重|增肌>`
- `python scripts/body_calc.py bodyfat <男|女> <颈围_cm> <腰围_cm> [臀围_cm] <身高_cm>`

如需了解各公式背后的科学依据，请参阅 `references/FORMULAS.md` 文件。

---

## 常见问题与注意事项

- wger 的运动数据接口**默认返回所有语言版本**——如需获取英文结果，务必添加参数 `language=2`
- wger 中包含**未经验证的用户提交内容**——如仅需查看已通过审核的运动项目，请添加参数 `status=2`
- USDA 提供的 `DEMO_KEY` 每小时仅有 **30次请求权限**——如需提高请求频率，可在批量请求之间添加 `sleep 2` 命令，或申请免费密钥
- USDA 的数据是按 **100克** 计算的——需提醒用户根据实际食用量进行换算
- BMI 指标无法区分肌肉与脂肪——肌肉量较大的人即便 BMI 较高也不一定代表健康状况不佳
- 体脂率计算公式仅为**估算值**（误差范围为±3-5%）——如需精确数值，建议进行 DEXA 扫描
- 1RM 计算公式的准确度在 **10次重复以上会下降**——为获得最佳估算结果，建议以3-5次为一组进行测试
- wger 的 `exercise/search` 接口使用的参数名为 `term`，而非 `query`

---

## 验证流程

执行锻炼搜索后：需确认返回的结果包含锻炼名称、目标肌群以及所需器械。  
执行营养查询后：需确认能获取每100克的宏量营养素数据，包括千卡值、蛋白质、脂肪和碳水化合物的含量。  
使用计算器后：需对输出结果进行合理性检查（例如，大多数成年人的每日总能量消耗应在1500至3500千卡之间）。  

---

## 快速参考

| 任务 | 数据来源 | 接口地址 |
|------|----------|----------|
| 按名称搜索锻炼 | wger | `GET /api/v2/exercise/search/?term=&language=english` |
| 获取锻炼详情 | wger | `GET /api/v2/exerciseinfo/{id}/` |
| 按目标肌群筛选 | wger | `GET /api/v2/exercise/?muscles={id}&language=2&status=2` |
| 按所需器械筛选 | wger | `GET /api/v2/exercise/?equipment={id}&language=2&status=2` |
| 列出锻炼类别 | wger | `GET /api/v2/exercisecategory/` |
| 列出目标肌群 | wger | `GET /api/v2/muscle/` |
| 搜索食物信息 | USDA | `GET /fdc/v1/foods/search?query=&dataType=Foundation,SR Legacy` |
| 获取食物详情 | USDA | `GET /fdc/v1/food/{fdcId}` |
| BMI / 日总能量消耗 / 一次最大力量 / 宏量营养素 | 离线计算 | `python scripts/body_calc.py` |
