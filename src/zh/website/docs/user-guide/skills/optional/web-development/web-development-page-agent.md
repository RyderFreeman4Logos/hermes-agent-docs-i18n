---
title: "Page Agent"
sidebar_label: "Page Agent"
description: "Embed alibaba/page-agent into your own web application — a pure-JavaScript in-page GUI agent that ships as a single <script> tag or npm package and lets end-..."
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Page Agent

将 alibaba/page-agent 嵌入您自己的 Web 应用程序中——这是一种纯 JavaScript 的页面内 GUI 智能体，以单个 <script> 标签或 npm 包的形式提供，允许您的网站最终用户通过自然语言指令操控界面（例如“点击登录按钮，然后将用户名填写为 John”）。无需 Python、无无头浏览器、也不需要任何扩展插件。当用户是希望为他们的 SaaS 平台、管理面板或 B2B 工具添加 AI 助手，或让传统 Web 应用能够通过自然语言操作，又或是想对比本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）大语言模型与 page-agent 的性能时，可使用此智能体。**不适用于服务器端浏览器自动化**——此类需求请转向 Hermes 内置的浏览器工具。

## 智能体元数据

| | |
|---|---|
| 来源 | 可选——可通过 `hermes skills install official/web-development/page-agent` 安装 |
| 路径 | `optional-skills/web-development/page-agent` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `web`、`javascript`、`agent`、`browser`、`gui`、`alibaba`、`embed`、`copilot`、`saas` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发此智能体时 Hermes 会加载的完整定义文件。当智能体处于激活状态时，智能体所看到的指令即为此内容。
:::

# page-agent

alibaba/page-agent（https://github.com/alibaba/page-agent，拥有 17k 多个星标，采用 MIT 许可协议）是一款用 TypeScript 编写的页面内 GUI 智能体。它运行在网页内部，将 DOM 内容转换为文本形式（不生成截图，也不支持多模态大语言模型），并能根据自然语言指令（如“点击登录按钮，然后将用户名填写为 John”）对当前页面执行操作。该智能体完全基于客户端运行——宿主网站只需引入相应脚本，并提供一个兼容 OpenAI 的大语言模型接口即可。

## 何时使用此智能体

当用户希望实现以下目标时，可加载此智能体：

- **在自身的 Web 应用程序中集成 AI 助手**（如 SaaS 平台、管理面板、B2B 工具、ERP 系统或 CRM 系统）——让仪表板上的用户能够直接输入“为 Acme Corp 创建发票并发送邮件”，而无需依次点击五个页面。
- **在不重写前端代码的情况下升级传统 Web 应用**——page-agent 可直接叠加在现有的 DOM 结构之上运行。
- **通过自然语言提升应用的可访问性**——语音输入或屏幕阅读器用户可通过描述操作需求来操控界面。
- **针对本地（Ollama）或云端（Qwen、OpenAI、OpenRouter）大语言模型演示或测试 page-agent 的性能**。
- **构建交互式培训或产品演示**——让 AI 在真实界面中实时引导用户了解“如何提交费用报销单”。

## 何时不应使用此智能体

- 如果用户希望**让 Hermes 自身来操控浏览器**，请使用 Hermes 内置的浏览器工具（Browserbase / Camofox）。page-agent 的作用方向与之相反。
- 如果用户需要**跨标签页自动化操作且不想嵌入代码**，可选用 Playwright、browser-use 或 page-agent 的 Chrome 扩展插件。
- 如果用户需要**视觉参考或截图功能**，由于 page-agent 仅支持文本形式的 DOM，此时应使用多模态浏览器智能体。

## 先决条件

- Node 22.13+ 或 24+，npm 10+（文档要求为 11+，但 10.9 也能正常使用）。
- 一个兼容 OpenAI 的大语言模型接口：Qwen（DashScope）、OpenAI、Ollama、OpenRouter，或任何支持 `/v1/chat/completions` 接口的服务。
- 配备开发者工具的浏览器（用于调试）。

## 方法一——通过 CDN 在 30 秒内完成演示（无需安装）

这是最快查看其功能的方式。该方法利用了 alibaba 提供的免费测试大语言模型代理——**仅限评估用途**，且需遵守相关使用条款。

只需将其添加到任意 HTML 页面中（或作为书签工具栏项粘贴到开发者工具的控制台即可）：

```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

一个面板会随即出现。输入指令即可，操作完成。  

书签快捷方式形式（可直接添加到书签栏，然后在任意页面上点击使用）：

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js';document.head.appendChild(s);})();
```

## 方案二——通过 npm 安装到您自己的 Web 应用中（生产环境使用）

在现有的 Web 项目内部（React / Vue / Svelte / 普通网页）：

```bash
npm install page-agent
```

将其与您自己的大语言模型端点相连——**切勿将演示用的 CDN 提供给真实用户使用**：

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: process.env.LLM_API_KEY,   // never hardcode
    language: 'en-US',
})

// Show the panel for end users:
agent.panel.show()

// Or drive it programmatically:
await agent.execute('Click submit button, then fill username as John')
```

**提供商示例**（任何兼容 OpenAI 的接口均可使用）：

| 提供商 | `baseURL` | `model` |
|--------|-----------|---------|
| Qwen / DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.5-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen3:14b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4.6` |

**核心配置字段**（传递给 `new PageAgent({...})`）：

