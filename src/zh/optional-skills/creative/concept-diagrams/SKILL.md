---
name: concept-diagrams
description: Generate flat, minimal light/dark-aware SVG diagrams as standalone HTML files, using a unified educational visual language with 9 semantic color ramps, sentence-case typography, and automatic dark mode. Best suited for educational and non-software visuals — physics setups, chemistry mechanisms, math curves, physical objects (aircraft, turbines, smartphones, mechanical watches), anatomy, floor plans, cross-sections, narrative journeys (lifecycle of X, process of Y), hub-spoke system integrations (smart city, IoT), and exploded layer views. If a more specialized skill exists for the subject (dedicated software/cloud architecture, hand-drawn sketches, animated explainers, etc.), prefer that — otherwise this skill can also serve as a general-purpose SVG diagram fallback with a clean educational look. Ships with 15 example diagrams.
version: 0.1.0
author: v1k22 (original PR), ported into hermes-agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagrams, svg, visualization, education, physics, chemistry, engineering]
    related_skills: [architecture-diagram, excalidraw, generative-widgets]
---

# 概念图绘制

通过统一的扁平化极简设计系统，生成专业级的 SVG 图表。输出结果为一个独立的 HTML 文件，可在任何现代浏览器中以一致的方式呈现，并自动支持浅色/深色模式切换。

## 适用场景

**最适合用于：**
- 物理实验装置、化学反应机制、数学曲线、生物学内容
- 实体物体（飞机、涡轮机、智能手机、机械表、细胞等）
- 解剖结构图、截面图、分解视图
- 平面图、建筑转换图
- 叙事流程（如 X 的生命周期、Y 的处理过程）
- 中心辐射式系统集成（智慧城市、物联网网络、电力网格）
- 各领域的教育类/教科书风格可视化内容
- 定量图表（分组柱状图、能量分布图）

**如需以下功能，请优先考虑其他工具：**
- 具有深色科技风格的专用软件或云基础设施架构设计（可考虑使用 `architecture-diagram` 工具）
- 手绘式白板草图（可考虑使用 `excalidraw` 工具）
- 动态演示或视频输出（可考虑使用动画技能）

如果该主题有更专业的技能可用，建议优先使用。若没有合适选项，此技能可作为通用的 SVG 图表备选方案——其输出将具备下文所述的简洁教育风格，几乎适用于所有主题，是合理的默认选择。

## 工作流程

1. 确定图表类型（见下文的“图表类型”说明）。
2. 按照设计系统规则布局各组成部分。
3. 以 `templates/template.html` 作为模板编写完整的 HTML 页面——将 SVG 内容粘贴到模板中标记为 `<!-- PASTE SVG HERE -->` 的位置。
4. 将文件保存为独立的 `.html` 文件（例如 `~/my-diagram.html` 或 `./my-diagram.html`）。
5. 用户可直接在浏览器中打开该文件——无需服务器，也无需额外依赖。

可选：如果用户需要浏览多个图表的画廊，可参考文末的“本地预览服务器”相关说明。

加载 HTML 模板：
```
skill_view(name="concept-diagrams", file_path="templates/template.html")
```

该模板集成了完整的CSS设计系统（包括以`c-*`开头的颜色类、文本类、明暗模式变量以及箭头标记样式）。您生成的SVG文件依赖于宿主页面中存在这些样式类。

---

## 设计系统

### 设计理念

- **扁平化**：不使用渐变、阴影、模糊、发光或霓虹效果。
- **极简主义**：仅展示核心内容，框内不添加装饰性图标。
- **一致性**：所有图表均采用相同的颜色、间距、字体及线条宽度。
- **支持深色模式**：通过CSS类实现颜色自动适配，无需为不同模式准备独立的SVG文件。

### 颜色方案

共有9组颜色渐变，每组包含7个色阶。只需将对应的类名添加到`<g>`元素或形状元素上，模板中的CSS即可处理明暗两种模式。

