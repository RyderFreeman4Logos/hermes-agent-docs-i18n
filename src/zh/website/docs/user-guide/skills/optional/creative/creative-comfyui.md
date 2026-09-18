---
title: "Comfyui — Generate images, video, and audio via diffusion workflows"
sidebar_label: "Comfyui"
description: "Generate images, video, and audio via diffusion workflows"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Comfyui

通过扩散模型工作流生成图像、视频、音频及 3D 内容。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/comfyui` 安装 |
| 路径 | `optional-skills/creative\comfyui` |
| 版本 | `5.1.0` |
| 开发者 | ['kshitijk4poor', 'alt-glitch', 'purzbeats'] |
| 许可协议 | MIT |
| 支持平台 | macos、linux、windows |
| 标签 | `comfyui`、`图像生成`、`stable-diffusion`、`flux`、`sd3`、`wan-video`、`hunyuan-video`、`创意`、`生成式AI`、`视频生成` |
| 相关技能 | [`stable-diffusion`](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) |

## 参考：完整的 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# ComfyUI

利用官方的 `comfy-cli` 进行设置与生命周期管理，并通过直接的 REST/WebSocket API 执行工作流，从而借助 ComfyUI 生成图像、视频、音频及 3D 内容。

## 该技能包含的内容

**参考文档（`references/`）：**

- `official-cli.md` — 包含所有带参数的 `comfy ...` 命令说明  
- `rest-api.md` — REST 与 WebSocket 接口（本地及云端）及数据格式规范  
- `workflow-format.md` — API 格式的 JSON 文件结构、常用节点类型及参数映射规则  
- `template-integrity.md` — 将 `comfyui-workflow-templates` 从编辑器格式转换为 API 格式：路径重定向处理、带点的动态输入键名（如 `values.a`、`resize_type.width`）、云端使用注意事项（302 重定向、免费套餐单次仅可运行 1 个任务、1080p 分辨率对应的显存限制），以及兼容 Discord 的 ffmpeg 合成功能。该文档由 [@purzbeats](https://github.com/purzbeats) 撰写。每当从官方模板开始使用时，请务必查阅此文档。  

**脚本文件（`scripts/`）：**

| 脚本 | 功能说明 |
|------|----------|
| `_common.py` | 公共模块，包含HTTP处理、云路由功能以及节点目录管理（不可直接运行） |
| `hardware_check.py` | 检测GPU/VRAM/磁盘性能 → 提供在本地运行还是使用Comfy Cloud的推荐方案 |
| `comfyui_setup.sh` | 执行硬件检测，同时安装comfy-cli与ComfyUI，完成启动并验证运行状态 |
| `extract_schema.py` | 读取工作流文件 → 列出所有可调节参数及模型依赖项 |
| `check_deps.py` | 对比工作流要求与当前服务器配置 → 显示缺失的节点或模型 |
| `auto_fix_deps.py` | 先执行check_deps检查，再自动运行`comfy node install`/`comfy model download`命令安装缺失组件 |
| `run_workflow.py` | 注入参数、提交任务、实时监控执行进度，并通过HTTP或WebSocket下载输出结果 |
| `run_batch.py` | 支持对同一工作流进行多次迭代运行，可根据用户套餐支持并行处理 |
| `ws_monitor.py` | 实时WebSocket监控工具，可查看任务执行状态及实时进度 |
| `health_check.py` | 集成检查清单，用于验证comfy-cli、服务器、模型以及整体系统的运行状况 |
| `fetch_logs.py` | 根据指定的prompt_id获取对应的错误堆栈信息或状态消息 |

**示例工作流（位于`workflows/`目录）：** SD 1.5、SDXL、Flux Dev、SDXL img2img、SDXL inpaint、ESRGAN upscale、AnimateDiff视频生成、Wan T2V。详情请参阅`workflows/README.md`。

## 适用场景

- 用户希望使用 Stable Diffusion、SDXL、Flux、SD3 等模型生成图像。  
- 用户想要运行特定的 ComfyUI 工作流文件。  
- 用户希望串联多个生成步骤（如 txt2img → 上采样 → 人脸修复）。  
- 用户需要使用 ControlNet、抠图功能、img2img 或其他高级处理流程。  
- 用户希望管理 ComfyUI 队列、查看模型信息或安装自定义节点。  
- 用户希望通过 AnimateDiff、Hunyuan、Wan、AudioCraft 等工具实现视频/音频/3D 内容的生成。  

## 架构：双层结构  

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────┐
│ Layer 1: comfy-cli (official lifecycle tool)        │
│   Setup, server lifecycle, custom nodes, models     │
│   → comfy install / launch / stop / node / model    │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│ Layer 2: REST/WebSocket API + skill scripts         │
│   Workflow execution, param injection, monitoring   │
│   POST /api/prompt, GET /api/view, WS /ws           │
│   → run_workflow.py, run_batch.py, ws_monitor.py    │
└─────────────────────────────────────────────────────┘
```
**为何需要两层架构？** 官方 CLI 在安装和服务器管理方面表现优异，但在工作流执行方面的支持十分有限。REST/WS API 则填补了这一空白——这些接口能够处理参数注入、执行监控以及输出下载等功能，而这些都是 CLI 所不具备的。

