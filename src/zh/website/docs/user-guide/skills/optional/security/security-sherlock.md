---
title: "Sherlock — Find accounts for a username across 400+ platforms"
sidebar_label: "Sherlock"
description: "Find accounts for a username across 400+ platforms"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Sherlock

在 400 多个平台上根据用户名查找对应账号。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/security/sherlock` 安装 |
| 路径 | `optional-skills/security/sherlock` |
| 版本 | `1.0.0` |
| 开发者 | unmodeled-tyler |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `osint`、`security`、`username`、`social-media`、`reconnaissance` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，代理程序会将这些内容视为操作指令。
:::

# Sherlock OSINT 用户名搜索

利用 [Sherlock Project](https://github.com/sherlock-project/sherlock) 在 400 多个社交网络中根据用户名查找对应的社交媒体账号。

## 适用场景

- 用户要求查找与某个用户名相关的账号
- 用户希望查看该用户名在各个平台上的可用性
- 用户正在进行 OSINT 或情报搜集研究
- 用户询问“该用户名注册在何处？”或类似问题

## 前提条件

- 已安装 Sherlock CLI：`pipx install sherlock-project` 或 `pip install sherlock-project`
- 或者：具备 Docker 使用能力（`docker run -it --rm sherlock/sherlock`）
- 能够访问相关社交平台以进行查询

## 操作步骤

### 1. 检查是否已安装 Sherlock

**在执行其他操作之前**，请先确认 Sherlock 是否已安装：

```bash
sherlock --version
```

如果命令执行失败：
- 建议安装：`pipx install sherlock-project`（推荐）或 `pip install sherlock-project`
- **切勿**尝试多种安装方式——请选择一种并继续操作
- 如果安装失败，需告知用户并停止执行

### 2. 提取用户名

**如果用户的消息中已明确说明，可直接从中提取用户名。**

以下情况**无需**使用“澄清”功能：
- “查找 nasa 的账户” → 用户名为 `nasa`
- “搜索 johndoe123” → 用户名为 `johndoe123`
- “检查 alice 是否存在于社交媒体上” → 用户名为 `alice`
- “在社交网络中查找用户 bob” → 用户名为 `bob`

**仅在下述情况才使用“澄清”功能：**
- 提到了多个可能的用户名（如“搜索 alice 或 bob”）
- 表述含糊不清（如仅说“搜索我的用户名”但未明确说明）
- 完全未提及用户名（如“进行一次开源情报搜索”）

提取时需使用消息中**确切**的用户名——保留原字母大小写、数字及下划线等格式。

### 3. 构建命令

**默认命令**（除非用户另有明确要求，否则使用此命令）：
```bash
sherlock --print-found --no-color "<username>" --timeout 90
```

**可选参数**（仅在用户明确要求时添加）：
- `--nsfw` — 包含不适宜公开的内容网站（仅应用户请求时使用）
- `--tor` — 通过 Tor 网络传输（仅当用户需要匿名时使用）

**切勿通过“澄清”功能询问这些选项**——直接执行默认搜索即可。如有需要，用户可自行提出特定要求。

### 4. 执行搜索

通过 `terminal` 工具运行该命令。根据网络状况及网站数量的不同，搜索通常需要 30 至 120 秒。

**终端调用示例：**
```json
{
  "command": "sherlock --print-found --no-color \"target_username\"",
  "timeout": 180
}
```

### 5. 解析并展示结果

Sherlock会以简洁的格式输出找到的账户信息。请对输出内容进行解析，并按以下格式展示：

1. **摘要行**：显示“用户名‘Y’共找到X个账户”
2. **分类链接**：如有必要，可按平台类型（社交平台、职业平台、论坛等）对账户进行分组
3. **输出文件位置**：Sherlock默认会将结果保存为<用户名>.txt格式的文件

**示例输出解析：**
```
[+] Instagram: https://instagram.com/username
[+] Twitter: https://twitter.com/username
[+] GitHub: https://github.com/username
```

尽可能以可点击链接的形式呈现查询结果。

## 常见问题

### 未找到结果
如果 Sherlock 未检测到任何账户，这通常说明该用户名并未在所检查的平台上注册。可建议：
- 检查拼写或变体形式
- 使用 `?` 通配符尝试相似的用户名：`sherlock "user?name"`
- 该用户可能设置了隐私设置或已删除账户

### 超时问题
部分网站响应速度较慢或会屏蔽自动化请求。可使用 `--timeout 120` 增加等待时间，或通过 `--site` 限定搜索范围。

### Tor 配置
使用 `--tor` 功能需先运行 Tor 守护进程。若用户希望保持匿名性但无法使用 Tor，可建议：
- 安装 Tor 服务
- 使用 `--proxy` 指定其他代理服务器

### 冗误检测
由于某些网站的响应结构原因，它总是会显示“已找到”结果。对于异常结果，应通过手动核查进行交叉验证。

### 请求频率限制
频繁的搜索可能会触发请求频率限制。对于批量用户名查询，可在多次调用之间添加延迟，或使用 `--local` 功能并利用缓存数据。

## 安装

### pipx（推荐方式）
```bash
pipx install sherlock-project
```

### pip
```bash
pip install sherlock-project
```

### Docker
```bash
docker pull sherlock/sherlock
docker run -it --rm sherlock/sherlock <username>
```

### Linux软件包
该工具可在Debian 13+、Ubuntu 22.10+、Homebrew、Kali及BlackArch系统上使用。

## 合规使用说明

本工具仅限用于合法的OSINT搜集与研究用途。请提醒用户遵守以下规定：
- 仅搜索自己拥有账号或获准调查的用户名
- 遵守各平台的服务条款
- 禁止将其用于骚扰、跟踪或任何非法活动
- 在分享查询结果前务必考虑其对隐私可能造成的影响

## 结果验证

运行sherlock工具后，请进行以下验证：
1. 输出内容应列出包含网址的相关网站
2. 若选择文件输出格式，会生成`<username>.txt`文件（为默认输出格式）
3. 若使用了`--print-found`参数，输出结果中应仅显示匹配项的`[+]`标记行

## 使用示例

**用户提问：**“你能帮我查一下用户名‘johndoe123’在社交媒体上是否存在吗？”

**智能体操作流程：**
1. 先执行`sherlock --version`命令，确认工具已正确安装
2. 由于已提供用户名，直接开始查询
3. 运行命令：`sherlock --print-found --no-color "johndoe123" --timeout 90`
4. 解析输出结果并展示相关链接

**回复格式：**
> 已找到12个用户名为‘johndoe123’的账号：
>
> • https://twitter.com/johndoe123
> • https://github.com/johndoe123
> • https://instagram.com/johndoe123
> • [... 其他链接]
>
> 查询结果已保存至：johndoe123.txt

---

**用户提问：**“帮我查找用户名‘alice’的相关信息，即便包含不适宜公开的内容也行。”

**智能体操作流程：**
1. 确认sherlock工具已安装
2. 用户已同时提供用户名及需要搜索不适宜内容的功能标志
3. 运行命令：`sherlock --print-found --no-color --nsfw "alice" --timeout 90`
4. 展示查询结果
