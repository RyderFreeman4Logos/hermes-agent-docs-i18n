---
name: spike
description: "Throwaway experiments to validate an idea before build."
version: 1.0.0
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spike, prototype, experiment, feasibility, throwaway, exploration, research, planning, mvp, proof-of-concept]
    related_skills: [sketch, subagent-driven-development, plan]
---

# 临时探索任务（Spike）

当用户希望在投入实际开发之前**初步评估某个想法的可行性**——比如验证方案的可行性、比较不同方案，或是发现仅靠常规研究无法解答的问题时，可使用此技能。临时探索任务按设计即为一次性使用：在完成其既定目标后即可直接舍弃。

当用户说出“让我试试看”、“我想看看X是否可行”、“先临时探索一下这个”、“在决定采用Y之前”、“快速制作Z的原型”、“这真的有可能吗？”或“比较A和B”之类的话语时，即可加载此技能。

## 何时不应使用此技能

- 答案可通过文档或代码查看——直接进行研究即可，无需实际开发；
- 该任务属于正式生产环境的工作——请改用`plan`技能；
- 该想法已通过验证——可直接进入实现阶段。

## 若用户已安装完整的GSD系统

如果`gsd-spike`作为同级技能出现（通过`npx get-shit-done-cc --hermes`安装），且用户希望使用完整的GSD工作流——包括持久的`.planning/spikes/`状态管理、跨会话的MANIFEST跟踪、Given/When/Then格式的验证结果，以及与GSD其他功能相整合的提交规范——则建议优先使用**`gsd-spike`**。而对于那些未安装（或不愿安装）完整系统的用户，此技能则是轻量级的独立版本。

## 核心流程

无论规模大小，每个临时探索任务都遵循以下循环：

```
decompose  →  research  →  build  →  verdict
   ↑__________________________________________↓
                  iterate on findings
```

### 1. 拆解需求

将用户的想法拆分为**2到5个独立的可行性问题**，每个问题对应一个测试点。需以“给定/当…时/那么…”的框架，通过表格呈现这些问题：

| 序号 | 测试点 | 需验证的内容（给定/当…时/那么…） | 风险等级 |
|------|--------|----------------------------------|----------|
| 001 | websocket-streaming | 给定一个WebSocket连接，当大语言模型开始流式输出token时，客户端应在100毫秒内接收到数据块 | 高 |
| 002a | pdf-parse-pdfjs | 给定一份多页PDF文件，当使用pdfjs库解析后，应能提取出结构化文本 | 中等 |
| 002b | pdf-parse-camelot | 给定一份多页PDF文件，当使用camelot库解析后，应能提取出结构化文本 | 中等 |

**测试点类型：**
- **标准型**——针对单个问题的一种实现方案
- **对比型**——针对同一问题采用不同实现方案（编号相同，后缀用`a`/`b`/`c`区分）

**优秀的测试点问题**应具备明确的可行性要求，并能产生可观察的结果。
**糟糕的测试点问题**则过于宽泛、无法产生可观察结果，或仅仅是“去查阅关于X的文档”。

应按风险等级排序，优先处理最可能让项目失败的那个测试点。如果核心部分无法实现，再开发简单部分也毫无意义。

只有当用户已经明确知道自己想要测试的内容并明确说明时，才可跳过拆解步骤，直接将其作为一个测试点处理。

### 2. 对齐需求（适用于多测试点的需求）

先展示测试点表格，然后询问用户：“是按此顺序全部开发，还是需要调整？”在编写任何代码之前，让用户自行删除、重新排序或修改需求描述。

### 3. 做调研（每个测试点在开发前进行）

测试点的设计并非无需调研——需要先充分研究以选出合适的实现方案，然后再进行开发。针对每个测试点需完成以下步骤：
1. **简要说明**：用2到3句话阐述该测试点的目的、重要性以及主要风险。
2. **若存在多种可行方案，则列出对比信息**：

   | 实现方案 | 工具/库 | 优点 | 缺点 | 当前状态 |
   |----------|---------|------|------|----------|
   | ... | ... | ... | ... | 正在维护 / 已废弃 / 测试版 |

3. **选定一个方案**，并说明理由。如果存在2种及以上可行的方案，可在同一测试点内快速实现多个版本进行对比。
4. 对于那些仅涉及逻辑处理且没有外部依赖的测试点，可直接跳过调研步骤。

在调研阶段可使用Hermes提供的工具：
- `web_search("python websocket streaming libraries 2025")`——查找候选方案
- `web_extract(urls=["https://websockets.readthedocs.io/..."])`——读取实际文档内容（返回Markdown格式）
- `terminal("pip show websockets | grep Version")`——查看项目虚拟环境中已安装的版本信息

对于没有文档页面的库，可通过`read_file`命令克隆该库并读取其`README.md`文件或`examples/`目录中的内容。如果用户已配置Context7 MCP，它也是一个不错的信息来源——可通过`mcp_*_resolve-library-id`和`mcp_*_query-docs`命令获取相关文档。

### 4. 开发实现

每个测试点对应一个独立目录，确保各部分能够独立运行。

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

**偏向于用户可交互的形式。** 如果唯一的输出仅是一条显示“功能正常”的日志行，那么这种快速测试便失去了意义。用户希望*切实感受到*该功能正在运行。按优先级排序的默认选项如下：

1. 一个可运行的 CLI 工具，能够接收输入并输出可观察的结果；
2. 一个用于展示功能的简单 HTML 页面；
3. 一个带有单个端点的微型 Web 服务器；
4. 一个包含明确断言条件的单元测试，用于验证功能表现。

**注重深度而非速度。** 绝不要在仅完成一次正常流程测试后就宣称“功能正常”。务必测试边缘情况，并跟进那些出人意料的结果。只有经过彻底的调查，所得出的结论才具有可信度。

**除非该快速测试有特殊需求，否则应避免**使用复杂的包管理工具、构建工具/打包器、Docker、环境配置文件以及配置系统。所有内容都应直接硬编码——因为这毕竟只是个快速测试。

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