## 快速入门

### 检测环境

```bash
# What's available?
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: installed"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "server: running"

# Can this machine run ComfyUI locally? (GPU/VRAM/disk check)
python scripts/hardware_check.py
```

如果尚未安装任何组件，请参阅下方的**设置与入门指南**——但务必先执行硬件检测。

### 一键健康检查

```bash
python scripts/health_check.py
# → JSON: comfy_cli on PATH? server reachable? at least one checkpoint? smoke-test passes?
```

## 核心工作流程

### 第一步：获取 API 格式的工作流 JSON 文件

工作流必须采用 API 格式（每个节点均包含 `class_type` 属性）。这些工作流来源包括：

- ComfyUI 网页界面 → **Workflow → Export (API)**（新版界面）或旧版界面中的“Save (API Format)”按钮；
- 该技能自带的 `workflows/` 目录（可直接运行的示例）；
- 社区下载的资源（如 civitai、Reddit、Discord 等平台），这类文件通常为编辑器格式，需先导入 ComfyUI 再重新导出。

编辑器格式（以顶层 `nodes` 和 `links` 数组的形式存在）**无法直接执行**。相关脚本会检测到这一点，并提示用户需要重新导出。

### 第二步：查看哪些参数可被控制

```bash
python scripts/extract_schema.py workflow_api.json --summary-only
# → {"parameter_count": 12, "has_negative_prompt": true, "has_seed": true, ...}

python scripts/extract_schema.py workflow_api.json
# → full schema with parameters, model deps, embedding refs
```

### 第3步：带参数运行

```bash
# Local (defaults to http://127.0.0.1:8188)
python scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": -1, "steps": 30}' \
  --output-dir ./outputs

# Cloud (export API key once; uses correct /api routing automatically)
export COMFY_CLOUD_API_KEY="comfyui-..."
python scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "..."}' \
  --host https://cloud.comfy.org \
  --output-dir ./outputs

# Real-time progress via WebSocket (requires `pip install websocket-client`)
python scripts/run_workflow.py \
  --workflow flux_dev.json \
  --args '{"prompt": "..."}' \
  --ws

# img2img / inpaint: pass --input-image to upload + reference automatically
python scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}'

# Batch / sweep: 8 random seeds, parallel up to cloud tier limit
python scripts/run_batch.py \
  --workflow sdxl.json \
  --args '{"prompt": "abstract"}' \
  --count 8 --randomize-seed --parallel 3 \
  --output-dir ./outputs/batch
```

当 `seed` 参数设置为 `-1`（或使用 `--randomize-seed` 选项省略该参数）时，每次运行都会生成一个全新的随机种子。

### 第 4 步：展示结果

脚本会向标准输出输出 JSON 格式的内容，详细说明每个输出文件的信息：

```json
{
  "status": "success",
  "prompt_id": "abc-123",
  "outputs": [
    {"file": "./outputs/sdxl_00001_.png", "node_id": "9",
     "type": "image", "filename": "sdxl_00001_.png"}
  ]
}
```

## 决策树

