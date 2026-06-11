# llama.cpp 的 Hugging Face URL 工作流

请优先使用仅基于 URL 的工作流。在查找 GGUF 文件、选择量化级别或构建 `llama-server` 命令时，无需依赖 `hf` 库或任何 API 客户端。 

## 核心 URL 地址

```text
Search:
https://huggingface.co/models?apps=llama.cpp&sort=trending

Search with text:
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending

Search with size bounds:
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending

Repo local-app view:
https://huggingface.co/<repo>?local-app=llama.cpp

Repo tree API:
https://huggingface.co/api/models/<repo>/tree/main?recursive=true

Repo file tree:
https://huggingface.co/<repo>/tree/main
```

## 1. 搜索兼容 llama.cpp 的模型

请从带有 `apps=llama.cpp` 参数的模型页面开始搜索。

可使用以下参数：
- `search=<term>`：用于指定模型系列名称，如 `Qwen`、`Gemma`、`Phi` 或 `Mistral`
- `num_parameters=min:0,max:24B` 及类似参数：适用于硬件性能有限的用户
- `sort=trending`：用于查找当前最受欢迎的仓库

如果用户尚未选定模型系列，请勿直接从随机生成的 GGUF 仓库开始搜索。应先进行搜索，再筛选候选项。

示例链接：https://huggingface.co/models?search=Qwen&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending

## 2. 使用 local-app 页面查看推荐的量化方案

打开：

```text
https://huggingface.co/<repo>?local-app=llama.cpp
```

按顺序提取以下内容：

1. 若有显示，提取完整的“Use this model”文本片段；
2. 从获取的页面文本或HTML中提取“Hardware compatibility”部分的内容，包括：
   - 量化标签
   - 文件大小
   - 位深分类信息
3. 片段中显示的任何其他启动参数，例如`--jinja`。

当“HF local-app”片段存在时，应以该片段为准。

请直接读取URL内容来完成提取，切勿依赖浏览器渲染的界面。如果获取的页面源代码中没有展示“Hardware compatibility”部分，则说明该部分不可见，此时应转而使用树形API，并参考`quantization.md`中的通用指南。

## 3. 通过树形API确认具体文件信息

打开：

```text
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

请将 JSON 响应视为仓库清单的权威数据来源。

保留以下类型的条目：

- `type` 的值为 `file`
- `path` 以 `.gguf` 结尾

使用以下字段：

- `path` 用于表示文件名和子目录路径
- `size` 用于表示字节大小
- 可选地使用 `lfs.size` 来确认 LFS 数据包的大小

将文件分类为以下几类：

- 已量化的单文件检查点，例如 `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`
- 投影器权重文件，通常为 `mmproj-*.gguf` 格式
- BF16 分片文件，通常位于 `BF16/` 目录下
- 其余所有文件

除非用户另有要求，否则忽略以下内容：

- `README.md`
- imatrix 文件或校准数据块

仅在 API 接口失效或用户希望查看网页版本时，才将 `https://huggingface.co/<repo>/tree/main` 作为人工备选方案使用。

## 4. 构建命令

推荐的操作顺序如下：

1. 从 local-app 页面复制精确的 HF 代码片段
2. 如果页面显示了明确的量化标签，则可使用简写方式选择对应文件

```bash
llama-server -hf <repo>:<QUANT>
```

3. 如果需要从 tree API 获取特定的文件，可使用针对该文件的专用表单：

```bash
llama-server --hf-repo <repo> --hf-file <filename.gguf>
```

4. 若希望在不使用服务器的情况下通过 CLI 进行操作，请使用：

```bash
llama-cli -hf <repo>:<QUANT>
```

当仓库使用了自定义标签或非标准命名方式，从而导致`:<QUANT>`的含义模糊不清时，请使用“精确文件”格式。

## 5. 示例：`unsloth/Qwen3.6-35B-A3B-GGUF`

请使用以下 URL：

```text
https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF?local-app=llama.cpp
https://huggingface.co/api/models/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main?recursive=true
https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/tree/main
```

在 local-app 页面中，硬件兼容性部分会显示如下信息：

- `UD-IQ4_XS` - 17.7 GB
- `UD-Q4_K_S` - 20.9 GB
- `UD-Q4_K_M` - 22.1 GB
- `UD-Q5_K_M` - 26.5 GB
- `UD-Q6_K` - 29.3 GB
- `Q8_0` - 36.9 GB

通过 tree API，则可以获取确切的文件名，例如：

- `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`
- `Qwen3.6-35B-A3B-UD-Q5_K_M.gguf`
- `Qwen3.6-35B-A3B-UD-Q6_K.gguf`
- `Qwen3.6-35B-A3B-Q8_0.gguf`
- `mmproj-F16.gguf`

该仓库的理想最终输出结果应为：

```text
Repo: unsloth/Qwen3.6-35B-A3B-GGUF
Recommended quant from HF: UD-Q4_K_M (22.1 GB)
llama-server: llama-server --hf-repo unsloth/Qwen3.6-35B-A3B-GGUF --hf-file Qwen3.6-35B-A3B-UD-Q4_K_M.gguf
Other GGUFs:
- Qwen3.6-35B-A3B-UD-Q5_K_M.gguf - 26.5 GB
- Qwen3.6-35B-A3B-UD-Q6_K.gguf - 29.3 GB
- Qwen3.6-35B-A3B-Q8_0.gguf - 36.9 GB
Projector:
- mmproj-F16.gguf - 899 MB
```

## 备注

- 代码库特定的量化标签非常重要。除非页面本身有相应说明，否则请勿将 `UD-Q4_K_M` 改写为 `Q4_K_M`。
- `mmproj` 文件是多模态模型的投影器权重，而非主语言模型检查点。
- 如果由于用户未配置硬件配置文件，或获取的页面源代码未显示相关内容而导致 HF 硬件兼容性面板缺失，仍应使用树形 API，并参考 `quantization.md` 中的通用量化指南。
- 如果该代码库已存在 GGUF 格式的模型文件，则无需直接进入转换流程。
