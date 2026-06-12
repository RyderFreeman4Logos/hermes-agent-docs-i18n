---
sidebar_position: 8
title: "Extending the CLI"
description: "Build wrapper CLIs that extend the Hermes TUI with custom widgets, keybindings, and layout changes"
---

# 扩展 CLI 功能

Hermes 在 `HermesCLI` 中提供了受保护的扩展钩子，使得封装层 CLI 能够添加控件、键盘绑定以及布局自定义功能，而无需覆盖长达 1000 多行的 `run()` 方法。这样一来，您的扩展就能与内部的变更保持解耦。

## 扩展点

目前共有五种可用的扩展接口：

| 钩子名称 | 功能用途 | 何时需要重写该钩子 |
|----------|----------|-------------------|
| `_get_extra_tui_widgets()` | 将控件注入布局中 | 需要持久性 UI 元素（如面板、状态行、迷你播放器） |
| `_register_extra_tui_keybindings(kb, *, input_area)` | 添加键盘快捷键 | 需要热键功能（用于切换面板、控制播放进度、模态窗口快捷操作等） |
| `_build_tui_layout_children(**widgets)` | 完全掌控控件顺序 | 需要重新排序或封装现有控件（较为少见） |
| `process_command()` | 添加自定义斜杠命令 | 需要处理 `/mycommand` 类型的命令（该钩子已存在） |
| `_build_tui_style_dict()` | 自定义 prompt_toolkit 样式 | 需要自定义颜色或样式设置（该钩子已存在） |

前三个为新的受保护钩子，后两个则早已存在。

## 快速入门：创建一个封装层 CLI

```python
#!/usr/bin/env python3
"""my_cli.py — Example wrapper CLI that extends Hermes."""

from cli import HermesCLI
from prompt_toolkit.layout import FormattedTextControl, Window
from prompt_toolkit.filters import Condition


class MyCLI(HermesCLI):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._panel_visible = False

    def _get_extra_tui_widgets(self):
        """Add a toggleable info panel above the status bar."""
        cli_ref = self
        return [
            Window(
                FormattedTextControl(lambda: "📊 My custom panel content"),
                height=1,
                filter=Condition(lambda: cli_ref._panel_visible),
            ),
        ]

    def _register_extra_tui_keybindings(self, kb, *, input_area):
        """F2 toggles the custom panel."""
        cli_ref = self

        @kb.add("f2")
        def _toggle_panel(event):
            cli_ref._panel_visible = not cli_ref._panel_visible

    def process_command(self, cmd: str) -> bool:
        """Add a /panel slash command."""
        if cmd.strip().lower() == "/panel":
            self._panel_visible = not self._panel_visible
            state = "visible" if self._panel_visible else "hidden"
            print(f"Panel is now {state}")
            return True
        return super().process_command(cmd)


if __name__ == "__main__":
    cli = MyCLI()
    cli.run()
```

运行它：

```bash
cd ~/.hermes/hermes-agent
source .venv/bin/activate
python my_cli.py
```

## Hook 参考文档

### `_get_extra_tui_widgets()`

该函数会返回一个包含 prompt_toolkit 小部件的列表，这些小部件将被插入到 TUI 布局中。它们会显示在**分隔符与状态栏之间**——即输入区域的上方、主要输出内容的下方。

```python
def _get_extra_tui_widgets(self) -> list:
    return []  # default: no extra widgets
```

每个组件都应当是 prompt_toolkit 提供的容器对象（例如 `Window`、`ConditionalContainer`、`HSplit`）。若需让这些组件具备切换功能，可使用 `ConditionalContainer` 或 `filter=Condition(...)`。

```python
from prompt_toolkit.layout import ConditionalContainer, Window, FormattedTextControl
from prompt_toolkit.filters import Condition

def _get_extra_tui_widgets(self):
    return [
        ConditionalContainer(
            Window(FormattedTextControl("Status: connected"), height=1),
            filter=Condition(lambda: self._show_status),
        ),
    ]
```

### `_register_extra_tui_keybindings(kb, *, input_area)`

该函数在Hermes完成自身键绑定配置之后、布局生成之前被调用。请将您自定义的键绑定添加到`kb`参数中。

```python
def _register_extra_tui_keybindings(self, kb, *, input_area):
    pass  # default: no extra keybindings
```

参数：
- **`kb`** — 用于 prompt_toolkit 应用程序的 `KeyBindings` 实例
- **`input_area`** — 主要的 `TextArea` 控件，用于读取或处理用户输入内容

```python
def _register_extra_tui_keybindings(self, kb, *, input_area):
    cli_ref = self

    @kb.add("f3")
    def _clear_input(event):
        input_area.text = ""

    @kb.add("f4")
    def _insert_template(event):
        input_area.text = "/search "
```

请避免与内置快捷键发生**冲突**，这些内置快捷键包括：`Enter`（提交）、`Escape Enter`（换行）、`Ctrl-C`（中断）、`Ctrl-D`（退出）、`Tab`（接受自动建议）。功能键 F2 及其组合键通常不会引发问题。

### `_build_tui_layout_children(**widgets)`

仅当您需要完全掌控小部件的排列顺序时才需重写此函数。大多数扩展程序应优先使用 `_get_extra_tui_widgets()`。

```python
def _build_tui_layout_children(self, *, sudo_widget, secret_widget,
    approval_widget, clarify_widget, model_picker_widget=None,
    spinner_widget=None, spacer, status_bar, input_rule_top,
    image_bar, input_area, input_rule_bot, voice_status_bar,
    completions_menu) -> list:
```

默认实现会返回相关结果（所有为 `None` 的组件都会被过滤掉）：

```python
[
    Window(height=0),       # anchor
    sudo_widget,            # sudo password prompt (conditional)
    secret_widget,          # secret input prompt (conditional)
    approval_widget,        # dangerous command approval (conditional)
    clarify_widget,         # clarify question UI (conditional)
    model_picker_widget,    # model picker overlay (conditional)
    spinner_widget,         # thinking spinner (conditional)
    spacer,                 # fills remaining vertical space
    *self._get_extra_tui_widgets(),  # YOUR WIDGETS GO HERE
    status_bar,             # model/token/context status line
    input_rule_top,         # ─── border above input
    image_bar,              # attached images indicator
    input_area,             # user text input
    input_rule_bot,         # ─── border below input
    voice_status_bar,       # voice mode status (conditional)
    completions_menu,       # autocomplete dropdown
]
```

## 布局图示

默认的从上到下布局如下：

1. **输出区域** — 滚动显示对话历史记录
2. **间隔区**
3. **附加组件** — 来自 `_get_extra_tui_widgets()`
4. **状态栏** — 显示模型类型、上下文占比及耗时
5. **图片栏** — 显示已附上的图片数量
6. **输入区域** — 用户输入提示语
7. **语音状态栏** — 录音指示器
8. **自动补全菜单** — 自动完成建议列表

## 使用技巧

- **状态变更后刷新显示**：调用 `self._invalidate()` 以触发 prompt_toolkit 的重新绘制。
- **访问智能体状态**：`self.agent`、`self.model` 和 `self.conversation_history` 均可直接使用。
- **自定义样式**：重写 `_build_tui_style_dict()` 方法，并为自定义样式类添加对应配置项。
- **斜杠命令处理**：重写 `process_command()` 方法来处理自定义命令，其余情况则调用 `super().process_command(cmd)`。
- **除非必要否则勿重写 `run()` 方法**——设计扩展钩子正是为了避免这种紧密耦合。
