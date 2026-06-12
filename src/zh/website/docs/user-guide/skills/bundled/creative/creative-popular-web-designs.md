---
title: "Popular Web Designs — 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS"
sidebar_label: "Popular Web Designs"
description: "54 real design systems (Stripe, Linear, Vercel) as HTML/CSS"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 热门网页设计模板

54 个真实的设计系统（如 Stripe、Linear、Vercel），可直接用于生成 HTML/CSS 代码。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/creative/popular-web-designs` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Teknium（设计系统数据来源于 VoltAgent/awesome-design-md） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能运行时，智能体将依据这些内容执行操作。
:::

# 热门网页设计模板

54 个可直接用于生成 HTML/CSS 的真实设计系统模板。每个模板都完整涵盖了网站的视觉规范：色彩方案、字体层级、组件样式、间距规则、阴影效果、响应式设计行为，以及包含精确 CSS 值的实用智能体指令。

## 相关设计技能

- **`claude-design`** — 用于处理设计*流程与风格*（明确需求范围、生成多种设计方案、验证本地 HTML 文件、避免 AI 设计中的低质量问题）。当用户希望根据知名品牌风格打造精心设计的页面时，可将其与该技能结合使用：`claude-design` 负责推动整个设计流程，而该技能则提供视觉设计规范。
- **`design-md`** — 适用于需要生成正式的 DESIGN.md 规范文件而非渲染后的最终作品的情况。

## 使用方法

1. 从下方的模板目录中选择一种设计风格
2. 加载该模板：`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`
3. 在生成 HTML 代码时使用这些设计规范和组件参数
4. 可与 `generative-widgets` 技能搭配使用，通过 cloudflared 隧道输出最终结果

每个模板顶部都包含 **Hermes 实现说明** 区块，其中包含：
- 可直接复用的 CDN 字体替代方案及 Google Fonts `<link>` 标签
- 主字体与等宽字体的 CSS 字体系列配置
- 关于使用 `write_file` 函数创建 HTML 文件以及 `browser_vision` 函数进行验证的提示

## HTML 生成流程

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <!-- Paste the Google Fonts <link> from the template's Hermes notes -->
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* Apply the template's color palette as CSS custom properties */
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
      /* ... more from template Section 2 */
    }
    /* Apply typography from template Section 3 */
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
    /* Apply component styles from template Section 4 */
    /* Apply layout from template Section 5 */
    /* Apply shadows from template Section 6 */
  </style>
</head>
<body>
  <!-- Build using component specs from the template -->
</body>
</html>
```

使用 `write_file` 函数写入文件，通过 `generative-widgets` 工作流（结合 cloudflared 隧道）进行部署，最后利用 `browser_vision` 工具验证结果，以确保视觉呈现的准确性。

## 字体替换参考

大多数网站使用的都是无法通过 CDN 获取的专有字体。每个模板都对应一个 Google Fonts 中的替代字体，用以在保持原有设计风格的同时实现兼容。常见映射关系如下：

| 专有字体 | CDN替代字体 | 设计特点 |
|---|---|---|
| Geist / Geist Sans | Google Fonts 中的 Geist | 几何感强，字符间距经过压缩处理 |
| Geist Mono | Google Fonts 中的 Geist Mono | 纯正等宽字体，包含连字功能 |
| sohne-var（Stripe使用） | Source Sans 3 | 轻盈优雅的风格 |
| Berkeley Mono | JetBrains Mono | 适用于技术领域的等宽字体 |
| Airbnb Cereal VF | DM Sans | 圆润友好的几何风格 |
| Circular（Spotify使用） | DM Sans | 具有几何感且色调温暖 |
| figmaSans | Inter | 简洁的人文主义风格 |
| Pin Sans（Pinterest使用） | DM Sans | 友好圆润的设计风格 |
| NVIDIA-EMEA | Inter（或系统默认Arial） | 工业风，设计简洁 |
| CoinbaseDisplay/Sans | DM Sans | 具有几何感且给人以可靠感 |
| UberMove | DM Sans | 字体粗壮，排版紧凑 |
| HashiCorp Sans | Inter | 企业风格，色调中性 |
| waldenburgNormal（Sanity使用） | Space Grotesk | 具有几何感，字符略显紧凑 |
| IBM Plex Sans/Mono | IBM Plex Sans/Mono | 可在 Google Fonts 中获取 |
| Rubik（Sentry使用） | Rubik | 可在 Google Fonts 中获取 |

