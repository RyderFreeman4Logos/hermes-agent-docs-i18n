# Stable Diffusion 故障排除指南

## 安装问题

### 包冲突

**错误信息**：`ImportError: cannot import name 'cached_download' from 'huggingface_hub'`

**解决方案**：
```bash
# Update huggingface_hub
pip install --upgrade huggingface_hub

# Reinstall diffusers
pip install --upgrade diffusers
```

### xFormers 安装失败

**错误信息**：`RuntimeError: CUDA error: no kernel image is available for execution`

**解决方案**：
```bash
# Check CUDA version
nvcc --version

# Install matching xformers
pip install xformers --index-url https://download.pytorch.org/whl/cu121  # For CUDA 12.1

# Or build from source
pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers
```

### Torch与CUDA版本不匹配

**错误信息**：`RuntimeError: CUDA error: CUBLAS_STATUS_NOT_INITIALIZED`

**解决方案**：
```bash
# Check versions
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"

# Reinstall PyTorch with correct CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## 内存问题

### CUDA 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存不足`

**解决方案**：

```python
# Solution 1: Enable CPU offloading
pipe.enable_model_cpu_offload()

# Solution 2: Sequential CPU offload (more aggressive)
pipe.enable_sequential_cpu_offload()

# Solution 3: Attention slicing
pipe.enable_attention_slicing()

# Solution 4: VAE slicing for large images
pipe.enable_vae_slicing()

# Solution 5: Use lower precision
pipe = DiffusionPipeline.from_pretrained(
    "model-id",
    torch_dtype=torch.float16  # or torch.bfloat16
)

# Solution 6: Reduce batch size
image = pipe(prompt, num_images_per_prompt=1).images[0]

# Solution 7: Generate smaller images
image = pipe(prompt, height=512, width=512).images[0]

# Solution 8: Clear cache between generations
import gc
torch.cuda.empty_cache()
gc.collect()
```

### 内存会随时间逐渐增长

**问题**：每进行一次生成，内存使用量都会增加

**解决方案**：
```python
import gc
import torch

def generate_with_cleanup(pipe, prompt, **kwargs):
    try:
        image = pipe(prompt, **kwargs).images[0]
        return image
    finally:
        # Clear cache after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
```

### 大模型加载失败

**错误信息**：`RuntimeError: 无法加载模型权重`

**解决方案**：
```python
# Use low CPU memory mode
pipe = DiffusionPipeline.from_pretrained(
    "large-model-id",
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16
)
```

## 生成问题

### 图像全黑

**问题**：生成的图像完全为黑色

**解决方案**：
```python
# Solution 1: Disable safety checker
pipe.safety_checker = None

# Solution 2: Check VAE scaling
# The issue might be with VAE encoding/decoding
latents = latents / pipe.vae.config.scaling_factor  # Before decode

# Solution 3: Ensure proper dtype
pipe = pipe.to(dtype=torch.float16)
pipe.vae = pipe.vae.to(dtype=torch.float32)  # VAE often needs fp32

# Solution 4: Check guidance scale
# Too high can cause issues
image = pipe(prompt, guidance_scale=7.5).images[0]  # Not 20+
```

### 噪声/静态图像

**问题**：输出内容呈现为随机噪声

**解决方案**：
```python
# Solution 1: Increase inference steps
image = pipe(prompt, num_inference_steps=50).images[0]

# Solution 2: Check scheduler configuration
pipe.scheduler = pipe.scheduler.from_config(pipe.scheduler.config)

# Solution 3: Verify model was loaded correctly
print(pipe.unet)  # Should show model architecture
```

### 图像模糊问题

**问题**：生成的图像质量较低或出现模糊现象

**解决方案**：
```python
# Solution 1: Use more steps
image = pipe(prompt, num_inference_steps=50).images[0]

# Solution 2: Use better VAE
from diffusers import AutoencoderKL
vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse")
pipe.vae = vae

# Solution 3: Use SDXL or refiner
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0"
)

# Solution 4: Upscale with img2img
upscale_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(...)
upscaled = upscale_pipe(
    prompt=prompt,
    image=image.resize((1024, 1024)),
    strength=0.3
).images[0]
```

### 提示未被正确执行

**问题**：生成的图像与提示内容不符

