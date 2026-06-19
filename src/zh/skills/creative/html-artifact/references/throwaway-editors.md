# 一次性编辑器

一次性编辑器是一种专为单一任务设计的单文件HTML界面，其末尾会包含一个**导出按钮**，用于将当前状态序列化到剪贴板，从而让你能够将结果粘贴到下一个提示词中。你可以利用它来处理积压的任务、优化提示词、切换功能开关、调整动画参数——之后再将结果以Markdown、JSON、差异格式或纯文本的形式复制出来。

其核心原则是：**该工具必须能够输出结果**。一个没有导出功能的精美编辑器对工作流程而言毫无用处。（例外情况包括：用于体验功能的原型，比如可拖拽排序的界面或动画测试工具，这类工具可以省略导出功能；而如果最终输出只是一个代码片段，那么一个静态的、可直接选择的内容区域`<pre>`即可视为有效的“导出方式”；在这种情况下无需额外添加剪贴板相关的JavaScript代码，直接通过选择即可。）

## 结构框架

状态 → 渲染 → 控制界面 → 导出 → 反馈。`templates/editor.html`就是这个框架的实现文件，具体内容需根据需求进行填充。

```html
<button id="copyBtn" class="btn-primary">Copy as markdown</button>
<button id="resetBtn" class="btn-ghost">Reset</button>
<script>
  const INITIAL = /* the real starting data */;
  let state = structuredClone(INITIAL);        // or read live from the DOM controls

  function render() { /* pure function of state -> DOM; idempotent; call after every change */ }

  function serialize(s) { /* return the pasteable string */ }

  let timer = null;
  function flash(btn, label, orig) {
    btn.textContent = label; btn.classList.add("copied");
    clearTimeout(timer);
    timer = setTimeout(() => { btn.textContent = orig; btn.classList.remove("copied"); }, 1200);
  }

  copyBtn.addEventListener("click", () => {
    writeClipboard(serialize(state)).then(
      () => flash(copyBtn, "Copied \u2713", "Copy as markdown"),
      () => flash(copyBtn, "Copied \u2713", "Copy as markdown")   // flash even on reject; fallback already ran
    );
  });
  resetBtn.addEventListener("click", () => { state = structuredClone(INITIAL); render(); });
  render();  // boot
</script>
```

**约定规范**：采用双按钮工具栏（主要功能为复制，辅助功能为重置）；操作反馈表现为将文本替换为“已复制 ✓”，并添加 `.copied` 类，持续时间仅为 1200 毫秒，同时通过 `clearTimeout` 函数进行定时清除；初始状态保持固定，以便实现简单的重置操作并为差异对比提供基准；在点击时根据当前状态进行序列化处理（不保留额外的并行导出缓冲区）；在导出时重新计算派生值（如计数、总和、差异），绝不可依赖过时的汇总数据。

## 状态管理方式，三种选择

- **克隆对象/数组** — 使用 `let state = structuredClone(INITIAL)` 创建状态副本，修改相关字段后调用 `render()` 函数。这种方式最适合用于需要在多列之间拖动内容的看板应用。
- **直接从控件读取实时数据** — 不创建专门的 JS 状态对象，而是通过 `currentState()` 函数按需读取复选框和输入框的内容。此方式最适合用于表单或标志编辑器。
- **直接使用编辑器文本本身** — 对于提示词或模板编辑器而言，`contenteditable` 元素中的文本本身就是状态表现形式，可通过 TreeWalker 技术读取该文本，其读取逻辑需与新增换行的处理方式保持一致。

## 能够在 `file://` 环境下正常工作的剪贴板处理方案

在 `file://` 协议的页面中，`navigator.clipboard` 对象往往未定义或因安全上下文问题而被拒绝使用。该解决方案会通过特性检测自动回退到使用屏幕外的文本区域结合 `execCommand` 方法，并且**始终返回一个 Promise 对象**，从而使调用方能够统一使用 `.then(flash)` 的方式处理结果。

```js
function writeClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);            // async API when available
  }
  const ta = document.createElement("textarea");           // fallback for file://
  ta.value = text;
  ta.style.position = "fixed";                             // fixed + off-screen = no scroll jump
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand("copy"); } catch (e) { /* ignore */ }
  document.body.removeChild(ta);
  return Promise.resolve();                                // uniform return so .then() always works
}
```

规则依次为：首先尝试特征检测；若失败，则在用户手势处理函数中采用文本框结合`execCommand('copy')`的方式（在`file://`协议下为同步操作）；将文本框置于屏幕外；用try/catch结构包裹`execCommand`调用；务必移除文本框；将结果转换为Promise格式；无论操作成功还是失败都显示提示信息（因为备用方案通常都能成功）。

## 导出格式——根据需求选择

| 格式 | 构建方式 | 适用场景 |
|---|---|---|
| **Markdown** | 通过`lines.push(...)` → `join("\n")`生成；使用`#`/`##`作为标题，`- **id**`作为列表项 | 将结果直接放入文档、PR或问题记录中供人工查看 |
| **差异对比格式**（`-`/`+`） | 对比`state`与`INITIAL`状态，输出`'- "k": '+from` / `'+ "k": '+to`格式的内容 | 仅应用变更内容或用于审查目的 |
| **JSON格式** | 手动构建以保持键的顺序，或使用`JSON.stringify(state, null, 2)` | 生成可供机器解析的配置，可直接粘贴到文件中 |
| **提示语/纯文本格式** | 直接读取编辑器中的内容 | 将提示语、模板或代码片段反馈给模型 |

当既需要审查又需要应用更改时，提供两种导出选项（复制并对比格式以及复制为JSON格式的按钮）。若需严格保持目标文件的结构，应手动实现序列化逻辑——因为`JSON.stringify`会重新排序和格式化内容，而手动构建字符串则能保留键组的原有顺序。

## 控制组件

尽可能使用原生HTML元素：<input type=range>用于滑块（可自定义滑块手柄样式），<input type=checkbox>用于切换状态，HTML5拖放功能（通过`draggable="true"`以及`dragstart`/`dragover`/`drop`事件实现，还可将放置点对齐到元素中心），以及`contenteditable`元素用于文本输入。无需分词器即可实时显示字符数反馈：可使用`Math.round(chars / 4.2)`计算。对于需要动态调整CSS样式的滑块，可定义自定义属性：`root.style.setProperty('--ease', btn.dataset.ease)`，再让CSS通过`var(--ease)`引用该值。