当模板的 CDN 字体与原始字体一致时（如 Inter、IBM Plex、Rubik、Geist），就不会出现风格丢失的问题。而当使用替代字体时（如用 DM Sans 代替 Circular，用 Source Sans 3 代替 sohne-var），则需严格遵循模板中规定的字体粗细、大小及字距设置——因为这些参数比具体的字体种类更能决定页面的视觉风格。

## 设计模板目录

### AI与机器学习领域

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `claude.md` | Anthropic Claude | 温暖的赤陶色点缀，简洁的编辑风格布局 |
| `cohere.md` | Cohere | 生动鲜明的渐变色彩，数据丰富的仪表盘风格 |
| `elevenlabs.md` | ElevenLabs | 深色电影感界面，搭配音频波形设计元素 |
| `minimax.md` | Minimax | 粗犷的深色界面，带有霓虹色点缀 |
| `mistral.ai.md` | Mistral AI | 法国风格极简设计，以紫色为主色调 |
| `ollama.md` | Ollama | 以终端界面为核心，纯黑色简约风格 |
| `opencode.ai.md` | OpenCode AI | 以开发者为中心的深色主题，全等宽字体显示 |
| `replicate.md` | Replicate | 干净的白色背景，以代码展示为主 |
| `runwayml.md` | RunwayML | 电影感的深色界面，内容布局丰富 |
| `together.ai.md` | Together AI | 具有技术感，采用蓝图式设计风格 |
| `voltagent.md` | VoltAgent | 深色背景如虚无空间，以翠绿色为点缀，完全基于终端风格 |
| `x.ai.md` | xAI | 极简的纯黑色设计，未来感极强，全等宽字体 |

### 开发工具与平台类

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `cursor.md` | Cursor | 流畅的深色界面，搭配渐变色彩点缀 |
| `expo.md` | Expo | 深色主题，字距紧凑，以代码展示为核心 |
| `linear.app.md` | Linear | 极简的深色模式，设计精准，带有紫色点缀 |
| `lovable.md` | Lovable | 鲜艳的渐变色彩，营造友好的开发者体验 |
| `mintlify.md` | Mintlify | 设计简洁，以绿色为点缀，便于阅读 |
| `posthog.md` | PostHog | 风格活泼，专为开发者设计的深色界面 |
| `raycast.md` | Raycast | 光滑的深色铬金属质感，搭配鲜明渐变色彩 |
| `resend.md` | Resend | 极简的深色主题，采用等宽字体作为设计元素 |
| `sentry.md` | Sentry | 深色仪表盘风格，信息密度高，以粉紫色为点缀 |
| `supabase.md` | Supabase | 深绿色主题，以代码为核心的开发者工具风格 |
| `superhuman.md` | Superhuman | 高端感的深色界面，以键盘操作为核心，带有紫色光效 |
| `vercel.md` | Vercel | 黑白对比鲜明，采用 Geist 字体系列 |
| `warp.md` | Warp | 类似 IDE 的深色界面，基于块状结构的命令式操作界面 |
| `zapier.md` | Zapier | 温暖的橙色色调，搭配友好的插图元素 |

