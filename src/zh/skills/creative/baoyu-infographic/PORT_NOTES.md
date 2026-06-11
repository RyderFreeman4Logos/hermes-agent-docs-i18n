# 端口说明 — baoyu-infographic

基于 [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) v1.56.1 版本移植而来。

## 与上游版本的差异

仅修改了 `SKILL.md` 文件，其余45个参考文件均为直接复制。

### SKILL.md 的调整内容

| 对比项 | 上游版本 | Hermes版本 |
|--------|----------|------------|
| 元数据命名空间 | `openclaw` | `hermes` |
| 触发方式 | `/baoyu-infographic` 斜杠命令 | 自然语言技能匹配 |
| 用户配置 | EXTEND.md 文件（项目/用户/XDG路径） | 已移除——不属于Hermes基础设施范畴 |
| 用户提问方式 | `AskUserQuestion`（批量提问） | `clarify` 工具（逐个提问） |
| 图像生成方式 | baoyu-imagine（Bun/TypeScript实现） | `image_generate` 工具 |
| 支持的平台 | Linux/macOS/Windows/WSL/PowerShell | 仅支持Linux/macOS |
| 文件操作方式 | Bash命令 | Hermes文件工具（write_file、read_file） |

### 保留的内容

- 所有布局定义文件（21个）
- 所有样式定义文件（21个）
- 核心参考文件（analysis-framework、base-prompt、structured-content-template）
- 推荐组合表
- 关键词快捷键表
| 核心原则与工作流程结构 |
| 作者、版本及首页归属信息 |

## 与上游版本的同步

如需获取上游版本的更新：
```bash
# Compare versions
curl -sL https://raw.githubusercontent.com/JimLiu/baoyu-skills/main/skills/baoyu-infographic/SKILL.md | head -5
# Look for version: line

# Diff reference files
diff <(curl -sL https://raw.githubusercontent.com/.../references/layouts/bento-grid.md) references/layouts/bento-grid.md
```

参考文件可直接被覆盖（因其内容与上游版本完全一致）。而 SKILL.md 文件则必须手动合并，因为它包含了针对 Hermes 系统的特定定制内容。
