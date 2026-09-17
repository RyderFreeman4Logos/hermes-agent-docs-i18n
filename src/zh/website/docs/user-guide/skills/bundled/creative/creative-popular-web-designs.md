---
title: "Popular Web Designs — 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS"
sidebar_label: "Popular Web Designs"
description: "54 real design systems (Stripe, Linear, Vercel) as HTML/CSS"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 流行网页设计模板

54个真实的设计系统（如 Stripe、Linear、Vercel），可直接用于生成 HTML/CSS 代码。

## 技能元数据

| | |
|---|---|
| 来源 | 已内置（默认安装） |
| 路径 | `skills/creative\popular-web-designs` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Teknium（设计系统数据源自 VoltAgent/awesome-design-md） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |

## 参考：完整 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# 流行网页设计模板

54个可直接用于生成 HTML/CSS 的真实设计系统模板。每个模板都完整涵盖了网站的视觉规范：色彩方案、字体层级、组件样式、间距系统、阴影效果、响应式设计行为，以及包含精确 CSS 值的实用智能体指令。

## 相关设计技能

- **`claude-design`** — 用于处理设计*流程与审美层面*的任务（如明确需求范围、生成多种设计方案、验证本地 HTML 文件质量、避免 AI 设计中的低级错误）。当用户希望根据知名品牌风格打造精心设计的页面时，可将其与该技能结合使用：`claude-design` 负责整个设计流程，而该技能则提供所需的视觉规范。
- **`design-md`** — 适用于需要生成正式的 DESIGN.md 格式规范文件而非渲染后成品的场景。
## 使用方法

1. 从下方的模板目录中选择一种设计样式。
2. 加载该设计：`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`
3. 在生成 HTML 时使用相应的设计规范与组件参数。
4. 结合 `generative-widgets` 技能，通过 cloudflared 隧道输出最终结果。

每个模板顶部都包含一个**Hermes 实现说明**板块，其中包含：
- 可直接复用的 CDN 字体替代方案及 Google Fonts `<link>` 标签
- 主字体与等宽字体的 CSS 字体系列配置
- 关于使用 `write_file` 功能创建 HTML 以及 `browser_vision` 功能进行验证的提示。

## HTML 生成模式

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

使用 `write_file` 函数编写文件，通过 `generative-widgets` 工作流（结合 cloudflared 隧道）进行部署，最后利用 `browser_vision` 工具验证结果，以确保视觉效果的准确性。

## 字体替换参考

大多数网站使用的都是无法通过 CDN 获取的专有字体。每个模板都对应一个 Google Fonts 中的替代字体，用以保持原有设计的风格。常见映射关系如下：

| 专有字体 | CDN替代字体 | 设计特点 |
|---|---|---|
| Geist / Geist Sans | Google Fonts 中的 Geist | 几何风格，缩放间距紧凑 |
| Geist Mono | Google Fonts 中的 Geist Mono | 简洁等宽字体，包含连字功能 |
| sohne-var（Stripe使用） | Source Sans 3 | 轻盈优雅的风格 |
| Berkeley Mono | JetBrains Mono | 适用于技术领域的等宽字体 |
| Airbnb Cereal VF | DM Sans | 圆润友好的几何风格 |
| Circular（Spotify使用） | DM Sans | 几何风格，色调温暖 |
| figmaSans | Inter | 简洁的人文主义风格 |
| Pin Sans（Pinterest使用） | DM Sans | 友好且圆润的字体 |
| NVIDIA-EMEA | Inter（或 Arial system） | 工业风，设计简洁 |
| CoinbaseDisplay/Sans | DM Sans | 几何风格，给人可靠感 |
| UberMove | DM Sans | 字体粗壮，结构紧密 |
| HashiCorp Sans | Inter | 企业级风格，色调中性 |
| waldenburgNormal（Sanity使用） | Space Grotesk | 几何风格，略微紧凑 |
| IBM Plex Sans/Mono | Google Fonts 中的 IBM Plex Sans/Mono | 可在 Google Fonts 中获取 |
| Rubik（Sentry使用） | Google Fonts 中的 Rubik | 可在 Google Fonts 中获取 |
当模板的 CDN 字体与原始字体（Inter、IBM Plex、Rubik、Geist）一致时，不会产生任何替换损失。若使用替代字体（例如用 DM Sans 替代 Circular，用 Source Sans 3 替代 sohne-var），则需严格遵循模板中设定的字体粗细、大小及字距参数——这些参数比具体的字体样式更能体现设计的视觉特征。

## 设计目录

### 人工智能与机器学习

| 模板文件 | 对应平台 | 风格特点 |
|---|---|---|
| `claude.md` | Anthropic Claude | 温暖的赤陶色调点缀，简洁的编辑风格布局 |
| `cohere.md` | Cohere | 生动鲜明的渐变效果，数据密集型的仪表板风格 |
| `elevenlabs.md` | ElevenLabs | 深色电影感用户界面，音频波形视觉元素 |
| `minimax.md` | Minimax | 大胆的深色界面搭配霓虹色调点缀 |
| `mistral.ai.md` | Mistral AI | 法式极简设计风格，紫色系色调 |
| `ollama.md` | Ollama | 以终端界面为主，单色简约风格 |
| `opencode.ai.md` | OpenCode AI | 以开发者为中心的深色主题，全等宽字体 |
| `replicate.md` | Replicate | 干净的白色背景，以代码展示为核心 |
| `runwayml.md` | RunwayML | 电影感的深色用户界面，丰富的媒体元素布局 |
| `together.ai.md` | Together AI | 具技术感的设计风格，类似蓝图的视觉呈现 |
| `voltagent.md` | VoltAgent | 绝对黑色的背景，翠绿色点缀，原生终端风格 |
| `x.ai.md` | xAI | 极简的单色设计，未来感十足，全等宽字体 |

