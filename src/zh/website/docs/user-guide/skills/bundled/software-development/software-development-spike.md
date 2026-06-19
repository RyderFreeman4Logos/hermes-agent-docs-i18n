---
title: "Spike — Throwaway experiments to validate an idea before build"
sidebar_label: "Spike"
description: "Throwaway experiments to validate an idea before build"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Spike

在正式构建之前，用于验证想法的临时实验。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development/spike` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent（基于 gsd-build/get-shit-done 改编） |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `spike`、`prototype`、`experiment`、`feasibility`、`throwaway`、`exploration`、`research`、`planning`、`mvp`、`proof-of-concept` |
| 相关技能 | [`html-artifact`](/docs/user-guide/skills/bundled/creative/creative-html-artifact)、[`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development)、[`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整 SKILL.md

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为内容。
:::

# Spike

当用户希望在投入实际构建之前**初步探索某个想法**时，可使用此技能——用于验证可行性、比较不同方案，或发现仅靠常规研究无法解答的疑问。Spike 设计上即为一次性使用，完成目标后即可丢弃。

当用户说出“让我试试这个”、“我想看看 X 是否可行”、“先做个临时实验”、“在决定使用 Y 之前”、“快速制作 Z 的原型”、“这真的可能吗？”或“比较 A 和 B”之类的话语时，即可加载此技能。

## 何时不应使用此技能

- 答案可通过文档或代码阅读获得——直接进行研究，无需构建
- 任务属于正式生产流程——请改用 `plan` 技能
- 该想法已得到验证——可直接进入实现阶段

## 如果用户已安装完整的 GSD 系统

如果 `gsd-spike` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），且用户希望使用完整的 GSD 工作流——包括持久的 `.planning/spikes/` 状态、跨会话的 MANIFEST 跟踪、Given/When/Then 判定格式，以及与 GSD 其他功能集成的提交规范——则建议优先使用 **`gsd-spike`**。此技能则是为那些没有（或不愿）使用完整系统的用户提供的轻量级独立版本。

## 核心流程

无论规模大小，每个 Spike 都遵循以下循环：

```
decompose  →  research  →  build  →  verdict
   ↑__________________________________________↓
                  iterate on findings
```

### 1. 拆解需求

将用户的想法拆分为**2-5个独立的可行性问题**。每个问题对应一个测试用例（spike），并采用“给定/当...时...则...”的框架以表格形式呈现：

| 序号 | 测试用例 | 需验证的条件（给定/当...时...则...） | 风险等级 |
|------|----------|----------------------------------|----------|
| 001 | websocket-streaming | 给定一个WS连接，当大语言模型开始流式输出Token时，客户端应在100毫秒内接收到数据块 | 高 |
| 002a | pdf-parse-pdfjs | 给定一份多页PDF文件，当使用pdfjs进行解析时，应能提取出结构化文本 | 中等 |
| 002b | pdf-parse-camelot | 给定一份多页PDF文件，当使用camelot进行解析时，应能提取出结构化文本 | 中等 |

**测试用例类型：**
- **标准型**——针对单个问题采用一种解决方案
- **对比型**——针对同一问题尝试不同方案（编号相同，后缀用`a`/`b`/`c`区分）

**优秀的测试用例问题**应具备明确的可行性，并能产生可观察的结果。
**糟糕的测试用例问题**则过于宽泛、无法产生可观察结果，或仅仅是“去阅读关于X的文档”。

**按风险程度排序**。优先处理最可能导致项目失败的那个测试用例。如果核心部分无法实现，再花时间开发简单部分毫无意义。

**仅在用户已明确知道自己想要测试的内容并如此说明时，才跳过拆解步骤**，直接将他们的想法作为一个整体测试用例。

### 2. 对齐需求（针对多个测试用例的需求）

先展示测试用例表格，然后询问：“是按此顺序全部开发，还是需要调整？”在编写任何代码之前，让用户自行决定删除、重新排序或修改需求描述。

### 3. 研究方案（每个测试用例在开发前进行）

测试用例并非无需研究——需要充分调研以选择合适的方案，然后再进行开发。针对每个测试用例需完成以下步骤：
1. **简要说明**：用2-3句话阐述该测试用例的目的、重要性以及主要风险。
2. **若存在多种可行方案，则列出对比信息**：

   | 方案 | 工具/库 | 优点 | 缺点 | 当前状态 |
   |------|--------|------|------|----------|
   | ... | ... | ... | ... | 维护中 / 已废弃 / 测试版 |

3. **选定一个方案**并说明理由。如果有多个可行的方案，可在同一个测试用例内快速实现多个版本进行对比。
4. **对于仅涉及逻辑运算且无外部依赖的案例，可直接跳过研究步骤**。

在研究阶段可使用Hermes提供的工具：
- `web_search("python websocket streaming libraries 2025")`——查找候选工具
- `web_extract(urls=["https://websockets.readthedocs.io/..."])`——读取实际文档内容（返回Markdown格式）
- `terminal("pip show websockets | grep Version")`——查看项目虚拟环境中已安装的版本信息

对于没有文档页面的库，可通过`read_file`命令克隆该库并读取其`README.md`文件或`examples/`目录中的内容。如果用户已配置Context7 MCP，它也是一个很好的信息来源——可通过`mcp_*_resolve-library-id`和`mcp_*_query-docs`命令获取相关文档。

### 4. 开发实现

每个测试用例对应一个独立的目录，确保其具有独立性。
```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```
**偏向于用户可交互的形式。** 如果唯一的输出只是一行“运行成功”的日志，那么这种快速测试就失去了意义。用户希望*切实感受到*该功能确实正在工作。按优先级排序的默认选项如下：

1. 一个可运行的 CLI 工具，能够接收输入并输出可见的结果；
2. 一个用于展示功能的简易 HTML 页面；
3. 带有一个端点的微型 Web 服务器；
4. 包含可识别断言条件的单元测试。

**注重深度而非速度。** 绝不要在仅通过一次正常流程测试后就宣称“功能正常”。应测试各种边界情况，并深入探究那些出人意料的结果。只有经过彻底的调查，所得出的结论才具有可信度。

**除非该快速测试有特殊需求，否则应避免**使用复杂的包管理工具、构建工具/打包器、Docker、环境配置文件以及配置系统。在快速测试中应将所有内容直接硬编码——毕竟这只是一个临时测试。

**构建一个快速测试**——典型的工具使用流程：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# Observe output, iterate.
```

**并行对比测试（002a / 002b）——任务委派功能。** 当有两种方案可以并行执行，且两者都需要实际的工程实现（而非仅10行代码的简单原型）时，可使用`delegate_task`功能将任务分解并分配处理。

```
delegate_task(tasks=[
    {"goal": "Build 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "Build 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子智能体都会输出各自的判断结果，你需要自行编写综合对比内容。

### 5. 判断结果

每个任务的 `README.md` 文件末尾均会标注：

```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
- ...

### What didn't
- ...

### Surprises
- ...

### Recommendation for the real build
- ...
```

**已验证** = 核心问题已得到肯定答复，并附有相关证据。  
**部分有效** = 在条件 X、Y、Z 下可正常运行——请将这些限制条件记录下来。  
**未验证** = 因此无法正常运行。这属于一次成功的探索性测试。  

## 对比测试

当两种方法能解答同一问题时（002a / 002b），请依次依次构建这两种方案，最后进行直接对比：

```markdown
## Head-to-head: pdfjs vs camelot

| Dimension | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| Extraction quality | 9/10 structured | 7/10 table-only |
| Setup complexity | npm install, 1 line | pip + ghostscript |
| Perf on 100-page PDF | 3s | 18s |
| Handles rotated text | no | yes |

**Winner:** pdfjs for our use case. Camelot if we need table-first extraction later.
```

## Frontier模式（选择下一个要测试的要点）

如果已有测试要点，且用户询问“接下来应该测试什么？”，系统会遍历现有目录并查找以下情况：

- **集成风险**——两个已验证的测试要点涉及同一资源，但却是独立进行的测试；
- **数据传递问题**——假设测试要点A的输出可与测试要点B的输入兼容，但实际上从未得到过验证；
- **需求认知缺口**——某些功能虽被假定存在，却缺乏实际验证；
- **替代方案**——针对那些处于“部分实现”或“已被否定”的测试要点，探索不同的处理方式。

系统会提出2到4个候选要点，并以“给定/当...时/那么...”的形式呈现，由用户自行选择。

## 输出要求

- 在项目根目录下创建`spikes/`文件夹（如果用户遵循GSD规范，则使用`.planning/spikes/`）；
- 每个测试要点对应一个子文件夹，命名为`NNN-描述性名称/`；
- 每个子文件夹内需包含`README.md`文件，详细记录该测试要点的目标、实现方法、测试结果及最终结论；
- 代码无需过于完善——如果一个测试要点需要花费两天时间才能“整理为可投入生产的版本”，那就说明它不是一个合格的测试要点。

## 出处说明

本指南改编自GSD（Get Shit Done）项目中的 `/gsd-spike` 工作流程——MIT授权 © 2025 Lex Christopherson（[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)）。完整的GSD系统还支持持久化存储测试要点状态、MANIFEST文件管理，以及与更完善的规范驱动型开发流程的集成；可通过 `npx get-shit-done-cc --hermes --global` 命令进行安装。