**解决方案**：
```python
# Solution 1: Increase guidance scale
image = pipe(prompt, guidance_scale=10.0).images[0]

# Solution 2: Use negative prompts
image = pipe(
    prompt="A red car",
    negative_prompt="blue, green, yellow, wrong color",
    guidance_scale=7.5
).images[0]

# Solution 3: Use prompt weighting
# Emphasize important words
prompt = "A (red:1.5) car on a street"

# Solution 4: Use longer, more detailed prompts
prompt = """
A bright red sports car, ferrari style, parked on a city street,
photorealistic, high detail, 8k, professional photography
"""
```

### 脸部/手部变形

**问题**：面部和手部看起来出现变形

**解决方案**：
```python
# Solution 1: Use negative prompts
negative_prompt = """
bad hands, bad anatomy, deformed, ugly, blurry,
extra fingers, mutated hands, poorly drawn hands,
poorly drawn face, mutation, deformed face
"""

# Solution 2: Use face-specific models
# ADetailer or similar post-processing

# Solution 3: Use ControlNet for poses
# Load pose estimation and condition generation

# Solution 4: Inpaint problematic areas
mask = create_face_mask(image)
fixed = inpaint_pipe(
    prompt="beautiful detailed face",
    image=image,
    mask_image=mask
).images[0]
```

## 调度器相关问题

### 调度器不兼容

**错误信息**：`ValueError: Scheduler ... is not compatible with pipeline`

**解决方案**：
```python
from diffusers import EulerDiscreteScheduler

# Create scheduler from config
pipe.scheduler = EulerDiscreteScheduler.from_config(
    pipe.scheduler.config
)

# Check compatible schedulers
print(pipe.scheduler.compatibles)
```

### 步骤数量错误

**问题**：在相同步数下，模型生成的输出质量不同

**解决方案**：
```python
# Reset timesteps explicitly
pipe.scheduler.set_timesteps(num_inference_steps)

# Check scheduler's step count
print(len(pipe.scheduler.timesteps))
```

## LoRA 相关问题

### LoRA 权重无法加载

**错误信息**：`RuntimeError: Error(s) in loading state_dict for UNet2DConditionModel`

**解决方案**：
```python
# Check weight file format
# Should be .safetensors or .bin

# Load with correct key prefix
pipe.load_lora_weights(
    "path/to/lora",
    weight_name="lora.safetensors"
)

# Try loading into specific component
pipe.unet.load_attn_procs("path/to/lora")
```

### LoRA 不影响输出结果

**问题**：无论是否使用 LoRA，生成的图像看起来都相同。

**解决方案**：
```python
# Fuse LoRA weights
pipe.fuse_lora(lora_scale=1.0)

# Or set scale explicitly
pipe.set_adapters(["lora_name"], adapter_weights=[1.0])

# Verify LoRA is loaded
print(list(pipe.unet.attn_processors.keys()))
```

### 多个LoRA发生冲突

**问题**：多个LoRA会生成异常内容

**解决方案**：
```python
# Load with different adapter names
pipe.load_lora_weights("lora1", adapter_name="style")
pipe.load_lora_weights("lora2", adapter_name="subject")

# Balance weights
pipe.set_adapters(
    ["style", "subject"],
    adapter_weights=[0.5, 0.5]  # Lower weights
)

# Or use LoRA merge before loading
# Merge LoRAs offline with appropriate ratios
```

## ControlNet 相关问题

### ControlNet 无法发挥控制作用

**问题**：ControlNet 对输出结果没有影响

**解决方案**：
```python
# Check control image format
# Should be RGB, matching generation size
control_image = control_image.resize((512, 512))

# Increase conditioning scale
image = pipe(
    prompt=prompt,
    image=control_image,
    controlnet_conditioning_scale=1.0,  # Try 0.5-1.5
    num_inference_steps=30
).images[0]

# Verify ControlNet is loaded
print(pipe.controlnet)
```

### 控制图像预处理

**修复方案**：
```python
from controlnet_aux import CannyDetector

# Proper preprocessing
canny = CannyDetector()
control_image = canny(input_image)

# Ensure correct format
control_image = control_image.convert("RGB")
control_image = control_image.resize((512, 512))
```

## Hub/下载相关问题

### 模型下载失败

**错误信息**：`requests.exceptions.ConnectionError`

