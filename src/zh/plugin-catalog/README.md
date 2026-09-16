# Hermes 插件目录

经 Nous 审核精选的 Hermes 插件。该目录中的每个 YAML 文件（`removed.yaml` 除外）都代表一个插件条目，可通过 `hermes plugins catalog` / `hermes plugins search` 查找，并使用 `hermes plugins install <name>` 进行安装。

## 接入策略

位于此目录即表示该插件已通过信任验证。以下规则确保了该目录的实用性：

1. **人工审核的准入机制。** 新条目仅能通过向 `hermes-agent` 仓库提交 Pull Request（PR）的方式添加，随后由维护者进行审查并合并。该系统不支持自助注册功能，也没有自动导入机制。

2. **必须使用精确的 SHA 值。** 每个条目都必须指定长度为 40 位的完整提交 SHA 值。分支、标签以及简写形式的 SHA 值都会被加载器拒绝。安装时需克隆该仓库并精确检出对应的提交版本。

3. **版本锁定时效要求。** 在进行版本锁定的时刻，所选版本应**至少已发布 2 周**，这一要求与 `optional-mcps/` 以及 pyproject 依赖项所遵循的供应链政策一致。这样做的目的是让社区有足够时间在 Hermes 发布相关指向之前发现存在安全风险的版本。

4. **SHA 值变更需通过新 PR 处理。** 要更新某个条目的锁定版本，需提交一个新的 PR，其差异内容（旧 SHA 值 → 新 SHA 值）将像其他任何更改一样接受重新审查——审查者需要确认所采用的上游提交范围是合理的。

5. **仅允许仓库所有者或核心贡献者提交。** 只有插件仓库的所有者或其核心贡献者才有资格提交条目。第三方仓库的随意提交将被拒收。

6. **声明的功能必须与实际一致。** `capabilities:` 部分中列出的功能（工具、钩子、中间件、环境变量等）必须与插件在锁定版本时实际注册的功能相符。否则验证将会失败——未经声明的功能新增会被视为安全问题。

## 条目结构规范

```yaml
name: example-plugin        # [a-z0-9_-]{1,64}, the catalog key
repo: https://github.com/owner/repo   # https:// only
sha: <40-hex commit sha>    # mandatory exact pin
subdir: ""                  # optional path within the repo
description: One-line description.
maintainer: OwnerName
tier: official              # official | community (default community)
requires_hermes: ">=0.19"   # optional
docs_url: ""                # optional
platforms: []               # optional, e.g. [linux, macos]; empty = all
capabilities:
  provides_tools: []
  provides_hooks: []
  provides_middleware: []
  requires_env: []
```

## removed.yaml — 黑名单文件

出于安全或策略考虑，当某个条目从目录中被移除时，系统会将其连同移除原因及日期一起记录在 `removed.yaml` 文件中。安装程序会拒绝安装任何与已移除条目的名称或仓库地址匹配的组件，因此恶意插件在被移除后也无法通过过时的标识符重新安装。与新增操作类似，条目的移除也是通过经过审核的 Pull Request 来实现的。
