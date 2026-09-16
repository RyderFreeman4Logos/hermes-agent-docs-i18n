# *ACL 论文格式规范

该目录包含了用于 *ACL 会议的最新 LaTeX 模板。

## 作者指南

向 *ACL 会议提交的论文必须使用官方的 ACL 格式模板。

这些 LaTeX 格式文件可通过以下方式获取：

- [Overleaf 模板](https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj)
- 本代码仓库
- [.zip 文件](https://github.com/acl-org/acl-style-files/archive/refs/heads/master.zip)

示例文件请参见 [`acl_latex.tex`](https://github.com/acl-org/acl-style-files/blob/master/acl_latex.tex)。

请遵循 *ACL 会议通用的论文格式要求：

- [论文格式指南](https://acl-org.github.io/ACLPUB/formatting.html)

作者不得修改这些格式文件，也不得使用为其他会议设计的模板。

## 会议组织者指南

如需根据自身会议需求调整格式文件，请先 fork 本代码仓库并进行必要修改。至少需要更新会议名称并重命名相关文件。

如果您对模板进行了可推广至未来会议的改进，欢迎提交 pull request。感谢您的支持！

在旧版本的模板中，作者需要填写START提交编号，以便在匿名化版本的每页顶部标注该编号。不过现在这一要求已不再必要，因为可以在START系统中自动完成此项标注功能。目前，程序负责人需通过电子邮件联系support@softconf.com提出申请。

## 修改样式文件的操作指南

- 在GitHub上合并拉取请求，或直接将代码推送到GitHub
- 从GitHub将代码拉取到本地仓库
- 接着，将本地仓库的代码推送到Overleaf项目
    - Overleaf项目地址为：https://www.overleaf.com/project/5f64f1fb97c4c50001b60549
    - Overleaf的Git地址为：https://git.overleaf.com/5f64f1fb97c4c50001b60549
- 最后，在Overleaf界面中点击“提交”，再选择“作为模板提交”，以此让Overleaf根据项目内容更新模板。