### 开发工具与平台 |

| 模板文件 | 适用平台 | 设计风格 |
|---|---|---|
| `cursor.md` | Cursor | 流畅的深色界面，搭配渐变色彩点缀 |
| `expo.md` | Expo | 深色主题，紧凑的字母间距，以代码展示为核心 |
| `linear.app.md` | Linear | 极简的深色模式，设计精准，带有紫色点缀 |
| `lovable.md` | Lovable | 有趣的渐变效果，营造友好的开发者体验 |
| `mintlify.md` | Mintlify | 设计简洁，以绿色为点缀，专为阅读优化 |
| `posthog.md` | PostHog | 风格活泼的标识设计，适合开发者的深色用户界面 |
| `raycast.md` | Raycast | 流畅的深色铬金属质感，搭配鲜艳的渐变色彩 |
| `resend.md` | Resend | 极简的深色主题，以等宽字体作为视觉点缀 |
| `sentry.md` | Sentry | 深色控制面板，信息呈现密集，带有粉紫色调点缀 |
| `supabase.md` | Supabase | 深绿色主题，以代码优先为理念的开发者工具 |
| `superhuman.md` | Superhuman | 高端的深色用户界面，以键盘操作为核心，带有紫色光效 |
| `vercel.md` | Vercel | 黑白对比鲜明，采用Geist字体系统 |
| `warp.md` | Warp | 类似IDE的深色界面，基于块结构的命令操作界面 |
| `zapier.md` | Zapier | 温暖的橙色调，搭配友好的插图元素 |

### 基础设施与云服务

| 模板 | 平台 | 风格 |
|---|---|---|
| `clickhouse.md` | ClickHouse | 黄色作为点缀，采用技术文档风格 |
| `composio.md` | Composio | 现代深色主题，搭配多彩的集成图标 |
| `hashicorp.md` | HashiCorp | 企业级简洁风格，黑白配色 |
| `mongodb.md` | MongoDB | 绿叶标识，以开发者文档为设计重点 |
| `sanity.md` | Sanity | 红色作为点缀，采用以内容为核心的排版方式 |
| `stripe.md` | Stripe | 独特的紫色渐变色彩，字体粗细为300，风格优雅 |

### 设计与生产力工具

| 模板 | 平台 | 风格 |
|---|---|---|
| `airtable.md` | Airtable | 色彩丰富，界面友好，注重数据结构化呈现 |
| `cal.md` | Cal.com | 简洁的中性色调UI，专为开发者设计的极简风格 |
| `clay.md` | Clay | 有机形状搭配柔和渐变，采用艺术导向的布局设计 |
| `figma.md` | Figma | 鲜艳的多色搭配，风格既有趣又专业 |
| `framer.md` | Framer | 强烈的黑蓝配色，以动态效果和设计感为核心 |
| `intercom.md` | Intercom | 友好的蓝色色调，采用对话式UI设计 |
| `miro.md` | Miro | 明亮的黄色作为点缀，营造无限画布的视觉效果 |
| `notion.md` | Notion | 温暖的极简风格，使用衬线字体标题，界面柔和 |
| `pinterest.md` | Pinterest | 红色作为点缀，采用砖块式网格布局，以图片为主 |
| `webflow.md` | Webflow | 蓝色作为点缀，呈现出精致的市场营销网站风格 |

### 金融科技与加密货币领域

| 模板 | 网站 | 风格 |
|---|---|---|
| `coinbase.md` | Coinbase | 清新的蓝色主题，注重信任感，具有机构级质感 |
| `kraken.md` | Kraken | 以紫色为点缀的深色界面，数据密集型控制面板 |
| `revolut.md` | Revolut | 流畅的深色界面，渐变卡片设计，展现金融科技领域的精准度 |
| `wise.md` | Wise | 明亮的绿色点缀，风格友好且清晰直观 |

### 企业版与个人版

| 模板 | 网站 | 风格 |
|---|---|---|
| `airbnb.md` | Airbnb | 温暖的珊瑚色点缀，以图片为主导，界面设计圆润 |
| `apple.md` | Apple | 宽裕的高级留白，采用 SF Pro 字体，搭配电影级视觉效果 |
| `bmw.md` | BMW | 深色高级质感表面，体现精准工程美学 |
| `ibm.md` | IBM | 基于 Carbon 设计系统，采用结构化的蓝色调色板 |
| `nvidia.md` | NVIDIA | 绿黑相间的能量感，凸显技术力量美学 |
| `spacex.md` | SpaceX | 极简的黑白风格，全幅图片展示，充满未来感 |
| `spotify.md` | Spotify | 深色背景上的亮绿色色调，醒目的字体设计，以专辑封面为主导 |
| `uber.md` | Uber | 强烈的黑白对比，紧凑的排版，展现都市活力 |

## 选择设计风格

根据内容匹配合适的风格：

- **开发者工具/仪表板：** Linear、Vercel、Supabase、Raycast、Sentry  
- **文档/内容平台：** Mintlify、Notion、Sanity、MongoDB  
- **营销/落地页设计：** Stripe、Framer、Apple、SpaceX  
- **深色模式界面：** Linear、Cursor、ElevenLabs、Warp、Superhuman  
- **浅色/简洁界面：** Vercel、Stripe、Notion、Cal.com、Replicate  
- **活泼友好风格：** PostHog、Figma、Lovable、Zapier、Miro  
- **高端奢华风格：** Apple、BMW、Stripe、Superhuman、Revolut  
- **数据密集型/仪表板：** Sentry、Kraken、Cohere、ClickHouse  
- **等宽字体/终端风格：** Ollama、OpenCode、x.ai、VoltAgent
