# 参考示例（Anthropic HTML效果展示库）

共有20个完整且独立的参考HTML文件——即Anthropic的[HTML效果展示库](https://github.com/anthropics/html-effectiveness)，采用MIT许可证授权。这些正是该技能所依据的标准范本。在开始编写内容之前（工作流程的第二步），**务必先阅读与自身使用模式相匹配的示例**：一个经过精心设计的完整示例具备文字描述无法呈现的排版密度、间距与结构优势。而其他参考资料则解释了这些设计模式背后的原理，能让你直观地了解其整体结构。

这些文件并未被纳入当前技能模块中（它们属于他人的活跃代码库，大小约为384 KB）。可通过附带的脚本获取它们——该脚本具备幂等性，因此每次只需运行一次即可；如果示例缺失，它会自动克隆该代码库，否则则会拉取最新版本。

## 先获取并阅读（编写前必做步骤）

```
terminal:  bash scripts/fetch-examples.sh
read_file  references/examples/<file-for-your-mode>.html
```

该脚本会将相关文件保存至 `references/examples/` 目录中。请务必先运行此脚本——它的执行成本极低且具备自我修复功能，因此您无需担心示例文件是否缺失。之后即可查看索引，或直接跳转到对应模式下的文件。

```
read_file references/examples/index.html              # categorized index of all 20
read_file references/examples/03-code-review-pr.html  # a specific example
```

只有当数据获取确实失败（无网络连接）时，才应退而仅使用那些精简后的模式参考资料——并且要明确说明这一点，因为此时你实际上是在没有原始代码的情况下进行工作。

## 各文件的功能说明 → 应该阅读哪一篇

选择与你的使用场景最接近的示例，阅读后加以调整，而非直接复制。

| 文件名 | 使用场景 | 适合在构建……时阅读 |
|---|---|---|
| `01-exploration-code-approaches.html` | 变体设计 | 对不同代码实现方案的优缺点进行并列对比，并给出推荐建议 |
| `02-exploration-visual-designs.html` | 变体设计 | 在明暗主题可切换的界面中展示实时设计方向 |
| `03-code-review-pr.html` | 代码审查 | 提供 PR 和差异对比功能——采用标准的三列差异网格、风险分析图以及注释气泡 |
| `04-code-understanding.html` | 代码解释 | 通过内联 SVG 的请求路径图和调用栈来展示代码执行流程 |
| `05-design-system.html` | 报告文档 | 提供设计令牌和组件参考手册 |
| `06-component-variants.html` | 编辑器功能 | 基于 `:root` 自定义属性控制项的实时组件矩阵展示 |
| `07-prototype-animation.html` | 编辑器功能 | CSS 微交互调节工具（包含缓动参数调整功能，以及静态 CSS 导出功能） |
| `08-prototype-interaction.html` | 编辑器功能 | 支持拖拽重新排序的可用性测试工具（仅基于 DOM，刻意不提供导出功能） |
| `09-slide-deck.html` | 报告文档 | 具有滚动定位功能的幻灯片演示文稿（纯 CSS 实现分页） |
| `10-svg-illustrations.html` | 图表展示 | 可独立导出的内联 SVG 插图 |
| `11-status-report.html` | 报告文档 | 每周状态报告（无需 JavaScript，使用形状令牌和统计图表呈现） |
| `12-incident-report.html` | 报告文档 | 事故事后分析报告（仅使用 CSS 的时间轴以及检查清单） |
| `13-flowchart-diagram.html` | 图表展示 | 带有注释的可点击流程图，同时配有同步的详细信息面板（采用 `data-k` 模式） |
| `14-research-feature-explainer.html` | 代码解释 | 解释功能 X 的工作原理——包含固定锚点导航的文档框架以及分页代码展示 |
| `15-research-concept-explainer.html` | 代码解释 | 交互式概念说明工具（包含确定性哈希 SVG 演示以及术语表） |
| `16-implementation-plan.html` | 规划文档 | 实施计划——包括里程碑时间表、SVG 架构以及 DOM 原型设计 |
| `17-pr-writeup.html` | 代码审查 | 为代码审查者准备的 PR 审阅指南——逐文件讲解、标记过的差异对比以及目录结构 |
| `18-editor-triage-board.html` | 编辑器功能 | 支持拖拽分类的待办板，可导出为 Markdown 格式 |
| `19-editor-feature-flags.html` | 编辑器功能 | 配置标志编辑器，支持差异对比以及完整 JSON 数据导出 |
| `20-editor-prompt-tuner.html` | 编辑器功能 | 提示词模板编辑器（支持内容编辑、实时预览以及提示词复制功能） |

这 20 个文件均为单文件结构，无依赖项，也无需构建流程——正符合该技能所要求的严谨标准。你可以利用它们来调整内容的密度、间距以及整体风格；而那些精简后的参考资料（如 `house-style.md`、`svg-diagrams.md`、`throwaway-editors.md` 等）则会解释每种设计模式为何采用当前形式。
