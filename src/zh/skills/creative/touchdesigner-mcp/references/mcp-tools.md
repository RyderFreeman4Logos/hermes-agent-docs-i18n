# twozero MCP 工具参考手册

包含 twozero MCP v2.774+（2026年4月版本）中的36种工具。所有工具均支持可选的 `target_instance` 参数，以便在多TD实例场景下使用。

## 执行与脚本编写

### td_execute_python

在TouchDesigner内部执行Python代码并返回结果。可完全访问TD Python API（如op、project、app等功能）。会捕获打印语句及最后一个表达式的值。该工具最适合用于：连接线路设置（inputConnectors）、表达式设置（par.X.expr/mode）、参数名称查询，以及批量创建脚本（5个及以上操作符）。若只需创建1-4个操作符，建议使用td_create_operator。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `code` | 字符串 | 是 | 需在TouchDesigner中执行的Python代码 |

## 网络结构

### td_get_network

获取TouchDesigner中指定路径下的操作符网络结构。返回格式为简洁的列表：名称、OPType、标志位。第一行为目标操作符的完整路径。标志位说明：ch:N=子节点数量，!cook=禁止计算，bypass=跳过，private=是否为私有节点，blocked:reason=阻塞原因，"comment text"=注释文本。depth=0（默认值）仅显示当前层级；depth=1显示一层子节点（缩进显示）。如需查看更深层的结构，可对特定COMP路径再次调用此函数。系统操作符（/ui、/sys）默认会被隐藏。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 否 | 需要检查的网络路径，例如'/'或'/project1' |
| `depth` | 整数 | 否 | 递归深度，即要查看的层级数。0=仅当前层级（推荐），1=包含COMP的直接子节点 |
| `includeSystem` | 布尔值 | 否 | 是否包含系统操作符（/ui、/sys）。默认值为false |
| `nodeXY` | 布尔值 | 否 | 是否包含nodeX、nodeY坐标信息。默认值为false |

### td_create_operator

在TouchDesigner中创建新的操作符（节点）。这是创建操作符的首选方式，可自动处理视口定位、查看器标志以及已固定位置的操作符。若需批量创建（5个及以上操作符），也可使用包含脚本的td_execute_python，但需先调用td_get_hints('construction')以获取正确的参数名称和布局规则。该工具支持所有TD操作符类型：TOP、CHOP、SOP、DAT、COMP、MAT。若未指定父节点，则会在用户当前视口位置的已打开网络中创建节点。在构建容器时，需先创建无父节点的baseCOMP，再为子节点设置parent=compPath。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `type` | 字符串 | 是 | 操作符类型，例如'textDAT'、'constantCHOP'、'noiseTOP'、'transformTOP'、'baseCOMP' |
| `parent` | 字符串 | 否 | 父操作符的路径。若未指定，则使用TD中当前打开的网络 |
| `name` | 字符串 | 否 | 新操作符的名称（可选，省略时TD会自动命名） |
| `parameters` | 对象 | 否 | 需要设置到新操作符上的参数键值对 |

### td_find_op

按名称和/或类型在整个项目中查找操作符。返回格式为TSV：路径、OPType、标志位。标志位说明：bypass=跳过，!cook=禁止计算，private=私有节点，blocked:reason=阻塞原因。如需在代码/表达式中搜索，可使用td_search；若需查找操作符本身，则使用td_find_op。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `name` | 字符串 | 否 | 操作符名称中需匹配的子字符串（不区分大小写）。例如'noise'可匹配noise1、noise2、myNoise |
| `type` | 字符串 | 否 | OPType中需匹配的子字符串（不区分大小写）。例如'noiseTOP'、'baseCOMP'、'CHOP'。使用精确类型可实现精准匹配，使用部分类型则可进行更广泛的搜索 |
| `root` | 字符串 | 否 | 搜索的起始操作符路径。默认值为'/project1' |
| `max_results` | 数字 | 否 | 需要返回的最大结果数量。默认值为50 |
| `max_depth` | 数字 | 否 | 从起始节点开始的最大递归深度。默认值为无限制 |
| `detail` | `basic` / `summary` | 否 | 结果详细程度。'basic'=仅显示名称/路径/类型（查询速度快）；'summary'=额外显示连接信息、非默认参数及表达式。默认值为'basic' |

