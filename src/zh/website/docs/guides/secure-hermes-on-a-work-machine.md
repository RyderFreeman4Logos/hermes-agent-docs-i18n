---
sidebar_position: 26
title: "Running Hermes on a Personal or Work Machine"
description: "A security-posture walkthrough for running Hermes Agent on the machine you live on — what the defaults protect, how to tighten further, and how to undo mistakes"
---

# 在个人电脑或工作机上运行 Hermes

你打算在自己使用的设备上运行代理程序——无论是个人笔记本电脑还是公司配发的工作站。该如何确保安全呢？

简短回答：默认设置已能提供大部分保护。Hermes 采用“默认安全”设计，通过多层防御机制来保障命令审批、文件写入安全以及凭证管理。本页面将介绍开箱即用的安全功能、在共享或工作机上需要加强哪些设置，以及出现错误时如何纠正。所有相关控制措施都在 [安全指南](/user-guide/security) 中有详细说明。

## 默认设置已提供的保护

全新安装且未进行任何配置时，以下安全机制已处于启用状态：

**危险命令需经过审批。** 在执行任何命令之前，Hermes 会将其与预定义的危险模式列表进行比对——包括递归删除、对 `/etc/` 目录的写入、磁盘操作、管道转壳等。默认的 `approvals.mode: smart` 模式会借助辅助大语言模型来评估风险：低风险命令会仅针对该命令自动获得批准，真正危险的命令则会直接被拒绝，而不确定的情况则会升级为需要人工确认。

**未响应审批提示即视为拒绝。** 如果你在超时时间（默认为300秒）内未对审批提示作出回应，该命令将被**拒绝**。离开办公桌并不意味着自动批准任何操作。

**严格的黑名单机制是底线保障。**某些命令——如 `rm -rf /`、分叉炸弹攻击、将物理磁盘清零等——无论处于何种审批模式、是否使用了 `--yolo` 选项或明确设置了“始终允许”，都会被直接拒绝。在审批层甚至看到这些命令之前，黑名单机制就已生效，且不存在任何可绕过的标志。

**对敏感路径的文件写入操作也会被阻止。**`write_file` 和 `patch` 工具不得访问操作系统凭证存储位置（如 `~/.ssh/`、`~/.aws/`、`~/.kube/`、`/etc/sudoers`、`~/.netrc`）、Hermes 自身的凭证存储（如 `auth.json`、`.env` 及配对数据），以及磁盘上的任何项目机密文件（如 `.env`、`.env.local`、`.envrc`）。此类被禁止的写入操作会立即返回错误——既不会出现审批提示，也无法通过聊天界面进行绕过。

**输出内容中的机密信息会被匿名处理。**默认情况下 `security.redact_secrets` 功能处于开启状态：工具输出中看似 API 密钥、令牌或密码的敏感内容，会在进入对话上下文及日志之前就被隐藏处理。

