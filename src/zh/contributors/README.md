# 贡献者邮箱与 GitHub 登录账号的映射关系

该目录用于替代在 `scripts/release.py` 文件中直接向 `AUTHOR_MAP` 添加条目的方式。由于旧版字典会导致多个紧急修复 PR 同时提交时频繁出现合并冲突——因为每个 PR 都会修改同一文件的相同代码行。而在此方案中，**每个映射关系都独立存储在一个文件中**，因此绝不会发生冲突。

## 如何添加映射关系

在 `emails/` 目录下，为每位提交者的邮箱创建一个单独的文件：

```bash
python3 scripts/add_contributor.py <email> <github-login>
# or by hand:
echo "<github-login>" > contributors/emails/<email>
```

- 文件**名称** = 精确的提交者邮箱地址（可通过 `git log --format='%ae'` 查看）。
- 文件**内容** = 第一行非注释行中的 GitHub 登录账号。
  以 `#` 开头的行属于注释（可用于 PR 参考）。

示例 — `contributors/emails/jane.doe@example.com`：

```
janedoe
# PR #12345 salvage (gateway: fix session key routing)
```

## 规则

- 请勿在 `scripts/release.py` 文件中的 `AUTHOR_MAP` 中添加新条目。该字典属于不可修改的旧数据；发布工具会将其与当前目录中的内容合并（出现重复时以目录中的条目为准）。
- GitHub 的自动回复邮件（格式为 `<id>+<login>@users.noreply.github.com` 和 `<login>@users.noreply.github.com`）可直接自动解析，无需额外配置文件。
- 若某个提交所使用的邮箱未在映射表中，`Contributor Attribution Check` CI 工作流将会导致该 PR 失败；失败信息中会明确列出应执行的命令。