### 基础设施与云服务类

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `clickhouse.md` | ClickHouse | 以黄色为点缀，采用技术文档风格的布局 |
| `composio.md` | Composio | 现代深色主题，搭配多彩的集成图标 |
| `hashicorp.md` | HashiCorp | 企业级简洁风格，以黑白两色为主 |
| `mongodb.md` | MongoDB | 以绿色树叶作为品牌标识，侧重于技术文档风格 |
| `sanity.md` | Sanity | 红色作为点缀，以内容展示为核心的编辑风格布局 |
| `stripe.md` | Stripe | 独特的紫色渐变色彩，搭配300号字重的优雅字体 |

### 设计与生产力工具类

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `airtable.md` | Airtable | 颜色丰富，风格友好，注重结构化数据展示 |
| `cal.md` | Cal.com | 简洁的中性风格界面，以开发者需求为导向的简约设计 |
| `clay.md` | Clay | 有机形状设计，柔和的渐变色彩，具有艺术感强的布局 |
| `figma.md` | Figma | 鲜艳的多色搭配，风格既有趣又专业 |
| `framer.md` | Framer | 粗犷的黑色与蓝色搭配，以动态效果和设计为核心 |
| `intercom.md` | Intercom | 友好的蓝色调色板，采用对话式界面设计 |
| `miro.md` | Miro | 鲜亮的黄色作为点缀，营造无限画布般的视觉体验 |
| `notion.md` | Notion | 温暖的极简风格，使用衬线字体作为标题，界面柔和 |
| `pinterest.md` | Pinterest | 红色作为点缀，采用砖块式网格布局，以图片展示为主 |
| `webflow.md` | Webflow | 蓝色作为点缀，呈现出精致的市场营销网站风格 |

### 金融科技与加密货币领域

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `coinbase.md` | Coinbase | 清新的蓝色品牌标识，注重建立信任感，具有机构级专业感 |
| `kraken.md` | Kraken | 深色界面以紫色为点缀，仪表盘信息密度高 |
| `revolut.md` | Revolut | 流畅的深色界面，卡片设计采用渐变效果，体现金融科技领域的精准度 |
| `wise.md` | Wise | 鲜亮的绿色作为点缀，风格友好且清晰易懂 |

### 企业级与消费类品牌

| 模板文件 | 对应网站 | 设计风格 |
|---|---|---|
| `airbnb.md` | Airbnb | 温暖的珊瑚色作为点缀，以照片展示为核心，界面设计圆润 |
| `apple.md` | Apple | 高品质的留白设计，使用 SF Pro 字体，搭配电影感强的图片 |
| `bmw.md` | BMW | 深色高级质感界面，体现精准的工程设计风格 |
| `ibm.md` | IBM | 基于 Carbon 设计系统的风格，采用有序的蓝色调色板 |
| `nvidia.md` | NVIDIA | 绿色与黑色相结合，体现强大的技术力量感 |
| `spacex.md` | SpaceX | 极简的黑白对比设计，全幅图片展示，充满未来感 |
| `spotify.md` | Spotify | 深色背景上搭配鲜艳的绿色，字体粗壮，以专辑封面作为设计核心 |
| `uber.md` | Uber | 粗犷的黑色与白色搭配，字体排版紧凑，体现城市活力 |

## 如何选择合适的设计模板

需根据内容类型来挑选合适的模板：

- **开发工具/仪表盘类**：Linear、Vercel、Supabase、Raycast、Sentry
- **文档/内容网站类**：Mintlify、Notion、Sanity、MongoDB
- **营销/landing页面类**：Stripe、Framer、Apple、SpaceX
- **深色模式界面**：Linear、Cursor、ElevenLabs、Warp、Superhuman
- **浅色/简洁界面**：Vercel、Stripe、Notion、Cal.com、Replicate
- **活泼/友好风格**：PostHog、Figma、Lovable、Zapier、Miro
- **高端/奢华风格**：Apple、BMW、Stripe、Superhuman、Revolut
- **信息密集型/仪表盘类**：Sentry、Kraken、Cohere、ClickHouse
- **等宽字体/终端风格**：Ollama、OpenCode、x.ai、VoltAgent