**您的数据只会被发送到您指定的目的地。**所有 API 调用**仅会发送到您配置的 LLM 服务提供商**。Hermes Agent 不会收集任何遥测数据、使用情况统计或分析信息。您的对话记录、内存内容及技能信息均会本地存储在 `~/.hermes/` 目录中。更多详情请参阅 [常见问题](/reference/faq#is-my-data-sent-anywhere)。

:::info
实际上还有更多安全机制——所有支持处理 URL 的工具都具备 SSRF 防护功能，MCP 子进程运行在过滤后的环境中，上下文文件还会经过注入攻击扫描。[安全性](/user-guide/security) 页面详细介绍了每一层的安全措施。
:::

## 用于共享电脑或工作机的安全加固设置

在存储有雇主数据、生产环境凭证或其他人文件的电脑上，可在默认设置之上叠加这些额外安全措施。

### 将审批方式改为手动

`smart` 模式会自动批准低风险命令。如果您希望亲自查看所有被标记的命令：

```yaml
approvals:
  mode: manual
```

手动模式会在执行被标记的命令之前始终向用户发出提示。

### 添加自定义禁止规则

`approvals.deny` 是一个包含通配符模式的列表，可无条件阻止匹配到的终端命令执行——即便在 `--yolo`、`/yolo` 或 `mode: off` 模式下也是如此。它相当于内置硬性黑名单的用户可编辑版本。您可以利用它来指定绝不能在这台机器上运行的命令：

```yaml
approvals:
  deny:
    - "git push --force*"
    - "*curl*|*sh*"
    - "dd if=* of=/dev/*"
```

模式匹配为不区分大小写的 [fnmatch](https://docs.python.org/3/library/fnmatch.html) 通配符，会针对整个命令文本进行比对。而且匹配过程会使用危险模式检测器所采用的相同标准化/去混淆后的版本，因此简单的引号技巧无法让规则失效。务必为模式加上引号——否则开头的裸星号会导致 YAML 解析错误。更改会立即生效，无需重启。详情请参阅：[用户自定义拒绝规则](/user-guide/security#user-defined-deny-rules-approvalsdeny)。

### 沙箱文件写入

`HERMES_WRITE_SAFE_ROOT` 可限制 `write_file` 和 `patch` 函数仅能在您指定的目录前缀中操作——任何其他路径都将被严格禁止。在 Unix 系统上，多个根目录可通过冒号分隔：

```bash
export HERMES_WRITE_SAFE_ROOT=/path/to/project:/home/you/.hermes
```

安全根目录内的敏感路径仍然被屏蔽——即使将其设置为 `$HOME`，也无法写入 `~/.ssh/id_rsa` 文件。

:::caution
请勿随意将此配置添加到 `~/.hermes/.env` 中。如果仅将其设置为项目目录，代理程序将无法写入 `~/.hermes/cron/jobs.json`、配置文件中的技能信息，以及该前缀之外的其他 Hermes 状态数据。建议如上所述，将您的 Hermes 主目录也作为第二个根目录包含进来。
:::

### 将命令执行移出主机

最彻底的隔离方式是完全不在本地机器上运行命令。该终端工具支持多种[后端](/user-guide/features/tools#terminal-backends)：

| 后端 | 隔离级别 |
|---------|-----------|
| `local` | 无隔离——在主机上运行（但仍会进行危险命令检测） |
| `docker` | 容器隔离——容器本身即构成安全边界 |
| `ssh` | 远程机器隔离——在独立的服务器上执行命令 |

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # Explicit allowlist only; empty keeps secrets out of the container
```

每个 Docker 容器均以强化安全设置运行——所有 Linux 权限能力均被禁用（仅保留最少必要功能），同时启用“禁止新权限授予”机制、设置进程数量限制，并对临时文件系统挂载施加大小限制。由于采用容器后端，容器内的破坏性命令无法危害主机，因此无需在此处进行危险命令检测。

对于 `ssh` 方式，需在 `config.yaml` 中设置 `terminal.backend: ssh`，并通过 `~/.hermes/.env` 文件中的 `TERMINAL_SSH_HOST`、`TERMINAL_SSH_USER` 和 `TERMINAL_SSH_KEY` 参数指定主机详细信息。详情请参阅[网络隔离](/user-guide/security#network-isolation)。

### 若启用消息功能：允许列表与配对机制

该机器上是否运行了[网关](/user-guide/security#user-authorization-gateway)？默认设置为拒绝访问：若未配置任何允许列表且未设置 `GATEWAY_ALLOW_ALL_USERS`，则**所有用户均会被拒绝**。建议明确指定相关设置。

```bash
# ~/.hermes/.env
TELEGRAM_ALLOWED_USERS=123456789
GATEWAY_ALLOWED_USERS=123456789
```

或者，可以使用动态配对方式而非硬编码 ID：系统会为未知用户生成一次性配对码，您可以通过 CLI 使用命令 `hermes pairing approve <platform> <code>` 来批准其访问权限。切勿在重要的机器上将 `GATEWAY_ALLOW_ALL_USERS=true` 的设置设为 true。

## 撤销机制：检查点与 `/rollback` 功能

审批机制可用于防止数据损坏，而[检查点功能](/user-guide/checkpoints-and-rollback)则可用于恢复受损状态。启用该功能后，Hermes 会在执行可能造成数据损失的操作——如 `write_file`、`patch`，以及 `rm`、`mv`、`sed -i`、`git reset` 等具有破坏性的终端命令——之前，自动将您的项目生成快照并存储在 `~/.hermes/checkpoints/store/` 下的隐藏 Git 存储库中。您的真实项目 `.git` 文件则不会受到任何影响。

检查点功能为可选设置。您可以按会话单独启用：

```bash
hermes chat --checkpoints
```

或全局设置：

```yaml
checkpoints:
  enabled: true
```

在会话中，可使用以下命令：

| 命令 | 说明 |
|---------|-------------|
| `/rollback` | 列出所有检查点及其变更统计信息 |
| `/rollback diff <N>` | 预览自检查点 N 之后的变更内容 |
| `/rollback <N>` | 恢复到检查点 N（同时撤销上一次对话内容） |
| `/rollback <N> <file>` | 从检查点 N 恢复单个文件 |

:::提示
在恢复之前，建议先使用 `/rollback diff <N>` 进行预览；为确保最大安全性，可将多个检查点与 git worktree 结合使用——每个 Hermes 会话都拥有独立的 worktree，而检查点则作为额外的安全层。
:::

## 该威胁模型涵盖的内容与未涵盖的内容

需明确这些控制措施旨在防范什么风险。正如[安全指南](/user-guide/security#user-defined-deny-rules-approvalsdeny)中所述：

> 拒绝规则是用来防范“诚实但出错”的智能体的防护机制，其威胁模型与危险模式检测器类似。它们并非用于隔离恶意攻击进程的沙箱——对于这类情况，应使用隔离后的后端环境（如 Docker、Modal）或限制数据输出的环境。

文件写入保护机制也是如此：它们仅适用于 `write_file` 和 `patch` 命令，而 `terminal` 工具则以相同的操作系统用户身份运行。拒绝列表能够减少意外损害，并为模型提供明确的停止信号；但它无法隔离恶意或已被攻破的智能体。如果您的需求是实现彻底隔离而非仅仅提供防护措施，那么答案就是使用隔离式的终端后端——那才是为此设计的边界。

## 谨慎的初始配置建议

以上所有内容均已整合完毕。您可根据需求在 `~/.hermes/config.yaml` 文件中进行相应调整：

```yaml
approvals:
  mode: manual                  # See every flagged command yourself
  timeout: 300                  # Unanswered prompts are denied (fail-closed)
  deny:                         # Never-run list — survives even /yolo
    - "git push --force*"
    - "*curl*|*sh*"
    - "dd if=* of=/dev/*"

security:
  redact_secrets: true          # Already the default; stated here for clarity

checkpoints:
  enabled: true                 # Snapshot before destructive operations

terminal:
  backend: docker               # Or ssh — keep execution off the host
  docker_forward_env: []        # No host secrets inside the container
```

在 `~/.hermes/.env` 文件中，如果您需要写入型沙箱环境：

```bash
HERMES_WRITE_SAFE_ROOT=/path/to/project:/home/you/.hermes
```

## 相关文档

- **[安全性](/user-guide/security)** —— 详尽的纵深防御指南：涵盖各类审批模式、容器加固选项、网关授权机制以及MCP凭证过滤规则  
- **[检查点与回滚](/user-guide/checkpoints-and-rollback)** —— 配置管理、存储维护及数据恢复流程说明  
- **[工具与工具集](/user-guide/features/tools)** —— 所有终端后端及其配置选项  
- **[配置管理](/user-guide/configuration)** —— 完整的 `config.yaml` 配置参考手册
