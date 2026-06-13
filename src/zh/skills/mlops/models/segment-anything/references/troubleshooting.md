# Segment Anything 故障排除指南

## 安装问题

### 未检测到 CUDA

**错误信息**：`RuntimeError: CUDA not available`

**解决方案**：
```python
# Check CUDA availability
import torch
print(torch.cuda.is_available())
print(torch.version.cuda)

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# If CUDA works but SAM doesn't use it
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to("cuda")  # Explicitly move to GPU
```

### 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'segment_anything'`

**解决方案**：
```bash
# Install from GitHub
pip install git+https://github.com/facebookresearch/segment-anything.git

# Or clone and install
git clone https://github.com/facebookresearch/segment-anything.git
cd segment-anything
pip install -e .

# Verify installation
python -c "from segment_anything import sam_model_registry; print('OK')"
```

### 缺少依赖项

**错误提示**：`ModuleNotFoundError: No module named 'cv2'` 或类似错误

**解决方案**：
```bash
# Install all optional dependencies
pip install opencv-python pycocotools matplotlib onnxruntime onnx

# For pycocotools on Windows
pip install pycocotools-windows
```

## 模型加载问题

### 未找到检查点文件

**错误信息**：`FileNotFoundError: checkpoint file not found`

**解决方案**：
```bash
# Download correct checkpoint
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# Verify file integrity
md5sum sam_vit_h_4b8939.pth
# Expected: a7bf3b02f3ebf1267aba913ff637d9a2

# Use absolute path
sam = sam_model_registry["vit_h"](checkpoint="/full/path/to/sam_vit_h_4b8939.pth")
```

### 模型类型不匹配

**错误信息**：`KeyError: 'unexpected key in state_dict'`

**解决方案**：
```python
# Ensure model type matches checkpoint
# vit_h checkpoint → vit_h model
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")

# vit_l checkpoint → vit_l model
sam = sam_model_registry["vit_l"](checkpoint="sam_vit_l_0b3195.pth")

# vit_b checkpoint → vit_b model
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")
```

### 加载过程中内存不足

**错误信息**：在加载模型时出现“CUDA内存不足”的错误。

**解决方案**：
```python
# Use smaller model
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")

# Load to CPU first, then move
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to("cpu")
torch.cuda.empty_cache()
sam.to("cuda")

# Use half precision
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam = sam.half()
sam.to("cuda")
```

## 推理问题

### 图像格式错误

**错误信息**：`ValueError: expected input to have 3 channels`

**解决方案**：
```python
import cv2

# Ensure RGB format
image = cv2.imread("image.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR to RGB

# Convert grayscale to RGB
if len(image.shape) == 2:
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

# Handle RGBA
if image.shape[2] == 4:
    image = image[:, :, :3]  # Drop alpha channel
```

### 坐标错误

**错误提示**：`IndexError: index out of bounds` 或掩码位置不正确

**解决方案**：
```python
# Ensure points are (x, y) not (row, col)
# x = column index, y = row index
point = np.array([[x, y]])  # Correct

# Verify coordinates are within image bounds
h, w = image.shape[:2]
assert 0 <= x < w and 0 <= y < h, "Point outside image"

# For bounding boxes: [x1, y1, x2, y2]
box = np.array([x1, y1, x2, y2])
assert x1 < x2 and y1 < y2, "Invalid box coordinates"
```

### 空掩码或错误掩码

**问题**：掩码与目标对象不匹配

**解决方案**：
```python
# Try multiple prompts
input_points = np.array([[x1, y1], [x2, y2]])
input_labels = np.array([1, 1])  # Multiple foreground points

# Add background points
input_points = np.array([[obj_x, obj_y], [bg_x, bg_y]])
input_labels = np.array([1, 0])  # 1=foreground, 0=background

# Use box prompt for large objects
box = np.array([x1, y1, x2, y2])
masks, scores, _ = predictor.predict(box=box, multimask_output=False)

# Combine box and point
masks, scores, _ = predictor.predict(
    point_coords=np.array([[center_x, center_y]]),
    point_labels=np.array([1]),
    box=np.array([x1, y1, x2, y2]),
    multimask_output=True
)

# Check scores and select best
print(f"Scores: {scores}")
best_mask = masks[np.argmax(scores)]
```

### 推理速度过慢

**问题**：预测耗时过长

**解决方案**：
```python
# Use smaller model
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")

# Reuse image embeddings
predictor.set_image(image)  # Compute once
for point in points:
    masks, _, _ = predictor.predict(...)  # Fast, reuses embeddings

# Reduce automatic generation points
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,  # Default is 32
)

# Use ONNX for deployment
# Export: python scripts/export_onnx_model.py --return-single-mask
```

## 自动遮罩生成问题

### 遮罩数量过多

**问题**：生成数千个相互重叠的遮罩

**解决方案**：
```python
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,          # Reduce from 32
    pred_iou_thresh=0.92,        # Increase from 0.88
    stability_score_thresh=0.98,  # Increase from 0.95
    box_nms_thresh=0.5,          # More aggressive NMS
    min_mask_region_area=500,    # Remove small masks
)
```

### 掩码数量不足

**问题**：自动生成时缺少对象

**解决方案**：
```python
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=64,          # Increase density
    pred_iou_thresh=0.80,        # Lower threshold
    stability_score_thresh=0.85,  # Lower threshold
    crop_n_layers=2,             # Add multi-scale
    min_mask_region_area=0,      # Keep all masks
)
```

### 小型物体被遗漏

**问题**：自动检测功能会忽略小型物体