**解决方案**：
```bash
# Set longer timeout
export HF_HUB_DOWNLOAD_TIMEOUT=600

# Use mirror if available
export HF_ENDPOINT=https://hf-mirror.com

# Or download manually
huggingface-cli download stable-diffusion-v1-5/stable-diffusion-v1-5
```

### 缓存问题

**错误信息**：`OSError: 无法从缓存中加载模型`

**解决方案**：
```bash
# Clear cache
rm -rf ~/.cache/huggingface/hub

# Or set different cache location
export HF_HOME=/path/to/cache

# Force re-download
pipe = DiffusionPipeline.from_pretrained(
    "model-id",
    force_download=True
)
```

### 受保护模型访问被拒

**错误信息**：`401 客户端错误：未经授权`

**解决方案**：
```bash
# Login to Hugging Face
huggingface-cli login

# Or use token
pipe = DiffusionPipeline.from_pretrained(
    "model-id",
    token="hf_xxxxx"
)

# Accept model license on Hub website first
```

## 性能问题

### 生成速度过慢

**问题**：内容生成耗时过长

**解决方案**：
```python
# Solution 1: Use faster scheduler
from diffusers import DPMSolverMultistepScheduler
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config
)

# Solution 2: Reduce steps
image = pipe(prompt, num_inference_steps=20).images[0]

# Solution 3: Use LCM
from diffusers import LCMScheduler
pipe.load_lora_weights("latent-consistency/lcm-lora-sdxl")
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
image = pipe(prompt, num_inference_steps=4, guidance_scale=1.0).images[0]

# Solution 4: Enable xFormers
pipe.enable_xformers_memory_efficient_attention()

# Solution 5: Compile model
pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
```

### 第一代速度较慢

**问题**：生成第一张图片所需时间过长

**解决方案**：
```python
# Warm up the model
_ = pipe("warmup", num_inference_steps=1)

# Then run actual generation
image = pipe(prompt, num_inference_steps=50).images[0]

# Compile for faster subsequent runs
pipe.unet = torch.compile(pipe.unet)
```

## 调试技巧

### 启用调试日志记录

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific modules
logging.getLogger("diffusers").setLevel(logging.DEBUG)
logging.getLogger("transformers").setLevel(logging.DEBUG)
```

### 检查模型组件

```python
# Print pipeline components
print(pipe.components)

# Check model config
print(pipe.unet.config)
print(pipe.vae.config)
print(pipe.scheduler.config)

# Verify device placement
print(pipe.device)
for name, module in pipe.components.items():
    if hasattr(module, 'device'):
        print(f"{name}: {module.device}")
```

### 验证输入参数

```python
# Check image dimensions
print(f"Height: {height}, Width: {width}")
assert height % 8 == 0, "Height must be divisible by 8"
assert width % 8 == 0, "Width must be divisible by 8"

# Check prompt tokenization
tokens = pipe.tokenizer(prompt, return_tensors="pt")
print(f"Token count: {tokens.input_ids.shape[1]}")  # Max 77 for SD
```

### 保存中间结果

```python
def save_latents_callback(pipe, step_index, timestep, callback_kwargs):
    latents = callback_kwargs["latents"]

    # Decode and save intermediate
    with torch.no_grad():
        image = pipe.vae.decode(latents / pipe.vae.config.scaling_factor).sample
    image = (image / 2 + 0.5).clamp(0, 1)
    image = image.cpu().permute(0, 2, 3, 1).numpy()[0]
    Image.fromarray((image * 255).astype("uint8")).save(f"step_{step_index}.png")

    return callback_kwargs

image = pipe(
    prompt,
    callback_on_step_end=save_latents_callback,
    callback_on_step_end_tensor_inputs=["latents"]
).images[0]
```

## 获取帮助

1. **文档说明**：https://huggingface.co/docs/diffusers  
2. **GitHub 问题报告**：https://github.com/huggingface/diffusers/issues  
3. **Discord 社群**：https://discord.gg/diffusers  
4. **论坛讨论**：https://discuss.huggingface.co  

### 报告问题时请提供以下信息

- Diffusers 版本：`pip show diffusers`  
- PyTorch 版本：`python -c "import torch; print(torch.__version__)"`  
- CUDA 版本：`nvcc --version`  
- GPU 型号：`nvidia-smi`  
- 完整的错误堆栈信息  
- 最简可复现代码示例  
- 所使用的模型名称/ID
