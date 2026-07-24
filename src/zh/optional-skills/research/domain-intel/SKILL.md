---
name: domain-intel
description: Passive recon of subdomains, SSL certs, WHOIS, and DNS.
platforms: [linux, macos, windows]
---

# 域名情报——被动式开源情报收集

仅使用 Python 标准库即可实现被动式域名侦察。
**无需任何依赖，也不需要 API 密钥。可在 Linux、macOS 和 Windows 系统上运行。**

## 辅助脚本

该功能包含 `scripts/domain_intel.py` —— 一个用于执行所有域名情报操作的完整命令行工具。

```bash
# Subdomain discovery via Certificate Transparency logs
python3 SKILL_DIR/scripts/domain_intel.py subdomains example.com

# SSL certificate inspection (expiry, cipher, SANs, issuer)
python3 SKILL_DIR/scripts/domain_intel.py ssl example.com

# WHOIS lookup (registrar, dates, name servers — 100+ TLDs)
python3 SKILL_DIR/scripts/domain_intel.py whois example.com

# DNS records (A, AAAA, MX, NS, TXT, CNAME)
python3 SKILL_DIR/scripts/domain_intel.py dns example.com

# Domain availability check (passive: DNS + WHOIS + SSL signals)
python3 SKILL_DIR/scripts/domain_intel.py available coolstartup.io

# Bulk analysis — multiple domains, multiple checks in parallel
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com google.com
python3 SKILL_DIR/scripts/domain_intel.py bulk example.com github.com --checks ssl,dns
```

`SKILL_DIR` 即包含该 `SKILL.md` 文件的目录。所有输出结果均为结构化的 JSON 格式。

## 可用命令

| 命令 | 功能说明 | 数据来源 |
|---------|----------|----------|
| `subdomains` | 从证书日志中查找子域名 | crt.sh（仅支持 HTTPS） |
| `ssl` | 检查 TLS 证书的详细信息 | 直接通过 TCP:443 连接到目标主机 |
| `whois` | 获取注册信息、注册商及注册日期 | WHOIS 服务器（TCP:43） |
| `dns` | 查询 A、AAAA、MX、NS、TXT、CNAME 记录 | 系统 DNS + Google DoH |
| `available` | 检查域名是否已注册 | DNS、WHOIS 及 SSL 相关信号 |
| `bulk` | 对多个域名同时执行多项检测 | 使用上述所有数据来源 |

## 何时使用本技能而非内置工具

- 针对基础设施相关问题（如子域名、SSL 证书、WHOIS、DNS 记录及域名可用性），请**使用本技能**
- 若需了解某个域名或公司的基本信息，建议使用 **`web_search`**
- 如需获取网页的实际内容，可使用 **`web_extract`**
- 对于简单的“该 URL 是否可访问”检测，可使用 **`terminal` 结合 `curl -I` 命令**

| 任务 | 更合适的工具 | 原因 |
|------|--------------|------|
| “example.com 是做什么的？” | `web_extract` | 能获取页面内容，而非 DNS/WHOIS 数据 |
| “查找某公司的信息” | `web_search` | 适用于通用信息检索，而非特定域名查询 |
| “这个网站安全吗？” | `web_search` | 信誉评估需要结合网页上下文 |
| “检查某个 URL 是否可访问” | `terminal` 结合 `curl -I` | 简单的 HTTP 可访问性检测 |
| “查找 X 的子域名” | **本技能** | 仅能通过被动方式获取此类信息 |
| “SSL 证书何时过期？” | **本技能** | 内置工具无法查看 TLS 证书详情 |
| “谁注册了这个域名？” | **本技能** | WHOIS 数据无法通过网页搜索获得 |
| “coolstartup.io 是否可用？” | **本技能** | 通过 DNS+WHOIS+SSL 的被动方式检测可用性 |

## 平台兼容性

基于纯 Python 标准库（`socket`、`ssl`、`urllib`、`json`、`concurrent.futures`），在 Linux、macOS 和 Windows 系统上均可正常运行，无需额外依赖。

- **crt.sh 查询**采用 HTTPS 协议（端口 443），可穿透大多数防火墙
- **WHOIS 查询**使用 TCP 端口 43，在严格限制的网络环境中可能会被屏蔽
- **DNS 查询**的 MX/NS/TXT 记录查询通过 Google DoH（HTTPS）实现，更易绕过防火墙限制
- **SSL 检查**需通过端口 443 连接到目标主机，是唯一的“主动”操作

## 数据来源

所有查询均为**被动式**操作——不进行端口扫描或漏洞检测：

- **crt.sh**：证书透明度日志（用于子域名发现，仅支持 HTTPS）
- **WHOIS 服务器**：直接通过 TCP 连接到 100 多个权威顶级域名注册商
- **Google DNS-over-HTTPS**：用于 MX、NS、TXT、CNAME 记录的解析，更易穿透防火墙
- **系统 DNS**：用于 A/AAAA 记录的解析
- **SSL 检查**是唯一的“主动”操作（通过 TCP 连接到目标主机:443）

## 备注

- WHOIS 查询使用 TCP 端口 43，在严格限制的网络环境中可能会被屏蔽
- 部分 WHOIS 服务器会根据 GDPR 法规隐去注册人信息，需向用户说明这一点
- 对于非常流行的域名（拥有数千个证书），crt.sh 的查询速度可能会较慢，建议用户做好相应预期
- 域名可用性检测基于启发式方法（结合 3 种被动信号），其准确性不如注册商 API

---

*由 [@FurkanL0](https://github.com/FurkanL0) 提供*