| 类名       | 50（最浅） | 100     | 200     | 400     | 600     | 800     | 900（最深） |
|------------|---------------|---------|---------|---------|---------|---------|---------------|
| `c-purple` | #EEEDFE | #CECBF6 | #AFA9EC | #7F77DD | #534AB7 | #3C3489 | #26215C |
| `c-teal`   | #E1F5EE | #9FE1CB | #5DCAA5 | #1D9E75 | #0F6E56 | #085041 | #04342C |
| `c-coral`  | #FAECE7 | #F5C4B3 | #F0997B | #D85A30 | #993C1D | #712B13 | #4A1B0C |
| `c-pink`   | #FBEAF0 | #F4C0D1 | #ED93B1 | #D4537E | #993556 | #72243E | #4B1528 |
| `c-gray`   | #F1EFE8 | #D3D1C7 | #B4B2A9 | #888780 | #5F5E5A | #444441 | #2C2C2A |
| `c-blue`   | #E6F1FB | #B5D4F4 | #85B7EB | #378ADD | #185FA5 | #0C447C | #042C53 |
| `c-green`  | #EAF3DE | #C0DD97 | #97C459 | #639922 | #3B6D11 | #27500A | #173404 |
| `c-amber`  | #FAEEDA | #FAC775 | #EF9F27 | #BA7517 | #854F0B | #633806 | #412402 |
| `c-red`    | #FCEBEB | #F7C1C1 | #F09595 | #E24B4A | #A32D2D | #791F1F | #501313 |

#### 颜色分配规则

颜色用于表达**含义**，而非顺序。切勿像彩虹一样循环使用不同颜色。

- 按**类别**对节点进行分组——同一类型的节点使用相同的颜色。
- 对于中性或结构性的节点（如起点、终点、通用步骤、用户角色），请使用`c-gray`。
- 每个图表建议使用**2-3种颜色**，而非6种以上。
- 通用类别优先选择`c-purple`、`c-teal`、`c-coral`、`c-pink`。
- `c-blue`、`c-green`、`c-amber`、`c-red`则用于表示特定语义（信息、成功、警告、错误）。

明暗模式下的色阶对应关系（由模板CSS处理，只需使用相应类名即可）：
- 明亮模式：填充色为50，线条色为600，标题色为800/副标题色为600。
- 深色模式：填充色为800，线条色为200，标题色为100/副标题色为200。

### 字体设计

仅允许使用两种字体大小，不得有任何例外。

| 类名 | 字号 | 字重 | 用途 |
|------|------|------|-----|
| `th`  | 14px | 500    | 节点标题、区域标签 |
| `ts`  | 12px | 400    | 副标题、描述文字、箭头标签 |
| `t`   | 14px | 400    | 普通文本 |

- **始终使用小写句首字母**。禁止使用大写开头或全大写形式。
- 所有 `<text>` 元素必须添加类名（`t`、`ts` 或 `th`），不得存在无类名的文本。
- 框内的所有文本需设置 `dominant-baseline="central"` 属性。
- 框内居中的文本需设置 `text-anchor="middle"` 属性。

**宽度估算（近似值）：**
- 字重500、字号14px：每个字符约8px宽度。
- 字重400、字号12px：每个字符约6.5px宽度。
- 始终需确保满足以下公式：`box_width >= (字符数 × 每字符像素数) + 48`（两侧各24px的边距）。

### 间距与布局

- **视图框**：`viewBox="0 0 680 H"`，其中H为内容高度加上40px的缓冲空间。
- **安全区域**：x轴范围为40至640，y轴范围为40至(H-40)。
- **框与框之间的间距**：至少为60px。
- **框内的内边距**：水平方向24px，垂直方向12px。
- **箭头与框边缘的间距**：10px。
- **单行框**：高度为44px。
- **双行框**：高度为56px，标题与副标题的基线之间间距为18px。
- **容器内边距**：每个容器内部至少保留20px的边距。
- **最大嵌套层级**：建议不超过2-3层。在680px的宽度下，更深层的嵌套会导致内容难以辨识。

### 线条与形状