### td_search

在TD项目中的所有代码（DAT脚本）、参数表达式以及字符串参数值中搜索文本。返回格式为TSV：路径、类型（code/expression/parameter/ref）、行号、文本内容。当context>0时返回JSON格式。单词之间为或关系。如需搜索完整短语，需使用引号：'GetLogin "op('login')"'.若只需快速检查某内容是否存在而无需获取全部结果，可设置count_only=true。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `query` | 字符串 | 是 | 搜索查询内容。多个单词表示或关系（任意一个匹配即可）。如需搜索完整短语，需用引号括起。例如：'GetLogin getLogin'可匹配两者中的任意一个 |
| `root` | 字符串 | 否 | 搜索的起始操作符路径。默认值为'/project1' |
| `scope` | `all` / `code` / `editable` / `expressions` / `parameters` | 否 | 搜索范围。'code'=仅搜索DAT脚本（查询速度快，约0.05秒）；'editable'=仅搜索可编辑代码（跳过继承的/引用的DAT文件）；'expressions'=仅搜索参数表达式；'parameters'=仅搜索字符串参数值；'all'=搜索所有内容（查询速度较慢，因需扫描所有参数，约1.5秒）。默认值为'all' |
| `case_sensitive` | 布尔值 | 否 | 是否区分大小写。默认值为false |
| `max_results` | 数字 | 否 | 需要返回的最大结果数量。默认值为50 |
| `context` | 数字 | 否 | 每次匹配结果前后需显示的行数。此参数可减少td_read_dat的调用次数。默认值为0 |
| `count_only` | 布尔值 | 否 | 仅返回匹配数量，不返回具体匹配内容。适用于快速检查是否存在匹配项 |
| `max_depth` | 数字 | 否 | 从起始节点开始的最大递归深度。默认值为无限制 |

### td_navigate_to

将TouchDesigner网络编辑器视口导航至指定的操作符，打开该操作符的父级网络并将视图居中显示在该操作符上。此功能可用于向用户指出问题所在，或在修改操作符之前先导航到该操作符。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | 需要导航到的操作符路径，例如'/project1/noise1' |

## 操作符信息查询

### td_get_operator_info

获取TouchDesigner中特定操作符（节点）的详细信息。detail='summary'时，返回连接信息、非默认参数、表达式以及CHOP通道的简洁信息；detail='full'时，则在上述信息的基础上，额外显示所有参数及其值、默认值和标签。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | 操作符的完整路径，例如'/project1/noise1' |
| `detail` | `summary` / `full` | 否 | 信息详细程度。'summary'=连接信息、表达式、非默认参数、自定义参数（标有pulse标记）及CHOP通道；'full'=summary信息加上所有参数信息。默认值为'full' |

### td_get_operators_info

