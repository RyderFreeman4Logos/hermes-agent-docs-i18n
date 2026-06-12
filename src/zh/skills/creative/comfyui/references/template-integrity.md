# ComfyUI 工作流模板完整性规范

> **由 [@purzbeats](https://github.com/purzbeats)** 撰写 — 改编自
> [purzbeats/hermes-agent-comfyui-helper](https://github.com/purzbeats/hermes-agent-comfyui-helper)。
> 当需要将官方的 `comfyui-workflow-templates` 包（编辑器格式）转换为可通过 `/api/prompt` 提交的 API 格式时，请参考本规范。若不遵循这些规则，转换过程中可能会存在一些容易被忽视的问题，从而导致难以诊断的验证错误。

## 背景

官方的 ComfyUI 模板包（`comfyui-workflow-templates`，当前版本为 v0.9.69）会被安装在 ComfyUI 虚拟环境中的如下路径：

```
<comfy-install>/.venv/lib/python3.*/site-packages/comfyui_workflow_templates_*/templates/
```

具体路径取决于 ComfyUI 的安装方式（comfy-cli 默认方式、Comfy Desktop、手动创建的虚拟环境等）。可通过以下方法查询出该路径：

```bash
comfy --workspace <ws> run-python -c "import comfyui_workflow_templates, pathlib; print(pathlib.Path(comfyui_workflow_templates.__file__).parent / 'templates')"
```

模板以**编辑器格式**提供——即位于`data['definitions']['subgraphs'][0]`内的`nodes`/`links`数组。在提交之前，必须将其转换为**API格式**（即`node_id -> {class_type, inputs}`的映射结构）。

---

## 规则 #1：尽可能保持模板与原始设计的接近性

- **严禁**从模板中删除、简化或“精简”任何节点。
- 模板的完整架构（双阶段处理流程、LoRA链、精简后的sigma参数、条件路径等）都是经过精心设计的——移除任何部分都会影响生成质量。
- 如果存在依赖图像的路径，但任务类型为文本转视频，**请保持该路径连接状态并开启旁路开关**——切勿删除相关节点。
- 仅可在明确要求时更改提示词文本、种子值及分辨率。

## 规则 #2：服务器验证错误为最终依据

当工作流提交失败时，服务器返回的响应如下所示：

```json
{
  "node_errors": {
    "238": {
      "errors": [{
        "message": "Required input is missing",
        "details": "width",
        "extra_info": { "input_name": "resize_type.width" }
      }]
    }
  }
}
```

**`extra_info.input_name` 字段会明确告知服务器需要的是哪个 JSON 键值。请严格按照其指示使用。** 如果该字段显示为 `"values.a"` 或 `"resize_type.width"`，这些就是 JSON 对象中实际的键名。切勿基于对该字段“应称为何”的猜测，将其“简化”为扁平化的名称。

## 规则 #3：不要从头重建——直接修复出问题的节点

每次从模板重新生成都会引入同样的错误。正确的做法是：

1. 先提交一次工作流。
2. 查看服务器返回的错误详情，获取准确的键名。
3. 对磁盘上的工作流文件进行有针对性的修补或修改。
4. 重新提交并检查错误是否已解决。

---

## 路由节点：绕过而非删除

大多数服务器（本地或云端）都不支持 `Reroute` 节点类型。在转换模板时：

1. 查看 `target_id` 等于该 `Reroute` 节点 ID 的链接，找出所有连接到该节点的输入。
2. 将所有引用 `Reroute` 的输入替换为 `[source_node_id, source_slot]` 的格式。
3. 从 API 映射中删除该 `Reroute` 节点。

**实际示例——LTX 2.3 t2v 模板：**

- `Reroute` 节点 255 从 `CheckpointLoaderSimple 236` 的第 2 个槽位接收 VAE 数据。
- 有三个节点将其 VAE 输入引向 `Reroute` 255：`LTXVImgToVideoInplace`（230）、`LTXVLatentUpsampler`（253）以及 `VAEDecodeTiled`（251）。
- 修复方法：将所有 `vae: ["255", 0]` 的格式替换为 `vae: ["236", 2]`。
- `CheckpointLoaderSimple` 的第 2 个槽位对应的是 VAE 数据（而非第 0 个槽位的模型数据）。

| | |
|---|---|
| ❌ 错误方式 | `vae: ["236", 0]` → 导致 `input_type(VAE)` 不匹配错误 |
| ✅ 正确方式 | `vae: ["236", 2]` |

---

## 动态模板节点：带点号的键名是正确的

### ComfyMathExpression (COMFY_AUTOGROW_V3)

```json
{
  "class_type": "ComfyMathExpression",
  "inputs": {
    "expression": "a/2",
    "values.a": ["257", 0]
  }
}
```

- `values` 为 `COMFY_AUTOGROW_V3` 类型的模板。  
- 链接中的输入名称分别为 `values.a`、`values.b` 等。  
- **请保持 JSON 键采用点号分隔的形式。**  
- 不要将其转换为 `{"values": {"a": ...}}` 的结构，也不要将其扁平化为仅 `"a"` 的形式。  

### ResizeImageMaskNode (COMFY_DYNAMICCOMBO_V3)

```json
{
  "class_type": "ResizeImageMaskNode",
  "inputs": {
    "input": ["276", 0],
    "scale_method": "lanczos",
    "resize_type": "scale dimensions",
    "resize_type.width": 1920,
    "resize_type.height": 1088,
    "resize_type.crop": "center"
  }
}
```

- `resize_type` 的值为 `COMFY_DYNAMICCOMBO_V3`。
- 各模式特定的字段包括：`resize_type.width`、`resize_type.height`、`resize_type.crop`。
- `scale_method` 的可选值有：`"nearest-exact"`、`"bilinear"`、`"area"`、`"bicubic"`、`"lanczos"`。
- **JSON 键名请保持点号格式不变。**
- 严禁将 `resize_type.width` 简化为仅 `"width"` 这种形式。

---

## 转换步骤

1. 从已安装的包路径中加载模板。
2. 解析 `data['definitions']['subgraphs'][0]`。
3. 遍历每个节点（跳过 Reroute 节点）：
   - 从 `sg['links']` 字典中获取关联的输入项。
   - 将 `widgets_values` 映射为对应的输入字段名称。
   - 保留模板中所有的点号格式键名不变。
4. 跳过 Reroute 节点：追踪数据来源并替换引用路径。
5. 仅修改提示词文本、种子值以及用户指定的参数。
6. 如果模板仅包含 `CreateVideo` 节点，则需添加 `SaveVideo` 终端节点。
7. 提交 → 检查错误 → 修复特定节点 → 再次提交。

## 模板中绝不能修改的内容

| 元素 | 原因 |
|------|------|
| 节点拓扑结构 | 图结构是针对特定模型设计的 |
| Sigmas 值 | 已根据模型与采样器的组合进行优化 |
| LoRA/蒸馏路径 | 即使看似未使用，也是保障质量所必需的 |
| 模型参数（cfg、steps、shifts） | 为特定模型设计 |
| 条件化链（零值处理、裁剪引导） | 对实现正确的条件化处理必不可少 |
| 直通连接线路 | 不要删除节点，也不要绕过它们 |

---

## 云平台兼容性（2025年5月验证）

完整的 LTX 2.3 T2V 模板（`video_ltx2_3_t2v.json`）无需任何修改即可在 Comfy Cloud 上运行。

**已在云平台上验证可用（所有自定义节点均支持）：**
`ComfyMathExpression`、`ResizeImageMaskNode`、`ResizeImagesByLongerEdge`、
`PrimitiveInt`、`PrimitiveStringMultiline`、`PrimitiveBoolean`、`SaveVideo`、
`LTXVCropGuides`、`LTXVImgToVideoInplace`、`LTXVConcatAVLatent`、
`LTXVSeparateAVLatent`、`LTXVLatentUpsampler`、`LTXVAudioVAELoader`、
`LTXVAudioVAEDecode`、`LTXVEmptyLatentAudio`、`LTXVPreprocess`、
`LTXVConditioning`、`ManualSigmas`、`LTXAVTextEncoderLoader`，以及所有核心节点。

**LTX 2.3 在云平台与本地环境下的性能对比（768x512分辨率）：**

- 云平台：每段视频处理时间约为39秒（速度是本地环境的4倍）。
- 本地环境（RTX 5090）：每段视频处理时间约为160秒。
- 云平台支持使用 `example.png` 作为占位符，用于绕过依赖图像的路径。
- 本地环境与云平台的提交格式完全相同：
  将 `{"prompt": wf, "extra_data": {}}` 发送到 `/api/prompt` 接口。
- 免费套餐允许同时运行1个任务。

**在云平台提交时需注意的常见问题：**

- 在免费套餐下，访问 `/api/object_info/<node>` 会返回404错误——无法远程查询节点结构，但工作流仍可正常运行。构建工作流之前，请务必先在本地测试 `object_info` 功能。
- 云平台的处理速度约为本地环境的4倍——除非需要本地环境进行调试，否则建议使用云平台进行批量处理。
- 云平台的 `/api/view` 接口会返回**302重定向到带签名的GCS地址**——需使用 `curl -s -L` 命令来跟随链接并下载文件。Python的 `urllib` 库会因401错误而失败（因为认证信息会被转发到GCS CDN）。
- `COMFY_CLOUD_API_KEY` 只存在于终端/bash环境变量中，不会出现在Python沙箱环境中。进行云平台API调用时，请使用subprocess或终端脚本。
- 云平台的免费套餐是**顺序处理任务**的（一次仅处理1个）。建议一次性提交所有任务，然后再查看处理历史记录。
- LTX 2.3在本地处理1920x1080分辨率的任务时会出现内存不足问题（即使使用RTX 5090也是如此）——因为上采样步骤会超出显存容量。对于1080p分辨率的任务，建议使用云平台处理；若要在本地处理，则建议设置为1280x720分辨率（处理时间约为每段视频90秒）。

---

## FFmpeg拼接设置（兼容Discord）

ComfyUI生成的视频通常采用`yuv444p`像素格式，该格式在Discord上无法正常显示。需使用以下命令重新编码：

```bash
ffmpeg -y -i input.mp4 \
  -c:v libx264 -profile:v main -preset medium -crf 13 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  output_discord.mp4
```

关键设置：

- `-pix_fmt yuv420p` — **Discord平台必需**，ComfyUI默认输出的格式为`yuv444p`。
- `-crf 13` — 在不大幅增加文件大小的前提下保持高画质（默认值23的压缩损失过大）。
- `-profile:v main` — 兼容性极佳。

如需对多个视频进行交叉淡入淡出拼接，可依次使用`xfade`（用于视频）和`acrossfade`（用于音频）。

```bash
ffmpeg -y -i a.mp4 -i b.mp4 -i c.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=3.04[v1];[v1][2:v]xfade=transition=fade:duration=1:offset=6.08[vout];[0:a][1:a]acrossfade=duration=1:c1=tri:c2=tri[a1];[a1][2:a]acrossfade=duration=1:c1=tri:c2=tri[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -profile:v main -crf 13 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  output.mp4
```

xfade效果的第#N个偏移值计算公式为：`(N+1) × duration - N × overlap`。