- **线条宽度**：所有节点边框的宽度均为0.5px，既非1px也非2px。
- **矩形圆角**：节点的圆角为`rx="8"`，内部容器的圆角为`rx="12"`，外部容器的圆角则为`rx="16"`至`rx="20"`。
- **连接线路径**：必须设置 `fill="none"`。否则SVG默认会使用黑色填充。

### 箭头标记

请在**每个**SVG文件的开头添加以下 `<defs>` 块：

```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

在相应行上使用 `marker-end="url(#arrow)"`。箭头会通过 `context-stroke` 继承该行的颜色。

### CSS 类（由模板提供）

模板页面提供了以下 CSS 类：

- 文本类：`.t`、`.ts`、`.th`
- 中性类：`.box`、`.arr`、`.leader`、`.node`
- 颜色渐变类：`.c-purple`、`.c-teal`、`.c-coral`、`.c-pink`、`.c-gray`、`.c-blue`、`.c-green`、`.c-amber`、`.c-red`（所有类均支持自动明暗模式切换）

您无需重新定义这些类——只需在 SVG 中直接使用即可。模板文件中已包含完整的 CSS 定义。

---

## SVG 基础模板

模板页面中的每个 SVG 都遵循完全相同的结构：

```xml
<svg width="100%" viewBox="0 0 680 {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Diagram content here -->

</svg>
```

请将 `{HEIGHT}` 替换为实际计算出的高度值（最后一个元素的底部位置加上 40px）。

### 节点样式

**单行节点（44px）：**
```xml
<g class="node c-blue">
  <rect x="100" y="20" width="180" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="190" y="42" text-anchor="middle" dominant-baseline="central">Service name</text>
</g>
```

**两行节点（56像素）：**
```xml
<g class="node c-teal">
  <rect x="100" y="20" width="200" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="200" y="38" text-anchor="middle" dominant-baseline="central">Service name</text>
  <text class="ts" x="200" y="56" text-anchor="middle" dominant-baseline="central">Short description</text>
</g>
```

**连接器（无标签）：**
```xml
<line x1="200" y1="76" x2="200" y2="120" class="arr" marker-end="url(#arrow)"/>
```

**容器（虚线或实线）：**
```xml
<g class="c-purple">
  <rect x="40" y="92" width="600" height="300" rx="16" stroke-width="0.5"/>
  <text class="th" x="66" y="116">Container label</text>
  <text class="ts" x="66" y="134">Subtitle info</text>
