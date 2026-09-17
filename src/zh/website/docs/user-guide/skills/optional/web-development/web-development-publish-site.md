---
title: "Publish Site — Versioned site deploys to GitHub/Cloudflare/Netlify Pages"
sidebar_label: "Publish Site"
description: "Versioned site deploys to GitHub/Cloudflare/Netlify Pages"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 发布网站

可将用户自行构建的网站、控制面板或 Web 应用（或您为他们构建的），部署到用户拥有的基础设施上——默认为 GitHub Pages，如需更多功能则可选择 Cloudflare Pages 或 Netlify。其工作流程包括：在本地进行预览以便最终确认，每次部署都通过 git 标签进行版本管理，通过一系列提供商逐步完成部署，通过真实的 HTTP 检测来验证在线地址的有效性，并确保随时可通过一条命令实现回滚。

该技能适用于处理静态网站以及单页应用构建后的输出文件（纯 HTML/CSS/JS 文件，或是 Vite/Next-export/Astro 等工具生成的 `dist/`/`build/` 目录）。它不支持服务器端运行环境——若需无需账户设置即可快速完成的无服务器部署，建议使用 `cloudflare-temporary-deploy` 这一可选技能。

## 适用场景

当用户提出以下需求时，可使用该技能：
- **将网站上线**——例如“发布这个网站”、“把网站托管到某个地方”、“给我一个可分享的链接”；
- **部署刚刚生成的仪表板、报告、作品集、文档站点或原型**；
- **用新内容更新已发布的网站**（重新部署即可生成新版本）；
- **将出问题的部署回滚到之前的版本**；
- **选择托管平台**——用户并不关心具体位置，只需一个网址即可。

## 先决条件

需至少配置一个已认证的提供商 CLI（按以下顺序进行检查）：
- **GitHub Pages（默认选项）**：执行 `gh auth status` 命令能成功返回结果。同时还需要安装 `git` 工具。
- **Cloudflare Pages**：执行 `wrangler whoami` 命令能成功返回结果（或已设置 `CLOUDFLARE_API_TOKEN`）。安装方法为：`npm i -g wrangler`，或直接使用 `npx wrangler@latest`。
- **Netlify（备用选项）**：执行 `netlify status` 命令能成功返回结果。需先安装 `npm i -g netlify-cli`。

此外还需满足以下条件：
- 一个用于发布的静态输出目录（可以是网站根目录，也可以是 `dist/`/`build/` 目录）。如果项目需要构建步骤，请先执行构建操作，再发布输出目录，切勿直接发布源代码。
- 若需进行本地预览分享，可安装 `cloudflared` 工具（非必需——使用 `python3 -m http.server` 即可实现仅限本地的预览功能）。

## 使用方法

以下所有命令均通过项目目录中的 `terminal` 工具执行。整个流程始终包含以下五个步骤：

1. 构建 → 2. 预览以获取审批 → 3. 提交代码并打标签（标记部署前的版本）→ 4. 通过提供商渠道进行部署 → 5. 使用 `curl` 检查在线地址并提交报告。

## 快速参考

| 步骤 | 命令 |
|---|---|
| 本地预览 | `python3 -m http.server 8080 --directory dist` |
| 可共享的预览链接 | `cloudflared tunnel --url http://localhost:8080` |
| 对部署版本进行标记 | `git add -A && git commit -m "deploy: <内容描述>" && git tag deploy-YYYYMMDD-HHMM` |
| GitHub Pages（分支模式） | `git subtree push --prefix dist origin gh-pages` |
| 在仓库中启用 Pages 功能 | `gh api repos/{owner}/{repo}/pages -X POST -f 'source[branch]=gh-pages' -f 'source[path]=/'` |
| Cloudflare Pages | `npx wrangler@latest pages deploy dist --project-name <名称>` |
| Netlify | `netlify deploy --prod --dir dist` |
| 回滚操作 | `git checkout <上一个标签> -- . && redeploy`（或通过提供商控制面板操作） |
| 验证在线状态 | `curl -sS -o /dev/null -w '%{http_code}' <网址>` → 应显示 `200` 状态码 |

## 操作流程

### 1. 在本地进行构建与预览

如需构建项目（可使用 `npm run build` 等命令），确定输出目录，然后通过服务器提供该目录的内容以供预览：

```bash
python3 -m http.server 8080 --directory dist
```

如需生成可共享的预览链接（用于让其他设备上的用户查看，或希望在正式发布前获得他们的确认），可在后台的 `终端` 会话中快速创建一个隧道：

```bash
cloudflared tunnel --url http://localhost:8080
```

在部署之前，将 `https://*.trycloudflare.com` 这一网址提供给用户并获取其确认。部署完成后即可终止该隧道连接。

### 2. 部署前必须基于特定版本——无一例外

所有部署都必须源自某个 git 提交记录，这样才能确保每次部署均可复现，同时也便于轻松回滚。

```bash
git init 2>/dev/null; git add -A
git commit -m "deploy: <short description>"
git tag "deploy-$(date +%Y%m%d-%H%M)"
```

如果该项目已拥有代码仓库，只需执行提交并添加标签操作即可。切勿部署未经过提交的文件。

### 3. 部署——提供商层级

**第一级——GitHub Pages（默认为免费服务；若已通过 `gh` 完成认证，则无需额外账户）：**