一次性获取多个操作符的详细信息。返回一个包含多个操作符信息对象的数组。相比多次调用td_get_operator_info，此方法更为高效。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `paths` | 数组 | 是 | 操作符的完整路径数组，例如[/project1/null1', '/project1/null2'] |
| `detail` | `summary` / `full` | 否 | 信息详细程度。默认值为'summary' |

### td_get_par_info

获取TouchDesigner中某种操作符类型的参数名称及详细信息。若未指定具体参数，则返回所有参数的简洁列表，包含参数名称、类型及菜单选项；若指定了参数，则返回这些参数的完整详细信息（包括帮助文本、菜单选项值及样式设置）。在需要先了解参数名称后再进行设置时，可使用此功能。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `op_type` | 字符串 | 是 | TD操作符类型名称，例如'noiseTOP'、'blurTOP'、'lfoCHOP'、'compositeTOP' |
| `pars` | 数组 | 否 | 可选参数，用于指定需要获取完整详细信息的特定参数名称 |

## 参数设置

### td_set_operator_pars

在TouchDesigner中为操作符设置参数及标志位。相比td_execute_python，此方法更适用于简单的参数修改。无需编写Python代码即可设置参数值或切换bypass/viewer状态。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | 操作符的路径 |
| `parameters` | 对象 | 否 | 需要设置的参数键值对 |
| `bypass` | 布尔值 | 否 | 设置操作符的bypass状态（COMP类型操作符不支持此功能） |
| `viewer` | 布尔值 | 否 | 设置操作符的viewer状态 |
| `allowCooking` | 布尔值 | 否 | 为COMP类型操作符设置烹饪标志。设置为False时，内部网络将停止计算（占用0 CPU资源）。此功能仅适用于COMP类型操作符 |

## 数据读写

### td_read_dat

读取TouchDesigner中DAT操作符的文本内容。返回内容时会附带行号。此功能可用于读取脚本、插件文件、GLSL着色器以及表格数据。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | DAT操作符的路径 |
| `start_line` | 整数 | 否 | 开始读取的行号（从1开始计数）。省略该参数则表示从文件开头读取 |
| `end_line` | 整数 | 否 | 结束读取的行号（包含该行）。省略该参数则表示读取到文件末尾 |

### td_write_dat

向TouchDesigner中的DAT操作符写入或替换文本内容。支持完全替换内容，也支持类似StrReplace的替换功能（old_text -> new_text）。此功能可用于编辑脚本、插件文件及着色器。但不会自动重新初始化插件文件。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | DAT操作符的路径 |
| `text` | 字符串 | 否 | 完全替换后的文本。只需提供此参数，或同时提供old_text和new_text，不能同时提供两者 |
| `old_text` | 字符串 | 否 | 需要查找并替换的文本（在DAT文件中必须唯一存在） |
| `new_text` | 字符串 | 否 | 替换后的文本 |
| `replace_all` | 布尔值 | 否 | 若设置为true，则替换old_text的所有出现次数（默认值为false，要求匹配项唯一） |

### td_read_chop

读取CHOP通道的样本数据。以数组形式返回各通道的值。当需要获取实际的样本值（如动画曲线、查找表、波形）而非仅通过td_get_operator_info获取汇总信息时，可使用此功能。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | CHOP操作符的路径 |
| `channels` | 数组 | 否 | 需要读取的通道名称。省略该参数则表示读取所有通道 |
| `start` | 整数 | 否 | 开始读取的样本索引（从0开始计数）。省略该参数则表示从开头读取 |
| `end` | 整数 | 否 | 结束读取的样本索引（包含该索引）。省略该参数则表示读取到文件末尾 |

### td_read_textport

读取TouchDesigner日志/文本端口（控制台输出）中的最后N行内容。此功能可用于查看TD产生的错误信息、警告信息以及打印输出内容。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `lines` | 整数 | 否 | 需要返回的最新行数 |

### td_clear_textport

清空MCP文本端口的日志缓冲区。在开始调试会话或编辑-运行-检查循环之前，可使用此功能确保td_read_textport输出的内容简洁明了。

该功能无参数（可选的`target_instance`除外）。

## 视觉捕获

### td_get_screenshot### td_get_screenshots

可一次性批量获取多个操作器的屏幕截图。这些图片会被保存为文件，并返回对应的文件路径。你可以使用文件读取工具来查看这些图片。该功能采用两步异步处理方式：第一步——传入“paths”数组启动任务，此时会返回`{'status': 'pending', 'batchId': '...', 'total': N}`；第二步——传入“batch_id”获取结果，返回值为`{'files': [{op, file}, ...]}`，随后即可读取文件查看图片。如果第二步仍显示“pending”状态，可再执行一次调用后重试。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `paths` | 数组 | 否 | 需要截图的所有操作器的完整路径列表。第一步必须提供此参数。 |
| `batch_id` | 字符串 | 否 | 第一步生成的批次编号，用于获取处理完成的截图。 |
| `max_size` | 整数 | 否 | 图像长边的最大像素尺寸（默认为512）。若设为0，则保持操作器原始分辨率（适用于需要精确还原UI的场景）。数值越大（如1024），图像细节越丰富。 |
| `output_path` | 字符串 | 否 | 图片保存的绝对路径（可选），例如`/Users/me/project/render.png`。若未指定，图片将保存至 `/tmp/pisang_mcp/screenshots/` 目录。请使用绝对路径——TouchDesigner的工作目录可能与代理程序的不同。 |
| `as_top` | 布尔值 | 否 | 若设为true，则直接以TOP格式捕获操作器图像（绕过视图渲染器），从而保留透明度信息。此功能仅适用于TOP类型的操作器；若目标不是TOP类型，系统会自动切换到视图模式。当你需要带有透明度的纯净PNG格式图像，例如将生成的图片保存以便在其他项目中使用时，可选用此参数。 |
| `format` | `auto` / `jpg` / `png` | 否 | 图像格式。默认值为“auto”：在视图模式下输出JPEG格式，当`as_top=true`时输出PNG格式。“jpg”始终输出JPEG格式（文件体积更小）；“png”始终输出PNG格式（无损）。 |

### td_get_screen_screenshot

通过TouchDesigner的screenGrabTOP功能捕获实际屏幕的截图。图片会被保存为文件，并返回文件路径。你可以使用文件读取工具来查看该图像。与td_get_screenshot（捕获操作器视图）不同，此功能显示的是用户在显示器上实际看到的内容——包括TouchDesigner窗口、UI面板等所有元素。当需要模拟鼠标/键盘输入以验证屏幕上的操作结果时，可使用此功能。典型工作流程为：`td_get_screen_screenshot` → 读取文件 → `td_input_execute` → 等待系统空闲 → 再次调用`td_get_screen_screenshot`。该功能也支持两步异步处理：第一步——无需传入request_id即可启动任务，返回值为`{'status':'pending','requestId':'...'}`；第二步——传入request_id获取结果，返回值为`{'file': '/tmp/.../screen_id.jpg', 'info': '...metadata...'}`，随后即可读取文件查看图像。该request_id还可与td_screen_point_to_global函数配合使用，用于后续的坐标查询。参数中的crop_x/y/w/h均为实际屏幕像素值（而非图像像素值），超出屏幕边界的裁剪区域会自动被限制在有效范围内。函数还具备智能默认值设置：若未指定max_size，则默认为全屏尺寸1920像素（便于整体查看）；对于裁剪后的图像，最大尺寸则为crop_w和crop_h中的较大值，从而确保图像保持1:1比例。在1:1比例下，屏幕坐标与图像像素坐标的关系为：`screen_coord = crop_origin + image_pixel`；否则则按照元数据中的公式计算。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `request_id` | 字符串 | 否 | 第一步生成的请求编号，用于获取处理完成的截图。 |
| `max_size` | 整数 | 否 | 图像长边的最大像素尺寸。若未指定，则默认为全屏尺寸1920像素；对于裁剪后的图像，默认为crop_w和crop_h中的较大值（保证1:1比例）。可手动指定该值以覆盖默认设置。 |
| `crop_x` | 整数 | 否 | 屏幕上的左边缘像素坐标。 |
| `crop_y` | 整数 | 否 | 屏幕上的上边缘像素坐标（y=0对应屏幕顶部）。 |
| `crop_w` | 整数 | 否 | 图像的宽度，以像素为单位。 |
| `crop_h` | 整数 | 否 | 图像的高度，以像素为单位。 |
| `display` | 整数 | 否 | 显示器索引（默认为0，即主显示器）。 |

## 上下文与使用场景

### td_get_focus

获取TouchDesigner（TD）中当前用户的焦点信息：包括处于激活状态的网络、已选操作器、当前正在使用的操作器，以及鼠标悬停对象（即鼠标光标下方的元素）。重要提示：当用户提到“this operator”或“вот этот”时，指的是已选中/当前正在使用的操作器，而非鼠标悬停对象。鼠标悬停位置仅是随机的鼠标位置，不应作为判断依据。若需立即为所有已选操作器开始批量截图，可传入`screenshots=true`参数——响应结果中将包含一个名为“screenshots”的字段，其中存储有批次编号；随后可通过`td_get_screenshots(batch_id=...)`来获取这些截图。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `screenshots` | 布尔值 | 否 | 若设为true，则为所有已选操作器启动批量截图任务。可通过`td_get_screenshots(batch_id=...)`来获取结果。 |
| `max_size` | 整数 | 否 | 当`screenshots=true`时，截图的最大尺寸（默认为512）。 |
| `as_top` | 布尔值 | 否 | 当`screenshots=true`时，该参数会一同传递给批量截图任务。 |

### td_get_errors

用于查找TouchDesigner（TD）操作器中存在的错误和警告信息。它会检查操作器的错误、警告，以及存在问题的参数表达式（如通道缺失、引用错误等）。此外，还会汇总并去重后显示日志中的近期脚本错误信息（包括错误回溯内容）——例如，1000个相同的鼠标移动错误会合并显示为1条记录，标注为×1000。若指定了具体路径，则仅检查该操作器及其子节点；若未指定路径，则检查当前处于激活状态的网络。若需检查整个项目，可使用“/”作为路径。当用户反馈某功能出现故障、存在错误、节点显示为红色或出现“горит ошибка”等提示时，可使用此功能。小贴士：在重现错误之前，可先调用`td_clear_textport`函数，以便让日志信息更清晰地聚焦在相关错误上。另外，当用户反馈程序运行卡顿或响应迟缓时，可将此功能与`td_get_perf`结合使用，同时检查错误情况和性能表现。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 否 | 需要检查的路径。若未指定，则检查当前处于激活状态的网络。若需检查整个项目，可使用“/”作为路径。 |
| `recursive` | 布尔值 | 否 | 是否递归检查子节点（默认值为true）。 |
| `include_log` | 布尔值 | 否 | 是否包含日志中的近期脚本错误信息，这些错误会按唯一特征进行分组显示（默认值为true）。在重现错误之前，建议先调用`td_clear_textport`函数，以便让结果更清晰。 |

### td_get_perf

用于获取TouchDesigner（TD）的性能数据。返回的为TSV格式的数据：首行是包含帧率、预算使用情况以及内存使用情况的汇总信息，后续行则按处理时间从长到短排列最耗时的操作器。各列含义如下：path、OPType、cpu/cook(ms)、gpu/cook(ms)、cpu/s、gpu/s、rate、flags。当用户反馈程序运行卡顿、帧率过低、性能不佳，或出现“тупит”、“тормозит”等类似问题时，可使用此功能进行排查。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 否 | 需要分析性能的路径。若未指定，则对当前处于激活状态的网络进行性能分析。若需分析整个项目，可使用“/”作为路径。 |
| `top` | 整数 | 否 | 需要返回的最耗时操作器的数量。 |

## 文档相关功能

### td_get_docs

获取关于TouchDesigner某个主题的完整文档。与提供简洁提示的td_get_hints不同，此功能会返回深入的参考资料。若不传入任何参数，即可查看所有可用主题及其描述；若传入具体主题名称，则可获取该主题的完整文档。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `topic` | 字符串 | 否 | 需要获取文档的主题。若不指定，则列出所有可用主题。 |

### td_get_hints

获取TouchDesigner中某个主题的相关提示及常用操作模式。在创建操作器或编写TD Python代码之前，调用此功能可了解正确的参数名称、表达式写法以及常用编程技巧。目前支持的主题包括：animation（动画）、noise（噪声）、connections（连接）、parameters（参数）、scripting（脚本编写）、construction（组件构建）、ui_analysis（UI分析）、panel_layout（面板布局）、screenshots（截图功能）、input_simulation（输入模拟）、undo（撤销操作）。重要提示：在构建包含多个操作器的复杂场景之前，务必先调用`topic='construction'`，以便获取正确的TOP/CHOP参数名称、compositeTOP输入顺序以及布局规范。同样，在使用td_input_execute函数之前，也建议先调用`topic='input_simulation'`，以了解焦点恢复机制、坐标系统以及相应的测试流程。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `topic` | 字符串 | 是 | 需要获取提示的主题。可选主题包括：'animation'、'noise'、'connections'、'parameters'、'scripting'、'construction'、'ui_analysis'、'panel_layout'、'screenshots'、'input_simulation'、'undo'、'networking'、'all' |

### td_agents_md

用于读取、写入或更新COMP容器内的agents_md文档。agents_md是一种Markdown格式的textDAT文件，用于描述该容器的用途、结构以及相关规范。支持的操作包括：action='read'——返回文档内容并检查其更新状态（将文档中描述的子节点信息与实际运行状态进行对比）；action='update'——根据实际运行状态刷新自动生成的部分内容（如子节点列表、连接关系），同时保留人工编写的部分内容；action='write'——设置完整的文档内容，若该文件不存在则自动创建。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | COMP容器的路径。 |
| `action` | `read` / `update` / `write` | 是 | read：获取内容并检查更新状态；update：刷新自动生成的内容；write：设置完整内容。 |
| `content` | 字符串 | 否 | Markdown格式的文档内容（仅在使用action='write'时需要提供）。 |

## 输入自动化功能

### td_input_execute向 TouchDesigner 发送一系列鼠标/键盘指令。这些指令会以平滑的贝塞尔曲线轨迹依次执行。该函数会立即返回结果——在继续操作之前，需不断调用 td_input_status() 直到状态变为 ‘idle’。指令类型包括：‘focus’ —— 将 TouchDesigner 置于前台；‘move’ —— 平滑移动鼠标：{type,x,y,duration,easing}；‘click’ —— 点击：{type,x,y,button,hold,duration,easing}，其中 hold 表示按住按钮的秒数，duration 表示点击前的平滑移动时间；‘dblclick’ —— 双击：{type,x,y,duration}；‘mousedown’/‘mouseup’ —— {type,x,y,button}；‘key’ —— 按键输入：{type,keys}，例如 ‘ctrl+z’、‘tab’、‘escape’、‘shift+f5’。在 macOS 系统上，此功能需要开启无障碍访问权限。‘type’ —— 模拟人类打字：{type,text,wpm,variance}，支持与布局无关的 Unicode 字符及可变输入速度。‘wait’ —— 暂停：{type,duration}；‘scroll’ —— 滚动：{type,x,y,dx,dy,steps}，模拟人类滚动操作：首先将鼠标移动到 (x,y) 位置，然后以自然的速度分多步进行垂直（+上）和水平（+右）滚动，默认步数为 4。鼠标指令的坐标空间可以是 ‘logical’（默认值），也可以是 ‘physical’。在 macOS 上，‘physical’ 指的是通过 td_get_screen_screenshot 获取的实际屏幕像素值，该值会自动转换为 CGEvent 的逻辑坐标。顶层设定的坐标空间将适用于所有未指定自身坐标空间的指令。出错处理选项为：‘stop’（默认值），出错时清空指令队列；‘continue’，跳过失败的指令。重要提示：首次使用前请调用 td_get_hints('input_simulation')，以了解焦点恢复、坐标系统及测试工作流程的相关信息。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `commands` | 数组 | 是 | 需要按顺序执行的指令字典列表。 |
| `coord_space` | `logical` / `physical` | 否 | 未指定自身坐标空间的鼠标指令所使用的默认坐标空间。‘logical’ 直接使用 CGEvent 坐标；‘physical’ 使用 td_get_screen_screenshot 获取的实际屏幕像素值，在 macOS 上会自动转换。 |
| `on_error` | `stop` / `continue` | 否 | 出错时采取的操作，默认为 ‘stop’。 |

### td_input_status

获取 td_input 指令队列的当前状态。在调用 td_input_execute 之后，需不断查询此函数直至状态变为 ‘idle’。返回值包括：状态（‘idle’/‘running’）、当前正在执行的指令、队列中剩余的指令数量以及上一次出现的错误信息。

无参数（可选参数 `target_instance` 除外）。

### td_input_clear

立即清空 td_input 指令队列并停止当前执行中的指令。

无参数（可选参数 `target_instance` 除外）。

### td_op_screen_rect

获取网络编辑器中某个操作节点的屏幕坐标。返回值为一个包含 {x,y,w,h,cx,cy} 的对象，其中 cx 和 cy 表示点击时的中心点坐标。可利用此功能确定需要点击特定操作节点的位置。仅当该操作节点所在的父级网络当前在网络编辑器面板中打开时，此功能才有效。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | 该操作节点的完整路径，例如 ‘/project1/myComp/noise1’ |

### td_click_screen_point

根据之前通过 td_get_screen_screenshot 获取的截图内容，定位屏幕上的某个点并执行点击操作。需传入截图的 request_id，以及标准化的 u/v 值或图像中的 image_x/image_y 值。该函数会使用物理屏幕坐标来排队执行点击指令，因此可直接用于基于截图确定的点击位置。可通过 duration/easing 参数控制鼠标在点击前的移动速度。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `request_id` | 字符串 | 是 | 由 td_get_screen_screenshot 返回的请求标识符。 |
| `u` | 数字 | 否 | 截图区域内标准化的水平位置（0 表示左侧，1 表示右侧），需与 v 参数一起使用。 |
| `v` | 数字 | 否 | 截图区域内标准化的垂直位置（0 表示顶部，1 表示底部），需与 u 参数一起使用。 |
| `image_x` | 数字 | 否 | 返回的截图图像中的水平像素坐标，需与 image_y 参数一起使用。 |
| `image_y` | 数字 | 否 | 返回的截图图像中的垂直像素坐标，需与 image_x 参数一起使用。 |
| `button` | `left` / `right` / `middle` | 否 | 要点击的鼠标按钮，默认为左键。 |
| `hold` | 数字 | 否 | 按住鼠标按钮后不放的秒数。 |
| `duration` | 数字 | 否 | 鼠标在点击前移动到目标位置的秒数。 |
| `easing` | `linear` / `ease-in` / `ease-out` / `ease-in-out` | 否 | 鼠标在点击前的移动缓动方式。 |
| `focus` | 布尔值 | 否 | 若设置为 true，则在点击前将 TouchDesigner 置于前台，并稍作等待以确保焦点已稳定。 |

### td_screen_point_to_global

将之前通过 td_get_screen_screenshot 获取的截图内容中的某个点，转换为绝对屏幕坐标。需传入截图的 request_id，以及标准化的 u/v 值（该截图区域内的 0..1 值）或返回图像中的 image_x/image_y 值。函数会返回绝对的物理屏幕坐标、逻辑坐标，以及可直接用于 td_input_execute 的指令数据。系统会保留最新的截图元数据，以便后续有其他代理程序能够根据 request_id 定位相应点。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `request_id` | 字符串 | 是 | 由 td_get_screen_screenshot 返回的请求标识符。 |
| `u` | 数字 | 否 | 截图区域内标准化的水平位置（0 表示左侧，1 表示右侧），需与 v 参数一起使用。 |
| `v` | 数字 | 否 | 截图区域内标准化的垂直位置（0 表示顶部，1 表示底部），需与 u 参数一起使用。 |
| `image_x` | 数字 | 否 | 返回的截图图像中的水平像素坐标，需与 image_y 参数一起使用。 |
| `image_y` | 数字 | 否 | 返回的截图图像中的垂直像素坐标，需与 image_x 参数一起使用。 |

## 系统相关功能

### td_list_instances

列出所有正在运行且拥有活跃 MCP 服务器的 TouchDesigner（TD）实例。返回每个实例的端口、项目名称、PID 以及 instanceId。在每次交互开始时调用此函数，即可查看可用的实例并选择要使用的那个实例。instanceId 在 TD 进程的整个生命周期内保持不变，会在其他所有工具调用中作为 target_instance 使用。

无参数（可选参数 `target_instance` 除外）。

### td_project_quit

保存并/或关闭当前的 TouchDesigner（TD）项目。可在关闭前先进行保存操作。函数会提示当前项目中是否有未保存的更改。若要关闭不同的实例，需传入 target_instance=instanceId 参数。警告：此操作将会关闭该实例上的 MCP 服务器。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `save` | 布尔值 | 否 | 关闭前是否先保存项目，默认为 true。 |
| `force` | 布尔值 | 否 | 强制关闭而不弹出保存对话框，默认为 false。 |

### td_reinit_extension

重新初始化 TouchDesigner（TD）中某个 COMP 文件里的插件。在通过 td_write_dat 完成所有代码编辑后，调用此函数以应用更改。切勿在每次微小修改后都调用此函数——应先批量处理所有更改。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `path` | 字符串 | 是 | 包含该插件的 COMP 文件的路径 |

### td_dev_log

读取 MCP 开发日志中的最近 N 条记录。仅当开发模式处于启用状态时才可用。可查看请求/响应的历史记录。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `count` | 整数 | 否 | 要返回的最近日志记录数量 |

### td_clear_dev_log

通过关闭旧日志文件并创建新文件来清空当前的 MCP 开发日志。仅当开发模式处于启用状态时才可用。

无参数（可选参数 `target_instance` 除外）。

### td_test_session

用于管理测试会话、错误报告以及对话记录的导出功能。重要提示：切勿主动建议用户导出聊天记录或提交报告。这些功能仅适用于特定场景：- export_chat / submit_report：仅在用户遇到插件或 TouchDesigner 的故障并希望报告问题，或用户明确要求导出对话记录时使用。绝不可在会话结束时或作为常规操作来建议用户执行这些操作。用户相关语句对应的操作如下：‘разбор тестовых сессий’ / ‘analyze test sessions’ → 先列出会话，然后获取并读取 meta.json 文件，最终得到 index.jsonl 和 calls/. ‘разбор репортов’ / ‘analyze user reports’ → 先列出 session=‘user’ 的报告，然后按名称获取具体报告。‘экспортируй чат’ / ‘export chat’ → （1）先生成 export_chat_id 并作为标记，（2）再使用该标记及 session 参数调用 export_chat。‘сообщи о проблеме’ / ‘report bug’ → 先导出聊天记录，检查其中是否包含隐私信息，之后使用 summary、tags 以及 result_op=file_path 参数调用 submit_report。可用操作包括：export_chat_id | export_chat | submit_report | start | note | import_chat | end | list | pull。list 操作的默认行为是自动检测代码库；对于用户报告，需指定 session='user'（仅开发模式可用）。pull 操作会自动搜索两个代码库，并自动判断应使用开发版还是用户版 Hub 访问方式。

| 参数 | 类型 | 是否必填 | 描述 |
|------|------|----------|------|
| `action` | `export_chat_id` / `export_chat` / `submit_report` / `start` / `note` / `import_chat` / `end` / `list` / `pull` | 是 | 操作类型：export_chat_id / export_chat / submit_report / start / note / import_chat / end / list / pull |
| `prompt` | 字符串 | 否 | （start 操作）测试提示语或任务描述 |
| `tags` | 数组 | 否 | （start 操作）用于分类的标签，例如 ['ui', 'layout'] |
| `text` | 字符串 | 否 | （note 操作）观察结果文本；（import_chat 操作）完整的对话文本。 |
| `outcome` | `success` / `partial` / `failure` | 否 | （end 操作）操作结果：success / partial / failure |
| `summary` | 字符串 | 否 | （end 操作）对所发生情况的简要总结 |
| `result_op` | 字符串 | 否 | （end 操作）用于保存结果文件的操作节点路径，文件名为 result.tox |
| `session` | 字符串 | 否 | （pull 操作）要下载的会话名称或子字符串 |
