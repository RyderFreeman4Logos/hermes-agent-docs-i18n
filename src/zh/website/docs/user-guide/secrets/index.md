# 密钥管理

Hermes能够在进程启动时从外部密钥管理系统中获取API密钥，而无需将其存储在`~/.hermes/.env`文件中。密钥管理系统的启动令牌会保存在`.env`文件中；其他所有提供商的密钥（如OpenAI、Anthropic、OpenRouter等）则可保留在管理系统中，并由中央统一进行轮换。

目前支持的功能包括：

- [Bitwarden密钥管理系统](./bitwarden) — 通过`bws` CLI工具实现，采用延迟加载机制，免费套餐也可使用。

此外，通过相同的接口还可轻松添加更多后端系统（如Vault、AWS Secrets Manager、1Password CLI等）。实现方式仅需在`agent/secret_sources/`目录下添加一个模块，并编写相应的CLI处理函数。如有特定需求，欢迎提交请求。
