# *ACL 论文格式规范

该目录收录了用于 *ACL 会议的最新 LaTeX 模板。

## 作者须知

向 *ACL 会议提交的论文必须使用官方的 ACL 格式模板。

这些 LaTeX 格式文件可通过以下方式获取：
- [Overleaf 模板](https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj)
- 本代码仓库
- [.zip 文件](https://github.com/acl-org/acl-style-files/archive/refs/heads/master.zip)

示例文件请参见 [`acl_latex.tex`](https://github.com/acl-org/acl-style-files/blob/master/acl_latex.tex)。

同时，请遵循 *ACL 会议通用的论文格式要求*：
- [论文格式指南](https://acl-org.github.io/ACLPUB/formatting.html)

作者不得修改这些格式文件，也不得使用为其他会议设计的模板。

## 会议组织者须知

如需根据自身会议需求调整格式文件，请先 Fork 本代码仓库并进行必要修改。至少需要更新会议名称并重命名相关文件。

若您对模板进行了可推广至未来会议的改进，欢迎提交 pull request。感谢您的支持！

在旧版本的模板中，作者需填写 START 提交编号，以便在匿名处理后的论文每页顶部标注该编号。目前这一要求已不再适用，因为 START 现已可自动完成该标注功能。当前的操作方式是由会议组织者发送邮件至 support@softconf.com 提出请求。

## 修改格式文件的操作步骤

1. 在 GitHub 上合并 pull request 或直接推送代码到 GitHub
2. 从 GitHub 拉取代码到本地仓库
3. 将本地仓库的代码推送到 Overleaf 项目
   - Overleaf 项目地址：https://www.overleaf.com/project/5f64f1fb97c4c50001b60549
   - Overleaf 的 Git 地址：https://git.overleaf.com/5f64f1fb97c4c50001b60549
4. 在 Overleaf 中点击“提交”，再选择“作为模板提交”，以便让 Overleaf 根据本地项目更新模板。