| User says | Tool | Command |
|-----------|------|---------|
| **Lifecycle (use comfy-cli)** | | |
| "install ComfyUI" | comfy-cli | `bash scripts/comfyui_setup.sh` |
| "start ComfyUI" | comfy-cli | `comfy launch --background` |
| "stop ComfyUI" | comfy-cli | `comfy stop` |
| "install X node" | comfy-cli | `comfy node install <name>` |
| "download X model" | comfy-cli | `comfy model download --url <url> --relative-path models/checkpoints` |
| "list installed models" | comfy-cli | `comfy model list` |
| "list installed nodes" | comfy-cli | `comfy node show installed` |
| **Execution (use scripts)** | | |
| "is everything ready?" | script | `health_check.py` (optionally with `--workflow X --smoke-test`) |
| "what can I change in this workflow?" | script | `extract_schema.py W.json` |
| "check if W's deps are met" | script | `check_deps.py W.json` |
| "fix missing deps" | script | `auto_fix_deps.py W.json` |
| "generate an image" | script | `run_workflow.py --workflow W --args '{...}'` |
| "use this image" (img2img) | script | `run_workflow.py --input-image image=./x.png ...` |
| "8 variations with random seeds" | script | `run_batch.py --count 8 --randomize-seed ...` |
| "show me live progress" | script | `ws_monitor.py --prompt-id <id>` |
| "fetch the error from job X" | script | `fetch_logs.py <prompt_id>` |
| **Direct REST** | | |
| "what's in the queue?" | REST | `curl http://HOST:8188/queue` (local) or `--host https://cloud.comfy.org` |
| "cancel that" | REST | `curl -X POST http://HOST:8188/interrupt` |
| "free GPU memory" | REST | `curl -X POST http://HOST:8188/free` |

## 设置与入门指南

当用户请求设置 ComfyUI 时，**首要步骤是询问他们希望使用 Comfy Cloud（托管服务，无需安装，仅需 API 密钥）还是本地模式（在自身设备上安装 ComfyUI）**。在得到答复之前，请勿开始运行任何安装命令或进行硬件检测。

**官方文档：** https://docs.comfy.org/installation  
**CLI 文档：** https://docs.comfy.org/comfy-cli/getting-started  
**云服务文档：** https://docs.comfy.org/get_started/cloud  
**云服务 API：** https://docs.comfy.org/development/cloud/overview  

### 第 0 步：确认是本地模式还是云服务模式（务必先问此问题）

推荐对话脚本：

> “您希望在自己的设备上本地运行 ComfyUI，还是使用 Comfy Cloud？
>
> - **Comfy Cloud** — 依托 RTX 6000 Pro GPU 运行，所有常用模型均已预装，无需额外设置。使用时需要 API 密钥（实际运行工作流需订阅付费服务；免费套餐仅支持读取功能）。如果您没有性能足够的 GPU，此选项较为合适。
> - **本地模式** — 免费使用，但您的设备必须满足以下硬件要求：
>   - 配备 **≥6 GB 显存** 的 NVIDIA GPU（SDXL 模型需 ≥8 GB，Flux/video 模型需 ≥12 GB），或
>   - 支持 ROCm 的 AMD GPU（仅限 Linux 系统），或
>   - 配备 **≥16 GB 统一内存** 的 Apple Silicon Mac（M1+ 系列，建议 ≥32 GB）。
>   - Intel Mac 以及无 GPU 的设备无法使用本地模式——请选择云服务方案。
>
> 您希望选择哪种方式？”

后续处理流程：

- **选择云服务** → 直接进入 **路径 A**。
- **选择本地模式** → 先进行硬件检测，再根据检测结果从路径 B–E 中选择相应步骤。
- **尚未决定** → 先执行硬件检测，由检测结果决定后续操作。
### 第一步：验证硬件（仅当用户选择本地运行时需要执行）

```bash
python scripts/hardware_check.py --json
# Optional: also probe `torch` for actual CUDA/MPS:
python scripts/hardware_check.py --json --check-pytorch
```

| 判定结果    | 含义                                                                 | 操作建议 |
|------------|----------------------------------------------------------------------|----------|
| `ok`       | ≥8 GB 独立显存，或 Apple Silicon 平台的 ≥32 GB 统一显存                 | 可本地安装——使用报告中的 `comfy_cli_flag` 参数 |
| `marginal` | SD1.5 模型可用；SDXL 模型运行勉强；Flux及视频相关模型几乎无法使用   | 轻量级工作流可本地运行，否则请选择**方案A：云端部署** |
| `cloud`    | 无可用 GPU，显存＜6 GB，Apple Silicon 平台的统一显存＜16 GB，或使用 Intel Mac 及 Rosetta Python 环境 | 除非用户明确要求本地安装，否则**应切换至云端部署** |

该脚本还会显示 `wsl: true`（通过 NVIDIA passthrough 技术在 WSL2 环境中运行）以及 `rosetta: true`（在 Apple Silicon 平台上使用 x86_64 版 Python——此类系统需重新安装为 ARM64 版本）。

