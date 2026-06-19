# SVG 图表

所有图表均为手动编写的内联 `<svg>` 格式——不使用 Mermaid、D3，也不包含图片。这种方式能够实现完全的控制权，并确保文件结构自包含。坐标是手动计算的，因此**必须进行视觉验证流程**（详见 `fidelity-and-verify.md`）：最常见的错误是箭头落在空白区域，或是编辑后各元素发生重叠。

对于简化版或用于教学目的的图表，请使用 `concept-archetypes.md` 中定义的 9-ramp 设计系统；而对于云架构、基础设施或系统架构图，则建议采用 `dark-tech.md` 中提供的深色主题版本。这两种风格均采用以下相同的结构化技术。

## 箭头标记

在 `<defs>` 中统一定义一次。建议使用 `context-stroke` 属性，这样箭头头部就能继承其所在线条的颜色（一个标记即可对应所有边线颜色）：

```xml
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

使用 `marker-end="url(#arrow)"` 进行应用。若需要固定的语义化颜色（如成功/失败/正常状态），而非采用继承机制，则应定义对应的标记 `#arrow`、`#arrow-rust`、`#arrow-olive`，并为其设置硬编码的 `fill` 属性。

## 节点组

节点是由包裹 `<rect>` 元素及居中显示的 `<text>` 元素的 `<g>` 元素构成的。应通过 CSS 类而非内联属性来设置样式——各种状态均定义在样式表中：

```xml
<g class="node">
  <rect x="100" y="20" width="180" height="44" rx="8"/>
  <text class="th" x="190" y="42" text-anchor="middle" dominant-baseline="central">Service</text>
</g>
```

```css
.node rect { fill: var(--white); stroke: var(--gray-300); stroke-width: 1.5; }
.node.hot rect { fill: rgba(217,119,87,0.10); stroke: var(--clay); }   /* focus */
.node.ok  rect { fill: rgba(120,140,93,0.12); stroke: var(--olive); }  /* success */
.node.bad rect { fill: rgba(176,74,63,0.10);  stroke: var(--rust); }   /* error */
text { pointer-events: none; }   /* so clicks hit the node group, not the label */
```

两行式节点：在标题下方18像素处添加第二个 `<text class="ts">` 标签作为副标题，将矩形高度设置为56像素。

## 决策菱形

节点由 `<path>` 元素构成的菱形表示，而非矩形：

```xml
<path class="gate" d="M310 262 L352 294 L310 326 L268 294 Z"/>
<text x="310" y="294" text-anchor="middle" dominant-baseline="central">valid?</text>
```

## 边缘与语义

直线边缘为 `<line>`；分支/失败边缘则为填充属性为 `fill="none"` 的贝塞尔曲线 `<path>`（SVG 路径的默认填充色为 `fill:black`）。可通过样式来体现具体含义：

```css
.edge      { stroke: var(--gray-500); stroke-width: 1.5; fill: none; marker-end: url(#arrow); }
.edge.yes  { stroke: var(--olive); }                       /* happy path */
.edge.no   { stroke: var(--rust); stroke-dasharray: 4 4; } /* failure / dashed */
```

在边的中点附近用小型等宽字体标注 `<text class="lbl">`，内容可填写“pass”、“fail → 503”或“retry”。

## 坐标网格规范

手动设置的坐标在编辑过程中容易发生偏移，需加以控制：

- **视图框**：使用 `viewBox="0 0 W H"` 的格式，其中宽度 W 为固定值（教育用途为680，基础设施场景约为720–960），高度 H 则为最后一个元素底部位置加上40像素的缓冲区。每添加一行后需重新计算 H 值。
- **车道/行**：将节点置于规则网格上。为每条车道指定一个列坐标 x，并设置固定的行间距（例如每90像素一行）。同一车道内的所有节点均使用相同的 x 值，以确保垂直边为直线。
- **间距要求**：各矩形之间至少保持60像素的距离；箭头与其指向的矩形之间需保留10像素间距。
- **滚动处理**：通过添加 `.diagram { overflow-x: auto; } .diagram svg { min-width: 760px; }` 这样の样式，可防止过宽的图表在移动设备上被压缩显示。
- **宽度校验**：矩形的宽度必须足以容纳其内的文本——即满足 `box_width >= chars * px_per_char + 48` 这一条件。以14像素、字体粗细为500时，约等于每字符8像素；若为12像素、字体粗细为400，则约为每字符6.5像素。

## 交互式图表（可选）

若希望流程图可点击，并同时显示同步的详细信息面板，可为每个节点添加 `data-k` 属性，再通过一个小型JavaScript字典来查询该属性对应的值。加载页面时务必设置一个默认的活跃节点，以避免信息面板为空；此外，即便关闭JavaScript，图表也应保持完整可读性。

```js
const DETAIL = { ingest: { title: "Ingest", body: "…", code: "…" }, /* … */ };
document.querySelectorAll('.node[data-k]').forEach(n => {
  n.addEventListener('click', () => {
    document.querySelectorAll('.node.active').forEach(a => a.classList.remove('active'));
    n.classList.add('active');
    const d = DETAIL[n.dataset.k];
    panel.querySelector('.t').textContent = d.title;
    panel.querySelector('.b').innerHTML = d.body;
  });
});
document.querySelector('.node[data-k="ingest"]').click();  // default-active
```

## 可导出的独立 SVG 文件（可选）

如果用户希望将 SVG 作为单独的可下载文件，该 SVG 必须包含独立的`<defs><style>`、独立的`<marker>`元素、背景色为`<rect fill="#FAF9F5">`的背景，以及硬编码的十六进制颜色值（不能使用`var()`函数，因为其在宿主页面外部无法解析）。具体要求如下：

```js
const blob = new Blob([new XMLSerializer().serializeToString(svg)], {type:'image/svg+xml'});
const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download:'diagram.svg'});
a.click(); URL.revokeObjectURL(a.href);
```
