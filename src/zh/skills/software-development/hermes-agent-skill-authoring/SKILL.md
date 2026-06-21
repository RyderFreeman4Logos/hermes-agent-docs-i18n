---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure, and writing-quality principles."
version: 1.1.0
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
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` 这些字段虽不会被验证器强制要求，但所有技能节点都应包含它们——若省略这些信息，您的技能将显得格格不入。

## 大小限制

- 描述部分：≤ 1024 字符（强制要求）。
- 完整的 SKILL.md 文件：≤ 100,000 字符（通过 `MAX_SKILL_CONTENT_CHARS` 参数进行限制，约合 36k 个标记）。
- 放在 `software-development/` 目录下的技能节点，其长度宜控制在 **8-14k 字符** 之间。若内容超过 20k 字符，建议将其拆分到 `references/*.md` 文件中，并在 SKILL.md 中通过引用方式提及。

## 写作质量原则

技能的存在旨在提升智能体处理任务的确定性。所谓“确定性”并非指每次运行都产生完全相同的输出，而是指智能体能始终遵循一致的、有效的处理逻辑。

在编写或修改任何技能时，请遵循以下质量检查标准：

1. **注重流程的确定性优化**。思考：当该技能被加载时，哪些行为应当发生变化？如果某行代码不会改变任何行为，那就将其删除。
2. **合理选择要加载的上下文信息**。通过模型调用的 Hermes 技能，其描述内容会在每一轮对话中都被读取。因此，请确保描述重点突出触发条件以及该技能的独特行为，详细内容可放在正文或关联的参考文件中。
3. **建立清晰的信息层级结构**。将始终必需的操作步骤放在 `SKILL.md` 中；而针对特定分支的复杂参考资料则可存放在 `references/`、`templates/` 或 `scripts/` 目录中，仅在需要时再予以引用。
4. **为每一步操作设定明确的完成标准**。每个有序步骤都应明确说明智能体如何判断该步骤已完成。良好的完成标准应是可验证的，且在关键情况下应是详尽无遗的——例如“所有被修改的文件均已处理”比“总结更改内容”更为具体。
5. **将规则与其所管理的概念放在一起**。避免将某个概念分散在文件的各个角落。定义、注意事项、示例及验证方法应尽量集中存放。
6. **使用简洁有力的关键词**。优先选用模型已熟悉的简明概念，如“闭环迭代”、“追踪线索”、“根本原因”、“回归测试”等，而非冗长的重复解释。恰当的关键词既能节省标记数量，又能明确操作方向。
7. **剔除重复内容和无用信息**。确保每个含义只在一个地方出现。逐句检查：该句子是否真的改变了智能体的行为？如果没有，直接删除而非试图润色。
8. **防止过早完成操作**。如果智能体往往急于跳过某一步，首先应明确该步骤的完成标准。只有当后续步骤会干扰当前步骤的顺利执行时，才考虑拆分流程。

常见的质量缺陷包括：

- **过早完成**——技能导致智能体在任务尚未真正完成时就继续执行下一环节。
- **内容重复**——同一规则出现在多个位置，导致信息混乱。
- **冗余残留**——因担心删除内容会带来风险，导致过时的代码行仍然存在。
- **结构杂乱**——包含过多始终可见的冗余内容；应将特定分支的参考资料放在引用路径之后。
- **无用描述**——包含智能体即便没有该技能也会遵循的通用建议。

## 统一的结构规范

仓库中的所有技能节点大致都遵循以下结构：

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
6. **注意：** 当前会话的技能加载器是缓存的——因此直到启动新会话之前，`skill_view` / `skills_list` 都无法看到新增的技能。这是正常现象，并非错误。

## 引用其他技能

在加载时，`metadata.hermes.related_skills` 会将仓库内的技能树与用户本地的技能树（位于 `~/.hermes/skills/`）合并。虽然可以从仓库内的技能引用用户本地的技能，但那些刚克隆该仓库的其他用户则无法访问这些被引用的技能。因此建议尽量仅通过仓库内的技能来互相引用。如果某个经常被引用的技能仅存在于 `~/.hermes/skills/` 中，可以考虑将其移至仓库中。

## 编辑仓库内的现有技能

- **小型修改（如拼写错误、补充注意事项、优化触发条件）：** 对于仓库内的技能，使用 `skill_manage(action='patch', name=..., old_string=..., new_string=...)` 即可。  
- **大规模重写：** 需要使用 `write_file` 编写完整的 SKILL.md 文件。虽然 `skill_manage(action='edit')` 也能实现此功能，但需要提供全部新内容。  
- **添加辅助文件：** 可通过 `write_file` 将文件写入 `skills/<category>/<name>/references/<file>.md`、`templates/<file>` 或 `scripts/<file>` 目录中。`skill_manage(action='write_file')` 也可实现此功能，且会遵循对 references/templates/scripts/assets 子目录的允许列表规则。  
- **务必提交更改——** 仓库内的技能属于源代码，而非运行时状态。

## 常见问题

1. **对仓库内的技能使用 `skill_manage(action='create')`。** 此操作会将内容写入 `~/.hermes/skills/`，而非仓库内的技能树。如需在仓库内创建技能，请使用 `write_file`。  
2. **`---` 前存在空白字符。** 验证工具会检查 `content.startswith("---")`，任何前导空行或 BOM 都会导致验证失败。  
3. **描述过于笼统。** 合规技能的描述应以 “Use when ...” 开头，并明确说明适用的*触发场景类别*，而非具体任务。“Use when debugging X” 比 “Debug X” 更为准确。  
4. **遗漏作者、许可证及元数据部分。** 虽然这不是验证工具的强制要求，但所有合规技能都应包含这些信息；省略这些内容会让技能显得未完成。  
5. **创建与现有技能重复的技能。** 在创建新技能之前，先列出 `skills/<category>/` 目录下的 2-3 个现有技能并加以研究。建议优先扩展现有技能，而非创建功能相似的新技能。  
6. **期望当前会话能立即看到新增技能。** 实际上无法立即显示，因为技能加载器是在会话启动时初始化的。可在新会话中查看，或使用完整路径通过 `skill_view` 查阅。  
7. **让技能内容逐渐堆积冗余。** 技能的描述应随着时间推移而愈发简洁明了。在添加新规则时，应同时删除被替代的旧表述，避免建议内容层层叠加。  
8. **写入无实际意义的空泛描述。** 如 “请小心”、“务必彻底” 或 “遵循最佳实践” 等表述往往无法改变模型的行为。建议用可验证的完成标准或更具体的措辞来替代。  
9. **链接到仓库中不存在的技能。** 虽然 `related_skills: [some-user-local-skill]` 对你自己有效，但会导致其他克隆者出现问题。建议仅使用仓库内的技能作为引用。

## 验证清单

- [ ] 文件位于 `skills/<category>/<name>/SKILL.md` 目录下（而非 `~/.hermes/skills/`）  
- [ ] 前置信息从字节 0 开始，以 `---` 标识，并以 `\n---\n` 结尾  
- [ ] 文件中包含 `name`、`description`、`version`、`author`、`license` 以及 `metadata.hermes.{tags, related_skills}` 字段  
- [ ] 名称长度不超过 64 个字符，且仅包含小写字母和连字符  
- [ ] 描述长度不超过 1024 个字符，且以 “Use when ...” 开头  
- [ ] 文件总长度不超过 100,000 个字符（建议控制在 8-15k 之间）  
- [ ] 文件结构应为：`# 标题` → `## 概述` → `## 适用场景` → 正文内容 → `## 常见问题` → `## 验证清单`  
- [ ] 每个有序步骤都配有可验证的完成标准  
- [ ] 描述需聚焦于触发条件，避免重复正文内容  
- [ ] 复杂或特定于分支的参考信息应逐步在关联文件中说明  
- [ ] 已删除无实际意义的空泛描述及重复规则  
- [ ] `related_skills` 中引用的技能均为仓库内的技能（或明确标注为允许的用户本地技能）  
- [ ] 已在目标分支上完成 `git add skills/<category>/<name>/ && git commit` 操作
