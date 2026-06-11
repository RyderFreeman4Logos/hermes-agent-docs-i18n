# 端口说明 — baoyu-article-illustrator

该版本基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.57.0 迁移而来。

## 与上游版本的差异

`SKILL.md`、`references/workflow.md`、`references/usage.md`、`references/style-presets.md`、`references/styles.md`、`references/prompt-construction.md` 以及 `prompts/system.md` 等文件均进行了适配处理。23个样式文件和4个调色板文件则保持原样复制。同时，`references/config/` 目录已被完全移除。

### 适配内容

| 变更项 | 上游版本 | Hermes版本 |
|--------|----------|------------|
| 元数据命名空间 | `openclaw` | `hermes` |
| 触发方式 | `/baoyu-article-illustrator`斜杠命令 + CLI参数 | 自然语言技能匹配 |
| 用户配置 | EXTEND.md（项目/用户/XDG路径）+首次设置流程 | 已移除——不属于Hermes基础设施范畴 |
| 用户提问方式 | `AskUserQuestion`（批量、多问题） | `clarify`工具（一次仅一个问题） |
| 图像生成方式 | `baoyu-imagine`（Bun/TypeScript实现，支持多提供商，可接受`--ref`参数并保存到本地路径） | `image_generate`（仅返回URL；由智能体通过`terminal`/`curl`下载图像） |
| 后端选择方式 | 用户通过CLI参数选择提供商 | 无法由智能体选择——`image_generate`会使用用户配置的FAL模型。同时已从`prompts/system.md`中移除硬编码的“nano banana pro”相关内容 |
| 参考图片处理方式 | 通过`--ref`参数传递给后端，再通过shell命令复制 | `vision_analyze`工具会提取图片的文本描述（二进制数据不会被`write_file`/`read_file`函数处理）；该描述会被嵌入到提示词中。如需本地保存，可选择使用`terminal cp`命令 |
| 支持的平台 | Linux/macOS/Windows/WSL/PowerShell | 仅支持Linux/macOS |
| 文件操作方式 | Bash命令 | Hermes内置文件工具：文本文件使用`write_file`/`read_file`，二进制文件及URL下载使用`terminal`，图像读取使用`vision_analyze` |
| 水印功能 | 由EXTEND.md中的`watermark.enabled`参数控制 | 可选——用户可针对每篇文章单独开启 |
| 输出目录 | EXTEND.md中的`default_output_dir`参数指定（可选子目录：imgs子目录/同一目录/illustrations子目录/独立目录） | 根据输入类型自动确定默认输出目录；用户可在请求中自行指定 |

### 保留的内容

- 类型×样式×调色板的三维框架
- 所有样式定义（23个文件，原样保留）
- 所有调色板定义（4个文件，原样保留）
- 核心参考文件（工作流程、提示词构建规则、样式设置、样式预设）——已针对Hermes工具集进行适配
- 核心设计原则与工作流程结构（分析→确认→草图绘制→生成提示词→图像生成）
- 将提示词文件作为可复现性记录的规范
- 作者信息、版本号及项目主页链接

## 与上游版本的同步

如需获取上游版本的更新：

```bash
# Compare versions
curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-article-illustrator/SKILL.md | head -5
# Look for version: line

# Diff style/palette files (safe to overwrite — unchanged from upstream)
diff <(curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-article-illustrator/references/styles/blueprint.md) references/styles/blueprint.md
```

`references/styles/*` 和 `references/palettes/*` 文件可直接被覆盖。而 `SKILL.md`、`references/workflow.md`、`references/usage.md`、`references/style-presets.md`、`references/styles.md`、`references/prompt-construction.md` 以及 `prompts/system.md` 则必须手动合并，因为这些文件包含了针对 Hermes 的特定调整（如工具集成方式、对后端的通用处理逻辑，以及已移除的 EXTEND.md 相关引用）。
