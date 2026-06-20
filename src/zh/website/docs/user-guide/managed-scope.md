---
sidebar_position: 3
title: "Managed Scope"
description: "Administrator-pinned, user-immutable config and secrets via a system-level managed directory"
---

# 受管理作用域

**受管理作用域**允许管理员推送配置与密钥的基准值，标准（非根用户）**无法覆盖**这些值。它适用于需要为机器上的所有用户统一指定某些配置的场景，例如模型提供者、共享的API基础URL，或`security.redact_secrets: true`设置。

当存在受管理作用域时，其所指定的值会优先于用户的`~/.hermes/config.yaml`、`~/.hermes/.env`文件，甚至是Shell环境变量中的对应配置——仅针对那些被明确指定的键。其余所有配置仍完全由用户控制。

:::注意 与包管理器锁定安装的区别
通过包管理器实现的安装方式（declarative-distro / formula）会阻止*所有*配置修改，并要求用户使用包管理器进行操作。而受管理作用域则是另一种机制：它按键为每个键注入*特定的不可变值*，而非锁定整个配置文件。这两种方式相互独立，可以同时存在。
:::

## 存储位置

受管理作用域的配置来自系统级目录，默认路径为`/etc/hermes`：

```text
/etc/hermes/
├── config.yaml     # managed config layer (wins over ~/.hermes/config.yaml)
└── .env            # managed env layer (wins over ~/.hermes/.env + shell)
```

该目录及其中的文件均属于 `root` 所有（目录权限为 `0755`，文件权限为 `0644`）：所有人均可读取，仅管理员具备写入权限。**这一文件系统权限设置便是强制执行机制**——普通用户可以读取受管理的文件，但无法对其进行修改。

这两个文件均为可选配置。若缺少受管理的目录或文件，仅表示“不存在受管理的范围”，此时配置的解析方式将与未启用该功能时完全相同。

### 更改目录位置

对于容器环境或非 `/etc` 部署场景，可通过 `HERMES_MANAGED_DIR` 环境变量来更改目录位置。这与 `HERMES_HOME` 类似，属于部署/启动路径相关参数，由其所有者——即负责管理这些文件的管理员来设置。Hermes **绝不会**将该值保存到任何 `.env` 文件中。

```bash
# Point managed scope at a custom directory (set by IT / the deployment, not the user)
export HERMES_MANAGED_DIR=/opt/org/hermes-policy
```

:::warning
如果用户能够设置 `HERMES_MANAGED_DIR`，他们就可以将受管理的范围重新指向自己控制的目录，从而绕过该机制。在实际部署中，此变量应由管理员固定设置（例如直接嵌入服务单元或容器镜像中），而不应允许用户自行修改。`hermes doctor` 会显示*最终确定的*受管理目录，因此可以查看这种重定向情况。
:::

## 优先级

对于受管理层指定的配置键，其优先级顺序如下（优先级越高则生效）：

| 层级 | config.yaml | .env |
|---|---|---|
| 1 | `/etc/hermes/config.yaml`（受管理） | `/etc/hermes/.env`（受管理） |
| 2 | `~/.hermes/config.yaml`（用户配置） | `~/.hermes/.env`（用户配置） |
| 3 | 内置默认值 | 已存在的shell环境变量 |

配置合并是在**最底层**进行的：固定 `model.default` 的值并不会限制其他 `model.*` 配置项。一个受管理的 `config.yaml` 文件的内容为：

```yaml
model:
  default: org/standard-model
```

强制所有用户使用 `model.default`，而将 `model.fallback`（以及其他所有键值）的设置权限交由用户自行掌控。

:::注意 优先级说明
对于那些被固定下来的键值而言，管理范围会刻意优先于Shell环境设置——否则也就谈不上“管理”了。这是唯一一个打破“环境变量优先于config.yaml配置”这一常规规则的情况，且该规则仅适用于管理层指定的特定键值。
:::

## 查看哪些内容处于受管理状态

```bash
hermes config        # shows a header naming the managed source + the pinned keys
hermes doctor        # reports the resolved managed dir + pinned key counts
```

如果您试图更改某个受管理的值，Hermes 会予以拒绝，并指出其来源。

```bash
$ hermes config set model.default my/model
Cannot set 'model.default': it is managed by your administrator
(/etc/hermes/config.yaml) and cannot be changed.
```

对于受管理的密钥也是如此——当 `.env` 文件中指定了某个环境变量的值时，`hermes config set` / setup 命令将不会覆盖该用户自定义的值。

## 设置受管理作用域（管理员专用）

```bash
sudo mkdir -p /etc/hermes

# Pin some config values for every user on this machine
sudo tee /etc/hermes/config.yaml >/dev/null <<'YAML'
model:
  provider: nous
security:
  redact_secrets: true
YAML

# Optionally pin a shared, non-sensitive env value
sudo tee /etc/hermes/.env >/dev/null <<'ENV'
OPENAI_API_BASE=https://inference.example.com/v1
ENV

sudo chmod 0755 /etc/hermes
sudo chmod 0644 /etc/hermes/config.yaml /etc/hermes/.env
```

这些更改将在下一次Hermes启动时生效（格式错误的托管文件会被记录并忽略——它不会阻碍启动，但管理员应通过`hermes doctor`检查以确保该策略已正确应用）。

## 安全模型与限制（v1版本）

- **仅通过文件系统权限进行管控。** 如果用户对托管目录拥有写入权限（或以`root`身份运行Hermes），则托管功能仅起到建议作用。
- **托管的`.env`文件为世界可读权限**（`0644`），因此任何本地用户均可读取通过该文件传递的敏感信息。建议将其用于存储共享的、非敏感的值（如组织API基础地址、功能默认设置），而非高度机密的密钥。
- **代理程序自身的工具并未被硬性禁止使用托管的*环境变量*值。** 托管的环境变量虽在启动时会被应用，但并无机制阻止代理在其自身的子进程Shell中设置不同的值。v1版本主要是为管理方便而设置的针对普通用户的隔离边界，并非无法突破的沙箱。

以下功能目前**有意不在v1版本的覆盖范围内**，未来可能会加入：

- 代理程序自身无法突破的严格隔离边界。
- macOS和Windows系统上的原生托管路径（v1版本优先支持Linux/POSIX系统）。
- 用于分层配置策略的插入式片段目录（`managed.d/`）。
- 经签名且经过完整性校验的托管文件。
- 远程/设备管理（MDM）分发方式。
- 对托管敏感信息更严格的（基于组级别的）权限控制。