若判定结果为 `cloud`，但用户仍希望本地安装，则不应默默继续操作。应原样显示 `notes` 数组中的内容，并询问用户是选择(a)切换至云端，还是(b)强行进行本地安装（在现代模型上这将导致内存不足或运行速度极慢）。

### 选择安装路径

首先进行硬件检测。只有当用户已明确告知其硬件配置时，才使用下表中的建议作为替代方案。

| 使用场景 | 推荐方案 |
|-----------|----------|
| 硬件检测结果为 `verdict: cloud` | **方案 A：Comfy Cloud** |
| 无 GPU 或希望先试用而不做长期投入 | **方案 A：Comfy Cloud** |
| Windows 系统 + NVIDIA 显卡 + 非技术用户 | **方案 B：ComfyUI 桌面版** |
| Windows 系统 + NVIDIA 显卡 + 技术用户 | **方案 C：便携版** 或 **方案 D：comfy-cli** |
| Linux 系统 + 任意 GPU | **方案 D：comfy-cli**（最简单） |
| macOS 系统 + Apple Silicon 芯片 | **方案 B：桌面版** 或 **方案 D：comfy-cli** |
| 无界面环境/服务器/CI 环境/Agent 环境 | **方案 D：comfy-cli** |

对于完全自动化的流程（硬件检测 → 安装 → 启动 → 验证）：

```bash
bash scripts/comfyui_setup.sh
# Or with overrides:
bash scripts/comfyui_setup.sh --m-series --port=8190 --workspace=/data/comfy
```

它会在内部运行 `hardware_check.py`，若检测结果为“云端”则拒绝进行本地安装（除非使用了 `--force-cloud-override` 参数），同时会选择合适的 `comfy-cli` 参数，并优先使用 `pipx`/`uvx` 而非全局的 `pip`，以避免污染系统 Python 环境。

---

### 方案 A：Comfy Cloud（无需本地安装）

适用于没有高性能 GPU 或希望无需任何配置的用户。服务运行在 RTX 6000 Pro 上。

**文档链接：** https://docs.comfy.org/get_started/cloud

1. 在 https://comfy.org/cloud 注册账号
2. 在 https://platform.comfy.org/login 处生成 API 密钥
3. 设置该密钥：
   ```bash
   export COMFY_CLOUD_API_KEY="your-comfyui-key"
   ```
4. 运行工作流：
   ```bash
   python scripts/run_workflow.py \
     --workflow workflows/flux_dev_txt2img.json \
     --args '{"prompt": "..."}' \
     --host https://cloud.comfy.org \
     --output-dir ./outputs
   ```

**价格信息：** https://www.comfy.org/cloud/pricing  
**并发任务数量：** 免费版/标准版为1个，创作者版为3个，专业版为5个。免费套餐适用。  
**无法通过API运行工作流**——仅可浏览模型。若需使用 `/api/prompt`、`/api/upload/*`、`/api/view` 等接口，则必须订阅付费服务。

---

### 方案B：ComfyUI桌面版（Windows / macOS）

专为非技术用户设计的单键安装程序，目前处于测试阶段。

**文档说明：** https://docs.comfy.org/installation/desktop  
- **Windows（NVIDIA显卡）：** https://download.comfy.org/windows/nsis/x64  
- **macOS（Apple Silicon芯片）：** https://comfy.org  

桌面版**不支持Linux系统**——请选择方案D。

---

### 方案C：ComfyUI便携版（仅Windows系统）

**文档说明：** https://docs.comfy.org/installation/comfyui_portable_windows  

可从 https://github.com/comfyanonymous/ComfyUI/releases 下载文件，解压后运行 `run_nvidia_gpu.bat`。如需更新，则执行 `update/update_comfyui_stable.bat`。

---

### 方案D：comfy-cli（所有平台适用——推荐用于Agent场景）

官方命令行工具是实现无界面/自动化部署的最佳选择。

**文档说明：** https://docs.comfy.org/comfy-cli/getting-started  

#### 安装comfy-cli

```bash
# Recommended:
pipx install comfy-cli
# Or use uvx without installing:
uvx --from comfy-cli comfy --help
# Or (if pipx/uvx unavailable):
pip install --user comfy-cli
```

以非交互方式禁用分析功能：
```bash
comfy --skip-prompt tracking disable
```

#### 安装 ComfyUI

```bash
comfy --skip-prompt install --nvidia              # NVIDIA (CUDA)
comfy --skip-prompt install --amd                 # AMD (ROCm, Linux)
comfy --skip-prompt install --m-series            # Apple Silicon (MPS)
comfy --skip-prompt install --cpu                 # CPU only (slow)
comfy --skip-prompt install --nvidia --fast-deps  # uv-based dep resolution
```

