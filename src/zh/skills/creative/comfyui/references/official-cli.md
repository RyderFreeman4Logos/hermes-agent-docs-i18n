# comfy-cli 命令参考手册

来自 [Comfy-Org/comfy-cli](https://github.com/Comfy-Org/comfy-cli) 的官方命令行工具。
文档地址：https://docs.comfy.org/comfy-cli/getting-started

## 安装

推荐安装顺序：

```bash
pipx install comfy-cli            # recommended (isolated env)
uvx --from comfy-cli comfy --help # zero-install via uv
pip install --user comfy-cli      # fallback
```

该技能对应的 `comfyui_setup.sh` 脚本会自动选择最优的配置方式。首次运行时可能会询问是否启用分析功能，如需以非交互模式禁用该功能，请执行相应操作：
```bash
comfy --skip-prompt tracking disable
```

## 全局选项

| 选项 | 描述 |
|------|-------------|
| `--workspace <路径>` | 指定特定的 ComfyUI 工作空间 |
| `--recent` | 使用最近使用过的工作空间 |
| `--here` | 将当前目录作为工作空间 |
| `--skip-prompt` | 跳过交互式提示（使用默认值） |
| `-v` / `--version` | 显示版本信息 |

工作空间解析优先级：
1. `--workspace`（明确指定的路径）
2. `--recent`（配置文件中指定的路径）
3. `--here`（当前工作目录）
4. `comfy set-default` 中指定的路径
5. 最近使用过的工作空间
6. `~/comfy/ComfyUI`（Linux系统）或 `~/Documents/comfy/ComfyUI`（macOS/Win系统）

## 生命周期命令

### `comfy install`

下载并安装 ComfyUI + ComfyUI-Manager。

```bash
comfy install                    # interactive GPU selection
comfy install --nvidia
comfy install --amd              # ROCm (Linux)
comfy install --m-series         # Apple Silicon (MPS)
comfy install --cpu              # CPU only (slow)
comfy install --fast-deps        # use uv for deps
comfy install --skip-manager     # skip ComfyUI-Manager
```

| 选项 | 描述 |
|--------|-------------|
| `--nvidia` / `--amd` / `--m-series` / `--cpu` | GPU类型 |
| `--cuda-version` | 11.8、12.1、12.4、12.6、12.8、12.9、13.0 |
| `--rocm-version` | 6.1、6.2、6.3、7.0、7.1 |
| `--fast-deps` | 基于uv的依赖解析方式 |
| `--skip-manager` | 跳过ComfyUI-Manager的安装 |
| `--skip-torch-or-directml` | 跳过PyTorch的安装 |
| `--version <ver>` | `0.2.0`、`latest`、`nightly` |
| `--commit <hash>` | 安装指定版本的提交内容 |
| `--pr "#1234"` | 从某个PR中安装版本 |
| `--restore` | 恢复已有安装的依赖项 |

### `comfy launch`

```bash
comfy launch                                   # foreground :8188
comfy launch --background                      # background daemon
comfy launch -- --listen 0.0.0.0               # LAN-accessible
comfy launch -- --port 8190                    # custom port
comfy launch -- --cpu                          # force CPU mode
comfy launch -- --lowvram                      # 6 GB cards
comfy launch --background -- --listen 0.0.0.0 --port 8190
```

`--` 之后的常用附加参数包括：`--listen`、`--port`、`--cpu`、`--lowvram`、`--novram`、`--fp16-vae`、`--force-fp32` 以及 `--disable-cuda-malloc`。

### `comfy stop`

```bash
comfy stop
```

### `comfy run`

将原始的工作流 JSON 文件提交给正在运行的服务器。该功能**功能有限**——不支持参数注入，也不支持结构化输出下载。如需为智能体使用此功能，请改用 `scripts/run_workflow.py`。

```bash
comfy run --workflow workflow_api.json
comfy run --workflow workflow_api.json --host 10.0.0.5 --port 8188
comfy run --workflow workflow_api.json --timeout 300 --wait
```

### `comfy which` 命令

```bash
comfy which          # show targeted workspace
comfy --recent which
```

### `comfy set-default` 命令

```bash
comfy set-default /path/to/ComfyUI
comfy set-default /path/to/ComfyUI --launch-extras="--listen 0.0.0.0"
```

### `comfy update` 命令

```bash
comfy update               # update ComfyUI core
comfy node update all      # update all custom nodes
```

## `comfy node` — 自定义节点管理

所有节点操作在底层均通过 ComfyUI-Manager（`cm-cli`）来实现。

```bash
comfy node show installed              # list installed
comfy node show enabled                # list enabled
comfy node show all                    # all available in registry
comfy node simple-show installed       # compact list

comfy node install comfyui-impact-pack
comfy node install <name> --uv-compile # ComfyUI-Manager v4.1+ unified resolver
comfy node uninstall <name>
comfy node update <name> | all
comfy node enable <name>
comfy node disable <name>
comfy node fix <name>                  # fix broken deps

comfy node install-deps --workflow=workflow.json
comfy node deps-in-workflow --workflow=w.json --output=deps.json

comfy node save-snapshot
comfy node restore-snapshot <file>

comfy node bisect start                # binary-search a culprit node
comfy node bisect good
comfy node bisect bad
comfy node bisect reset
```

### 依赖解析选项

| 标志 | 描述 |
|------|-------------|
| `--fast-deps` | comfy-cli 内置的 uv 解析器 |
| `--uv-compile` | ComfyUI-Manager v4.1+ 统一解析器（推荐） |
| `--no-deps` | 跳过依赖安装 |

将 `uv-compile` 设为默认值：`comfy manager uv-compile-default true`

---

## `comfy model` — 模型管理

```bash
comfy model list
comfy model list --relative-path models/checkpoints

comfy model download --url <URL>
comfy model download --url <URL> --relative-path models/loras
comfy model download --url <URL> --filename custom_name.safetensors

comfy model remove                     # interactive
comfy model remove --relative-path models/checkpoints --model-names "model.safetensors"
```

| 选项 | 描述 |
|--------|-------------|
| `--url` | 下载地址（CivitAI、HuggingFace 或直接链接） |
| `--relative-path` | 工作区内的子目录路径（例如 `models/checkpoints`） |
| `--filename` | 自定义保存文件名 |
| `--set-civitai-api-token` | 保存 CivitAI 访问令牌 |
| `--set-hf-api-token` | 保存 HuggingFace 访问令牌 |
| `--downloader` | 下载器，可选 `httpx`（默认）或 `aria2` |

标准模型目录结构：
```
ComfyUI/models/
├── checkpoints/        # Full model files
├── loras/              # LoRA adapters
├── vae/                # VAE models
├── controlnet/         # ControlNet models
├── clip/               # CLIP / T5 text encoders
├── clip_vision/        # CLIP vision encoders
├── upscale_models/     # ESRGAN / SwinIR / etc.
├── embeddings/         # Textual inversion embeddings
├── unet/               # Standalone UNet weights
├── diffusion_models/   # Flux / SD3 / Wan diffusion models
├── animatediff_models/ # AnimateDiff motion modules
├── ipadapter/          # IPAdapter weights
└── style_models/       # Style adapters
```

## `comfy manager` — ComfyUI 管理器设置

```bash
comfy manager disable               # disable Manager completely
comfy manager enable-gui            # enable new GUI
comfy manager disable-gui           # API-only
comfy manager enable-legacy-gui     # legacy GUI
comfy manager uv-compile-default true   # make --uv-compile the default
comfy manager clear                 # clear startup action
```

## `comfy pr-cache` — 前端 Pull Request 缓存功能

```bash
comfy pr-cache list
comfy pr-cache clean
comfy pr-cache clean 456
```

缓存有效期为7天，最多可存储10个构建版本。

---

## 配置

| 操作系统 | 路径 |
|----|------|
| Linux | `~/.config/comfy-cli/config.ini` |
| macOS | `~/Library/Application Support/comfy-cli/config.ini` |
| Windows | `~/AppData/Local/comfy-cli/config.ini` |

存储内容包括：默认工作区、最近使用的工作区、后台服务器进程ID、API令牌、管理器图形界面模式以及启动附加参数。

## 资源发现

自定义节点注册表：
- https://registry.comfy.org/

模型浏览平台：
- https://huggingface.co/models
- https://civitai.com（部分内容包含不适宜公开的内容；许多模型需要API令牌才能访问）
- https://comfyworkflows.com（社区分享的工作流）