```bash
gh repo create <name> --public --source . --push   # skip if repo exists
git subtree push --prefix dist origin gh-pages      # publish build output
gh api "repos/{owner}/<name>/pages" -X POST \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'  # first time only
```

该网站地址为 `https://<owner>.github.io/<name>/`。如果该地址对应的是仓库根目录（不存在构建目录），请直接推送 `main` 分支，并将 Pages 的源代码分支设置为 `main`，而非使用子树路径方式。对于需要频繁重新部署的构建型项目，建议使用官方的 `actions/deploy-pages` 工作流，这样即可实现自动发布。

**第二步 — Cloudflare Pages（适用于需要自定义域名、重定向/请求头功能或 Functions 的场景）：**

```bash
npx wrangler@latest pages deploy dist --project-name <name>
```

首次运行时会创建项目，并输出 `https://<name>.pages.dev` 这一网址。自定义域名则可通过 Cloudflare 控制面板进行配置（路径为 Pages → 项目 → 自定义域名）。

**第 3 步 — Netlify（作为备用方案，或当用户已使用该平台时）：**

```bash
netlify deploy --prod --dir dist
```

执行 `netlify deploy --dir dist`（无需使用 `--prod` 参数）会生成一个预发布版本地址，可作为第二阶段的预览用途。

### 4. 回滚操作

回滚即重新部署之前的标签版本。切勿直接手动编辑线上发布的内容。

```bash
git checkout deploy-<previous> -- .   # or: git checkout deploy-<previous>; rebuild
# then rerun the same deploy command from step 3
```

Cloudflare Pages和Netlify也在其控制台提供了每次部署的历史记录功能（“回滚到该版本”），在无法使用CLI时能更快速地恢复到之前的状态。

### 5. 密钥与环境变量

- **绝不要将密钥、API密钥或`.env`文件提交到代码仓库**——这些内容会在Pages托管平台上公开可见。在首次提交前请使用`git status`进行检查，并将`.env*`文件加入`.gitignore`中。
- 运行时所需的环境变量应通过对应平台的控制台进行配置：Cloudflare Pages为“设置”→“环境变量”；Netlify为“站点设置”→“环境变量”。GitHub Pages仅支持静态内容，没有服务器端环境变量；任何嵌入到代码包中的内容本质上都是公开的。如果构建过程中包含了敏感密钥，请及时提醒用户。

## 常见问题

- **在GitHub Pages上，单页应用路由会出现404错误**。Pages不支持重写规则，因此需要将输出目录下的`index.html`复制为`404.html`（执行命令：`cp dist/index.html dist/404.html`），这样才能让客户端路由正常工作。Cloudflare Pages和Netlify则通过 `_redirects` 规则来解决此问题（规则示例：`/* /index.html 200`）。
- **GitHub Pages的构建速度较慢**。首次启用后，网站可能需要1到10分钟才会显示出来；之后每次推送代码大约需要1分钟。遇到404错误时不要立即判定构建失败，建议先使用`curl`命令多次查询，再进一步排查问题。
- **路径区分大小写**。Pages所基于的Linux系统是区分大小写的；在MacOS/Windows环境下能正常加载的网站，如果资源文件被命名为`Logo.PNG`但实际提交时为`logo.png`，则可能会出现404错误。当遇到资源加载失败时，可通过在HTML文件中搜索来检查是否存在大小写不一致的情况。
- **项目页面的基础路径。** 应将内容部署在 `https://<owner>.github.io/<name>/` 下的 `/<name>/` 目录下——直接使用如 `/app.js` 这样的绝对资源地址会导致问题。建议使用相对路径，或设置构建工具的基础路径（如 `vite build --base=/<name>/`）。
- **`wrangler` 认证流程需要浏览器支持。** 执行 `wrangler login` 会启动 OAuth 认证流程；在无头环境中，建议使用 `CLOUDFLARE_API_TOKEN`（用户可在 dash.cloudflare.com → API Tokens 中生成），并且绝不能将该令牌输出到日志中。
- **自定义域名的 DNS 传播时间。** 新创建的 CNAME 记录可能需要几分钟到几小时才能生效。首先请通过提供商提供的默认域名（如 `*.pages.dev`、`*.netlify.app`、`*.github.io`）进行测试，然后再检查自定义域名——切勿将两种不同的失败情况混为一谈。
- **直接部署源代码而非构建输出。** 如果实际网站存储在 `dist/` 目录中，却直接发布仓库根目录的内容，会导致页面仅显示目录列表或原始的 JSX 代码。务必确认输出目录中存在 `index.html` 文件。

## 验证步骤

切勿仅根据部署日志就判定任务成功。在向用户反馈之前，请先执行以下操作：

1. 使用命令 `curl -sS -o /dev/null -w '%{http_code}' <live-url>`，若返回值为 `200`，则表示部署成功（对于首次在 GitHub Pages 上部署的站点，建议等待约 2 分钟后再尝试）。
2. 使用命令 `curl -sS <live-url> | head -30`，查看是否包含预期的 `index.html` 内容；如有需要，也可通过 `web_extract` 工具对实时网址的标记结构进行进一步验证。
3. 对于单页应用，还需使用 `curl` 访问某个深层页面路径（例如 `/about`），确认返回状态为 `200` 而非 `404`。
4. 使用命令 `git tag --list 'deploy-*'`，查看此次部署对应的标签名称。

确认所有步骤无误后，再将实时网址以及可用于回滚的部署标签告知用户。
