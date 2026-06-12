# ComfyUI 工作流 JSON 格式

## 两种格式——仅 API 格式可被执行

对于 `/api/prompt` 接口以及该技能中的所有脚本，都必须使用**API 格式**。
Web UI 还会生成一种用于可视化编辑的“编辑器格式”，但**无法**直接提交。

### API 格式

顶层键为字符串形式的节点 ID。每个节点都包含 `class_type` 和 `inputs` 属性：

```json
{
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 156680208700286,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "_meta": {"title": "KSampler"}
  },
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}
  }
}
```

**检测方式：** 每个顶层值均包含 `class_type`。该技能通过 `_common.is_api_format()` 函数来执行此项检测。

### 编辑器格式（不可直接执行）

该格式包含用于表示可视化图的 `nodes[]` 和 `links[]` 数组。如需转换，可在 ComfyUI 的网页界面中选择 **Workflow → Export (API)**（新版界面）或“Save (API Format)”按钮（旧版界面）。

**检测方式：** 顶层结构包含 `"nodes"` 和 `"links"` 两个键。

## 输入项：字面值与链接

```json
"inputs": {
  "text": "a cat",         // literal — modifiable
  "seed": 42,              // literal — modifiable
  "clip": ["4", 1]         // link — wiring; do NOT overwrite
}
```

链接为长度为2的数组，格式为`[upstream_node_id, output_slot]`。该技能的参数注入器会拒绝用字面值直接覆盖此类链接（此时会记录警告并跳过该操作）。

## 常见节点类型及其可控制参数

完整的参数列表位于`scripts/_common.py`文件中，包括`PARAM_PATTERNS`和`MODEL_LOADERS`部分。重点内容如下：

### 文本提示词

| 节点类别 | 关键字段 |
|----------|----------|
| `CLIPTextEncode` | `text` |
| `CLIPTextEncodeSDXL` | `text_g`, `text_l`, `width`, `height` |
| `CLIPTextEncodeFlux` | `clip_l`, `t5xxl`, `guidance` |

为区分正样本与负样本，该技能会通过Reroute/Primitive节点追溯到源节点`CLIPTextEncode`，并依据 `_meta.title` 中的关键词（如“negative”、“neg”、“anti”）来判断。

### 抽样过程

| 节点类别 | 关键字段 |
|----------|----------|
| `KSampler` | `seed`, `steps`, `cfg`, `sampler_name`, `scheduler`, `denoise` |
| `KSamplerAdvanced` | `noise_seed`, `steps`, `cfg`, `start_at_step`, `end_at_step` |
| `SamplerCustom` | `noise_seed`, `cfg`, `sampler`, `sigmas` |
| `SamplerCustomAdvanced` | 通过RandomNoise输入获取`noise_seed` |
| `RandomNoise` | `noise_seed` |
| `BasicScheduler` | `steps`, `scheduler`, `denoise` |
| `KSamplerSelect` | `sampler_name` |
| `BasicGuider` / `CFGGuider` | `cfg` |
| `ModelSamplingFlux` | `max_shift`, `base_shift`, `width`, `height` |
| `SDTurboScheduler` | `steps`, `denoise` |

### 潜在空间/维度参数

| 节点类别 | 关键字段 |
|----------|----------|
| `EmptyLatentImage` | `width`, `height`, `batch_size` |
| `EmptySD3LatentImage` | `width`, `height`, `batch_size` |
| `EmptyHunyuanLatentVideo` | `width`, `height`, `length`, `batch_size` |
| `EmptyMochiLatentVideo` | `width`, `height`, `length`, `batch_size` |
| `EmptyLTXVLatentVideo` | `width`, `height`, `length`, `batch_size` |

### 模型加载

| 节点类别 | 关键字段 | 文件夹路径 |
|----------|----------|------------|
| `CheckpointLoaderSimple` | `ckpt_name` | `checkpoints` |
| `LoraLoader` | `lora_name`, `strength_model`, `strength_clip` | `loras` |
| `LoraLoaderModelOnly` | `lora_name`, `strength_model` | `loras` |
| `VAELoader` | `vae_name` | `vae` |
| `ControlNetLoader` | `control_net_name` | `controlnet` |
| `CLIPLoader` | `clip_name` | `clip` |
| `DualCLIPLoader` | `clip_name1`, `clip_name2` | `clip` |
| `TripleCLIPLoader` | `clip_name1/2/3` | `clip` |
| `UNETLoader` | `unet_name` | `unet` |
| `DiffusionModelLoader` | `model_name` | `diffusion_models` |
| `UpscaleModelLoader` | `model_name` | `upscale_models` |
| `IPAdapterModelLoader` | `ipadapter_file` | `ipadapter` |
| `ADE_AnimateDiffLoaderWithContext` | `model_name`, `motion_scale` | `animatediff_models` |

### 图像输入/输出

