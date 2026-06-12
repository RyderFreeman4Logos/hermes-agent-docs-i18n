---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [plan, requesting-code-review]
---

# 编写 Hermes-Agent 技能（在代码仓库中）

## 概述

SKILL.md 文件可以存储在两个位置：

1. **用户本地**：`~/.hermes/skills/<可选分类>/<名称>/SKILL.md` —— 为个人使用，不会被共享。可通过 `skill_manage(action='create')` 创建。
2. **代码仓库中（适用于当前项目）**：`/home/bb/hermes-agent/skills/<分类>/<名称>/SKILL.md` —— 会被提交并随软件包一起分发。需使用 `write_file` 加上 `git add` 操作完成。`skill_manage(action='create')` 不适用于此路径下的文件。

## 适用场景

- 用户要求你在“当前分支/代码仓库/提交版本”中添加某项技能
- 你要提交的可复用工作流需要随 hermes-agent 一同分发
- 你需要编辑 `/home/bb/hermes-agent/skills/` 下已存在的技能（进行小范围修改时使用 `patch`，彻底重写时使用 `write_file`；对于代码仓库中的技能，`skill_manage` 仍可用于打补丁，但无法用于创建新技能）

## 必需的 Frontmatter 格式

格式规范依据：`tools/skill_manager_tool.py::_validate_frontmatter`。必须满足以下要求：

- 文件以 `---` 作为开头字符（不能有前置空行）
- 内容之前以 `\n---\n` 结尾
- 文件内容需能被解析为 YAML 映射格式
- 必须包含 `name` 字段
- 必须包含 `description` 字段，长度不得超过 **1024 个字符**（即 `MAX_DESCRIPTION_LENGTH` 的限制）
- 在结尾的 `---` 之后必须有非空内容

`skills/software-development/` 下的所有技能均遵循此标准结构。

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

验证器不会强制要求必须包含 `version` / `author` / `license` / `metadata` 这些字段，但所有节点都应具备这些信息——若省略它们，您的技能包就会显得格格不入。

## 大小限制

- 描述部分：≤ 1024 字符（必须遵守）。
- 完整的 SKILL.md 文件：≤ 100,000 字符（通过 `MAX_SKILL_CONTENT_CHARS` 参数进行限制，约合 36k 个标记）。
- 属于 `software-development/` 目录下的节点技能包大小应在 **8-14k 字符** 之间。请尽量控制在这个范围内。如果内容超过 20k 字符，建议将其拆分到 `references/*.md` 文件中，并在 SKILL.md 中引用这些文件。

## 节点匹配结构

仓库中的每个技能包大致都遵循以下结构：

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

并非每个部分都是必填的，但要想让该技能具备与同类产品相媲美的水准，至少需要包含“概述”、“适用场景”、可操作的详细内容以及常见陷阱说明。  

## 目录放置位置

```
skills/<category>/<skill-name>/SKILL.md
```

当前仓库中存在的分类（可通过 `ls skills/` 查看）包括：`autonomous-ai-agents`、`creative`、`data-science`、`devops`、`dogfood`、`email`、`gaming`、`github`、`leisure`、`mcp`、`media`、`mlops/*`、`note-taking`、`productivity`、`red-teaming`、`research`、`smart-home`、`social-media`、`software-development`。

请从现有分类中选择最接近的一项，切勿随意创建新的顶级分类。

## 工作流程

1. 调查目标分类下的**同行**：
   ```
   ls skills/<category>/
   ```
1. 阅读2-3份同类SKILL.md文件，以此作为参考来把握文风与结构。  
2. 若不确定具体要求，可查看`tools/skill_manager_tool.py`中的验证规则。  
3. 使用`write_file`函数将内容写入`skills/<category>/<name>/SKILL.md`路径下。  
4. 在本地进行验证：
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. 在当前分支上执行 **Git add + commit** 操作。  
6. **注意：** 当前会话的技能加载器为缓存模式——在开启新会话之前，`skill_view` / `skills_list` 功能将无法显示新增的技能。这是正常现象，并非故障。

