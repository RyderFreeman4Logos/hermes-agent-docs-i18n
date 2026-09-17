---
title: "Spike — Throwaway experiments to validate an idea before build"
sidebar_label: "Spike"
description: "Throwaway experiments to validate an idea before build"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Spike

在正式构建之前，用于验证某个想法的临时性实验。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development\spike` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent（基于 gsd-build/get-shit-done 改编） |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `spike`、`prototype`、`experiment`、`feasibility`、`throwaway`、`exploration`、`research`、`planning`、`mvp`、`proof-of-concept` |
| 相关技能 | [`sketch`](/docs/user-guide/skills/optional/creative/creative-sketch)、[`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当该技能处于激活状态时，智能体将以此作为操作指令。
:::

# Spike

当用户希望在投入大量精力进行正式构建之前**初步探索某个想法**——验证其可行性、比较不同方案，或发现仅靠常规研究无法解答的疑问时，可使用此技能。Spike 设计上即为一次性工具，完成既定目标后即可直接弃用。

当用户说出“让我试试看”、“我想验证一下X是否可行”、“快速构思一下这个方案”、“在决定采用Y之前”、“先做一个Z的简易原型”、“这真的有可能吗？”或“对比一下A和B”之类的话语时，应加载此功能。

## 何时不应使用此功能

- 答案可通过文档或代码查看获得——直接进行研究即可，无需构建；
- 该任务属于正式生产流程——请改用`plan`技能；
- 该想法已得到验证——可直接进入实施阶段。

## 若用户已安装完整的GSD系统

如果`gsd-spike`作为同级技能出现（通过`npx get-shit-done-cc --hermes`安装），当用户希望使用完整的GSD工作流时，建议优先选择**`gsd-spike`**。完整工作流具备持久化的`.planning/spikes/`状态管理、跨会话的MANIFEST跟踪功能、Given/When/Then格式的验证结果，以及与GSD其他组件相兼容的提交规范。而对于那些没有（或不想使用）完整系统的用户，该技能则提供了轻量级的独立版本。

## 核心流程

无论规模大小，每个快速构思任务都遵循以下循环：

```
decompose  →  research  →  build  →  verdict
   ↑__________________________________________↓
                  iterate on findings
```

### 1. 拆解需求

将用户的想法拆分为**2到5个独立的可行性问题**。每个问题对应一个“探索性任务”。需以表格形式呈现，并采用“给定/当...时...则...”的框架：

| 序号 | 探索性任务 | 需验证的条件（给定/当...时...则...） | 风险等级 |
|------|------------|-----------------------------------|----------|
| 001 | websocket-streaming | 给定一个WebSocket连接，当大语言模型开始流式输出Token时，客户端应在100毫秒内收到数据块 | 高 |
| 002a | pdf-parse-pdfjs | 给定一份多页PDF文件，当使用pdfjs库进行解析时，应能提取出结构化文本 | 中等 |
| 002b | pdf-parse-camelot | 给定一份多页PDF文件，当使用camelot库进行解析时，应能提取出结构化文本 | 中等 |

**探索性任务的类型：**
- **标准型**——针对单个问题采用一种解决方案
- **对比型**——针对同一问题尝试不同方案（编号相同，后缀用字母`a`/`b`/`c`区分）

**好的探索性任务问题**应具备明确的可行性目标且能产生可观察的结果。
**不好的探索性任务问题**则过于宽泛、无法产生可观察结果，或仅仅是“去查阅关于X的文档”。

**按风险等级排序**。优先处理最可能导致项目失败的探索性任务。如果核心难点无法解决，再花时间开发简单部分毫无意义。

**仅当用户已明确知道自己想要测试的内容并明确说明时**，才跳过拆解步骤，直接将其想法视为一个单独的探索性任务。

### 2. 对齐需求（适用于包含多个探索性任务的场景）

先展示探索性任务表格，然后询问：“是按此顺序全部开发，还是需要调整？”在编写任何代码之前，让用户自行决定删除、重新排序或修改任务内容。

### 3. 做研究（每个探索性任务在开发前进行）

开展探索性研究并非毫无必要——你需要进行充分的研究以选定合适的方法，然后再着手实现。针对每个探索任务，请遵循以下步骤：