</g>
```

## 图表类型

根据主题选择合适的布局：

1. **流程图** — 用于展示 CI/CD 流水线、请求生命周期、审批工作流及数据处理流程。采用单向流动方式（自上而下或从左至右），每行最多包含 4-5 个节点。
2. **结构/容器图** — 适用于表示云基础设施的嵌套关系以及分层系统架构。由大型外部容器包裹内部区域，用虚线矩形表示逻辑分组。
3. **API/端点映射图** — 用于展示 REST 路由和 GraphQL 模式。以根节点为起点，分支出多个资源组，每个资源组内包含端点节点。
4. **微服务拓扑图** — 适用于描述服务网格和事件驱动系统。将各服务视为节点，用箭头表示通信方式，节点间通过消息队列连接。
5. **数据流图** — 用于展示 ETL 流水线和流处理架构。数据从左侧源头流向右侧处理节点，最终到达目标端。
6. **实体/结构图** — 适用于绘制车辆、建筑物、硬件部件或人体解剖结构等。需使用与实际形状匹配的图形元素：<path>用于表示弯曲物体，<polygon>用于表示锥形物体，<ellipse>/<circle>用于表示圆柱形部件，嵌套的<rect>则用于表示分隔区域。详情请参阅 `references/physical-shape-cookbook.md`。
7. **基础设施/系统集成图** — 适用于展示智慧城市、物联网网络及多领域系统架构。采用中心平台连接各子系统的辐射状布局，并使用不同的语义线条样式（如 `.data-line`、`.power-line`、`.water-pipe`、`.road`）。详情请参阅 `references/infrastructure-patterns.md`。
8. **UI/仪表板原型图** — 用于设计管理面板和监控仪表板。在屏幕框架内嵌套图表、仪表盘元素等。详情请参阅 `references/dashboard-patterns.md`。

对于实体图、基础设施图和仪表板图，生成前需加载对应的参考文件——这些文件提供了现成的 CSS 类和图形基础元素。

---

## 验证清单

在最终确定任何 SVG 文件之前，请务必检查以下所有项目：

1. 所有 `<text>` 元素都必须具有 `t`、`ts` 或 `th` 类名。
2. 箱体内的所有 `<text>` 元素都需设置 `dominant-baseline="central"` 属性。
3. 用作箭头的所有连接器 `<path>` 或 `<line>` 元素都需设置 `fill="none"` 属性。
4. 不存在箭头线条穿过无关箱体的情况。
5. 当文本字体大小为 14px 时，`box_width` 需满足 `box_width >= (最长标签字符数 × 8) + 48` 的要求。
6. 当文本字体大小为 12px 时，`box_width` 需满足 `box_width >= (最长标签字符数 × 6.5) + 48` 的要求。
7. ViewBox 的高度应等于最底部元素的高度再加上 40px。
8. 所有内容都需保持在 x=40 到 x=640 的范围内。
9. 颜色类（如 `c-*`）必须应用于 `<g>` 元素或图形元素上，绝不能应用于 `<path>` 连接器上。
10. 文件中必须存在箭头定义的 `<defs>` 块。
11. 不允许使用渐变、阴影、模糊或发光效果。
12. 所有节点边框的线条宽度均为 0.5px。

---

## 输出与预览

### 默认输出：独立 HTML 文件

生成一个用户可直接打开的单一 `.html` 文件。无需服务器，无依赖项，可在离线环境中使用。文件格式如下：

```python
# 1. Load the template
template = skill_view("concept-diagrams", "templates/template.html")

# 2. Fill in title, subtitle, and paste your SVG
html = template.replace(
    "<!-- DIAGRAM TITLE HERE -->", "SN2 reaction mechanism"
).replace(
    "<!-- OPTIONAL SUBTITLE HERE -->", "Bimolecular nucleophilic substitution"
).replace(
    "<!-- PASTE SVG HERE -->", svg_content
)

# 3. Write to a user-chosen path (or ./ by default)
write_file("./sn2-mechanism.html", html)
```

告知用户如何打开它：

```
# macOS
open ./sn2-mechanism.html
# Linux
xdg-open ./sn2-mechanism.html
```

### 可选功能：本地预览服务器（多图表展示库）

仅当用户明确要求查看多个图表的浏览式展示库时才使用此功能。

**规则：**
- 仅绑定到 `127.0.0.1`，绝不可使用 `0.0.0.0`。在共享网络环境中，通过所有网络接口公开图表存在安全风险。
- 选择一个空闲端口（切勿硬编码端口值），并将选定的网址告知用户。
- 该服务器为可选功能，需用户主动启用——优先提供独立的 HTML 文件。

推荐配置方式（由操作系统自动选择空闲的临时端口）：

```bash
# Put each diagram in its own folder under .diagrams/
mkdir -p .diagrams/sn2-mechanism
# ...write .diagrams/sn2-mechanism/index.html...

# Serve on loopback only, free port
cd .diagrams && python3 -c "
import http.server, socketserver
with socketserver.TCPServer(('127.0.0.1', 0), http.server.SimpleHTTPRequestHandler) as s:
    print(f'Serving at http://127.0.0.1:{s.server_address[1]}/')
    s.serve_forever()
