# 修改与注释 — XML 详细信息

`docx_revisions.py` 和 `docx_comments.py` 的深度参考文档。当您需要理解原始的 WordprocessingML 数据、扩展这些脚本，或调试格式异常的文档时，请查阅本文档。日常使用仅需参考 SKILL.md 即可。

## 被跟踪的更改（w:ins / w:del）

Word 会在 `http://schemas.openxmlformats.org/wordprocessingml/2006/main` 这一 `w` 命名空间下的段落元素（`w:p`）内部，通过包装元素的形式来记录运行级上的被跟踪更改：

```xml
<w:p>
  <w:r><w:t>Base </w:t></w:r>
  <w:ins w:id="1" w:author="Editor" w:date="2026-01-02T03:04:05Z">
    <w:r><w:t>inserted text</w:t></w:r>
  </w:ins>
  <w:del w:id="2" w:author="Editor" w:date="2026-01-02T03:04:05Z">
    <w:r><w:delText>deleted text</w:delText></w:r>
  </w:del>
</w:p>
```

脚本所依赖的关键事实：

- 被删除的文本存储在 `w:delText` 中，而非 `w:t` —— 正因如此，纯文本提取方式会自然地显示“已接受”的视图（可见的是插入内容，隐藏的是删除内容）。
- 解决策略逻辑：
  - 接受 `w:ins` → 展开结构（将子节点上移并移除包裹层）
  - 拒绝 `w:ins` → 移除包裹层及其内部内容
  - 接受 `w:del` → 移除包裹层及其内部内容
  - 拒绝 `w:del` → 将每个 `w:delText` 重命名为 `w:t`，然后再展开结构
- 修改内容可以出现在允许放置块级内容的任何位置：正文、表格单元格（包括嵌套表格）、页眉、页脚以及文本框。脚本通过 `root.iter(W+"ins", W+"del")` 遍历正文根节点以及所有页眉/页脚部分根节点，从而能找到任意深度的修改内容。
- 每个修改*元素*的 `w:id` 值都是唯一的，但一次逻辑编辑会话可能会生成多个元素。`accept`/`reject --id` 指令正是针对带有该 id 的元素执行的。

脚本未处理的内容（虽可通过 `docx_read.py --revisions` 检测到但选择忽略）包括：段落标记修改（`w:pPr` 上的 `w:rPr/w:ins`）、表格行插入/删除（`w:trPr/w:ins`）、格式变更记录（`w:rPrChange`、`w:pPrChange`）以及移动操作（`w:moveFrom`/`w:moveTo`）。在常规编辑器中移动操作较为少见；若存在此类操作，建议直接使用 Word 软件处理，而非自行猜测。

## 说明

需要协同工作的三个组件：

1. **`word/comments.xml`** — 每条评论对应一个`w:comment`元素，该元素包含`w:id`、`w:author`、`w:initials`、`w:date`以及评论正文段落。这些元素通过关系类型`.../comments`和内容类型`application/vnd...wordprocessingml.comments+xml`与`document.xml`相关联（同时还需要一个`[Content_Types].xml`配置文件进行覆盖——当相关模块被注册时，python-docx会自动生成该文件）。
2. **段落中的范围标记** — 在被锚定的文本片段之前放置`w:commentRangeStart w:id="N"`，在其之后放置`w:commentRangeEnd w:id="N"`。
3. **引用片段** — 一个包含`w:commentReference w:id="N"`的`w:r`元素，位于范围标记之后，用于将注释内容与对应位置关联起来。

`docx_comments.py`的功能表现：

- **list** 和 **delete** 操作始终在 XML 层级上进行，因此能够处理来自任何生成器的文档。对于 `anchored_text` 的重建，则是按文档中的各个部分根节点的顺序依次遍历，针对每个 ID 收集其起始与结束标记之间的 `w:t` 文本内容。
- **add** 操作首先会将目标文本分割成独立的文本段。如果匹配内容恰好位于某个文本段的中间，该文本段就会在对应位置被拆分（拆分时会复制 `w:rPr` 元素，从而保留原有的格式）。之后根据版本不同采取不同处理方式：
  - 若使用 python-docx ≥ 1.2 版本，则直接调用其内置的 `document.add_comment(runs, ...)` API（该 API 会同时创建注释部分、标记以及引用文本段）；
  - 若使用旧版本或通过 `--xml` 参数运行脚本，则会生成 `word/comments.xml` 文件，通过 OPC 层注册相关部分与关联关系，再手动插入标记和引用内容。
- 删除注释时会移除对应的 `w:comment` 元素以及该 ID 对应的三种标记类型；而文档中的锚定文本则不会受到影响。

较新版本的 Word 还会生成 `commentsExtended.xml` 文件，用于存储注释的线程关系及最终处理状态。但这些脚本既不会读取也不会生成该文件：其中的回复信息和“已解决”标记均不可见，且通过该功能添加的注释均为普通顶级注释。
