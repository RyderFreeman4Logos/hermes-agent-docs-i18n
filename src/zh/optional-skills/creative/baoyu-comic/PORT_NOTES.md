# 端口说明 — baoyu-comic

基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.56.1 进行移植。

## 与上游版本的差异

### SKILL.md 的调整

| 变更项 | 上游版本 | Hermes版本 |
|--------|----------|------------|
| 元数据命名空间 | `openclaw` | `hermes`（包含 `tags` 和 `homepage`） |
| 触发方式 | 斜杠命令/CLI参数 | 自然语言技能匹配 |
| 用户配置 | EXTEND.md 文件（项目/用户/XDG路径） | 已移除——不属于Hermes基础设施范畴 |
| 用户提问方式 | `AskUserQuestion`（批量提问） | `clarify` 工具（每次仅一个问题） |
| 图像生成 | baoyu-imagine（Bun/TypeScript实现，支持 `--ref` 参数） | `image_generate`——**仅支持提示词输入**，返回URL；不接受参考图像输入；智能体需将URL下载到输出目录 |
| PDF合并功能 | `scripts/merge-to-pdf.ts`（Bun + `pdf-lib`库） | 已移除——该功能不在本次移植范围内；页面仅以PNG格式提供 |
| 支持平台 | Linux/macOS/Windows/WSL/PowerShell | 仅支持Linux/macOS |
| 文件操作 | 通用指令 | Hermes内置文件工具（`write_file`、`read_file`） |

### 结构上的移除内容

- **`references/config/` 目录**（已完全移除）：
  - `first-time-setup.md`——阻碍基于EXTEND.md的首次设置流程
  - `preferences-schema.md`——EXTEND.md的YAML结构定义文件
  - `watermark-guide.md`——水印配置文件（与EXTEND.md相关）
- **`scripts/` 目录**（已完全移除）：上游版本的 `merge-to-pdf.ts` 依赖 `pdf-lib` 库，而Hermes仓库中并未声明该依赖。为避免新增依赖，本次移植放弃了PDF合并功能，仅输出单页PNG图像。
- **`workflow.md` 中的步骤8“合并为PDF”已被移除**；步骤9“完成报告”则重新编号为步骤8。
- **`workflow.md` 中的步骤1.1“加载偏好设置（EXTEND.md）”已被删除**；步骤1.2/1.3相应重新编号为1.1/1.2。
- **通用的“用户输入工具”与“图像生成工具”说明部分**——SKILL.md不再列出多种可能工具的备用规则，而是直接引用 `clarify` 和 `image_generate` 功能。

### 图像生成策略的变更

`image_generate` 的结构仅支持 `prompt` 和 `aspect_ratio`（`landscape` | `portrait` | `square`）参数。上游版本的参考图像生成机制（通过 `--ref characters.png` 保证角色一致性，同时允许用户提供参考图以指定风格/色调/场景）无法适配该工具，因此工作流程进行了重构：

- 对于多页漫画，仍会生成**角色表PNG图像**，但其用途已转变为供人工审核的可视化参考文件，以及后续重新生成图像或手动修改提示词时的参考依据。各页面的提示词则直接来自 `characters/characters.md` 中的**文本描述**（在步骤5中直接嵌入）。`image_generate` 功能不会将该PNG图像作为视觉输入处理。
- 用户提供的参考图像功能已简化为提取**风格**/**色调**/**场景**等特征——这些特征会被直接嵌入提示词中；而图像文件本身仅作为来源证明保存在 `refs/` 目录下。
- 现在，各页面的提示词要求必须直接嵌入角色描述内容（从 `characters/characters.md` 复制而来）——这是确保跨页面角色一致性唯一的手段。
- **下载步骤**：每次调用 `image_generate` 后，系统都会将返回的URL下载到磁盘（例如使用 `curl -fsSL "<url>" -o <target>.png` 命令），并在继续执行后续流程前对下载的文件进行验证。

### SKILL.md 的简化内容

- CLI选项列（如 `--art`、`--tone`、`--layout`、`--aspect`、`--lang`、`--ref`、`--storyboard-only`、`--prompts-only`、`--images-only`、`--regenerate`）已改为纯英文的选项描述。
- 预设文件（`presets/*.md`）和 `ohmsha-guide.md`：原本的 `` `--style X` `` / `` `--art X --tone Y` `` 简写形式，现已改为 `art=X, tone=Y` 的格式，并搭配自然语言描述。
- `partial-workflows.md`：针对各技能的斜杠命令调用方式已改写为更符合用户意图的表达；与PDF相关的输出内容也已移除。
- `auto-selection.md`：优先级设置中不再考虑EXTEND.md相关选项。
- `analysis-framework.md`：语言优先级说明已更新（顺序变为：用户选项 → 对话内容 → 原始文本）。

### 文件命名规范

用户粘贴的源内容将保存为 `source-{slug}.md` 格式，其中 `{slug}` 为输出目录所使用的连字符分隔主题标识符。备份文件则采用相同格式，但在文件名后添加 `-backup-YYYYMMDD-HHMMSS` 后缀。现在，SKILL.md 和 `workflow.md` 均遵循这一统一的命名规范。

### 完全保留的内容

- 所有6种艺术风格定义（位于 `references/art-styles/` 目录）
- 所有7种色调定义（位于 `references/tones/` 目录）
- 所有7种布局定义（位于 `references/layouts/` 目录）
- 核心模板文件：`character-template.md`、`storyboard-template.md`、`base-prompt.md`
- 预设文件的主体内容（仅调整了开头几行；特殊规则保持不变）
- 作者信息、版本号及首页链接

## 与上游版本的同步

如需获取上游版本的更新：

```bash
# Compare versions
curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-comic/SKILL.md | head -5
# Look for the version: line

# Diff a reference file
diff <(curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-comic/references/art-styles/manga.md) \
     references/art-styles/manga.md
```

艺术风格、色调及布局参考文件通常可以直接被覆盖（因为它们是直接沿用上游版本的内容）。而 `SKILL.md`、`references/workflow.md`、`references/partial-workflows.md`、`references/auto-selection.md`、`references/analysis-framework.md`、`references/ohmsha-guide.md` 以及 `references/presets/*.md` 这些文件则必须手动合并，因为其中包含了针对 Hermes 系统的特定调整内容。

如果上游版本新增了兼容 Hermes 的 PDF 合并功能（无需额外安装 npm 依赖），则只需恢复 `scripts/` 目录，并在 `workflow.md` 文件中重新添加第 8 步即可。