" &
```

如果用户坚持使用固定端口，请使用 `127.0.0.1:<port>` —— 绝对不要使用 `0.0.0.0`。同时需在文档中说明如何停止服务器（如 `kill %1` 或 `pkill -f "http.server"`）。

---

## 示例参考

`examples/` 目录中包含了 15 个经过测试的完整图表示例。在编写类似类型的新图表之前，可先查看这些示例以了解可行的实现方式：

| 文件名 | 类型 | 所展示内容 |
|--------|------|------------|
| `hospital-emergency-department-flow.md` | 流程图 | 基于语义颜色的优先级路由机制 |
| `feature-film-production-pipeline.md` | 流程图 | 分阶段工作流程及横向子流程 |
| `automated-password-reset-flow.md` | 流程图 | 包含错误处理分支的认证流程 |
| `autonomous-llm-research-agent-flow.md` | 流程图 | 回环箭头与决策分支结构 |
| `place-order-uml-sequence.md` | 序列图 | UML 序列图风格 |
| `commercial-aircraft-structure.md` | 实体图 | 通过路径、多边形和椭圆呈现真实形状 |
| `wind-turbine-structure.md` | 实体横截面图 | 地下/地上结构区分及颜色编码 |
| `smartphone-layer-anatomy.md` | 展开图 | 左右交替的标签标注及分层组件展示 |
| `apartment-floor-plan-conversion.md` | 平面图 | 墙壁、门框，拟议修改内容以红色虚线标出 |
| `banana-journey-tree-to-smoothie.md` | 叙事流程图 | 弯曲路径与逐步状态变化 |
| `cpu-ooo-microarchitecture.md` | 硬件流水线图 | 分支结构及内存层次结构侧边栏 |
| `sn2-reaction-mechanism.md` | 化学反应图 | 分子结构、曲线箭头及能量变化曲线 |
| `smart-city-infrastructure.md` | 中心辐射式图 | 不同系统对应的不同语义线条样式 |
| `electricity-grid-flow.md` | 多阶段流程图 | 电压层次结构及流程指示标记 |
| `ml-benchmark-grouped-bar-chart.md` | 图表 | 分组柱状图及双坐标轴设计 |

可通过以下方式加载任意示例：
```
skill_view(name="concept-diagrams", file_path="examples/<filename>")
```

## 快速参考：不同场景下的适用工具

| 用户需求 | 图表类型 | 推荐配色 |
|---------|----------|----------|
| “展示流程” | 流程图 | 起始/结束节点用灰色，步骤用紫色，错误用红色，部署环节用青色 |
| “绘制数据流” | 数据管道图（左右布局） | 数据源用灰色，处理环节用紫色，数据接收端用青色 |
| “可视化系统结构” | 结构示意图 | 容器用紫色，服务用青色，数据用珊瑚色 |
| “映射接口端点” | API树状图 | 根节点用紫色，每个资源组对应一条分支路径 |
| “展示各项服务” | 微服务拓扑图 | 入口节点用灰色，服务用青色，消息总线用紫色，工作节点用珊瑚色 |
| “绘制飞机/车辆” | 实物结构图 | 采用路径、多边形和椭圆来呈现逼真的外形 |
| “智慧城市/IoT系统” | 中心辐射式集成图 | 根据不同子系统采用不同的线条样式 |
| “展示控制面板” | 用户界面原型图 | 背景为深色，警报提示使用青色、紫色和珊瑚色作为图表颜色 |
| “电网/电力系统” | 多阶段流程图 | 根据电压等级差异调整线条粗细（高压/中压/低压） |
| “风力发电机/涡轮机” | 实物横截面图 | 基础设施、塔身及机舱部分分别用不同颜色标注 |
| “X的运行过程/生命周期” | 叙事式流程图 | 用蜿蜒的路径展示变化过程，同时体现状态逐步转变的趋势 |
| “X的层次结构/分解视图” | 分解层视图 | 采用垂直堆叠方式展示各层级，标签交替排列 |
| “CPU/处理流程” | 硬件处理流程图 | 用垂直线条表示不同处理阶段，再通过分支连接到执行端口 |
| “平面图/公寓布局” | 平面示意图 | 用线条绘制墙壁和门，拟议的改动部分用红色虚线标出 |
| “反应机制” | 化学反应图 | 用原子、化学键、曲线箭头、过渡态及能量曲线来展示反应过程 |
