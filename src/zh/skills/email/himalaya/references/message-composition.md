# 使用 MML（MIME 元语言）构建邮件内容

Himalaya 采用 MML 来构建电子邮件。MML 是一种基于 XML 的简单语法，可用于生成 MIME 格式的邮件内容。

## 基本邮件结构

一封电子邮件由一系列**标头**和随后的**正文**组成，二者之间以空行分隔：

```
From: sender@example.com
To: recipient@example.com
Subject: Hello World

This is the message body.
```

## 标头

常用标头包括：

- `From`：发送方地址
- `To`：主要收件人地址
- `Cc`：抄送收件人地址
- `Bcc`：密送收件人地址
- `Subject`：消息主题
- `Reply-To`：回复地址（如与 `From` 不同）
- `In-Reply-To`：正在回复的消息编号

### 地址格式

```
To: user@example.com
To: John Doe <john@example.com>
To: "John Doe" <john@example.com>
To: user1@example.com, user2@example.com, "Jane" <jane@example.com>
```

## 纯文本邮件
普通的纯文本邮件：

```
From: alice@localhost
To: bob@localhost
Subject: Plain Text Example

Hello, this is a plain text email.
No special formatting needed.

Best,
Alice
```

## 用于丰富电子邮件的 MML 技术

### 多部分消息

可选的文本/HTML 部分：

```
From: alice@localhost
To: bob@localhost
Subject: Multipart Example

<#multipart type=alternative>
This is the plain text version.
<#part type=text/html>
<html><body><h1>This is the HTML version</h1></body></html>
<#/multipart>
```

### 附件

上传文件：

```
From: alice@localhost
To: bob@localhost
Subject: With Attachment

Here is the document you requested.

<#part filename=/path/to/document.pdf><#/part>
```

自定义名称的附件：

```
<#part filename=/path/to/file.pdf name=report.pdf><#/part>
```

多个附件：

```
<#part filename=/path/to/doc1.pdf><#/part>
<#part filename=/path/to/doc2.pdf><#/part>
```

### 内联图片

将图片内嵌在文本中：

```
From: alice@localhost
To: bob@localhost
Subject: Inline Image

<#multipart type=related>
<#part type=text/html>
<html><body>
<p>Check out this image:</p>
<img src="cid:image1">
</body></html>
<#part disposition=inline id=image1 filename=/path/to/image.png><#/part>
<#/multipart>
```

### 混合内容（文本与附件）

```
From: alice@localhost
To: bob@localhost
Subject: Mixed Content

<#multipart type=mixed>
<#part type=text/plain>
Please find the attached files.

Best,
Alice
<#part filename=/path/to/file1.pdf><#/part>
<#part filename=/path/to/file2.zip><#/part>
<#/multipart>
```

## MML 标签参考

### `<#multipart>`

用于将多个部分组合在一起。

- `type=alternative`：相同内容的不同表现形式
- `type=mixed`：独立的各个部分（文本 + 附件）
- `type=related`：相互引用的部分（HTML + 图片）

### `<#part>`

用于定义消息的某个部分。

- `type=<mime-type>`：内容类型（例如 `text/html`、`application/pdf`）
- `filename=<path>`：要附加的文件路径
- `name=<name>`：附件的显示名称
- `disposition=inline`：以内联方式显示而非作为附件
- `id=<cid>`：用于在 HTML 中引用的内容标识符

## 通过 CLI 组装消息

### 交互式组装

将打开您的 `$EDITOR` 编辑器：

```bash
himalaya message write
```

### 回复（打开编辑器并显示带引号的消息内容）

```bash
himalaya message reply 42
himalaya message reply 42 --all  # reply-all
```

### 转发

```bash
himalaya message forward 42
```

### 从标准输入发送数据

```bash
cat message.txt | himalaya template send
```

### 通过 CLI 预填请求头

```bash
himalaya message write \
  -H "To:recipient@example.com" \
  -H "Subject:Quick Message" \
  "Message body here"
```

## 小贴士

- 编辑器启动时会显示一个模板，您只需填写标题和正文内容即可。
- 保存并退出编辑器即可发送邮件；不保存直接退出则可取消操作。
- 在发送邮件时，MML格式的内容会被转换为对应的MIME格式。
- 若需查看接收到的邮件的原始MIME结构，可使用 `himalaya message export --full` 命令。