| 节点类别 | 关键字段 |
|----------|----------|
| `LoadImage` | `image`（上传后的服务器端文件名） |
| `LoadImageMask` | `image`, `channel`（`red` / `green` / `blue` / `alpha`） |
| `VAEEncode` / `VAEDecode` | 无可控制字段 |
| `VAEEncodeForInpaint` | `grow_mask_by` |
| `SaveImage` | `filename_prefix` |
| `VHS_VideoCombine` | `frame_rate`, `format`, `filename_prefix`, `loop_count`, `pingpong` |

### ControlNet

| 节点类别 | 关键字段 |
|----------|----------|
| `ControlNetApply` | `strength` |
| `ControlNetApplyAdvanced` | `strength`, `start_percent`, `end_percent` |

### IPAdapter（社区插件 `comfyui_ipadapter_plus`）

| 节点类别 | 关键字段 |
|----------|----------|
| `IPAdapterAdvanced` | `weight`, `start_at`, `end_at` |
| `IPAdapter` | `weight` |

### 嵌入向量（用于提示词字符串中）

ComfyUI会扫描提示词文本，查找`embedding:NAME`这样的语法结构。该技能的`_common.iter_embedding_refs()`函数会将这些嵌入向量作为模型依赖项提取出来。

```text
"a beautiful cat, embedding:goodvibes:1.2, embedding:art-style"
```

`extract_schema.py`与`check_deps.py`会将这些问题分别显示在`embedding_dependencies`和`missing_embeddings`中。

## 参数注入模式

```python
import json, copy

with open("workflow_api.json") as f:
    workflow = json.load(f)

wf = copy.deepcopy(workflow)
wf["6"]["inputs"]["text"] = "a beautiful sunset"
wf["7"]["inputs"]["text"] = "ugly, blurry"
wf["3"]["inputs"]["seed"] = 42
wf["3"]["inputs"]["steps"] = 30
wf["5"]["inputs"]["width"] = 1024
wf["5"]["inputs"]["height"] = 1024
```

`scripts/extract_schema.py` 负责自动识别哪些节点 ID/字段对应于哪些面向用户的参数。该脚本会返回一个 `parameters` 字典，`run_workflow.py` 会读取此字典并使用 `--args` 指定的值进行填充。

## 可控参数的识别方法（启发式规则）

对于未知的工作流：

1. **提示词文本** — 任何形式的 `CLIPTextEncode.text`。可通过从 `KSampler.positive` / `.negative` 回溯连接关系来明确区分（不可仅依赖元标题）。
2. **种子值** — `KSampler.seed` / `KSamplerAdvanced.noise_seed` / `RandomNoise.noise_seed`。
3. **尺寸** — `Empty*LatentImage.width/height`（数值必须是 8 的倍数）。
4. **迭代步数 / CFG 值** — `KSampler.steps`、`KSampler.cfg`。通常迭代步数为 20–50，CFG 值为 5–15（Flux 模型使用引导参数而非 CFG 值）。
5. **模型 / 检查点文件** — `CheckpointLoaderSimple.ckpt_name`。文件名必须与已安装的文件完全一致。
6. **LoRA 参数** — `LoraLoader.lora_name`、`.strength_model`。
7. **用于 img2img / inpaint 操作的图像** — `LoadImage.image`，即上传后的服务器端文件名。
8. **去噪强度** — `KSampler.denoise`，取值范围为 0.0–1.0：1.0 表示忽略输入图像，0.0 表示原样输出。对于 img2img 操作，最佳值为 0.4–0.7。

## 输出节点

输出结果由以下类型的节点生成。该技能的 `OUTPUT_NODES` 集合还会扩展包含常见的社区插件提供的节点。

| 节点类型 | 输出键 | 内容 |
|----------|--------|------|
| `SaveImage` | `images` | 包含 `{filename, subfolder, type}` 的列表 |
| `PreviewImage` | `images` | 临时预览版本（不会被保存） |
| `VHS_VideoCombine` | `gifs`（旧版本）或 `videos`/`video`（新版本云端服务） | 视频文件引用 |
| `SaveAudio` | `audio` | 音频文件引用 |
| `SaveAnimatedWEBP` / `SaveAnimatedPNG` | `images` | 动画图像 |
| `Save3D` | `3d` | 3D 资产引用 |

执行完成后，可从本地路径 `/history/{prompt_id}` 或云端路径 `/api/jobs/{prompt_id}` 下载输出结果，路径结构为 `outputs` → `{node_id}` → `{key}`。

## 包装格式的处理

某些保存的 JSON 文件会将工作流信息封装在 `"prompt"` 键下（其结构与 `/api/prompt` 的请求数据格式一致）。该技能内置的 `_common.unwrap_workflow()` 函数可处理此类情况，支持以下任意一种格式：

- 原始 API 格式：`{"3": {...}, "4": {...}}`
- 包装格式：`{"prompt": {"3": {...}}, "client_id": "..."}`

对于采用编辑器格式的文件，该函数会给出明确的错误提示并指示用户重新导出。