1. **明确任务目标**：用2-3句话说明该任务的含义、重要性以及主要风险点。
2. **列出可选方案**：若存在多种可行方案，则需列出：
   | 方案 | 工具/库 | 优点 | 缺点 | 当前状态 |
   |------|---------|------|------|----------|
   | ... | ... | ... | ... | 在维护中 / 已废弃 / 测试版 |

3. **选定一种方案**：并说明选择理由。如果有多个可行的方案，可在该探索任务中快速实现它们的不同变体。
4. **跳过研究步骤**：对于那些仅依赖纯逻辑且无外部依赖的方案，可直接进行开发。

在研究阶段可利用Hermes提供的工具：
- `web_search("python websocket streaming libraries 2025")` —— 搜索候选库
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` —— 阅读相关文档（返回Markdown格式内容）
- `terminal("pip show websockets | grep Version")` —— 查看项目虚拟环境中已安装的版本信息

对于没有文档页面的库，可先克隆该库，再通过`read_file`函数读取其`README.md`文件或`examples/`目录中的内容。如果用户已配置Context7 MCP，它也是一个很好的信息来源——可使用`mcp_*_resolve-library-id`和`mcp_*_query-docs`函数获取相关资料。

### 4. 开发实现

每个探索任务应对应一个独立的目录，确保其具有独立性。
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
**偏向于用户可交互的形式。** 如果唯一的输出仅是一行表明“功能正常”的日志，那么这种快速测试便失去了意义。用户希望*切实感受到*该功能正在运行。按优先级排序的默认选项如下：

1. 一个可运行的 CLI 工具，能够接收输入并输出可见结果；
2. 一个用于演示功能的简单 HTML 页面；
3. 带有一个端点的微型 Web 服务器；
4. 包含可识别断言条件的单元测试。

**质量重于速度。** 绝不要在仅通过一次正常流程测试后就宣称“功能正常”。务必测试边界情况，并跟进那些出乎意料的发现。只有经过严谨的调查，得出的结论才具有可信度。

**除非该快速测试有特殊需求，否则应避免**使用复杂的包管理工具、构建工具/打包器、Docker、环境配置文件以及配置系统。所有内容都应直接硬编码——毕竟这只是一次快速测试而已。

**构建一个快速测试**的典型工具流程：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python main.py")
# Observe output, iterate.
```

**并行对比测试（002a / 002b）——任务委派功能。** 当有两种方案可以并行执行，且两者都需要真正的工程实现（而非仅10行代码的简易原型）时，可使用`delegate_task`功能将任务分发出去：

```
delegate_task(tasks=[
    {"goal": "Build 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "Build 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子智能体都会输出各自的判定结果，由您来综合判断谁更优。

### 5. 判定结果

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
**部分有效** = 在限制条件 X、Y、Z 下可以正常运行——请将这些限制条件记录下来。  
**未验证** = 因此无法正常运行。这属于一次成功的探索性测试。  

## 对比测试

当两种方法用于回答同一个问题（002a / 002b）时，应先依次构建这两种方案，最后进行直接对比：

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

## Frontier模式（选择下一个要处理的测试点）

如果已有测试点，且用户询问“接下来应该处理哪个测试点？”，系统会遍历现有目录并查找以下情况：

- **集成风险**——两个已验证的测试点针对同一资源，但却是独立进行的测试；
- **数据传递问题**——假设测试点A的输出与测试点B的输入兼容，但实际上从未经过验证；
- **愿景缺口**——某些功能虽被假定存在，但尚未得到证实；
- **替代方案**——针对那些状态为“部分完成”或“无效”的测试点，探索不同的处理方式。

系统会提出2到4个候选测试点，并以“给定/当...时/那么...”的形式呈现，由用户自行选择。

## 输出要求

- 在项目根目录下创建`spikes/`文件夹（如果用户遵循GSD规范，则使用`.planning/spikes/`）；
- 每个测试点对应一个子目录，命名为`NNN-描述性名称/`；
- 每个测试点需配备`README.md`文件，说明问题、处理方法、结果及最终结论；
- 代码无需过于完善——如果一个测试点需要花费两天时间才能“准备好投入生产环境”，那就说明它不是一个合格的测试点。

## 出处说明

本指南改编自GSD（Get Shit Done）项目中的 `/gsd-spike` 工作流程——MIT许可，© 2025 Lex Christopherson（[gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)）。完整的GSD系统还支持测试点状态的持久化存储、MANIFEST文件管理，以及与更完善的规范驱动型开发流程的集成；可通过`npx get-shit-done-cc --hermes --global`命令进行安装。