## 引用其他技能

在加载时，`metadata.hermes.related_skills` 会合并仓库内的技能树（位于 `skills/` 目录）与用户本地技能树（位于 `~/.hermes/skills/`）。虽然可以从仓库内的技能引用用户本地的技能，但其他克隆该仓库的用户则无法识别这些本地技能。建议尽量仅通过仓库内的技能来互相引用。如果某个高频使用的技能仅存在于 `~/.hermes/skills/` 中，可考虑将其移至仓库中。

## 编辑仓库内的现有技能

- **小型修复（如拼写错误、补充注意事项、优化触发条件）：** 对于仓库内的技能，使用 `skill_manage(action='patch', name=..., old_string=..., new_string=...)` 即可。  
- **大规模重写：** 需要直接用 `write_file` 编辑整个 SKILL.md 文件。虽然 `skill_manage(action='edit')` 也能实现，但必须提供完整的新内容。  
- **添加辅助文件：** 可通过 `write_file` 在 `skills/<category>/<name>/references/<file>.md`、`templates/<file>` 或 `scripts/<file>` 目录下创建文件。`skill_manage(action='write_file')` 也可用于此目的，且会严格遵循参考文件/模板/脚本/资源文件的目录允许列表。  
- **务必执行提交操作**——仓库内的技能属于源代码，而非运行时状态。

## 常见问题

1. **对仓库内的技能使用 `skill_manage(action='create')`。** 此命令会将内容写入 `~/.hermes/skills/` 目录，而非仓库内的技能树。如需在仓库内创建技能，请使用 `write_file`。  
2. **`---` 前存在多余空格。** 验证工具会检查 `content.startswith("---")`，若有前置空行或 BOM 字符，将导致验证失败。  
3. **描述内容过于笼统。** 合规的技能描述应以 “Use when ...” 开头，并明确说明适用的*触发场景类别*，而非具体任务。“Use when debugging X” 比 “Debug X” 更为规范。  
4. **遗漏作者、许可证及元数据字段。** 虽然这不是验证工具的强制要求，但所有合规技能都应包含这些信息；缺失会导致技能看起来未完成。  
5. **创建与现有技能重复的技能。** 在创建新技能之前，建议先列出 `skills/<category>/` 目录下的 2-3 个现有技能，并考虑在其基础上进行扩展，而非直接创建功能相似的新技能。  
6. **误以为当前会话能立即看到新增技能。** 实际上无法立即显示，因为技能加载器仅在会话启动时初始化。建议在新建会话中查看，或通过提供完整路径使用 `skill_view` 功能查询。  
7. **链接到仓库中不存在的技能。** 虽然 `related_skills: [some-user-local-skill]` 对当前用户有效，但会导致其他克隆者出现问题。建议仅使用仓库内的技能作为引用。

## 验证清单

- [ ] 文件位于 `skills/<category>/<name>/SKILL.md` 目录下（而非 `~/.hermes/skills/` 目录）  
- [ ] 前置内容从字节 0 开始以 `---` 标识，结尾处为 `\n---\n`  
- [ ] 文件中包含 `name`、`description`、`version`、`author`、`license` 以及 `metadata.hermes.{tags, related_skills}` 字段  
- [ ] 名称长度不超过 64 个字符，且仅包含小写字母和连字符  
- [ ] 描述内容长度不超过 1024 个字符，并以 “Use when ...” 开头  
- [ ] 文件总长度不超过 100,000 个字符（建议控制在 8-15k 字符之间）  
- [ ] 文件结构应为：`# 标题` → `## 概述` → `## 适用场景` → 正文内容 → `## 常见问题` → `## 验证清单`  
- [ ] `related_skills` 中引用的技能应在仓库内存在（或明确标注为允许使用用户本地技能）  
- [ ] 已在目标分支上完成 `git add skills/<category>/<name>/ && git commit` 操作
