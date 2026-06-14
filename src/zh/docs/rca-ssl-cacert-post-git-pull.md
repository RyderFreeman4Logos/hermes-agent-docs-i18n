# 根因分析：执行 `hermes update` 后 SSL 证书包损坏

**状态：** 已通过 `fix(ssl): 在调用提供商接口之前检测到损坏的证书包` 解决  
**严重程度：** P2 —— 在用户修复依赖项或证书配置之前，代理会一直出现无法识别的提供商/客户端故障。

## 摘要

部分执行的 `hermes update`、被中断的虚拟环境修复操作，或是过时的证书包环境变量，都可能导致 Python 的 TLS 配置指向一个缺失、为空或无法加载的证书包。此时，首次发起的 HTTPS 客户端创建或请求就会失败，出现类似 `FileNotFoundError: [Errno 2] No such file or directory` 的错误，或是未明确指出损坏证书路径的低级 SSL 错误。

## 根本原因

Hermes 在调用提供商接口、获取模型元数据、处理网关传输以及使用 Web 工具时，会依赖 OpenAI/httpx 和基于 requests 的客户端。这些客户端会从以下位置读取证书包配置：

- `HERMES_CA_BUNDLE`
- `SSL_CERT_FILE`
- `REQUESTS_CA_BUNDLE`
- `CURL_CA_BUNDLE`
- 以及预装的 `certifi` 包中的 `cacert.pem` 文件

当虚拟环境仅部分更新，或上述某个环境变量指向的文件已不存在时，提供商客户端构建过程就会失败，而 Hermes 还来不及生成有用的错误提示。

## 解决方案

在 `agent/agent_init.py` 中创建兼容 OpenAI 的提供商客户端之前，`agent/ssl_guard.py` 会先对证书包配置进行验证。其功能包括：

1. 检查明确的证书包环境变量，并准确指出出问题的变量及路径；
2. 确认 `certifi` 包可正常导入；
3. 验证 `certifi.where()` 指向的文件确实存在且大小合理；
4. 从每个经过检查的证书包中构建 `ssl.SSLContext` 对象；
5. 在 httpx/OpenAI 抛出原始低级错误之前，先抛出带有修复建议的类型化 `SSLConfigurationError` 异常。

`hermes_cli doctor` 命令也在 “SSL / 证书” 选项下提供了相同的检测功能，用户无需启动模型会话即可诊断问题。

## 恢复方法

当在代理初始化过程中触发该保护机制时，用户会看到类似如下的提示信息：

```text
Failed to initialize OpenAI client: SSL_CERT_FILE points to a missing CA bundle: C:\path\to\missing\cacert.pem
Repair: python -m pip install --force-reinstall certifi openai httpx
If you configured a custom corporate CA bundle, fix or unset the broken CA bundle environment variable.
```

对于出现常规损坏的 Hermes 虚拟环境，需重新安装出问题的客户端依赖项：

```bash
python -m pip install --force-reinstall certifi openai httpx
```

在自定义或企业级证书颁发机构配置中，需调整环境变量，使其指向真实的 PEM 格式证书包；若希望 Hermes 直接使用内置的 `certifi` 证书存储，则可直接将该变量置为空值。

## 环境应急方案

如需跳过预检机制，可设置 `HERMES_SKIP_SSL_GUARD=1`。此选项仅适用于沙箱环境或受信任管理环境——在这些环境中，Python 所识别的证书路径可能较为特殊，但已知下游客户端仍能正常工作。