默认路径为：Linux系统下为`~/comfy/ComfyUI`，macOS/Windows系统下为`~/Documents/comfy/ComfyUI`。如需更改路径，可使用命令`comfy --workspace /custom/path install`进行指定。

#### 启动 / 验证

```bash
comfy launch --background                       # background daemon on :8188
comfy launch -- --listen 0.0.0.0 --port 8190    # LAN-accessible custom port
curl -s http://127.0.0.1:8188/system_stats      # health check
```

### 路径 E：手动安装（高级版/不支持的硬件）

适用于 Ascend NPU、Cambricon MLU、Intel Arc 以及其他不受支持的设备。

**文档链接：** https://docs.comfy.org/installation/manual_install

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

### 安装完成后：下载模型

```bash
# SDXL (general purpose, ~6.5 GB)
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5 (lighter, ~4 GB, good for 6 GB cards)
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8 (smaller variant, ~12 GB)
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI (set token first):
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```

列出已安装的节点：`comfy model list`。

### 安装完成后：安装自定义节点

```bash
comfy node install comfyui-impact-pack             # popular utility pack
comfy node install comfyui-animatediff-evolved     # video generation
comfy node install comfyui-controlnet-aux          # ControlNet preprocessors
comfy node install comfyui-essentials              # common helpers
comfy node update all
comfy node install-deps --workflow=workflow.json   # install everything a workflow needs
```

### 安装完成后：验证操作

```bash
python scripts/health_check.py
# → comfy_cli on PATH? server reachable? checkpoints? smoke test?

python scripts/check_deps.py my_workflow.json
# → are this workflow's nodes/models/embeddings installed?

python scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```

## 图像上传（img2img / 修复绘图）

最简单的方法是使用 `run_workflow.py` 并结合 `--input-image` 参数：

```bash
python scripts/run_workflow.py \
  --workflow workflows/sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it cyberpunk", "denoise": 0.6}'
```

该标志会上传`photo.png`文件，随后将其服务器端的文件名注入到名为`image`的任意架构参数中。对于图像修复任务，则需同时传入这两个参数。

```bash
python scripts/run_workflow.py \
  --workflow workflows/sdxl_inpaint.json \
  --input-image image=./photo.png \
  --input-image mask_image=./mask.png \
  --args '{"prompt": "fill with flowers"}'
```

通过 REST 接口手动上传：
```bash
curl -X POST "http://127.0.0.1:8188/upload/image" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
# Returns: {"name": "photo.png", "subfolder": "", "type": "input"}

# Cloud equivalent:
curl -X POST "https://cloud.comfy.org/api/upload/image" \
  -H "X-API-Key: $COMFY_CLOUD_API_KEY" \
  -F "image=@photo.png" -F "type=input" -F "overwrite=true"
```

## 云端特定设置

- **基础网址：** `https://cloud.comfy.org`
- **认证方式：** 使用 `X-API-Key` 请求头（WebSocket 则使用 `?token=KEY`）
- **API 密钥：** 仅需设置一次 `$COMFY_CLOUD_API_KEY`，脚本便会自动读取该密钥
- **输出文件下载：** `/api/view` 会返回一个指向带签名 URL 的 302 状态跳转；脚本会跟随该链接，并在从存储后端获取数据前移除 `X-API-Key`（从而避免 API 密钥泄露至 S3/CloudFront）
- **与本地 ComfyUI 的端点差异：**
  - `/api/object_info`、`/api/queue`、`/api/userdata` —— 免费套餐用户无法访问，会返回 **403 错误**；仅付费用户可使用。
  - 云端版本中 `/history` 已更名为 `/history_v2`，脚本会自动进行路由跳转。
  - 云端版本中 `/models/<folder>` 已更名为 `/experiment/models/<folder>`，脚本同样会自动处理路由。
  - WebSocket 连接中当前的 `clientId` 参数会被忽略——同一用户的所有连接都会收到相同的广播信息，需在客户端通过 `prompt_id` 进行过滤。
  - 上传文件时虽支持 `subfolder` 参数，但实际会被忽略——云端采用扁平化的命名空间结构。
- **并发任务限制：** 免费/标准套餐：1 个；创作者套餐：3 个；专业套餐：5 个。超出限额的任务会自动进入队列。如需充分利用对应套餐的并发上限，可使用 `run_batch.py --parallel N` 命令。