- `model`、`baseURL`、`apiKey` —— 用于连接大型语言模型
- `language` —— 用户界面语言（如 `en-US`、`zh-CN` 等）
- 还提供了允许列表与数据屏蔽功能，可限制智能体能够访问的内容——完整选项列表请参见 https://alibaba.github.io/page-agent/

**安全性提示。** 在实际部署时，请勿将 `apiKey` 放置在客户端代码中——应通过后端代理来发起大型语言模型请求，并将 `baseURL` 指向该代理。演示用的 CDN 之所以存在，是因为阿里巴巴为测试目的搭建了该代理。

## 方案三 —— 克隆源代码仓库（进行贡献或自行修改）

当用户希望直接修改 page-agent 本身、通过本地 IIFE 包在任意网站上对其进行测试，或开发浏览器扩展时，可选用此方案。

```bash
git clone https://github.com/alibaba/page-agent.git
cd page-agent
npm ci              # exact lockfile install (or `npm i` to allow updates)
```

在仓库根目录下创建一个包含LLM端点信息的`.env`文件。示例如下：

```
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
```

Ollama 版本：

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=NA
LLM_MODEL_NAME=qwen3:14b
```

常用命令：

```bash
npm start           # docs/website dev server
npm run build       # build every package
npm run dev:demo    # serve IIFE bundle at http://localhost:5174/page-agent.demo.js
npm run dev:ext     # develop the browser extension (WXT + React)
npm run build:ext   # build the extension
```

使用本地的 IIFE 模块包，即可在任意网站上进行测试。请添加此书签链接：

```javascript
javascript:(function(){var s=document.createElement('script');s.src=`http://localhost:5174/page-agent.demo.js?t=${Math.random()}`;s.onload=()=>console.log('PageAgent ready!');document.head.appendChild(s);})();
```

接着执行 `npm run dev:demo`，在任何页面上点击书签链接，即可注入本地构建的版本。每次保存文件后都会自动重新构建。

**警告：** 在开发模式下，`.env` 文件中的 `LLM_API_KEY` 会被直接嵌入到 IIFE 打包文件中。请勿共享该打包文件，也不要将其提交到版本控制系统中，更不要将相关 URL 贴送到 Slack 中。（已验证：通过搜索公开的开发版打包文件，确实可以找到 `.env` 文件中的原始键值。）

## 项目结构（路径 3）

采用基于 npm workspaces 的单仓库架构。主要包如下：

| 包名 | 路径 | 功能 |
|------|------|------|
| `page-agent` | `packages/page-agent/` | 包含用户界面面板的主入口 |
| `@page-agent/core` | `packages/core/` | 无界面的核心智能体逻辑 |
| `@page-agent/mcp` | `packages/mcp/` | MCP 服务器（测试版） |
| — | `packages/llms/` | 大语言模型客户端 |
| — | `packages/page-controller/` | DOM 操作及视觉反馈功能 |
| — | `packages/ui/` | 面板组件及国际化支持 |
| — | `packages/extension/` | Chrome/Firefox 扩展程序 |
| — | `packages/website/` | 文档页面及官网 |

## 验证功能是否正常

完成路径 1 或路径 2 后：
1. 在浏览器中打开目标页面，并启用开发者工具。
2. 应该能看到一个悬浮面板。如果未出现，请查看控制台中的错误信息（常见原因包括大语言模型端点的 CORS 问题、`baseURL` 设置错误或 API 密钥无效）。
3. 输入与页面上内容相关的简单指令，例如“点击登录链接”。
4. 查看网络标签页，应能看到指向 `baseURL` 的请求。

完成路径 3 后：
1. 执行 `npm run dev:demo`，会输出 `Accepting connections at http://localhost:5174`。
2. 运行 `curl -I http://localhost:5174/page-agent.demo.js`，应返回 `HTTP/1.1 200 OK`，且 `Content-Type` 为 `application/javascript`。
3. 在任意网站上点击书签链接，即可显示对应面板。

## 常见问题与注意事项

- **在生产环境中使用演示版 CDN** —— 不要这样做。该 CDN 有访问频率限制，依赖阿里巴巴的免费代理服务，且其服务条款明确禁止在正式生产环境中使用。
- **API 密钥泄露** —— 任何传递给 `new PageAgent({apiKey: ...})` 的密钥都会被包含在 JS 打包文件中。在实际部署时，务必通过自建后端作为代理。
- **非 OpenAI 兼容的端点** 可能会静默失败或报出难以理解的错误。如果您的服务提供商需要 Anthropic/Gemini 格式的输出，建议在前面添加一个 OpenAI 兼容的代理工具（如 LiteLLM、OpenRouter）。
- **CSP 安全策略拦截** —— 设置了严格 Content-Security-Policy 的网站可能会拒绝加载 CDN 脚本，或禁止内联代码执行。这种情况下，需从自身服务器托管相关文件。
- 在路径 3 中修改 `.env` 文件后，需要重新启动开发服务器 —— Vite 只会在启动时读取环境变量。
- **Node 版本要求** —— 该项目指定支持的 Node 版本为 `^22.13.0 || >=24`。Node 20 会因引擎版本问题导致 `npm ci` 命令执行失败。
- **npm 版本差异** —— 文档推荐使用 npm 11+，但实际上 npm 10.9 也能正常工作。

## 参考资料

- 项目仓库：https://github.com/alibaba/page-agent
- 文档地址：https://alibaba.github.io/page-agent/
- 许可协议：MIT（基于 browser-use 的 DOM 处理技术实现，版权所有 © 2024 Gregor Zunic）
