---
title: Egress proxy
sidebar_position: 1
---

# 出站代理

专为远程终端沙箱提供的可选出站凭证注入防火墙。沙箱中仅存储不可见的代理令牌，真正的 API 密钥永远不会离开主机。

- [iron-proxy](./iron-proxy) — 来自 [ironsh/iron-proxy](https://github.com/ironsh/iron-proxy) 的单二进制文件 TLS 拦截代理，由 `hermes egress` 实现延迟安装与管理。