## 队列与系统管理

```bash
# Local
curl -s http://127.0.0.1:8188/queue | python -m json.tool
curl -X POST http://127.0.0.1:8188/queue -d '{"clear": true}'    # cancel pending
curl -X POST http://127.0.0.1:8188/interrupt                      # cancel running
curl -X POST http://127.0.0.1:8188/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}'

# Cloud — same paths under /api/, plus:
python scripts/fetch_logs.py --tail-queue --host https://cloud.comfy.org
```

## 常见问题

1. **必须使用 API 格式** — 所有的脚本以及 `/api/prompt` 接口均要求输入符合 API 格式的流程 JSON。这些脚本会检测到编辑器格式（即顶层的 `nodes` 和 `links` 数组），并提示您通过“流程 → 导出（API）”（新版界面）或“保存（API 格式）”（旧版界面）重新导出。

2. **服务器必须处于运行状态** — 所有操作都需要一个正在运行的服务器。`comfy launch --background` 可以启动服务器，您可以通过 `curl http://127.0.0.1:8188/system_stats` 来确认服务器是否正常运行。

3. **模型名称必须完全准确** — 名称区分大小写，且必须包含文件扩展名。`check_deps.py` 会进行模糊匹配（包括带/不带扩展名以及目录前缀的情况），但流程本身必须使用标准名称。您可以使用 `comfy model list` 查看已安装的模型。

4. **缺少自定义节点** — 出现“class_type not found”错误表示有必需的节点未安装。`check_deps.py` 会提示需要安装哪个包，而 `auto_fix_deps.py` 可以自动为您完成安装。

5. **工作目录问题** — `comfy-cli` 会自动检测 ComfyUI 的工作目录。如果出现“未找到工作目录”的错误，请使用 `comfy --workspace /path/to/ComfyUI <command>` 或 `comfy set-default /path/to/ComfyUI` 来指定工作目录。

6. **云服务免费套餐的 API 限制** — 对于免费账户，`/api/prompt`、`/api/view`、`/api/upload/*` 和 `/api/object_info` 等接口都会返回 403 错误。`health_check.py` 和 `check_deps.py` 能够妥善处理这种情况，并给出明确的提示信息。

7. **视频/音频工作流的超时设置**——当输出节点为 `VHS_VideoCombine`、`SaveVideo` 等类型时会自动检测该设置；默认值从 300 秒延长至 900 秒。如需手动修改，可使用 `--timeout 1800` 参数进行指定。

8. **输出文件名中的路径遍历防护**——服务器提供的文件名会经过 `safe_path_join` 处理，从而阻止任何试图绕过 `--output-dir` 设置的路径。请始终启用此防护机制，因为使用自定义保存节点的工作流可能会生成任意路径。

9. **工作流 JSON 即为任意代码**——由于自定义节点会运行 Python 代码，因此提交未知工作流时其信任级别与执行 `eval` 函数相当。在运行之前，请务必检查来自不可信来源的工作流内容。

10. **自动随机化种子值**——在 `--args` 参数中传入 `seed: -1`（或使用 `--randomize-seed` 选项而不指定具体种子值），即可让每次运行都生成新的种子值。实际的种子值会被记录到标准错误流中。

11. **`tracking` 提示**——首次运行 `comfy` 时可能会出现关于数据统计的提示。如需跳过该交互式提示，可使用 `comfy --skip-prompt tracking disable` 命令。`comfyui_setup.sh` 脚本已自动处理了此项设置。

## 验证检查清单

可使用 `python scripts/health_check.py` 一次性运行所有检查项。也可手动逐一验证。

- [ ] `hardware_check.py` 的检测结果为 `ok`，或者用户明确选择了 Comfy Cloud  
- [ ] `comfy --version` 命令能够正常运行（或 `uvx --from comfy-cli comfy --help` 命令也可正常使用）  
- [ ] `curl http://HOST:PORT/system_stats` 命令能返回 JSON 格式的数据  
- [ ] `comfy model list` 命令能显示至少一个本地检查点，或者 `/api/experiment/models/checkpoints` 接口能返回云端模型列表  
- [ ] 工作流 JSON 文件符合 API 格式要求  
- [ ] `check_deps.py` 命令检测结果显示 `is_ready: true`（若处于云端免费套餐，则仅显示 `node_check_skipped`）  
- [ ] 使用小型工作流进行测试运行后能够成功完成，输出结果将保存在 `--output-dir` 指定的目录中
