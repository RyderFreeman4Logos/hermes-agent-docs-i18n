---
sidebar_position: 18
title: "Desktop Native Sign-In (RFC 8252)"
description: "How the Hermes Desktop app signs in to a gated gateway using your system browser and PKCE — no embedded webview, no session cookies"
---

# 桌面端原生登录（RFC 8252）

当 Hermes 桌面应用连接到**受保护的网关**（即位于 OAuth 提供商之后的托管或自托管控制面板）时，它可以通过两种方式进行登录：

1. **原生登录（RFC 8252）**——应用会打开您系统的**原生浏览器**，让您在已信任的浏览器中完成授权，随后应用会将获取的令牌存储在操作系统的钥匙串中。**无需嵌入式网页视图，也不使用浏览器会话 Cookie**。只要网关支持该功能，这便是默认登录方式。
2. **嵌入式登录（旧版备用方案）**——应用会打开一个小型内置浏览器窗口，并捕获网关的会话 Cookie。当网关为不支持原生登录的旧版本时，系统会自动采用此方式。

您无需手动选择其中一种登录方式——应用会自动检测网关的支持能力，并选择最优方案。本页面将解释其工作原理及设计原因。

## 为何选择原生登录

在原生应用中嵌入浏览器用于 OAuth 登录存在诸多众所周知的弊端：登录页面无法读取您现有的浏览器会话（因此需要重新输入凭证并再次进行多因素认证），密码管理器和通行密钥往往也无法正常使用，而且应用还必须从私有的网页视图中读取会话 Cookie。RFC 8252（“面向原生应用的 OAuth 2.0”）则提供了行业最佳实践，可避免所有这些问题：**在系统浏览器中完成授权流程，再将相应的令牌交给应用**。

对于 Hermes 而言，原生登录意味着：

- **无嵌入式网页视图**。授权过程将在 Safari、Chrome、Firefox 或 Edge 等您常用的浏览器中完成，您的登录信息、扩展程序及通行密钥都能完好保留。
- **无会话 Cookie**。应用会存储经过操作系统钥匙串（Electron 的 `safeStorage`）加密处理的 OAuth **访问令牌**（有效期较短）和**刷新令牌**。REST 请求和 WebSocket 连接均通过 `Authorization: Bearer` 请求头进行身份验证，而非依赖 Cookie。

## 工作原理

```
Desktop app                Gateway (/auth/native/*)          Nous Portal (IDP)
   │ 1. open loopback 127.0.0.1:<random port>
   │ 2. system browser ─►  /auth/native/authorize
   │    (PKCE challenge)    (starts the normal PKCE login) ─► /oauth/authorize
   │                        ◄──── code ──── /auth/callback ◄──┘
   │                        3. mint one-time gateway code
   │ ◄─ 302 127.0.0.1/cb?code=… ─┘
   │ 4. POST /auth/native/token (code + PKCE verifier)
   │ ◄─ 5. { access_token, refresh_token, expires_at } ───────┘
   │ 6. store in OS keychain; use Bearer for REST + WS tickets
```

该网关负责**协调整个认证流程**：它既是面向桌面应用的授权服务器，同时也是面向上游身份提供商（Nous Portal）的OAuth客户端。这种设计是必要的，因为上游的`client_id`及允许的重定向URI均绑定在网关自身的域名下——桌面应用无法直接作为Portal的客户端。尽管如此，桌面应用仍能获得完整的RFC 8252标准体验：拥有独立的PKCE密钥对、独立的回环重定向机制以及属于自己的令牌。

**PKCE（RFC 7636）**用于保护回环重定向环节：没有永远不会离开应用内部的代码验证器，一次性生成的网关代码便毫无用处。这类代码为单次使用且有效期极短。

## 功能检测与回退机制

桌面应用会读取网关公开的 `/api/status` 接口，该接口会返回一个 `auth_flows` 数组，其含义如下：

| `auth_flows` 值 | 含义 |
|--------------------|------|
| `["cookie", "native_pkce"]` | 网关支持原生登录方式 → 应用将使用该方式 |
| `["cookie"]` | 网关仅支持传统登录流程 → 应用将使用内置网页视图 |
| *(该字段缺失)* | 使用旧版网关 → 应用将使用内置网页视图 |

如果虽声明支持原生登录，但因本地原因失败——例如安全工具拦截了回环监听请求，或用户关闭了浏览器标签页——应用会**自动回退到内置登录流程**，确保用户仍能完成登录。

## 令牌生命周期

- **访问令牌**：有效期较短（数分钟）。在每次REST请求以及生成WebSocket连接令牌时，都会以 `Authorization: Bearer` 的格式携带该令牌。
- **刷新令牌**：有效期较长，且会定期轮换。当访问令牌即将过期时，应用会调用 `/auth/native/refresh` 接口来同时更换两种令牌，随后更新密钥链中的存储内容。
- **终端失效处理**：如果刷新令牌已过期、被撤销或检测到重复使用，应用会清除存储的令牌，并提示用户重新登录。
- **注销操作**：会同时清除原生令牌（密钥链中的内容）以及该网关对应的所有传统会话Cookie。

## 面向网关运维人员

只要注册了可代理的OAuth提供商（例如内置的**Nous**提供商），任何支持网关接入的门户都默认支持原生登录功能，无需额外配置——`/auth/native/*` 路由以及 `auth_flows` 的展示功能均属于dashboard-auth子系统的一部分。仅支持密码或令牌登录的提供商不会显示 `native_pkce` 选项（因为没有上游重定向地址可供代理），这类部署将继续使用原有的登录方式。

相关接口均为公开接口，用于预认证阶段，与现有的 `/auth/*` OAuth路由相同：

- `GET /auth/native/authorize` —— 启动通过网关代理的PKCE登录流程
- `POST /auth/native/token` —— 用回环代码及验证器交换为令牌
- `POST /auth/native/refresh` —— 从应用的刷新令牌中生成新的令牌

## 相关文档

- [通过SSH/远程主机进行OAuth认证](./oauth-over-ssh.md) —— 针对远程机器上的提供商/MCP OAuth实现的回环回调机制。
- [使用Nous Portal运行Hermes](./run-hermes-with-nous-portal.md)
