# 为 Hermes Agent 做贡献

感谢您为 Hermes Agent 出力！本指南涵盖了您所需了解的所有内容：配置开发环境、理解架构设计、确定要开发的功能，以及如何让您的 Pull Request 被顺利接受。

---

## 贡献优先级

我们按以下顺序重视各类贡献：

1. **错误修复** —— 包括程序崩溃、异常行为、数据丢失等问题。始终是最高优先级。
2. **跨平台兼容性** —— 支持 macOS、不同 Linux 发行版以及 Windows 上的 WSL2。我们希望 Hermes 能在所有环境中正常运行。
3. **安全性增强** —— 针对命令注入、提示词注入、路径遍历、权限提升等风险。详情请参阅[安全注意事项](#consideraciones-de-seguridad)。
4. **性能与稳定性** —— 重试逻辑、错误处理机制以及优雅的降级策略。
5. **新技能功能** —— 但仅限那些具有广泛实用价值的。详情请参阅[应该是技能还是工具？](#debería-ser-una-habilidad-o-una-herramienta)。
6. **新工具功能** —— 很少有此类需求。大多数功能都应以技能形式实现。更多内容见下文。
7. **文档完善** —— 包括错误修正、内容澄清以及新增示例。

---

## 应该是技能还是工具？

这是新贡献者最常遇到的问题。答案几乎总是**技能**。

### 以下情况应将其设为技能：

- 该功能可通过指令 + shell 命令 + 现有工具来实现；
- 涉及外部 CLI 或 API，且代理可通过 `terminal` 或 `web_extract` 调用它们；
- 不需要自定义 Python 集成，也不需要在代理内部集成 API 密钥管理功能；
- 示例：在 arXiv 上进行搜索、git 工作流处理、Docker 管理、PDF 处理、通过 CLI 工具发送邮件等。

### 以下情况应将其设为工具：

- 需要端到端的 API 密钥集成、认证流程，或由代理的 harness 负责管理多个组件的配置；
- 需要自定义的处理逻辑，且该逻辑必须在每次调用时都精确执行（而非依赖 LLM 的“最佳尝试”解读）；
- 需要处理二进制数据、流式数据或实时事件，而这些数据无法通过终端传递；
- 示例：浏览器自动化（使用 Browserbase 管理会话）、文本转语音（音频编码 + 平台播放）、视觉分析（处理 base64 格式的图像）等。

### 该技能是否应该被纳入？

已内置的技能（位于 `skills/` 目录中）会随每次 Hermes 安装一同提供。这些技能必须**对大多数用户都具有广泛实用性**，例如：
- 文档处理、网络搜索、常见开发工作流、系统管理功能；
- 能被大量不同用户频繁使用。

如果您的技能虽已正式推出且实用，但并非所有人都需要（例如支付服务集成、依赖较大的功能），请将其放入**`optional-skills/`**目录——该目录中的内容会随仓库一同提供，但默认不会启用。用户可通过 `hermes skills browse` 查看这些“官方”技能，并使用 `hermes skills install` 进行安装（无需担心第三方风险，具有内置信任机制）。

如果您的技能属于专业领域、由社区贡献或面向特定细分场景，建议将其放在**Skills Hub**中——将其上传到技能注册平台，并在 [Nous Research 的 Discord 频道](https://discord.gg/NousResearch) 上分享。用户同样可以通过 `hermes skills install` 安装此类技能。

---

## 内存提供器：作为独立插件发布

**我们不再接受在此仓库中新增内存提供器。** 已内置在 `plugins/memory/` 目录中的提供器集合（honcho、mem0、supermemory、byterover、hindsight、holographic、openviking、retaindb）已停止接收新功能。如果您想添加新的内存后端，建议将其作为**独立的插件仓库**发布，用户可将其安装到 `~/.hermes/plugins/` 目录中（或通过 pip 的入口点进行安装）。

独立的内存插件需满足以下要求：

- 实现相同的 ABC 接口 `MemoryProvider`（位于 `agent/memory_provider.py` 文件中），包括 `sync_turn`、`prefetch`、`shutdown` 方法，此外还可选择实现 `post_setup(hermes_home, config)` 方法以便与配置助手集成；
- 使用相同的发现机制——`discover_memory_providers()` 函数会从用户/项目级别的插件目录以及 pip 的入口点中扫描这些插件；
- 通过 `post_setup()` 方法与 `hermes memory setup` 功能集成，无需修改核心代码；
- 可以在 `cli.py` 文件中通过 `register_cli(subparser)` 方法注册自己的 CLI 子命令；
- 能够获得与树形结构中内置提供器相同的生命周期钩子和配置管道功能。

任何试图在 `plugins/memory/` 下新增子目录的 Pull Request 都会被拒绝，系统会提示您将相应提供器作为独立仓库发布。现有的树形结构中的提供器将继续保留，欢迎针对它们进行错误修复。

这并非质量门槛——而是出于耦合度和维护性的考虑。内存提供器是最常见的插件类型，不应全部集中在同一个目录中。

---

## 开发环境配置

### 先决条件

| 需求项 | 备注 |
|--------|------|
| **Git** | 需安装 `git-lfs` 扩展 |
| **Python 3.11–3.13** | 若缺失，uv 会自动帮您安装 |
| **uv** | 快速的 Python 包管理工具（[点击安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选——用于浏览器工具和 WhatsApp 桥接功能（需与根目录 `package.json` 中指定的引擎版本一致） |

### 克隆并安装

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Crear venv con Python 3.11
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# Instalar con todos los extras (mensajería, cron, menús CLI, herramientas de desarrollo)
uv pip install -e ".[all,dev]"

# Opcional: herramientas de navegador
npm install
```

### 开发环境配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# Añadir al menos una clave de proveedor LLM:
echo "OPENROUTER_API_KEY=***" >> ~/.hermes/.env
```

### 执行

```bash
# Enlace simbólico para acceso global
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes

# Verificar
hermes doctor
hermes chat -q "Hola"
```

### 执行测试

```bash
# Preferido — coincide con CI (entorno hermético, 4 workers xdist); ver AGENTS.md
scripts/run_tests.sh

# Alternativa (activa el venv primero). El wrapper sigue recomendándose
# para paridad con GitHub Actions antes de abrir un PR:
pytest tests/ -v
```

## 项目结构

```
hermes-agent/
├── run_agent.py              # Clase AIAgent — bucle de conversación central, despacho de herramientas, persistencia de sesión
├── cli.py                    # Clase HermesCLI — TUI interactiva, integración prompt_toolkit
├── model_tools.py            # Orquestación de herramientas (capa delgada sobre tools/registry.py)
├── toolsets.py               # Agrupaciones y presets de herramientas (hermes-cli, hermes-telegram, etc.)
├── hermes_state.py           # Base de datos de sesiones SQLite con búsqueda de texto completo FTS5, títulos de sesión
├── batch_runner.py           # Procesamiento en lote paralelo para generación de trayectorias
│
├── agent/                    # Internos del agente (módulos extraídos)
│   ├── prompt_builder.py         # Ensamblaje del prompt del sistema (identidad, habilidades, archivos de contexto, memoria)
│   ├── context_compressor.py     # Auto-resumición al acercarse a los límites de contexto
│   ├── auxiliary_client.py       # Resuelve clientes OpenAI auxiliares (resumición, visión)
│   ├── display.py                # KawaiiSpinner, formateo del progreso de herramientas
│   ├── model_metadata.py         # Longitudes de contexto del modelo, estimación de tokens
│   └── trajectory.py             # Ayudantes para guardar trayectorias
│
├── hermes_cli/               # Implementaciones de comandos CLI
│   ├── main.py                   # Punto de entrada, análisis de argumentos, despacho de comandos
│   ├── config.py                 # Gestión de configuración, migración, definiciones de variables de entorno
│   ├── setup.py                  # Asistente de configuración interactivo
│   ├── auth.py                   # Resolución de proveedor, OAuth, Nous Portal
│   ├── models.py                 # Listas de selección de modelos de OpenRouter
│   ├── banner.py                 # Banner de bienvenida, arte ASCII
│   ├── commands.py               # Registro central de comandos de barra (CommandDef), autocompletado, ayudantes del gateway
│   ├── callbacks.py              # Callbacks interactivos (aclarar, sudo, aprobación)
│   ├── doctor.py                 # Diagnósticos
│   ├── skills_hub.py             # CLI del Skills Hub + comando de barra /skills
│   └── skin_engine.py            # Motor de skins/temas — personalización visual de CLI basada en datos
│
├── tools/                    # Implementaciones de herramientas (auto-registradas)
│   ├── registry.py               # Registro central de herramientas (esquemas, manejadores, despacho)
│   ├── approval.py               # Detección de comandos peligrosos + aprobación por sesión
│   ├── terminal_tool.py          # Orquestación del terminal (sudo, ciclo de vida del entorno, backends)
│   ├── file_operations.py        # read_file, write_file, búsqueda, patch, etc.
│   ├── web_tools.py              # web_search, web_extract (Paralelo/Firecrawl + resumición Gemini)
│   ├── vision_tools.py           # Análisis de imágenes a través de modelos multimodales
│   ├── delegate_tool.py          # Lanzamiento de subagentes y ejecución paralela de tareas
│   ├── code_execution_tool.py    # Python sandboxado con acceso a herramientas vía RPC
│   ├── session_search_tool.py    # Búsqueda en conversaciones pasadas con FTS5 + ventanas ancladas
│   ├── cronjob_tools.py          # Gestión de tareas programadas
│   ├── skill_tools.py            # Búsqueda, carga y gestión de habilidades
│   └── environments/             # Backends de ejecución del terminal
│       ├── base.py                   # ABC BaseEnvironment
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # Gateway de mensajería
│   ├── run.py                    # GatewayRunner — ciclo de vida de plataformas, enrutamiento de mensajes, cron
│   ├── config.py                 # Resolución de configuración de plataformas
│   ├── session.py                # Almacén de sesiones, prompts de contexto, políticas de reset
│   └── platforms/                # Adaptadores de plataformas
│       ├── telegram.py, discord_adapter.py, slack.py, whatsapp.py
│
├── scripts/                  # Scripts del instalador y puente
│   ├── install.sh                # Instalador Linux/macOS
│   ├── install.ps1               # Instalador Windows PowerShell
│   └── whatsapp-bridge/          # Puente WhatsApp Node.js (Baileys)
│
├── skills/                   # Habilidades incluidas (copiadas a ~/.hermes/skills/ en la instalación)
├── optional-skills/          # Habilidades opcionales oficiales (descubribles vía hub, no activadas por defecto)
├── tests/                    # Suite de tests
├── website/                  # Sitio de documentación (hermes-agent.nousresearch.com)
│
├── cli-config.yaml.example   # Configuración de ejemplo (copiada a ~/.hermes/config.yaml)
└── AGENTS.md                 # Guía de desarrollo para asistentes de codificación IA
```

### 用户配置（存储在 `~/.hermes/` 目录中）

| 路径 | 用途 |
|------|-----------|
| `~/.hermes/config.yaml` | 配置参数（模型、终端、工具集、压缩功能等） |
| `~/.hermes/.env` | API 密钥与敏感信息 |
| `~/.hermes/auth.json` | OAuth 认证凭证（Nous Portal） |
| `~/.hermes/skills/` | 所有已激活的技能（包括从中心平台安装的以及由智能体创建的技能） |
| `~/.hermes/memories/` | 持久化记忆内容（MEMORY.md、USER.md） |
| `~/.hermes/state.db` | SQLite 会话数据库 |
| `~/.hermes/sessions/` | 网关路由索引（`sessions.json`）、请求日志、网关生成的 `*.jsonl` 格式转录文件；当配置了 `sessions.write_json_snapshots: true` 时，还会包含按会话生成的 JSON 快照。默认情况下会话快照功能处于关闭状态，此时 state.db 即为标准数据源。 |
| `~/.hermes/cron/` | 定时任务相关数据 |
| `~/.hermes/whatsapp/session/` | WhatsApp 桥接工具的认证凭证 |

---

## 架构概述

### 核心循环机制

```
Mensaje del usuario → AIAgent._run_agent_loop()
  ├── Construir prompt del sistema (prompt_builder.py)
  ├── Construir kwargs de API (modelo, mensajes, herramientas, configuración de razonamiento)
  ├── Llamar al LLM (API compatible con OpenAI)
  ├── Si tool_calls en la respuesta:
  │     ├── Ejecutar cada herramienta a través del despacho del registro
  │     ├── Añadir resultados de herramientas a la conversación
  │     └── Volver a la llamada al LLM
  ├── Si respuesta de texto:
  │     ├── Persistir sesión en DB
  │     └── Devolver final_response
  └── Compresión de contexto si se acerca al límite de tokens
```

### 核心设计模式

- **自动注册工具**：每个工具文件在导入时都会调用 `registry.register()`。`model_tools.py` 通过导入所有工具模块来启用工具发现功能。
- **按工具集分组**：工具会被归类到不同的工具集（如 `web`、`terminal`、`file`、`browser` 等）中，这些工具集可根据平台需求进行开启或关闭。
- **会话持久化**：所有对话都会存储在 SQLite 数据库中（由 `hermes_state.py` 负责），支持全文搜索，并为每个会话分配唯一标识。
- **临时注入机制**：系统提示语和填充信息仅在调用 API 时被注入，不会被保存到数据库或日志中。
- **提供者抽象层**：该代理可兼容任何支持 OpenAI 的 API，提供者的确定工作在初始化阶段完成。
- **提供者路由**：当使用 OpenRouter 时，`config.yaml` 中的 `provider_routing` 用于控制提供者的选择。

---

## 代码风格规范

- 遵循 **PEP 8** 标准，但实际应用中不做严格的行长限制
- **注释**：仅用于解释那些不显而易见的意图、设计决策或 API 的特殊之处，切勿描述代码的功能实现
- **错误处理**：需捕获特定的异常，并使用 `logger.warning()`/`logger.error()` 进行记录——对于意外错误，请使用 `exc_info=True`
- **跨平台兼容性**：切勿假设代码仅在 Unix 环境下运行。详情请参阅 [跨平台兼容性](#compatibilidad-multiplataforma)

---

## 添加新工具

在编写新工具之前，先思考这样一个问题：[它是否更适合被定义为一种技能？](#debería-ser-una-habilidad-o-una-herramienta)

工具会自动注册到中央注册表中。每个工具文件都会同时包含其结构定义、处理逻辑以及注册信息：

```python
"""my_tool — Breve descripción de lo que hace esta herramienta."""

import json
from tools.registry import registry


def my_tool(param1: str, param2: int = 10, **kwargs) -> str:
    """Manejador. Devuelve un resultado en cadena (a menudo JSON)."""
    result = do_work(param1, param2)
    return json.dumps(result)


MY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Qué hace esta herramienta y cuándo debería usarla el agente.",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Qué es param1"},
                "param2": {"type": "integer", "description": "Qué es param2", "default": 10},
            },
            "required": ["param1"],
        },
    },
}


def _check_requirements() -> bool:
    """Devuelve True si las dependencias de esta herramienta están disponibles."""
    return True


registry.register(
    name="my_tool",
    toolset="my_toolset",
    schema=MY_TOOL_SCHEMA,
    handler=lambda args, **kw: my_tool(**args, **kw),
    check_fn=_check_requirements,
)
```

**连接工具集（必需）：** 内置工具会自动被发现：当加载 `model_tools` 时，`tools/registry.py` 中的 `discover_builtin_tools()` 函数会导入任何包含顶层调用 `registry.register(...)` 的 `tools/*.py` 文件。无需在 `model_tools.py` 中手动维护导入列表。

您仍需将工具名称添加到 `toolsets.py` 中对应的列表中（例如 `_HERMES_CORE_TOOLS` 或专用的工具集）；否则，该工具虽然会被注册，但永远不会向智能体暴露。

请查阅 `AGENTS.md` 文件中的 **添加新工具** 部分，以了解与配置文件相关的路径以及插件与核心组件的区别。

---

## 添加技能

内置技能存储在 `skills/` 目录中，并按类别进行组织。官方提供的可选技能则采用相同的结构，存放在 `optional-skills/` 目录下：

```
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # Requerido: instrucciones principales
│       └── scripts/              # Opcional: scripts auxiliares
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

### SKILL.md 文件格式

```markdown
---
name: my-skill
description: Breve descripción (mostrada en los resultados de búsqueda de habilidades)
version: 1.0.0
author: Tu Nombre
license: MIT
platforms: [macos, linux]          # Opcional — restringir a plataformas de SO específicas
required_environment_variables:    # Opcional — metadatos de configuración segura al cargar
  - name: MY_API_KEY
    prompt: Clave API
    help: Dónde obtenerla
    required_for: funcionalidad completa
prerequisites:                     # Requisitos de tiempo de ejecución heredados opcionales
  env_vars: [MY_API_KEY]
  commands: [curl, jq]
metadata:
  hermes:
    tags: [Categoría, Subcategoría, Palabras clave]
    related_skills: [other-skill-name]
    fallback_for_toolsets: [web]
    requires_toolsets: [terminal]
---

# Título de la Habilidad

Introducción breve.

## Cuándo Usar
Condiciones de activación — ¿cuándo debería el agente cargar esta habilidad?

## Referencia Rápida
Tabla de comandos o llamadas API comunes.

## Procedimiento
Instrucciones paso a paso que el agente sigue.

## Problemas Conocidos
Modos de fallo conocidos y cómo manejarlos.

## Verificación
Cómo confirma el agente que funcionó.
```

### 技能作者规范（必须遵守）

所有新创建或升级的技能——无论是官方提供的、可选的还是用户贡献的——在合并之前都必须符合以下标准：

1. **`description` 长度不得超过 60 个字符，需为单句，并以句号结尾。** 过长的描述会占用过多的技能列表界面空间。该字段应描述技能的功能，而非实现方式，禁止使用任何营销用语（如“强大”、“全面”、“流畅”、“高级”等）。

2. **SKILL.md 正文中所提及的工具必须是 Hermes 自带的工具，或是该技能明确依赖的 MCP 服务器工具。** 工具名称需用反引号标出，例如：`` `terminal` ``、`` `web_extract` ``、`` `web_search` ``、`` `read_file` ``、`` `write_file` `` 等。

3. **`platforms:` 字段的内容需与脚本的实际导入情况一致。** 仅使用 POSIX 原语的技能必须明确说明其支持的平台。

4. **`author` 字段应首先注明负责开发的人类贡献者。**

5. **SKILL.md 的结构需遵循现代章节顺序：标题、2-3 句的简介，随后依次为：`## 适用场景`、`## 先决条件`、`## 使用方法`、`## 快速参考`、`## 操作步骤`、`## 已知问题`、`## 验证方式`。**

6. **脚本文件应存放于 `scripts/` 目录中，参考资料放在 `references/`，模板则存放在 `templates/`。**

7. **测试文件需位于 `tests/skills/test_<skill>_skill.py` 中**，且只能使用标准库、pytest 以及 `unittest.mock` 工具，禁止进行实时网络请求。

8. **对 `.env.example` 文件的修改应被封装在结构清晰的代码块中。**

---

## 添加皮肤/主题

Hermes 采用基于数据的皮肤系统——因此无需修改代码即可添加新皮肤。

**方案 A：用户自定义皮肤（YAML 文件）**

创建 `~/.hermes/skins/<名称>.yaml` 文件：

```yaml
name: mitema
description: Breve descripción del tema

colors:
  banner_border: "#HEX"
  banner_title: "#HEX"
  banner_accent: "#HEX"
  banner_dim: "#HEX"
  banner_text: "#HEX"
  response_border: "#HEX"

spinner:
  waiting_faces: ["(⚔)", "(⛨)"]
  thinking_faces: ["(⚔)", "(⌁)"]
  thinking_verbs: ["forjando", "planeando"]

branding:
  agent_name: "Mi Agente"
  welcome: "Mensaje de bienvenida"
  response_label: " ⚔ Agente "
  prompt_symbol: "⚔"

tool_prefix: "╎"
```

所有字段均为可选——缺失的值将继承自默认皮肤设置。

**选项 B：内置皮肤**

在 `hermes_cli/skin_engine.py` 中添加 `_BUILTIN_SKINS` 字典。使用与上文相同的结构，但以 Python 字典的形式呈现。

**启用方式：**
- CLI：`/skin mitema`，或在 config.yaml 中设置 `display.skin: mitema`

---

## 多平台兼容性

Hermes 可在 Linux、macOS 以及原生 Windows 环境（包括 WSL2）上运行。在编写涉及操作系统的代码时，请假设*任何*平台都可能访问您的代码路径。

> **提交 PR 前：** 运行 `scripts/check-windows-footguns.py` 以检测 diff 中常见的 Windows 安全漏洞模式。该工具基于 grep 开发，成本较低；CI 系统也会在每个 PR 中执行此检查。

### 关键规则

1. **切勿使用 `os.kill(pid, 0)` 来检测进程是否存活。** 在 Windows 上，这**并非无操作**。请改用 `psutil.pid_exists(pid)`。

2. **在调用 shell 命令前使用 `shutil.which()`——不要假设 Windows 拥有与 Linux 相同的工具。** `ps`、`kill`、`grep`、`awk` 等命令在 Windows 上根本不存在。

3. **`termios` 和 `fcntl` 仅适用于 Unix 系统。** 请始终捕获 `ImportError` 和 `NotImplementedError` 异常。

4. **文件编码问题。** Windows 可能会以 `cp1252` 编码保存 `.env` 文件。请务必处理编码错误。

5. **进程管理。** `os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 以及 POSIX 信号处理在 Windows 上有所不同。

6. **Windows 上不存在的信号：** `SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2` 等。

7. **路径分隔符。** 请使用 `pathlib.Path`，而非用 `/` 连接字符串。

8. **在 Windows 上，符号链接需要高级权限**（除非已启用开发者模式）。

9. **POSIX 文件权限模式（0o600、0o644 等）默认不适用于 NTFS 文件系统。**

10. **Windows 上的解耦后台守护进程需要使用 `pythonw.exe`，而非 `python.exe`。**

---

## 安全性考虑

Hermes 可以访问终端，因此安全性至关重要。

### 现有防护措施

| 防护层 | 实现方式 |
|------|---------------|
| **sudo 密码管道保护** | 使用 `shlex.quote()` 防止 shell 注入攻击 |
| **危险命令检测** | `tools/approval.py` 中的正则表达式配合用户审批流程 |
| **cron 脚本提示注入防护** | `tools/cronjob_tools.py` 中的扫描器可阻止指令取消模式 |
| **写入禁止列表** | 通过 `os.path.realpath()` 解析受保护路径，防止绕过符号链接 |
| **Skills Guard** | 用于扫描从中心平台安装的技能的安全工具（`tools/skills_guard.py`） |
| **代码执行沙箱** | 子进程 `execute_code` 在移除 API 密钥的环境中运行 |
| **容器加固** | Docker 环境：移除所有特权，禁止权限提升，设置 PID 限制及有限的 tmpfs 存储空间 |

### 在提交涉及安全性的代码时

- **在将用户输入插入 shell 命令时，务必使用 `shlex.quote()` 进行处理**
- **在基于路径的访问控制检查之前，先用 `os.path.realpath()` 解析符号链接**
- **切勿记录敏感信息。** API 密钥、令牌和密码绝不能出现在日志输出中
- **在工具执行周围捕获通用异常**，避免单次故障导致代理循环中断
- **如果您的更改涉及文件路径、进程管理或 shell 命令，请在所有平台上进行测试**

### 依赖项锁定策略（供应链加固）

鉴于 2026 年 3 月发生的 [litellm 供应链攻击](https://github.com/BerriAI/litellm/issues/24512) 以及 2026 年 5 月的 [Mini Shai-Hulud 蠕虫攻击事件](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack)，所有依赖项都必须遵循以下规则：

| 依赖来源类型 | 所需处理方式 | 原因说明 |
|---|---|---|
| **PyPI 包** | `>=版本号,<下一个主版本号` | PyPI 上的版本在发布后不可更改，但您可以在指定范围内推送新版本 |
| **Git 地址** | 提交的完整 SHA 值 | 分支和标签是可变的引用；SHA 值则通过内容唯一标识 |
| **GitHub Actions** | 提交的完整 SHA 值 + 版本注释 | Actions 标签也是可变引用。应锁定为 `uses: owner/action@<sha>  # vX.Y.Z` 的形式 |
| **仅用于 CI 的 pip 安装** | `==精确版本号` | CI 环境是隔离的，允许使用精确版本 |

**每个 PR 中新增的 PyPI 依赖项都必须设置上限 `<下一个主版本号>`。** 未设置上限且仅指定 `>=X.Y.Z` 版本的 PR 将会被拒绝。

---

## Pull Request 流程

### 分支命名规范

```
fix/descripcion        # Correcciones de errores
feat/descripcion       # Nuevas funcionalidades
docs/descripcion       # Documentación
test/descripcion       # Tests
refactor/descripcion   # Reestructuración de código
```

### 提交前准备

1. **运行测试**：使用 `scripts/run_tests.sh`（推荐方式，与 CI 流程一致），或在激活项目虚拟环境后执行 `pytest tests/ -v`。
2. **手动测试**：启动 `hermes` 并调用你修改过的代码路径进行测试。
3. **检查跨平台兼容性**：如果涉及文件读写、进程管理或终端操作，务必在 macOS、Linux 和 WSL2 环境下进行测试。
4. **保持 PR 的专注性**：每个 PR 应仅包含一个逻辑变更。不要将错误修复、代码重构与新功能开发混在同一个 PR 中。

### PR 描述内容

需包含以下信息：
- **更改了什么**以及**原因**
- **如何测试**（错误情况的复现步骤，功能模块的使用示例）
- **已测试的平台**
- 关联的相关 issue 参考链接

### 提交信息规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准：

```
<tipo>(<alcance>): <descripción>
```

| 类型 | 用途 |
|------|------|
| `fix` | 错误修复 |
| `feat` | 新功能开发 |
| `docs` | 文档编写 |
| `test` | 测试用例 |
| `refactor` | 代码重构（不改变功能行为） |
| `chore` | 构建、持续集成及依赖项更新 |

覆盖范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

示例：
```
fix(cli): prevenir bloqueo en save_config_value cuando el modelo es una cadena
feat(gateway): añadir aislamiento de sesión multi-usuario de WhatsApp
fix(security): prevenir inyección de shell en el piping de contraseña sudo
test(tools): añadir tests unitarios para file_operations
```

---

## 报告问题

- 请使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues) 提交问题  
- 需提供以下信息：操作系统、Python 版本、Hermes 版本（通过 `hermes version` 命令查看）、完整的错误堆栈信息  
- 同时需附上问题复现步骤  
- 在提交重复问题之前，请先查看已有的相关 issue  
- 若发现安全漏洞，请通过私密方式报告  

---

## 社区

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch) —— 用于提问、展示项目及交流技能  
- **GitHub Discussions**：用于设计建议及架构讨论  
- **Skills Hub**：可将专业技能上传至该平台，并与社区成员共享  

---

## 许可证

通过贡献代码，即表示您同意您的贡献将依据 [MIT 许可证](LICENSE) 进行授权。
