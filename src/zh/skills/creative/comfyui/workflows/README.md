# 示例工作流

这些是针对最常见任务设计的 API 格式示例工作流。在您安装了列出的模型（或具备相应的云访问权限）后，即可通过 `scripts/run_workflow.py` 直接运行它们。

| 文件名 | 功能 | 所需模型 | 最低显存要求 |
|--------|------|----------|--------------|
| `sd15_txt2img.json` | SD 1.5 文本生成图像（512×512） | SD1.5 检查点文件，例如 `v1-5-pruned-emaonly.safetensors` | 4 GB |
| `sdxl_txt2img.json` | SDXL 文本生成图像（1024×1024） | `sd_xl_base_1.0.safetensors` | 8 GB |
| `flux_dev_txt2img.json` | Flux Dev 文本生成图像（1024×1024） | `flux1-dev.safetensors`、`t5xxl_fp16.safetensors`、`clip_l.safetensors`、`ae.safetensors` | 24 GB（或使用 `flux1-dev-fp8`） |
| `sdxl_img2img.json` | SDXL 图像生成图像 | SDXL 检查点文件 | 8 GB |
| `sdxl_inpaint.json` | SDXL 修复填充（图像+遮罩） | SDXL 检查点文件 | 8 GB |
| `upscale_4x.json` | 独立型 4 倍 ESRGAN 上采样 | `4x-UltraSharp.pth`（或任意上采样模型） | 4 GB |
| `animatediff_video.json` | AnimateDiff 文本生成视频（16 帧） | SD1.5 检查点文件、`mm_sd_v15_v2.ckpt` 动态模块 | 8 GB |
| `wan_video_t2v.json` | Wan 2.x 文本生成视频（约 33 帧） | `wan2.2_t2v_1.3B_fp16.safetensors`、`umt5_xxl_fp16.safetensors`、`wan_2.1_vae.safetensors` | 24 GB |

## 快速入门

```bash
# Run a workflow with prompt injection
python3 ../scripts/run_workflow.py \
  --workflow sdxl_txt2img.json \
  --args '{"prompt": "majestic eagle in flight", "seed": 12345, "steps": 35}' \
  --output-dir ./out

# Img2img: upload an input image first via the script's helper
python3 ../scripts/run_workflow.py \
  --workflow sdxl_img2img.json \
  --input-image image=./photo.png \
  --args '{"prompt": "make it watercolor", "denoise": 0.6}' \
  --output-dir ./out

# Cloud (set API key once)
export COMFY_CLOUD_API_KEY="comfyui-..."
python3 ../scripts/run_workflow.py \
  --workflow flux_dev_txt2img.json \
  --args '{"prompt": "a fox in a misty forest"}' \
  --host https://cloud.comfy.org \
  --output-dir ./out

# What can I tweak in this workflow?
python3 ../scripts/extract_schema.py sdxl_txt2img.json --summary-only

# Are all required models / nodes installed?
python3 ../scripts/check_deps.py wan_video_t2v.json
```

## 备注

- **修复画布遮罩**：白色像素表示“重新生成该区域”，黑色像素表示保留原状。ComfyUI的`LoadImageMask`默认读取**红色通道**；请将遮罩导出为单通道图像，或将其视为普通RGB图像，其中红色值代表强度。

- **img2img中的去噪强度**：`0.0`表示输出结果与输入完全一致，`1.0`则表示完全忽略输入。通常而言，0.4–0.7为最佳数值范围。

- **Flux Dev**的基础版本需要约24 GB的VRAM。而`flux1-dev-fp8.safetensors`版本（已在Comfy Cloud上提供）可将此需求大致减半。

- **视频处理流程**可能需要数分钟时间。该技能会自动检测视频输出节点，并将默认超时时间延长至900秒。如需手动调整，可使用`--timeout 1800`参数进行设置。

- 这些JSON文件刻意采用**API格式**（顶层键为带有`class_type`属性的节点ID），而非编辑器格式。若要在ComfyUI的网页界面中打开这些文件进行可视化编辑，请使用“Workflow → Load (API Format)”或“Workflow → Open”，然后按照提示操作。

## 云端模型名与本地模型名的区别

Comfy Cloud预装的检查点文件有时会带有`-fp16`后缀（如`v1-5-pruned-emaonly-fp16.safetensors`），而官方提供的本地下载版本则保留原始名称（如`v1-5-pruned-emaonly.safetensors`）。示例流程中使用的均为本地版本的官方命名。在云端运行时，可通过相应参数进行覆盖设置。

```bash
python3 ../scripts/run_workflow.py \
  --workflow sd15_txt2img.json \
  --args '{"ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors", "prompt": "..."}' \
  --host https://cloud.comfy.org
```

`ckpt_name`、`vae_name`、`lora_name`、`unet_name`等参数均被`extract_schema.py`定义为可调控的参数——您可以通过`comfy model list`（本地环境）或`curl /api/experiment/models/checkpoints`（云端环境）来查看已安装的模型信息。
