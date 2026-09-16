# 构建可填写表单：规范格式与工作流程

同一份 JSON 规范同时用于驱动 `pdf_form_layout.py`（设计校验）和 `pdf_make_form.py`（AcroForm 构建）。坐标采用 PDF 点制，原点位于页面左下角（1 点 = 1/72 英寸；A4 尺寸为 595.27 × 841.89，Letter 尺寸为 612 × 792）。

## 规范中的形状定义

```json
{
  "title": "Example Intake Form",
  "author": "example-author",
  "page_size": "A4",
  "page_count": 1,
  "fields": [
    {"name": "surname", "type": "text", "page": 1,
     "label": "Surname", "label_box": [72, 700, 150, 714],
     "entry_box": [160, 696, 400, 716],
     "value": "", "tooltip": "Family name"},

    {"name": "agree", "type": "checkbox", "page": 1,
     "label": "I agree", "label_box": [72, 660, 150, 674],
     "entry_box": [160, 658, 176, 674], "checked": false},

    {"name": "color", "type": "radio", "page": 1,
     "label": "Color", "label_box": [72, 620, 150, 634],
     "entry_box": [160, 616, 400, 636],
     "options": ["red", "blue"], "value": "blue"},

    {"name": "size", "type": "dropdown", "page": 1,
     "label": "Size", "label_box": [72, 580, 150, 594],
     "entry_box": [160, 576, 300, 596],
     "options": ["small", "large"], "value": "small"}
  ]
}
```

- `page_size`：可选值为 `"A4"`、`"letter"`，或以点为单位的 `[宽度, 高度]`。
- `page_count`：为可选参数，会自动扩展至目标页面的最大页数。
- 矩形区域的坐标格式为 `[x0, y0, x1, y1]`，且需满足 `x0 < x1`、`y0 < y1`。
- `label` 会以静态文本形式显示在 `label_box` 附近；对于无需标注的字段，可省略该参数及 `label_box`。
- `radio` 类型：选项按钮会水平排列在 `entry_box` 内，每个选项占一个位置，并配有简短的静态标签。`value` 参数可通过导出名称预先选定某个选项。
- `dropdown` 类型：对应 AcroForm 的选择（组合）字段。

## 字段类型 → pdf_read.py --fields 的输出内容

| 规范类型 | /FT | 填写后的值格式 |
|---|---|---|
| 文本 | /Tx (`text`) | 字符串形式 |
| 复选框 | /Btn (`button`) | `/Yes` 或 `/Off` |
| 单选按钮 | /Btn (`button`) | `/<导出名称>`，例如 `/red` |
| 下拉菜单 | /Ch (`choice`) | 选项的字符串形式 |

使用 `pdf_fill_form.py` 填写表单时，复选框接受 `true`/`false`；单选按钮的值需以斜杠开头（如 `"/red"`）；下拉菜单的值则为直接的选项字符串。

## 布局校验规则（pdf_form_layout.py）

针对每个字段在其指定的页面上：
- 矩形区域必须格式正确且位于页面边界之内；
- 输入框的尺寸至少为 8×8 点（文本/下拉菜单输入框的高度为 12 点）；
- 同一页面上的多个输入框不得重叠（若出现重叠，后续的字段会被标记）；
- 标签必须距离其对应的输入框不超过 150 点，且不得与输入框重叠。
退出码为 0 表示检查正常，为 1 表示存在至少一个问题；JSON 报告会针对每个字段列出具体的“问题”。建议在构建之前先对规范文件进行代码检查——修正 JSON 中的数值错误比调试已生成的 PDF 要容易得多。

## 可视化审查流程

```bash
python3 scripts/pdf_form_layout.py spec.json --render-overlay overlay.png [--pdf built.pdf]
```

红色矩形代表输入框（带有字段名称），蓝色则代表标签框。若不使用 `--pdf` 参数，叠加内容将绘制在空白页面上（仅支持 PIL 格式，始终可用）；而使用 `--pdf` 参数时，则会在其下方对真实页面进行光栅化处理（需要安装 pypdfium2 或 pdftoppm，否则报告会显示“rendered”: false 并给出安装建议）。将生成的 PNG 文件输入到 `vision_analyze` 工具中，即可分别检测碰撞、对齐问题以及异常标签。

## 单选组的相关注意事项（reportlab + pypdf）

- reportlab 要求每个单选组至少包含两个 `radio()` 调用；仅包含一个选项的单选组会导致字段功能异常。
- 预选值是在生成报告时通过 `"value"` 参数设定的；若之后想通过 `pdf_fill_form.py` 更改选择项，则需要使用带斜杠的导出名称（如 `/red`）。
- 在使用 pypdf 进行填充后，某些查看器对 reportlab 设计的单选组显示效果可能不一致。建议同时通过 `--fields` 参数查看数据真实性，再结合渲染后的页面图像确认视觉呈现情况，而不能仅依赖其中一种方式。
- 对单选组进行扁平化处理是最不可靠的扁平化方式——在发布之前务必检查输出图像的质量。
