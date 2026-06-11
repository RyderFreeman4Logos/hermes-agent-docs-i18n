# Excalidraw 深色模式图表

若要创建深色主题的图表，需在数组中将一个巨大的深色背景矩形作为**第一个元素**。该矩形的尺寸应足够大，能够覆盖整个视图区域：

```json
{
  "type": "rectangle", "id": "darkbg",
  "x": -4000, "y": -3000, "width": 10000, "height": 7500,
  "backgroundColor": "#1e1e2e", "fillStyle": "solid",
  "strokeColor": "transparent", "strokeWidth": 0
}
```

在深色背景上显示元素时，请使用以下颜色方案。

## 深色背景下的文本颜色

| 颜色 | 十六进制值 | 用途 |
|-------|-----------|------|
| 白色 | `#e5e5e5` | 主要文本、标题 |
| 淡灰色 | `#a0a0a0` | 辅助文本、注释 |
| 黑色 | `#555` 或更深颜色 | 在深色背景下不可见！ |

## 深色背景下的形状填充色

| 颜色 | 十六进制值 | 适用场景 |
|-------|-----------|----------|
| 深蓝色 | `#1e3a5f` | 主要节点 |
| 深绿色 | `#1a4d2e` | 成功状态、输出内容 |
| 深紫色 | `#2d1b69` | 处理中状态、特殊标识 |
| 深橙色 | `#5c3d1a` | 警告状态、待处理任务 |
| 深红色 | `#5c1a1a` | 错误状态、严重问题 |
| 深青色 | `#1a4d4d` | 存储相关内容、数据 |

## 深色背景下的描边与箭头颜色

建议使用主颜色方案中的标准主色调——这些颜色在深色背景下依然足够醒目：
- 蓝色 `#4a9eed`、琥珀色 `#f59e0b`、绿色 `#22c55e`、红色 `#ef4444`、紫色 `#8b5cf6`

若需较为柔和的形状边框，可使用 `#555555`。

## 示例：深色模式下的带标签矩形

请使用容器绑定方式（而非无效的 `"label"` 属性）来实现。在深色背景下，将文本的 `strokeColor` 设置为 `"#e5e5e5"`，以确保文字可见。

```json
[
  {
    "type": "rectangle", "id": "r1",
    "x": 100, "y": 100, "width": 200, "height": 80,
    "backgroundColor": "#1e3a5f", "fillStyle": "solid",
    "strokeColor": "#4a9eed", "strokeWidth": 2,
    "roundness": { "type": 3 },
    "boundElements": [{ "id": "t_r1", "type": "text" }]
  },
  {
    "type": "text", "id": "t_r1",
    "x": 105, "y": 120, "width": 190, "height": 25,
    "text": "Dark Node", "fontSize": 20, "fontFamily": 1,
    "strokeColor": "#e5e5e5",
    "textAlign": "center", "verticalAlign": "middle",
    "containerId": "r1", "originalText": "Dark Node", "autoResize": true
  }
]
```

注意：对于位于深色背景上的独立文本元素，务必明确设置 `"strokeColor": "#e5e5e5"`。默认值 `#1e1e1e` 在深色背景下是不可见的。

