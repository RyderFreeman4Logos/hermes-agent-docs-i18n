# 为 Hermes Agent 做贡献

感谢您为 Hermes Agent 出力！本指南涵盖了您所需了解的所有内容：配置开发环境、理解架构设计、确定要开发的功能，以及如何让您的 Pull Request 被顺利接受。

---

## 贡献优先级

我们按照以下顺序重视各类贡献：

1. **错误修复** —— 程序卡死、异常行为、数据丢失等问题。始终具有最高优先级。
2. **跨平台兼容性** —— macOS、不同版本的 Linux 以及 Windows 上的 WSL2。我们希望 Hermes 能在所有环境中正常运行。
3. **安全性增强** —— 壳代码注入、提示符注入、路径遍历、权限提升等问题。详情请参阅[安全注意事项](#consideraciones-de-seguridad)。
4. **性能与稳定性** —— 重试逻辑、错误处理机制以及优雅的降级策略。
5. **新技能功能** —— 但仅限那些具有广泛实用价值的。详情请参阅[应该是技能还是工具？](#debería-ser-una-habilidad-o-una-herramienta)。
6. **新工具功能** —— 很少有此类需求。大多数功能都应以技能的形式实现。更多内容见下文。
7. **文档完善** —— 错误修正、内容澄清以及新增示例。

---

## 应该是技能还是工具？

这是新贡献者最常遇到的问题。答案几乎总是**技能**。

### 以下情况应将其设计为技能：

- 该功能可通过指令、Shell命令以及现有工具来实现。  
- 它可集成外部CLI或API，让Agent能够通过`terminal`或`web_extract`来调用这些工具。  
- 无需在Agent中实现自定义的Python集成，也不需要内置的API密钥管理功能。  
- 示例：在arXiv上搜索、Git工作流处理、Docker管理、PDF处理，以及通过CLI工具发送邮件。  

### 何时应将其打造为工具：  
- 当需要端到端的集成，涉及API密钥、认证流程，或需由Agent的框架统一管理多个组件的配置时；  
- 当需要执行高度精确的自定义处理逻辑（而非依赖LLM的“尽力而为”式解读）时；  
- 当处理二进制数据、流式数据或实时事件，而这些数据无法通过终端传输时。  
- 示例：浏览器自动化（如Browserbase会话管理）、文本转语音（音频编码及平台推送）、视觉分析（处理base64格式的图像）。  

### 是否应包含该技能？  
随Hermes一同提供的技能文件位于`skills/`目录中，这些技能必须**对大多数用户都具有极高的实用性**：  
- 文档处理、网络搜索、常见的开发工作流、系统管理；  
- 能被广泛的用户群体频繁使用。
如果你的技能虽官方认可且实用，但并非普遍必需（例如支付服务集成、重量级依赖项），请将其放入 **`optional-skills/`** 目录——该目录中的技能会随仓库一同提供，但默认处于未激活状态。用户可通过 `hermes skills browse` 查看到这些标记为“官方”的技能，并使用 `hermes skills install` 进行安装（无需担心第三方风险，具备内置信任机制）。

若你的技能属于专业领域、由社区贡献或面向特定群体，那么将其放在 **Skills Hub** 中更为合适——你可以将其上传至技能注册平台，并在 [Nous Research 的 Discord 频道](https://discord.gg/NousResearch) 上分享。用户同样可以通过 `hermes skills install` 安装此类技能。

---

## 内存提供者：作为独立插件发布

**我们不再接受在此仓库中新增内存提供者。** 已内置在 `plugins/memory/` 目录中的那些提供者（honcho、mem0、supermemory、byterover、hindsight、holographic、openviking、retaindb）均已封停。如果你想添加新的内存后端，建议将其作为**独立的插件仓库**发布，让用户通过 `~/.hermes/plugins/` 路径（或通过 pip 的入口点）进行安装。

独立的记忆插件：

- 它们实现了相同的 `MemoryProvider` ABC（位于 `agent/memory_provider.py` 文件中），包括 `sync_turn`、`prefetch`、`shutdown` 函数，以及用于与配置助手集成的可选函数 `post_setup(hermes_home, config)`。
- 它们使用相同的发现机制——`discover_memory_providers()` 会从用户/项目插件目录及 pip 的入口点中查找这些提供者。
- 它们可通过 `post_setup()` 函数与 `hermes memory setup` 功能集成，而无需修改核心代码。
- 它们可以通过在 `cli.py` 文件中的 `register_cli(subparser)` 函数注册自己的 CLI 子命令。
- 它们能够使用与树结构中内置提供者相同的生命周期钩子及配置管道功能。

对于那些试图在 `plugins/memory/` 下创建新目录的 Pull Request，将会被拒绝，建议将相关提供者发布为独立的仓库。现有的树结构中的提供者将继续保留，同时也欢迎针对这些提供者的错误修复。

这并非质量标准问题，而是耦合度与维护性方面的考量。内存提供者是最常见的插件类型，但并非所有此类插件都应存在于这个树结构中。

---

## 开发配置

### 先决条件

| 要求 | 备注 |
|-----------|-------|
| **Git** | 需已安装 `git-lfs` 扩展 |
| **Python 3.11–3.13** | 若缺失，uv 会自动进行安装 |
| **uv** | 快速的 Python 包管理工具（[点击安装](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 非必需——用于浏览器工具及 WhatsApp 桥接功能（需与 `package.json` 根目录中的引擎版本一致） |

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

### 运行测试

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
| `~/.hermes/auth.json` | OAuth 凭据（Nous Portal） |
| `~/.hermes/skills/` | 所有已激活的技能（包括从 Hub 安装的以及由 Agent 创建的技能） |
| `~/.hermes/memories/` | 持久化记忆内容（MEMORY.md、USER.md） |
| `~/.hermes/state.db` | SQLite 会话数据库 |
| `~/.hermes/sessions/` | 网关路由索引（sessions.json）、请求日志、网关生成的 `*.jsonl` 转录文件，以及通过 `/save` 命令导出的内容。系统不再自动生成 JSON 快照；现有文件会被保留，且 state.db 为标准版本。 |
| `~/.hermes/cron/` | 定时任务相关数据 |
| `~/.hermes/whatsapp/session/` | WhatsApp 桥接工具的凭证 |

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

- **自动注册工具**：每个工具文件在导入时都会调用 `registry.register()` 函数。`model_tools.py` 通过导入所有工具模块来启动工具发现机制。
- **按工具集分组**：工具会被归类到不同的工具集中（如 `web`、`terminal`、`file`、`browser` 等），这些工具集可根据平台需求启用或禁用。
- **会话持久化**：所有对话均存储在 SQLite 数据库中（由 `hermes_state.py` 负责管理），支持全文本搜索，并为每个会话生成唯一的标题。
- **临时注入机制**：系统提示语和填充信息会在调用 API 时被动态注入，绝不会被保存到数据库或日志文件中。
- **提供者抽象层**：该代理可适配任何兼容 OpenAI 的 API，提供者的确定工作在初始化阶段完成。
- **提供者路由功能**：当使用 OpenRouter 时，`config.yaml` 文件中的 `provider_routing` 设置可用于控制提供者的选择。

---

## 代码风格规范

- **PEP 8**：在实践中灵活应用（我们不强制要求严格的行长度限制）
- **注释**：仅用于解释那些不显而易见的意图、约定或 API 的特殊之处。无需描述代码的功能
- **错误处理**：捕获特定的异常。使用 `logger.warning()`/`logger.error()` 进行记录——对于意外出现的错误，请使用 `exc_info=True`
- **跨平台兼容性**：切勿默认代码仅在 Unix 环境下运行。请参阅[跨平台兼容性](#compatibilidad-multiplataforma)指南

---

## 添加新工具

在编写工具之前，先问自己这样一个问题：[它是否应该被视为一项技能而非工具？](#debería-ser-una-habilidad-o-una-herramienta)

这些工具会自动注册到中央注册表中。每个工具文件都会同时包含其架构定义、处理逻辑以及相关注册信息：

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

**连接工具集（必需）：** 内置工具会自动被发现：任何包含顶层调用 `registry.register(...)` 的 `tools/*.py` 文件，都会在加载 `model_tools` 时被 `tools/registry.py` 中的 `discover_builtin_tools()` 导入。无需在 `model_tools.py` 中手动维护导入列表。

您仍需将工具名称添加到 `toolsets.py` 中的相应列表中（例如 `_HERMES_CORE_TOOLS` 或专用的工具集）；否则，该工具虽会被注册，但永远不会向智能体暴露。

请查阅 `AGENTS.md` 文件中的**添加新工具**部分，以了解与配置文件相关的路径以及插件与核心组件的区别。

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

### 技能归属标准（强制要求）

所有新创建或升级的技能——无论是内置的、可选的还是用户贡献的——在合并之前都必须符合这些标准：

1. **`description` 的长度需控制在 60 个字符以内，只能包含一句内容，并以句号结尾。** 过长的描述会占据技能列表界面的过多空间。应描述技能的功能能力，而非实现细节，同时禁止使用任何营销性词汇（如“强大”“全面”“流畅”“先进”等）。

2. **SKILL.md 正文中所提及的工具必须是 Hermes 自带的原生工具，或是该技能明确指定的 MCP 服务器。** 工具名称需使用反引号标注，例如：`` `terminal` ``、`` `web_extract` ``、`` `web_search` ``、`` `read_file` ``、`` `write_file` `` 等。

3. **`platforms:` 字段的内容会依据脚本的实际导入情况来进行验证。** 那些仅使用 POSIX 原语的技能，必须明确列出其支持的平台。

4. **`author` 字段应首先注明负责开发的人类贡献者。**

5. **SKILL.md 的结构需遵循现代章节顺序：标题、2-3 句的简介，随后依次为 `## 适用场景`、`## 先决条件`、`## 使用方法`、`## 快速参考`、`## 操作步骤`、`## 已知问题`以及 `## 验证方式`。**

6. **脚本文件应存放在 `scripts/` 目录中，参考资料放在 `references/` 目录，模板则存放于 `templates/` 目录。**

7. **测试文件位于 `tests/skills/test_<skill>_skill.py` 中**，且仅允许使用标准库、pytest 以及 `unittest.mock` 工具，不得包含任何实时网络请求。

8. **对 `.env.example` 文件的修改内容，需被置于一个格式清晰的独立代码块中。**

---

## 添加皮肤/主题

Hermes采用基于数据的皮肤系统——添加新皮肤无需修改代码。

**选项A：用户皮肤（YAML文件）**

创建`~/.hermes/skins/<名称>.yaml`文件：

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

在 `hermes_cli/skin_engine.py` 中添加 `_BUILTIN_SKINS` 字典。其结构与上文相同，但以 Python 字典的形式呈现。

**启用方式：**
- CLI：输入 `/skin mitema`，或在 config.yaml 中设置 `display.skin: mitema`

---

## 多平台兼容性

Hermes 可在 Linux、macOS 以及原生 Windows 环境（包括 WSL2）下运行。在编写涉及操作系统的代码时，请假设*任何*平台都可能访问您的代码路径。

> **提交 Pull Request 前：** 运行 `scripts/check-windows-footguns.py` 以检测 diff 中常见的 Windows 安全问题模式。该工具基于 grep 开发，成本较低；CI 系统也会在每个 PR 中自动执行此检查。

### 关键规则

1. **切勿使用 `os.kill(pid, 0)` 来检测进程是否存活。**在 Windows 系统中，该操作**并非无效果**。请改用 `psutil.pid_exists(pid)`。

2. **在调用 shell 命令之前，请先使用 `shutil.which()`——不要假设 Windows 拥有与 Linux 相同的工具。**`ps`、`kill`、`grep`、`awk` 等命令在 Windows 中根本不存在。

3. **`termios` 和 `fcntl` 仅适用于 Unix 系统。**务必同时处理 `ImportError` 和 `NotImplementedError` 异常。

4. **文件编码问题。**Windows 可能会以 `cp1252` 编码保存 `.env` 文件。务必妥善处理编码错误。

5. **进程管理功能。**`os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 以及 POSIX 信号处理机制在 Windows 中有所不同。

6. **Windows 中不存在的信号：**`SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2` 等。

7. **路径分隔符。**请使用 `pathlib.Path`，而非通过字符串拼接加上 `/` 符号。

8. **在 Windows 上创建符号链接需要高级权限**（除非已启用开发者模式）。

9. **POSIX 文件权限模式（如 0o600、0o644 等）在 NTFS 文件系统上默认不生效。**

10. **Windows 下的独立后台守护进程需要使用 `pythonw.exe`，而非 `python.exe`。**

---

## 安全注意事项

Hermes 具有终端访问权限，因此安全问题至关重要。

### 现有的防护措施

| 功能 | 实现方式 |
|------|-----------|
| **sudo 密码传递** | 使用 `shlex.quote()` 防止shell注入攻击 |
| **危险命令检测** | 通过 `tools/approval.py` 中的正则表达式模式结合用户审批流程进行识别 |
| **cron 提示符注入防护** | `tools/cronjob_tools.py` 中的扫描器可拦截用于取消指令的恶意模式 |
| **写入拒绝列表** | 通过 `os.path.realpath()` 解析受保护路径，防止通过符号链接绕过限制 |
| **Skills Guard** | 对从中心平台安装的技能进行安全扫描（由 `tools/skills_guard.py` 负责） |
| **代码执行沙箱** | `execute_code` 子进程在已移除API密钥的环境中运行 |
| **容器加固** | Docker环境：移除所有额外功能，禁止权限提升，设置PID限制，并限制tmpfs大小 |

### 在提交涉及安全敏感性的代码时

- 在将用户输入插入 shell 命令时，**始终使用 `shlex.quote()`** 进行处理  
- 在基于路径的访问控制检查之前，使用 `os.path.realpath()` **解析符号链接**  
- **切勿记录敏感信息**。API 密钥、令牌和密码绝不能出现在日志输出中  
- 在工具执行周围**捕获通用异常**，以防止单次故障阻塞代理循环  
- 若您的更改涉及文件路径、进程管理或 shell 命令，请在**所有平台**上进行测试  

### 依赖项锁定策略（强化供应链安全）  

鉴于 2026 年 3 月发生的 [litellm 供应链安全漏洞](https://github.com/BerriAI/litellm/issues/24512)以及 2026 年 5 月的 [Mini Shai-Hulud 蠕虫攻击事件](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack)，所有依赖项都必须遵循以下规则：

| 源类型 | 所需处理方式 | 原因说明 |
|---|---|---|
| **PyPI 包** | `>=当前版本,<下一个更大版本` | PyPI 上的版本在发布后不可更改，但可在您指定的范围内推送新版本。 |
| **Git URL** | 提交的完整 SHA 值 | 分支和标签属于可变引用；SHA 值则由实际内容决定。 |
| **GitHub Actions** | 提交的完整 SHA 值 + 版本注释 | Actions 标签属于可变引用。应将其固定为 `uses: owner/action@<sha>  # vX.Y.Z` 的格式。 |
| **仅用于 CI 的 pip 安装** | `==精确版本号` | CI 环境是隔离构建的，允许版本号发生变动。 |

**在 Pull Request 中，每个新增的 PyPI 依赖都必须设置上限 `<下一个更大版本>`。** 若 PR 中包含未指定上限的 `>=X.Y.Z` 格式要求，将被拒绝。

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

1. **运行测试**：使用 `scripts/run_tests.sh`（推荐方式，与 CI 流水线相同），或在激活项目虚拟环境后执行 `pytest tests/ -v`。
2. **手动测试**：启动 `hermes` 并调用你修改过的代码路径进行测试。
3. **检查跨平台兼容性**：如果涉及文件读写、进程管理或终端操作，务必在 macOS、Linux 和 WSL2 环境下进行测试。
4. **保持 PR 的专注性**：每个 PR 应仅包含一个逻辑变更。切勿将错误修复、代码重构与新功能开发混在一起。

### PR 描述内容

需包含以下信息：
- **具体修改了什么**以及**原因**
- **如何验证改动**（错误情况的复现步骤，功能模块的使用示例）
- **已测试过的平台**
- 引用相关的 issue 号码

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
| `refactor` | 代码重构（不改变原有行为） |
| `chore` | 构建、持续集成及依赖项更新 |

适用范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

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
- 需包含以下信息：操作系统、Python 版本、Hermes 版本（通过 `hermes --version` 查看）、完整的错误堆栈信息
- 需附上问题复现步骤
- 在提交重复问题前，请先查看现有问题
- 如发现安全漏洞，请通过私密方式报告

---

## 社区

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch) —— 用于提问、展示项目及分享技能
- **GitHub Discussions**：用于设计建议及架构讨论
- **Skills Hub**：可将专业技能上传至该平台并与社区共享

---

## 许可证

通过贡献代码，即表示您同意您的贡献将依据 [MIT 许可证](LICENSE) 进行授权。
