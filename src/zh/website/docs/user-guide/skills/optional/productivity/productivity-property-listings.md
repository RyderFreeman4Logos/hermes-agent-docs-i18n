---
title: "Property Listings — Present property and rental listings as desktop cards"
sidebar_label: "Property Listings"
description: "Present property and rental listings as desktop cards"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 房产列表展示

以桌面卡片的形式展示房产及出租房源信息。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/productivity/property-listings` 安装 |
| 路径 | `optional-skills/productivity/property-listings` |
| 版本 | `0.1.0` |
| 开发者 | Teknium (teknium1)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `property`、`rental`、`real-estate`、`listings`、`desktop`、`cards` |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 房产列表展示技能

在 Hermes 桌面端对话记录中，以可浏览的卡片形式展示已查询到的房产信息。
该功能仅用于信息呈现，不提供房源搜索服务或投资估值功能。

## 适用场景

- 展示房产或出租房源的搜索结果、对比候选列表或重新排序房源。
- 对已展示过的房源进行后续跟进：继续使用卡片格式，以便保持候选列表的可比性。
- 在桌面应用之外使用时，可使用包含来源链接的普通 Markdown 格式；其他客户端无需渲染专门的房源展示框架。

## 先决条件

- 用于原生卡片的 Hermes 桌面端对话功能；其后端可以是本地的，也可以是远程的。
- 属性详情由用户提供，或通过 `web_search`、`web_extract`，以及当前会话中可用的浏览器工具进行验证。
- 卡片格式化无需额外的 API 密钥或依赖项。

## 运行方式

可通过技能目录安装此可选技能，或使用 `terminal` 命令来运行：

```text
hermes skills install official/productivity/property-listings
```

在展示房源信息时，可使用 `skill_view(name="property-listings")` 来加载该技能。需要注意的是，安装该技能并不会自动更新当前对话中的技能索引；如需自动识别，请开启新对话，或直接加载已安装的技能。

## 快速参考

需输出一个语言标识为 `listing` 且内容为有效 JSON 的代码块。用于比较时，可传入单个对象、对象数组，或 `{ "listings": [...] }` 的格式。

| 字段 | 形式与含义 |
|---|---|
| `address` | 必填项，需为非空的街道地址或房产标题。 |
| `price` | 格式化后的字符串，需包含货币单位及租赁期限（如适用）。 |
| `beds`, `baths` | 正数形式的数值；未知值可省略。 |
| `size` | 包含单位的信息格式化后的面积值。 |
| `note` | 说明该房源值得关注的理由。 |
| `facts` | 经核实的简短规格或设施信息数组。 |
| `catches` | 游览前需核实的风险或疑问列表。 |
| `images` | 按房源顺序排列的直接 HTTPS 图片链接，第一个为主图。 |
| `links` | 包含 `{ "label": "来源", "url": "https://..." }` 格式的详情页链接数组，而非搜索结果链接。 |

## 操作步骤

1. 需收集房源的地址、价格、规格参数、照片以及官方详细页面链接。要区分已核实的信息与未知信息，严禁编造价格、设施信息或照片链接。  
2. 将同一房源在不同平台上的重复信息合并为一条记录，同时保留有用的来源链接。需在相关描述中注明信息的来源日期及房源现状的注意事项。  
3. 对每条展示的房源信息都需输出`listing`格式的结构化数据，包括后续更新及重新排序后的信息。描述内容应简明扼要，尚未解决的问题则需标注在`catches`字段中。  
4. 发送之前请务必检查JSON格式是否正确。此示例仅用于展示所有字段的格式，实际使用时需用经过核实的房源数据替换其中的数值及示例链接。

```listing
{
  "address": "12 Example Lane",
  "price": "$2,400/mo",
  "beds": 3,
  "baths": 2.5,
  "size": "1,600 sqft",
  "note": "Fits the requested space and budget.",
  "facts": ["12-month lease", "Covered parking"],
  "catches": ["Verify pet policy and total move-in fees"],
  "images": ["https://example.com/property/front.jpg", "https://example.com/property/kitchen.jpg"],
  "links": [{"label": "Listing details", "url": "https://example.com/property/12"}]
}
```

## 常见问题

- 卡片内容是基于收集到的数据生成的，而非从房源列表网址或嵌入式门户页面获取的。
- 简化版的卡片仅需地址信息。对于未知字段，应直接省略，而非凭猜测填写。
- 请使用直接的远程图片URL，避免使用本地路径、数据URL或搜索结果页面。已过期或被屏蔽的图片会从图库中消失，但文字和链接依然有效。
- 每个卡片所展示的房源数量最多为24套，每套房源的图片数量最多为40张，而“事实信息”、“注意事项”及“链接”部分的条目数则限制为12条。渲染器会对文本字段进行截断，最长显示400个字符。
- 若JSON格式错误或卡片缺少标识信息，系统将回退为普通的代码块显示。有效的卡片并不能保证其对应的房源信息是最新或准确的。

## 验证标准

- 每个展示的房源都必须包含地址及经过验证的来源链接；未知信息需明确标注。
- 桌面端会以原生卡片的形式展示地址、价格、规格参数、“事实信息”、“注意事项”及“链接”等内容。
- 照片会以图库形式呈现，点击某张照片即可打开图片预览窗。当照片数量达到3张或以上时，系统会采用主图加辅助图的拼接方式展示；其余照片仍可在该图库中查看。
- 若卡片无法正常渲染，请先检查语言设置及JSON格式，随后保留包含相同事实信息和链接的可读性Markdown格式作为备用内容。