**解决方案**：
```python
# Use crop layers for multi-scale detection
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    crop_n_layers=2,
    crop_n_points_downscale_factor=1,  # Don't reduce points in crops
    min_mask_region_area=10,  # Very small minimum
)

# Or process image patches
def segment_with_patches(image, patch_size=512, overlap=64):
    h, w = image.shape[:2]
    all_masks = []

    for y in range(0, h, patch_size - overlap):
        for x in range(0, w, patch_size - overlap):
            patch = image[y:y+patch_size, x:x+patch_size]
            masks = mask_generator.generate(patch)

            # Offset masks to original coordinates
            for m in masks:
                m['bbox'][0] += x
                m['bbox'][1] += y
                # Offset segmentation mask too

            all_masks.extend(masks)

    return all_masks
```

## 内存问题

### CUDA 内存不足

**错误信息**：`torch.cuda.OutOfMemoryError: CUDA 内存不足`

**解决方案**：
```python
# Use smaller model
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")

# Clear cache between images
torch.cuda.empty_cache()

# Process images sequentially, not batched
for image in images:
    predictor.set_image(image)
    masks, _, _ = predictor.predict(...)
    torch.cuda.empty_cache()

# Reduce image size
max_size = 1024
h, w = image.shape[:2]
if max(h, w) > max_size:
    scale = max_size / max(h, w)
    image = cv2.resize(image, (int(w*scale), int(h*scale)))

# Use CPU for large batch processing
sam.to("cpu")
```

### 内存不足

**问题**：系统内存耗尽

**解决方案**：
```python
# Process images one at a time
for img_path in image_paths:
    image = cv2.imread(img_path)
    masks = process_image(image)
    save_results(masks)
    del image, masks
    gc.collect()

# Use generators instead of lists
def generate_masks_lazy(image_paths):
    for path in image_paths:
        image = cv2.imread(path)
        masks = mask_generator.generate(image)
        yield path, masks
```

## ONNX 导出问题

### 导出失败

**错误提示**：多种不同的导出错误

**解决方案**：
```bash
# Install correct ONNX version
pip install onnx==1.14.0 onnxruntime==1.15.0

# Use correct opset version
python scripts/export_onnx_model.py \
    --checkpoint sam_vit_h_4b8939.pth \
    --model-type vit_h \
    --output sam.onnx \
    --opset 17
```

### ONNX 运行时错误

**错误信息**：推理过程中出现 `ONNXRuntimeError` 错误。

**解决方案**：
```python
import onnxruntime

# Check available providers
print(onnxruntime.get_available_providers())

# Use CPU provider if GPU fails
session = onnxruntime.InferenceSession(
    "sam.onnx",
    providers=['CPUExecutionProvider']
)

# Verify input shapes
for input in session.get_inputs():
    print(f"{input.name}: {input.shape}")
```

## HuggingFace 集成问题

### 处理器错误

**错误类型**：SamProcessor 相关问题

**解决方案**：
```python
from transformers import SamModel, SamProcessor

# Use matching processor and model
model = SamModel.from_pretrained("facebook/sam-vit-huge")
processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")

# Ensure input format
input_points = [[[x, y]]]  # Nested list for batch dimension
inputs = processor(image, input_points=input_points, return_tensors="pt")

# Post-process correctly
masks = processor.image_processor.post_process_masks(
    outputs.pred_masks.cpu(),
    inputs["original_sizes"].cpu(),
    inputs["reshaped_input_sizes"].cpu()
)
```

## 质量问题

### 面具边缘不平滑

**问题**：面具的边缘粗糙且呈现像素化现象

**解决方案**：
```python
import cv2
from scipy import ndimage

def smooth_mask(mask, sigma=2):
    """Smooth mask edges."""
    # Gaussian blur
    smooth = ndimage.gaussian_filter(mask.astype(float), sigma=sigma)
    return smooth > 0.5

def refine_edges(mask, kernel_size=5):
    """Refine mask edges with morphological operations."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    # Close small gaps
    closed = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    # Open to remove noise
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
    return opened.astype(bool)
```

### 分割不完整

**问题**：掩码未能覆盖整个对象

**解决方案**：
```python
# Add multiple points
input_points = np.array([
    [obj_center_x, obj_center_y],
    [obj_left_x, obj_center_y],
    [obj_right_x, obj_center_y],
    [obj_center_x, obj_top_y],
    [obj_center_x, obj_bottom_y]
])
input_labels = np.array([1, 1, 1, 1, 1])

# Use bounding box
masks, _, _ = predictor.predict(
    box=np.array([x1, y1, x2, y2]),
    multimask_output=False
)

# Iterative refinement
mask_input = None
for point in points:
    masks, scores, logits = predictor.predict(
        point_coords=point.reshape(1, 2),
        point_labels=np.array([1]),
        mask_input=mask_input,
        multimask_output=False
    )
    mask_input = logits
```

## 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| `CUDA out of memory` | GPU内存已满 | 使用更小的模型，清除缓存 |
| `expected 3 channels` | 图像格式不正确 | 转换为RGB格式 |
| `index out of bounds` | 坐标无效 | 检查点/框的边界范围 |
| `checkpoint not found` | 路径错误 | 使用绝对路径 |
| `unexpected key` | 模型与检查点不匹配 | 确保模型类型一致 |
| `invalid box coordinates` | x1 > x2 或 y1 > y2 | 修正框的坐标格式 |

## 获取帮助

1. **GitHub问题跟踪页**：https://github.com/facebookresearch/segment-anything/issues
2. **HuggingFace论坛**：https://discuss.huggingface.co
3. **相关论文**：https://arxiv.org/abs/2304.02643

### 报告问题时请提供以下信息：

- Python版本
- PyTorch版本：`python -c "import torch; print(torch.__version__)"`
- CUDA版本：`python -c "import torch; print(torch.version.cuda)"`
- SAM模型类型（vit_b/l/h）
- 完整的错误堆栈跟踪信息
- 最简可复现代码示例
