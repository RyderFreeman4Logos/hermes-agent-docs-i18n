---
sidebar_position: 18
title: "Desktop Native Sign-In (RFC 8252)"
description: "How the Hermes Desktop app signs in to a gated gateway using your system browser and PKCE — no embedded webview, no session cookies"
---

# 桌面端原生登录（RFC 8252）

当 Hermes 桌面应用连接到**受保护的网关**（即位于 OAuth 提供商之后的托管或自托管控制面板）时，它可以通过两种方式登录：

1. **原生登录（RFC 8252）**——应用会打开您**系统的真实浏览器**，让您在已信任的浏览器中完成授权，随后应用会将获取到的令牌以仅所有者可访问的文件形式存储在用户数据目录中（可选择使用操作系统的密钥链进行加密——路径为“设置”→“网关”）。**无需嵌入 WebView，也不会使用浏览器会话 Cookie。**只要网关支持该功能，这便是默认登录方式。
2. **嵌入式登录（旧版回退方案）**——应用会打开一个小型内置浏览器窗口并捕获网关的会话 Cookie。当网关为不支持原生登录的旧版本时，系统会自动采用此方式。

您无需手动选择其中一种登录方式——应用会自动检测网关的支持能力，并选择最优方案。本页面将解释其工作原理及设计原因。

## 为何选择原生登录

在原生应用中嵌入浏览器用于 OAuth 登录存在诸多众所周知的弊端：登录页面无法读取您现有的浏览器会话（因此需要重新输入凭据并再次进行多因素认证），密码管理器和通行密钥往往无法使用，而且应用还必须从私有的 WebView 中读取会话 Cookie。RFC 8252（“面向原生应用的 OAuth 2.0”）则提供了行业公认的最佳实践，可避免所有这些问题：**在系统浏览器中完成授权流程，再将令牌直接传递给应用。**

对于 Hermes 而言，原生登录意味着：

- **无内置网页视图。** 授权过程在 Safari / Chrome / Firefox / Edge 等您常用的浏览器中完成，您的登录信息、扩展程序以及密码密钥均不会受到影响。
- **无会话 Cookie。** 该应用仅保存短期的 OAuth **访问令牌**和**刷新令牌**，这些令牌以仅所有者可访问的文件形式存储；当在“设置 → Gateway”中开启使用钥匙串的功能时，它们会通过操作系统的钥匙串（Electron 的 `safeStorage`）进行加密保护。REST 请求和 WebSocket 连接均通过 `Authorization: Bearer` 标头进行身份验证，而非依赖 Cookie 文件。

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
   │ 6. store in local token store; use Bearer for REST + WS tickets
```

网关负责**协调整个认证流程**：它既是面向桌面应用的授权服务器，同时也是面向上游身份提供方（Nous Portal）的OAuth客户端。这一设计是必要的，因为上游的`client_id`及允许的重定向URI均绑定在网关自身的域名下——桌面应用无法直接作为Portal的客户端。尽管如此，桌面应用仍能获得完整的RFC 8252标准体验：拥有独立的PKCE密钥对、独立的回环重定向机制以及属于自己的访问令牌。

**PKCE（RFC 7636）**用于保护回环认证环节：如果没有永远不会离开应用的代码验证器，一次性生成的网关代码将毫无用处。这类代码为单次使用且有效期极短。

## 功能检测与回退机制

桌面应用会读取网关公开的 `/api/status` 接口，该接口会返回一个 `auth_flows` 数组，其含义如下：

| `auth_flows` 值 | 含义 |
|--------------------|------|
| `["cookie", "native_pkce"]` | 网关支持原生登录方式 → 应用将使用该方式 |
| `["cookie"]` | 网关仅支持传统登录流程 → 应用将使用内置的网页视图 |
| *(该字段缺失)* | 为旧版网关 → 应用将使用内置的网页视图 |

如果虽然网关声明支持原生登录，但由于本地原因失败——例如安全工具拦截了回环监听请求，或用户关闭了浏览器标签页——应用会**自动回退到内置的登录流程**，确保用户仍能完成登录。

## 访问令牌的生命周期

- **访问令牌**：有效期较短（数分钟）。会在每次 REST 请求以及生成 WebSocket 令牌时，以 `Authorization: Bearer` 的格式附带发送。  
- **刷新令牌**：有效期较长且会定期轮换。当访问令牌即将过期时，应用会调用 `/auth/native/refresh` 来同时更新两种令牌，随后更新其令牌存储。  
- **终端失效处理**：若刷新令牌已失效（过期、被撤销或检测到重复使用），应用会清除存储的令牌，并提示用户重新登录。  
- **登出操作**：会同时清除存储的所有本地令牌，以及该网关对应的旧版会话 Cookie。

## 面向网关运营商

只要注册了交互式会话提供程序，任何带有访问控制的网关均会自动支持本地登录功能。无需任何额外配置——`/auth/native/*` 路由以及 `auth_flows` 广告信息均属于 dashboard-auth 子系统的一部分。OAuth 提供程序（例如内置的 **Nous** 提供程序）会负责处理上游身份提供商的重定向；而密码型提供程序（例如内置的 **basic-auth** 插件）则会让系统浏览器直接跳转到网关的 `/login` 凭证表单——这正是操作系统密码管理器（如 macOS 的密码管理功能）能够自动填充表单的原因，而嵌入式桌面网页视图则无法实现此功能。仅基于令牌的认证方式（例如 drain）不属于交互式登录，也不会宣告 `native_pkce` 特性。

相关端点均为公开接口，属于预认证启动阶段，与现有的 `/auth/*` OAuth 路由相同：

- `GET /auth/native/authorize` — 启动代理式的 PKCE 登录流程  
- `POST /auth/native/token` — 用回环码及验证器交换令牌  
- `POST /auth/native/refresh` — 更换应用中的刷新令牌  

## 参考资料

- [通过 SSH/远程主机实现 OAuth](./oauth-over-ssh.md) — 适用于远程机器上 Provider/MCP OAuth 的回环回调模式。  
- [使用 Nous Portal 运行 Hermes](./run-hermes-with-nous-portal.md)
